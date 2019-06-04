"""
Extract HTML tables from a URL, file, or string and return a dictionary:

   {
       'table1': {
           'heads': [ 'col_hdg1', 'col_hdg2', ... 'col_hdgN' ],
           'rows': [
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
                  .
                  .
                  .
               ]
            },
        'table2': {
           'heads': [ 'col_hdg1', 'col_hdg2', ... 'col_hdgN' ],
           'rows': [
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
               [ 'col_val1', 'col_val2', ... 'col_valN' ],
                  .
                  .
                  .
               ]
            },
              .
              .
              .
        }

    
    Note: The table names are taken from the heading immediately preceeding the table
          definition or, if no heading precedes the table definition, is generated as
          'Unlabelled Table NN', where 'NN' is the table's sequence number.
"""

from urllib.request import *
from html.parser import HTMLParser
import sys

def get_html_tables(html_file):
    class MyHTMLParser(HTMLParser):
        state = {'counter': 0, 'heading': False, 'last_heading': None, 'last_tag': None, 'tables': {}}

        def handle_starttag(self, tag, attrs):
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.state['last_tag'] = 'h'

            elif tag == 'table':
                self.state['counter'] += 1
                self.state['last_tag'] = tag

                if self.state['last_heading']:
                    if self.state['counter'] < 2:
                        self.state['table_name'] = self.state['last_heading']
                    else:
                        self.state['table_name'] = '%s + %s' % (self.state['last_heading'], self.state['counter'])
                else:
                    self.state['table_name'] = 'Unlabelled Table %s' % self.state['counter']

                table_name = self.state['table_name']
                self.state['tables'][table_name] = {'rows': []}

            elif tag == 'tr':
                self.state['last_tag'] = tag
                self.state['row'] = []

            elif tag ==  'th':
                self.state['last_tag'] = tag
                self.state['heading'] = True

            elif tag ==  'td':
                self.state['last_tag'] = tag
                self.state['heading'] = False

            else:
                self.state['last_tag'] = None


        def handle_endtag(self, tag):
            if tag == 'table':
                table_name = self.state['table_name']
                if 'heads' not in self.state['tables'][table_name]:
                    self.state['tables'][table_name]['heads'] = []
                    if len(self.state['tables'][table_name]['rows']) > 0:
                        for ix in range(1, len(self.state['tables'][table_name]['rows'][0])+1):
                            self.state['tables'][table_name]['heads'].append('Unlabelled Column %s' % ix)
                    
            if tag == 'tr':
                table_name = self.state['table_name']
                if self.state['heading']:
                    self.state['tables'][table_name]['heads'] = self.state['row']
                else:
                    self.state['tables'][table_name]['rows'].append(self.state['row'])


            self.state['last_tag'] = None

        def handle_data(self, data):
            if self.state['last_tag'] == 'h':
                self.state['counter'] = 0
                self.state['last_heading'] = data

            elif self.state['last_tag'] in ['td', 'th']:
                self.state['row'].append(data)

    def decode(obj):
        if isinstance(obj, str):
            return obj
        else:
            return obj.decode('utf-8')

    parser = MyHTMLParser()
    if len(html_file) > 7 and (html_file[:7] == 'http://' or html_file[:8] == 'https://'):
        with urlopen(html_file) as response:
            parser.feed(' '.join(decode(response.read()).split()))
    elif len(html_file) > 7 and html_file[:7] == 'file://':
        with open(html_file[7:]) as response:
            parser.feed(' '.join(decode(response.read()).split()))
    else:
        parser.feed(' '.join(decode(html_file).split()))

    return parser.state['tables']

if __name__ == "__main__":
    get_html_tables(sys.argv[1])
