from csv2_common import check_keys, show_table

def generate_bash_completion_script(gvar):
    """
    List settings.
    """

    print('_cloudscheduler()\n{\n    local cur prev objects actions\n    COMPREPLY=()\n    ' \
        'cur="${COMP_WORDS[COMP_CWORD]}"\n    prev="${COMP_WORDS[COMP_CWORD-1]}"\n\n    ' \
        '#\n    # Complete the following ojects:\n    #\n    ' \
        'objects="%s"\n\n    #\n    ' \
        '# For each object, complete the following actions:\n    #\n    case "${prev}" in' % \
        ' '.join(sorted(gvar['actions'].keys()))
        )

    for object in sorted(gvar['actions']):
        print('        %s)\n            actions="%s"\n' \
            '            COMPREPLY=( $(compgen -W "${actions}" -- ${cur}) )\n' \
            '            return 0\n            ;;' % \
            (object, ' '.join(sorted(gvar['actions'][object][1].keys())))
            )

    print('        *)\n        ;;\n    ' \
        'esac\n\n    COMPREPLY=($(compgen -W "${objects}" -- ${cur}))\n    ' \
        'return 0\n}\ncomplete -F _cloudscheduler cloudscheduler'
        )
