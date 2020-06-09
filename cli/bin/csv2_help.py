from subprocess import Popen, PIPE
import os
import shutil
import tempfile

def help(gvar, mandatory=None, required=None, options=None, requires_server=True):
    """
    Print long and short help messages.
    """


    # If help requested, display the help for the current command.
    if gvar['user_settings']['help']:
        if not gvar['object']:
            print('Usage: cloudscheduler <object> <action> [<options>]')
            print('Help requested for "cloudscheduler". One of the following objects must be specified:')
            for obj in sorted(gvar['actions']):
                if gvar['super_user'] or not gvar['actions'][obj][0]:
                    print('  %s' % obj)

        elif gvar['object'] not in gvar['actions']:
            print('Usage: cloudscheduler <object> <actions> [<options>]')
            print('Help requested for "cloudscheduler %s". The specified object is invalid. One of the following must be specified:' % gvar['object'])
            for obj in sorted(gvar['actions']):
                if gvar['super_user'] or not gvar['actions'][obj][0]:
                    print('  %s' % obj)

        elif not gvar['action']:
            print('Usage: cloudscheduler {} <action> [<options>]'.format(gvar['object']))
            print('Help requested for "cloudscheduler %s". One of the following actions must be specified:' % gvar['object'])
            for action in sorted(gvar['actions'][gvar['object']][1]):
                print('  %s' % action)

        elif gvar['action'] not in gvar['actions'][gvar['object']][1]:
            print('Usage: cloudscheduler {} <action> [<options>]'.format(gvar['object']))
            print('Help requested for "cloudscheduler %s %s". The specified action is invalid. One of the following must be specified:' % (gvar['object'], gvar['action']))
            for action in sorted(gvar['actions'][gvar['object']][1]):
                print('  %s' % action)

        else:
            print('Usage: cloudscheduler {} {} [<options>]'.format(gvar['object'], gvar['action']))
            if requires_server and 'server-address' not in gvar['user_settings']:
                print('*')
                print('* The "cloudscheduler %s %s" command sends requests to a cloudscheduler server and requires the server' % (gvar['object'], gvar['action']))
                print('* address and your identity (either by user name and password or by grid certificate and key). The following')
                print('* parameters provide the required information:')
                print('*   -sa  |  --server-address')
                print('*   -sgc |  --server-grid-cert')
                print('*   -sgk |  --server-grid-key')
                print('*   -spw |  --server-password')
                print('*   -su  |  --server-user')
                print('*')
                print('* These messages are displayed because you have not used the "cloudscheduler defaults set" command to save')
                print('* the server address and your identity for the server "%s".' % gvar['pid_defaults']['server'])
                print('*')

            if mandatory:
                print('Help requested for "cloudscheduler %s %s". The following parameters are mandatory and must be specified on the command line:' % (gvar['object'], gvar['action']))
                for key in mandatory:
                    print('  %s' % key[1])

            if required:
                if mandatory:
                    print('A command line or a default value is required for the following parameters:')
                else:
                    print('Help requested for "cloudscheduler %s %s". A command line or a default value is required for the following parameters:' % (gvar['object'], gvar['action']))
                for key in required:
                    print('  %s' % key[1])

            if options:
                if mandatory or required:
                    print('The following optional parameters may be specified:')
                else:
                    print('Help requested for "cloudscheduler %s %s". The following optional parameters may be specified:' % (gvar['object'], gvar['action']))
      
                for key in options:
                    print('  %s' % key[1])

            if not mandatory and not required and not options and not requires_server:
                print('Help requested for "cloudscheduler %s %s". There are no parameters for this command.' % (gvar['object'], gvar['action']))

        print('For more information, use -H.')

    # If long-help requested, use the "man" command to display the long-help for the current command.
    elif gvar['user_settings']['long-help']:
        # Determine man page and call display routine.
        if not gvar['object']:
            _long_help(gvar, 'cloudscheduler', 'csv2.1')

        elif gvar['object'] not in gvar['actions']:
            print('Long help requested for "cloudscheduler %s". The specified object is invalid. One of the following must be specified:' % gvar['object'])
            for obj in sorted(gvar['actions']):
                print('  %s' % obj)

        elif not gvar['action']:
            _long_help(gvar, 'cloudscheduler %s' % gvar['object'], 'csv2_%s.1' % gvar['object'])

        elif gvar['action'] not in gvar['actions'][gvar['object']][1]:
            print('Long help requested for "cloudscheduler %s %s". The specified action is invalid. One of the following must be specified:' % (gvar['object'], gvar['action']))
            for action in sorted(gvar['actions'][gvar['object']][1]):
                print('  %s' % action)

        else:
            _long_help(gvar, 'cloudscheduler %s %s' % (gvar['object'], gvar['action']), 'csv2_%s_%s.1' % (gvar['object'], gvar['action']))

    # No help requested, return to caller.
    else:
        return

    # Help requests just exit.
    exit(0)

def _long_help(gvar, man_id, man_page):
    """
    Internal function to print long help messages.
    """

    # Determine man page directory and issue the "man" command.
    for man_dir in [
        '%s/man' % os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '/usr/share/man/man1',
        '/usr/local/share/man/man1'
        ]:

        if os.path.isfile('%s/%s' % (man_dir, man_page)):
            help_page = man_page
        elif os.path.isfile('%s/%s.gz' % (man_dir, man_page)):
            help_page = '%s.gz' % man_page
        else:
            help_page = None

        if help_page:
            if gvar['platform'][:6].lower() == 'macos-':
                p1 = Popen(['groff', '-T', 'ascii', '-man', help_page], cwd=man_dir, stdout=PIPE, stderr=PIPE)
                p2 = Popen(['less'], cwd=man_dir, stdin=p1.stdout, stderr=PIPE)
                p2.communicate()
                return

            else:
                p = Popen(['man', '-l', help_page], cwd=man_dir, stderr=PIPE)
                p.communicate()
                if p.returncode == 0:
                    return

                tmp_dir = tempfile.mkdtemp()
                p = Popen(['cp', '-rp', man_dir, tmp_dir])
                p.communicate()

                p = Popen(['man', '-l', help_page], cwd='%s/man' % tmp_dir, stderr=PIPE)
                p.communicate()
                
                shutil.rmtree(tmp_dir)
                return

