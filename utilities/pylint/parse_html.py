'''
Post-processor for Pylint reports used by create_report.sh.
Adds the ability to hide / display messages, adds the time when the report was created, and adds tags around code blocks so that they are formatted properly.
'''

from datetime import datetime
from os.path import abspath, dirname
from re import fullmatch, match, search, sub
from sys import argv, stderr, stdin

def main():
    if len(argv) < 2:
        print('Usage: python3 parse_html.py current_git_branch')
        raise SystemExit
    branch = argv[1]
    
    dateCreated = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    # Adds a text input and buttons to hide or display given warning types. Adds the report creation time.
    injection = '''
        <script>
        function hide() {
            var toHide = document.getElementById('symbol').value;
            var rows = document.getElementsByTagName('tr');
            var i;
            for (i = 0; i < rows.length; i++)  {
                if (rows[i].innerHTML.indexOf(toHide) != -1) {
                    rows[i].style.display = 'none';
                }
            }
        }
        function unhide() {
            var toDisplay = document.getElementById('symbol').value;
            var rows = document.getElementsByTagName('tr');
            var i;
            for (i = 0; i < rows.length; i++)  {
                if (rows[i].innerHTML.indexOf(toDisplay) != -1) {
                    rows[i].style.display = '';
                }
            }
        }
        </script>\n''' + \
        f'<p>Report created at {dateCreated}.</p>\n' + \
        '''<p>Enter a message symbol to display or hide all messages with that symbol (eg import-error).</p>
        <input type='text' id='symbol'>
        <button onclick='hide()'>Hide</button>
        <button onclick='unhide()'>Unhide</button>
        '''

    # Parse each line of the HTML, embedding `injection` near the top, adding links to files on GitHub, and wrapping code in `<pre><code>` tags so that it is formatted nicely.
    new_row = False
    duplicate_code = False
    path = ''
    linkFrag = '<a href="https://github.com/hep-gc/cloudscheduler/tree/'
    for line in stdin:
        # Add links to lines on GitHub.
        if new_row:
            line = sub(r'<td>(\d+)</td>', lambda m: f'<td>{linkFrag}{branch}{path}#L{m[1]}" target="_blank">{m[1]}</a></td>', line)
            new_row = False
        elif not new_row and match(r'\s*<tr>', line):
            new_row = True
        # Add links to files on GitHub.
        elif match(r'\s*<h3>\s*Module', line):
            # (<code>/hepuser/grobertson/dev/cli/bin/csv2_accounting.py</code>)
            # /hepuser/grobertson/dev/
            # stable-2.6
            # cli/bin/csv2_accounting.py
            # https://github.com/hep-gc/cloudscheduler/tree/stable-2.6/cli/bin/csv2_accounting.py
            cloudschedulerRoot = fullmatch(r'(/.*)/[^/]*/[^/]*', dirname(abspath(__file__)))[1]
            path = search(r'\(<code>(.*)</code>\)', line)[1].replace(cloudschedulerRoot, '')
            # Notice that the double quote of the href as well as the tag is never closed. This is added in separately.
            tag = f'{linkFrag}{branch}{path}'
            line = sub(r'\(<code>(.*)</code>\)', lambda m: f'({tag}" target="_blank"><code>{m[1]}</code></a>)', line)
        # Add tags around code to format it nicely.
        elif not duplicate_code and match(r'\s*<td>Similar lines in \d+ files', line):
            duplicate_code = True
            line = line.replace('<td>', '<td><pre><code>')
        elif duplicate_code and '</td>' in line:
            line = line.replace('</td>', '</code></pre></td>')
            duplicate_code = False
        # Embed `injection`.
        elif match(r'\s*<h1>', line):
            line = f'{line}{injection}'
        print(line, end='')

if __name__ == '__main__':
    main()
