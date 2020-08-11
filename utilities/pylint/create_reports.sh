# Creates HTML Pylint reports in this directory for cli/, cloudscheduler/, data_collectors/, lib/, and unit_tests/.
# Requires both pylint and pylint-json2html.

export PATH="$PATH:/usr/local/bin"
export PYTHONPATH="$PYTHONPATH:../..:../../cli/bin:../../cloudscheduler:../../lib:../../unit_tests"
dirs=('cli' 'cloudscheduler' 'data_collectors' 'lib' 'unit_tests')
for dir in "${dirs[@]}"; do
    echo "Creating ${dir}_report.html..."
    branch=$(git symbolic-ref --short HEAD)
    pylint "../../${dir}" --rcfile=.pylintrc | pylint-json2html | python3 parse_html.py ${branch} > "${dir}_report.html"
done
