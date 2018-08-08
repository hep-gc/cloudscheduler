def generate_bash_completion_script(gvar):
    """
    List settings.
    """

    options = {'job': {'list': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-jh', '--job-hold', '-jI', '--job-id', '-ji', '--job-image', '-jp', '--job-priority', '-jR', '--job-requirements', '-jrc', '--job-request-cpus', '-jrd', '--job-request-disk', '-jrr', '--job-request-ram', '-jrs', '--job-request-swap', '-jS', '--job-status', '-jtc', '--job-target-clouds', '-ju', '--job-user', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API']}, 'helpers': {'get_option_list': [], 'generate_bash_completion_script': []}, 'user': {'update': ['-un', '--username', '-g', '--group', '-gn', '--group-name', '-go', '--group-option', '-H', '--long-help', '-h', '--help', '-s', '--server', '-SU', '--super-user', '-ucn', '--user-common-name', '-upw', '--user-password', '-xA', '--expose-API'], 'list': ['-g', '--group', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-un', '--username', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'delete': ['-un', '--username', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API', '-Y', '--yes'], 'add': ['-un', '--username', '-upw', '--user-password', '-g', '--group', '-gn', '--group-name', '-H', '--long-help', '-h', '--help', '-s', '--server', '-SU', '--super-user', '-ucn', '--user-common-name', '-xA', '--expose-API']}, 'defaults': {'set': ['-s', '--server', '-ca', '--cloud-address', '-ce', '--cloud-enabled', '-cn', '--cloud-name', '-cpw', '--cloud-password', '-cP', '--cloud-project-domain', '-cp', '--cloud-project', '-cr', '--cloud-region', '-csp', '--cloud-spot-price', '-ct', '--cloud-type', '-cU', '--cloud-user-domain', '-cu', '--cloud-user', '-f', '--file-path', '-g', '--group', '-gm', '--group-manager', '-gme', '--group-metadata-exclusion', '-gmo', '--group-metadata-option', '-gn', '--group-name', '-go', '--group-option', '-H', '--long-help', '-h', '--help', '-jc', '--job-cores', '-jd', '--job-disk', '-jh', '--job-hold', '-jI', '--job-id', '-ji', '--job-image', '-jp', '--job-priority', '-jR', '--job-requirements', '-jr', '--job-ram', '-jrc', '--job-request-cpus', '-jrd', '--job-request-disk', '-jrr', '--job-request-ram', '-jrs', '--job-request-swap', '-jS', '--job-status', '-js', '--job-swap', '-jtc', '--job-target-clouds', '-ju', '--job-user', '-me', '--metadata-enabled', '-mmt', '--metadata-mime-type', '-mn', '--metadata-name', '-mp', '--metadata-priority', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-sa', '--server-address', '-sC', '--server-grid-cert', '-sK', '--server-grid-key', '-spw', '--server-password', '-SU', '--super-user', '-su', '--server-user', '-te', '--text-editor', '-ucn', '--user-common-name', '-un', '--username', '-uo', '--user-option', '-upw', '--user-password', '-V', '--view', '-VC', '--view-columns', '-vc', '--vm-cores', '-vd', '--vm-disk', '-vF', '--vm-foreign', '-vf', '--vm-flavor', '-vi', '--vm-image', '-vh', '--vm-hostname', '-vk', '--vm-keypair', '-vka', '--vm-keep-alive', '-vo', '--vm-option', '-vr', '--vm-ram', '-vS', '--vm-status', '-vs', '--vm-swap', '-xA', '--expose-API', '-Y', '--yes'], 'list': ['-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns'], 'delete': ['-s', '--server', '-H', '--long-help', '-h', '--help', '-Y', '--yes']}, 'group': {'metadata-load': ['-f', '--file-path', '-mn', '--metadata-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-me', '--metadata-enabled', '-mmt', '--metadata-mime-type', '-mp', '--metadata-priority', '-s', '--server', '-xA', '--expose-API'], 'update': ['-gn', '--group-name', '-g', '--group', '-gm', '--group-manager', '-H', '--long-help', '-h', '--help', '-s', '--server', '-un', '--username', '-uo', '--user-option', '-xA', '--expose-API'], 'metadata-delete': ['-mn', '--metadata-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API', '-Y', '--yes'], 'delete': ['-gn', '--group-name', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API', '-Y', '--yes'], 'metadata-edit': ['-mn', '--metadata-name','-te', '--text-editor', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API'], 'add': ['-gm', '--group-manager', '-gn', '--group-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-un', '--username', '-xA', '--expose-API'], 'defaults': ['-g', '--group', '-H', '--long-help', '-h', '--help', '-jc', '--job-cores', '-jd', '--job-disk', '-jr', '--job-ram', '-js', '--job-swap', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-vf', '--vm-flavor', '-vi', '--vm-image', '-vka', '--vm-keep-alive', '-xA', '--expose-API'], 'metadata-list': ['-g', '--group', '-H', '--long-help', '-h', '--help', '-mn', '--metadata-name','-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'metadata-update': ['-mn', '--metadata-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-me', '--metadata-enabled', '-mmt', '--metadata-mime-type', '-mp', '--metadata-priority', '-s', '--server', '-xA', '--expose-API'], 'list': ['-g', '--group', '-gn', '--group-name', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys','-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API']}, 'cloud': {'metadata-load': ['-cn', '--cloud-name', '-f', '--file-path', '-mn', '--metadata-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-me', '--metadata-enabled', '-mmt', '--metadata-mime-type', '-mp', '--metadata-priority', '-s', '--server', '-xA', '--expose-API'], 'status': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'metadata-delete': ['-cn', '--cloud-name', '-mn', '--metadata-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API', '-Y', '--yes'], 'delete': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API', '-Y', '--yes'], 'metadata-edit': ['-cn', '--cloud-name', '-mn', '--metadata-name', '-te', '--text-editor', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-xA', '--expose-API'], 'add': ['-ca', '--cloud-address', '-cn', '--cloud-name', '-cpw', '--cloud-password', '-cp', '--cloud-project', '-cr', '--cloud-region', '-ct', '--cloud-type', '-cu', '--cloud-user', '-ce', '--cloud-enabled', '-cP', '--cloud-project-domain', '-csp', '--cloud-spot-price', '-cU', '--cloud-user-domain', '-g', '--group', '-gme', '--group-metadata-exclusion', '-H', '--long-help', '-h', '--help', '-s', '--server', '-vc', '--vm-cores', '-vf', '--vm-flavor', '-vi', '--vm-image', '-vk', '--vm-keypair', '-vka', '--vm-keep-alive', '-vr', '--vm-ram', '-xA', '--expose-API'], 'metadata-list': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-mn', '--metadata-name', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'metadata-collation': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'list': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-xA', '--expose-API'], 'metadata-update': ['-cn', '--cloud-name', '-mn', '--metadata-name', '-g', '--group','-H', '--long-help', '-h', '--help', '-me', '--metadata-enabled', '-mmt', '--metadata-mime-type', '-mp', '--metadata-priority', '-s', '--server', '-xA', '--expose-API'], 'update': ['-cn', '--cloud-name', '-ca', '--cloud-address', '-ce', '--cloud-enabled', '-cpw', '--cloud-password', '-cP', '--cloud-project-domain', '-cp', '--cloud-project', '-cr', '--cloud-region', '-csp', '--cloud-spot-price', '-ct', '--cloud-type', '-cU', '--cloud-user-domain', '-cu', '--cloud-user', '-g', '--group', '-gme', '--group-metadata-exclusion', '-gmo', '--group-metadata-option', '-H', '--long-help', '-h', '--help', '-s', '--server', '-vc', '--vm-cores', '-vf', '--vm-flavor', '-vi', '--vm-image', '-vk', '--vm-keypair', '-vka', '--vm-keep-alive', '-vr', '--vm-ram', '-xA', '--expose-API']}, 'vm': {'update': ['-vo', '--vm-option', '-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-s', '--server', '-vh', '--vm-hostname', '-vS', '--vm-status', '-xA', '--expose-API'], 'list': ['-cn', '--cloud-name', '-g', '--group', '-H', '--long-help', '-h', '--help', '-NV', '--no-view', '-ok', '--only-keys', '-r', '--rotate', '-s', '--server', '-V', '--view', '-VC', '--view-columns', '-vc', '--vm-cores', '-vd', '--vm-disk', '-vF', '--vm-foreign', '-vf', '--vm-flavor', '-vh', '--vm-hostname', '-vr', '--vm-ram', '-vS', '--vm-status', '-vs', '--vm-swap', '-xA', '--expose-API']}}

    arguments = {
        '-ce|--cloud-enabled': '-W "true false yes no 1 0"',
        '-ct|--cloud-type': '-W "amazon azure google local opennebula openstack"',
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
            (object, ' '.join(sorted(gvar['actions'][object][1].keys())))
        )

    print('        *:*)\n            ;;\n    ' \
        'esac\n\n    COMPREPLY=($(compgen -W "${objects}" -- ${cur}))\n    ' \
        'return 0\n}\ncomplete -o filenames -F _cloudscheduler cloudscheduler'
    )

def get_option_list(gvar):
    """
    Action parameters
    """
    from subprocess import run, PIPE

    options = {}
    for object in sorted(gvar['actions']):
        options[object] = {}
        for action in sorted(gvar['actions'][object][1].keys()):
            options[object][action] = []
            if object == 'helpers':
                continue
            result = run(['cloudscheduler', object, action, '-h'], stdout=PIPE)
            for row in result.stdout.decode('utf-8').split('\n'):
                if row.strip().startswith('-'):
                    options[object][action] += [elm.strip() for elm in row.split('|')]
    print(options)
