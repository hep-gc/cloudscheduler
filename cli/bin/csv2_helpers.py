def generate_bash_completion_script(gvar):
    """
    List settings.
    """

    if gvar['retrieve_options']:
        return []

    options = get_option_list(gvar)

    arguments = {
        '-bk|--backup-key': '-f',
        '-br|--backup-repository': '-f',
        '-cc|--config-category': '-W "csjobs.py csmachines.py openstackPoller.py web_frontend"',
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

    print('_cloudscheduler()\n{\n    local cur prev first second objects actions options\n    COMPREPLY=()\n    ' \
        'cur="${COMP_WORDS[COMP_CWORD]}"\n    prev="${COMP_WORDS[COMP_CWORD-1]}"\n    first="${COMP_WORDS[1]}"\n    second="${COMP_WORDS[2]}"\n\n    ' \
        '#\n    # Complete the following objects:\n    #\n    ' \
        'objects="%s"\n' % \
        ' '.join(sorted(gvar['actions'].keys()))
    )

    print(
        '    #\n    # Complete args and file paths\n    #\n    ' \
        'case "${prev}" in'
    )

    for arg in arguments:
        print(
            '        %s)\n            COMPREPLY=( $(compgen %s -- ${cur}) )\n            return 0\n            ;;' % \
            (arg, arguments[arg])
        )

    print(
        '        *)\n            ;;\n    esac\n\n    ' \
        '#\n    # For each object, complete the following actions:\n    #\n    case "${first}:${second}" in'
    )

    for object in sorted(gvar['actions']):
        for action in sorted(gvar['actions'][object][1].keys()):
            print('        %s:%s)\n            options="%s"\n' \
                '            COMPREPLY=( $(compgen -W "${options}" -- ${cur}) )\n' \
                '            return 0\n            ;;' % \
                (object, action, ' '.join(options[object][action]))
            )
        print('        %s:*)\n            actions="%s"\n' \
            '            COMPREPLY=( $(compgen -W "${actions}" -- ${cur}) )\n' \
            '            return 0\n            ;;' % \
            (object, ' '.join(sorted(gvar['actions'][object][1].keys()) + ['--long-help', '--help']))
        )

    print('        *:*)\n            ;;\n    ' \
        'esac\n\n    COMPREPLY=($(compgen -W "${objects} --long-help --help" -- ${cur}))\n    ' \
        'return 0\n}\ncomplete -o filenames -F _cloudscheduler cloudscheduler'
    )

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
