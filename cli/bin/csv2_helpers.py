from csv2_common import command_hash
from subprocess import Popen, PIPE
import json
import os

def check_documentation(gvar):
    """
    Check for complete documentation.
    """

    if gvar['retrieve_options']:
        return []

    def scan_1_doc_dir(gvar, man_path):
        for fn in os.listdir(man_path):
            if os.path.isdir('%s/%s' % (man_path, fn)):
                scan_1_doc_dir(gvar, '%s/%s' % (man_path, fn))
            elif os.path.isfile('%s/%s' % (man_path, fn)):
                gvar['docs'][fn] = {'dir': '../%s' % man_path[len(gvar['command_dir'])-3:], 'count': 0}

    def scan_2_doc_dir(gvar, man_path):
        for fn in os.listdir(man_path):
            if os.path.isdir('%s/%s' % (man_path, fn)):
                scan_2_doc_dir(gvar, '%s/%s' % (man_path, fn))
            elif os.path.isfile('%s/%s' % (man_path, fn)):
                fd = open('%s/%s' % (man_path, fn))
                doc_data = fd.read()
                fd.close()

                for fn2 in gvar['docs']:
                    words = doc_data.split('.so %s/%s' % (gvar['docs'][fn2]['dir'], fn2))
                    gvar['docs'][fn2]['count'] += len(words)-1

    gvar['docs'] = {}
    scan_1_doc_dir(gvar, os.path.realpath('%s/../man' % gvar['command_dir']))
    scan_2_doc_dir(gvar, os.path.realpath('%s/../man' % gvar['command_dir']))

    cks = {}
    gvar['retrieve_options'] = True
    for object in gvar['actions']:
        for action in gvar['actions'][object][1]:
            for ck in gvar['actions'][object][1][action](gvar):
                if ck not in cks:
                   cks[ck] = []

                cks[ck].append('%s/%s' % (object, action))

    gvar['retrieve_options'] = False

    p = Popen([
        'awk',
        '-r',
        '/^.so/',
        '%s/../man/*' % gvar['command_dir']
        ], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()

    ckx = {}
    for ix in range(len(gvar['command_keys'])):
        ck = gvar['command_keys'][ix][0]
        ckx[ck] = {'ix': ix, 'doc': False, 'ref1': [], 'ref2': 0}
        fn = '%s.so' % gvar['command_keys'][ix][1][1:].replace('-', '_').lower()
        if fn in gvar['docs']:
            ckx[ck]['doc'] = True
            ckx[ck]['ref2'] = gvar['docs'][fn]['count']

    fmt_string = '%-48s %-10s %-10s %8s (%s) %s'
    print(fmt_string % ('Command Parameter', 'Short Name', 'Documented', 'Includes', 'Count', 'Calls'))
    for ck in ckx:
        ix = ckx[ck]['ix']
        if ck in cks:
            ckx[ck]['ref1'] = cks[ck]

        if ckx[ck]['doc'] == False or len(ckx[ck]['ref1']) < 1 or ckx[ck]['ref2'] < 1:
            print(fmt_string % (gvar['command_keys'][ix][1], gvar['command_keys'][ix][0], ckx[ck]['doc'], ckx[ck]['ref2'], len(ckx[ck]['ref1']), ckx[ck]['ref1']))


def generate_bash_completion_script(gvar):
    """
    List settings.
    """

    if gvar['retrieve_options']:
        return []

    if not os.path.isdir('%s/.bash_completion.d' % gvar['home_dir']):
        os.mkdir('%s/.bash_completion.d' % gvar['home_dir'])

        fd = open('%s/.bash_completion' % gvar['home_dir'], 'a')
        fd.write(
            'if [ -e ~/.bash_completion.d ]; then\n' \
            '    for ix in $(ls ~/.bash_completion.d); do\n' \
            '        . ~/.bash_completion.d/$ix\n' \
            '    done\n' \
            'fi\n' 
            )
        fd.close()

    options = get_option_list(gvar)

    arguments = {
        '-bk|--backup-key': '-f',
        '-br|--backup-repository': '-f',
        '-cc|--config-category': '-W "condor_poller.py openstackPoller.py web_frontend"',
        '-ce|--cloud-enabled': '-W "true false yes no 1 0"',
        '-ct|--cloud-type': '-W "amazon azure google local opennebula openstack"',
        '-eg|--enable-glint': '-W "True False"',
        '-f|--file-path': '-f',
        '-gmo|--group-metadata-option': '-W "add delete"',
        '-go|--group-option': '-W "add delete"',
        '-jh|--job-hold': '-W "1 0"',
        '-jS|--job-status': '-W "1 2 3 4 5"',
        '-me|--metadata-enabled': '-W "true false yes no 1 0"',
        '-mmt|--metadata-mime-type': '-W "cloud-config ucernvm-config"',
        '-SU|--super-user': '-W "yes no true false 1 0"',
        '-uo|--user-option': '-W "add delete"',
        '-vF|--vm-foreign': '-W "1 0"',
        '-vo|--vm-option': '-W "kill retire manctl sysctl"',
        '-vS|--vm-status': '-W "foreign native manual error unregistered retiring running other"',
    }

    fd = open('%s/.bash_completion.d/cloudscheduler' % gvar['home_dir'], 'w')

    fd.write('# %s\n_cloudscheduler()\n{\n    local cur prev first second objects actions options\n    COMPREPLY=()\n    ' \
        'cur="${COMP_WORDS[COMP_CWORD]}"\n    prev="${COMP_WORDS[COMP_CWORD-1]}"\n    first="${COMP_WORDS[1]}"\n    second="${COMP_WORDS[2]}"\n\n    ' \
        '#\n    # Complete the following objects:\n    #\n    ' \
        'objects="%s"\n' % (
            command_hash(gvar),
            ' '.join(sorted(gvar['actions'].keys()))
            )
    )

    fd.write(
        '    #\n    # Complete args and file paths\n    #\n    ' \
        'case "${prev}" in'
    )

    for arg in arguments:
        fd.write(
            '        %s)\n            COMPREPLY=( $(compgen %s -- ${cur}) )\n            return 0\n            ;;' % \
            (arg, arguments[arg])
        )

    fd.write(
        '        *)\n            ;;\n    esac\n\n    ' \
        '#\n    # For each object, complete the following actions:\n    #\n    case "${first}:${second}" in'
    )

    for object in sorted(gvar['actions']):
        for action in sorted(gvar['actions'][object][1].keys()):
            fd.write('        %s:%s)\n            options="%s"\n' \
                '            COMPREPLY=( $(compgen -W "${options}" -- ${cur}) )\n' \
                '            return 0\n            ;;' % \
                (object, action, ' '.join(options[object][action]))
            )
        fd.write('        %s:*)\n            actions="%s"\n' \
            '            COMPREPLY=( $(compgen -W "${actions}" -- ${cur}) )\n' \
            '            return 0\n            ;;' % \
            (object, ' '.join(sorted(gvar['actions'][object][1].keys()) + ['--long-help', '--help', "--version"]))
        )

    fd.write('        *:*)\n            ;;\n    ' \
        'esac\n\n    COMPREPLY=($(compgen -W "${objects} --long-help --help --version" -- ${cur}))\n    ' \
        'return 0\n}\ncomplete -o filenames -F _cloudscheduler cloudscheduler'
    )

    fd.close()

    print('***\n*** Bash completion script regenerated. To use, start a new shell or source "%s/.bash_completion".\n***' % gvar['home_dir'])

def get_option_list(gvar):
    """
    Action parameters
    """
    gvar['retrieve_options'] = True

    options = {}
    for object in sorted(gvar['actions']):
        options[object] = {}
        for action in sorted(gvar['actions'][object][1].keys()):
            options[object][action] = []
            short_options = gvar['actions'][object][1][action](gvar)
            for key in gvar['command_keys']:
                if key and short_options and ((key[0] in short_options) or ('*' in short_options)):
                    options[object][action].append(key[1])
    
    gvar['retrieve_options'] = False
    
    return options

def print_json_syntax_tree(gvar):
    """
    JSON dump the command syntax variables.
    """

    if gvar['retrieve_options']:
        return []

    syntax_tree = {}
    for object in gvar['actions']:
        syntax_tree[object] = []
        for action in sorted(gvar['actions'][object][1]):
            syntax_tree[object].append(action)

    print(json.dumps(syntax_tree))
