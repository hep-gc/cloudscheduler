#!/bin/bash
# This script finds instances of "and" or "or" used in sqlalchemy statements.
# These should be replaced with "&" or "|" when found as they do not function as expected.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
NUM=${#DIR}-10
DIR="${DIR:0:NUM}*"
grep -e '\<select(.*\<and\>' -e '\<select(.*\<or\>' $DIR -r
