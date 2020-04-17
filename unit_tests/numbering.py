'''
Corrects misnumbered tests.
Assumes that all tests already have some number assigned to them in the form:
    # 01 [optional description]
    <Test>
Or:
    # 01 - 02 [optional description]
    <Tests>
'''

from sys import argv, stderr
import re

def main():
    if len(argv) < 2:
        print('Usage: python3 {} test_foo.py [test_bar.py ...]'.format(argv[0]), file=stderr)
        raise SystemExit
    
    filenames = []
    for arg in argv[1:]:
        # If multiple files are specified by a single arg, e.g. 'test_alias_*', it will come as a list of strs.
        if isinstance(arg, list):
            filenames.extend(arg)
        # Assume it is a str.
        else:
            filenames.append(arg)

    for filename in filenames:
        try:
            with open(filename) as test_file:
                test_lines = test_file.readlines()
        except FileNotFoundError:
            print('{} not found.'.format(filename), file=stderr)
            continue
        test_num = 1
        for i, line in enumerate(test_lines):
            interval_match = re.match(r'(\s*)# (\d+) ?- ?(\d+)', line)
            if interval_match:
                interval_length = int(interval_match[3]) - int(interval_match[2])
                test_lines[i] = '{}# {:02d} - {:02d}{}'.format(interval_match[1], test_num, test_num + interval_length, line[len(interval_match[0]):])
                test_num += interval_length + 1
            else:
                test_lines[i], sub_made = re.subn(r'^(\s*)# \d+', r'\1# {:02d}'.format(test_num), line, count=1)
                if sub_made:
                    test_num += 1
        with open(filename, 'w') as test_file:
            test_file.writelines(test_lines)

if __name__ == '__main__':
    main()
