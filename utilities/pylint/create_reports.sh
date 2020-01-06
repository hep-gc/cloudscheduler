# Creates HTML Pylint reports in this directory for cli/, cloudscheduler/, data_collectors/, lib/, and unit_tests/.
# This version is slightly different than the one on csv2-sa.
# Requires both pylint and pylint-json2html.

# PYTHONPATH is set to prevent import-errors, but there are some import-errors that confusingly still occur.
export PYTHONPATH="${PYTHONPATH}:../..:../../cli/bin:../../cloudscheduler:../../lib:../../unit_tests"
echo 'Creating cli_report.html...'
pylint ../../cli --rcfile=.pylintrc | pylint-json2html | python3 add_row_removal.py > cli_report.html
echo 'Creating cloudscheduler_report.html...'
pylint ../../cloudscheduler --rcfile=.pylintrc | pylint-json2html | python3 add_row_removal.py > cloudscheduler_report.html
echo 'Creating data_collectors_report.html...'
pylint ../../data_collectors --rcfile=.pylintrc | pylint-json2html | python3 add_row_removal.py > data_collectors_report.html
echo 'Creating lib_report.html...'
pylint ../../lib --rcfile=.pylintrc | pylint-json2html | python3 add_row_removal.py > lib_report.html
echo 'Creating unit_tests_report.html...'
pylint ../../unit_tests --rcfile=.pylintrc | pylint-json2html | python3 add_row_removal.py > unit_tests_report.html
