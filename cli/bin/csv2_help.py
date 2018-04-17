from subprocess import Popen, PIPE
import os

def _help(gvar, mandatory=None, options=None):
    """
    Print long and short help messages.
    """


    # If help requested, display the help for the current command.
    if gvar['user_settings']['help']:
        if not gvar['object']:
            print('Help requested for "csv2". One of the following objects must be specified:')
            for obj in sorted(gvar['actions']):
                print('  %s' % obj)

        elif gvar['object'] not in gvar['actions']:
            print('Help requested for "csv2 %s". The specified object is invalid. One of the following must be specified:' % gvar['object'])
            for obj in sorted(gvar['actions']):
                print('  %s' % obj)

        elif not gvar['action']:
            print('Help requested for "csv2 %s". One of the following actions must be specified:' % gvar['object'])
            for action in sorted(gvar['actions'][gvar['object']]):
                print('  %s' % action)

        elif gvar['action'] not in gvar['actions'][gvar['object']]:
            print('Help requested for "csv2 %s %s". The specified action is invalid. One of the following must be specified:' % (gvar['object'], gvar['action']))
            for action in sorted(gvar['actions'][gvar['object']]):
                print('  %s' % action)

        else:
            if mandatory:
                print('Help requested for "csv2 %s %s". The following parameters are required:' % (gvar['object'], gvar['action']))
                for key in mandatory:
                    print('  %s' % key[1])

            if options:
                if mandatory:
                    print('The following optional parameters may be specified:')
                else:
                    print('Help requested for "csv2 %s %s". The following optional parameters may be specified:' % (gvar['object'], gvar['action']))
      
                for key in options:
                    print('  %s' % key[1])

            if not mandatory and not options:
                print('Help requested for "csv2 %s %s". There are no parameters for this command.' % (gvar['object'], gvar['action']))

        print('For more information, use -H.')

    # If long-help requested, use the "man" command to display the long-help for the current command.
    elif gvar['user_settings']['long-help']:
        # Determine man page and call display routine.
        if not gvar['object']:
            __long_help(gvar, 'csv2', 'csv2.1')

        elif gvar['object'] not in gvar['actions']:
            print('Long help requested for "csv2 %s". The specified object is invalid. One of the following must be specified:' % gvar['object'])
            for obj in sorted(gvar['actions']):
                print('  %s' % obj)

        elif not gvar['action']:
            __long_help(gvar, 'csv2 %s' % gvar['object'], 'csv2_%s.1' % gvar['object'])

        elif gvar['action'] not in gvar['actions'][gvar['object']]:
            print('Long help requested for "csv2 %s %s". The specified action is invalid. One of the following must be specified:' % (gvar['object'], gvar['action']))
            for action in sorted(gvar['actions'][gvar['object']]):
                print('  %s' % action)

        else:
            __long_help(gvar, 'csv2 %s %s' % (gvar['object'], gvar['action']), 'csv2_%s_%s.1' % (gvar['object'], gvar['action']))

    # No help requested, return to caller.
    else:
        return

    # Help requests just exit.
    exit(0)

def __long_help(gvar, man_id, man_page):
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
            del(help_page)

        if help_page:
            p = Popen(['man', '-l', help_page], cwd=man_dir)
            p.communicate()
            return

    else:
        print('Long help requested for "%s". The required man page does not exist.' % man_id)
