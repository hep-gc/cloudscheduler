'''
Post-processor for Pylint reports used by create_report.sh.
Adds the ability to hide / display messages, adds the time when the report was created, and adds tags around code blocks so that they are formatted properly.
'''

from sys import stdin
from datetime import datetime  
from re import match, sub

dateCreated = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
injection = '''
        <script>
        function display() {
                var toDisplay = document.getElementById('symbol').value;
                var rows = document.getElementsByTagName('tr');
                var i;
                for (i = 0; i < rows.length; i++)  {
                        if (rows[i].innerHTML.indexOf(toDisplay) != -1) {
                                rows[i].style.display = '';
                        }
                }
        }
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
        </script>\n''' + \
        f'<p>Report created at {dateCreated}.</p>\n' + \
        '''<p>Enter a message symbol to display or hide all messages with that symbol (eg import-error).</p>
        <input type='text' id='symbol'>
        <button onclick='display()'>Display</button>
        <button onclick='hide()'>Hide</button>\n'''

duplicate_code = False
for line in stdin:
        if not duplicate_code and match(r'^\s*<td>Similar lines in \d+ files', line):
                duplicate_code = True
                line = sub(r'^(\s*)<td>(.*)', r'\1<td><pre><code>\2', line)
        elif duplicate_code and '</td>' in line:
                line = line.replace('</td>', '</code></pre></td')
                duplicate_code = False
        print(line, end='')
        if '<h1>' in line:
               print(injection, end='')

