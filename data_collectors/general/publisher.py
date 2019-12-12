from cloudscheduler.lib.db_config import *
from cloudscheduler.lib.poller_functions import start_cycle, wait_cycle
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor

import multiprocessing
from multiprocessing import Process

from requests import get 
import logging
import os
import shutil
import sys
import shutil

def publish():
    multiprocessing.current_process().name = "Status Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), 'ProcessMonitor'], refreshable=True)

    menu_begin = [ 
        '<nav class="top-nav">\n',
        '  <ul style="background-color: #000000">\n',
        '    <div class="float-left">\n',
        '      <li class="spacer"> </li>\n',
        '      <li><a class="status-nav" href="/">All Groups</a></li>\n'
        ]   

    menu_end = [
        '    </div>\n'
        '  </ul>\n'
        '</nav>\n'
        ]   

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    try:
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.refresh()

            # Retrieve published status.
            csv2_response = get(
                '%s/cloud/published_status/' % config.categories[os.path.basename(sys.argv[0])]["csv2_url"],
                headers={'Accept': 'text/html', 'Referer': config.categories[os.path.basename(sys.argv[0])]["csv2_url"]},
                auth=(config.categories[os.path.basename(sys.argv[0])]["user"], config.categories[os.path.basename(sys.argv[0])]["password"])
                )
            html = csv2_response.content.decode('utf-8')

            # Split status page into useable blocks.
            html1 = html.split('<nav class="top-nav">', 1)
            html2 = html1[1].split('</nav>', 1)
            html3 = html2[1].split('status-nav', 1)
            html4 = html3[1].split('<!--publicize-->')

            # Remove private blocks.
            html5 = []
            groups = []
            public = True
            for block in html4:
                if '<!--private-->' == block[:14]:
                    public = False
                elif '<!--public-->' == block[:13]:
                    public = True
                elif '<!--group ' == block[:10]:
                    group = block[10:].split('-->', 1)
                    if group[0] != '' and group[0] not in groups:
                        groups.append(group[0])

                if public:
                    html5.append(block)

            menu_body = []
            for group in sorted(groups):
                menu_body.append('      <li><a class="%s-nav" href="/%s">%s</a></li>\n' % (group, group, group))

            # Create all groups public page (index.html).
            with open('%s/.no_show' % config.categories[os.path.basename(sys.argv[0])]["public_directory"], 'w') as fd: 
                fd.write(html1[0])
                fd.write(''.join(menu_begin + menu_body + menu_end))
                fd.write('%sstatus-nav' % html3[0])
                fd.write(''.join(html5))

            shutil.move('%s/.no_show' % config.categories[os.path.basename(sys.argv[0])]["public_directory"], '%s/index.html' % config.categories[os.path.basename(sys.argv[0])]["public_directory"])

            # Create a pulic page for each group.
            current_group = '-'
            for group in groups:
                public = True
                with open('%s/.no_show' % config.categories[os.path.basename(sys.argv[0])]["public_directory"], 'w') as fd:
                    fd.write(html1[0])
                    fd.write(''.join(menu_begin + menu_body + menu_end))
                    fd.write('<style> body.%s-nav{ position: absolute; top: 62px; padding-bottom: 129px; overflow: auto; } .%s-nav a.%s-nav { background: green; color:white; }</style>\n' % (group, group, group))
                    fd.write('%s%s-nav' % (html3[0], group))

                    for block in html5:
                        if '<!--group ' == block[:10]:
                            public = False
                            current_group = block[10:].split('-->', 1)[0]
                        elif '<!--group-end-->' == block[:16]:
                            public = True

                        if public or group == current_group:
                            fd.write(block)

                shutil.move('%s/.no_show' % config.categories[os.path.basename(sys.argv[0])]["public_directory"], '%s/%s' % (config.categories[os.path.basename(sys.argv[0])]["public_directory"], group))

            wait_cycle(cycle_start_time, poll_time_history, config.categories[os.path.basename(sys.argv[0])]["sleep_interval_publish"])

    except Exception as exc:
        logging.exception("Problem during general execution:")
        logging.exception(exc)
        logging.error("Exiting..")
        config.db_close()
        exit(1)


if __name__ == '__main__':

    process_ids = {
        'publish': publish,
    }

    procMon = ProcessMonitor(config_params=[os.path.basename(sys.argv[0]), "ProcessMonitor"], pool_size=8, orange_count_row='csv2_publisher_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()

    logging.info("**************************** starting publisher *********************************")

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            config.refresh()
            procMon.check_processes()
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
