"""
Utilities for dealing with cloud init files and yaml.
"""

import os
import sys
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
import requests


def build_multi_mime_message(yaml_tuples):
    """yaml_tuples - a list of tuples with name, yaml content, mime type """
    if not yaml_tuples:
        return ""
    combined_message = MIMEMultipart()
    for i in yaml_tuples:
        if i[1] is None or i[2] is None:
            return None
        sub_message = MIMEText(i[1], i[2], sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (i[0]))
        combined_message.attach(sub_message)
    return str(combined_message)

def read_file_type_pairs(file_type_pair):
    """
    :param file_type_pair: string in filepath:mimetype format - may be http:// based
    :return: tuple with content of the file, and content mime type
    """
    log = logging.getLogger(__name__)
    content = None
    format_type = None
    if file_type_pair.startswith('http'):
        try:
            (pre, http_loc, format_type) = file_type_pair.split(":", 2)
            http_loc = ':'.join([pre, http_loc])
            http_loc = http_loc.strip()
            format_type = format_type.strip()
        except ValueError:
            if len(file_type_pair.split(":")) == 2: # missing the content type
                http_loc = file_type_pair.strip()
                format_type = "cloud-config"
        try:
            response = requests.get(http_loc)
            content = response.content
        except requests.exceptions.HTTPError as ex:
            log.exception("Unable to read url: %s: %s", http_loc, ex)
            return (None, None)
        except requests.exceptions.RequestException as ex:
            log.exception("Unable to read url: %s: %s", http_loc, ex)
            return (None, None)
    else:
        try:
            (filename, format_type) = file_type_pair.split(":", 1)
            filename = filename.strip()
            format_type = format_type.strip()
        except ValueError:
            filename = file_type_pair
            format_type = "cloud-config"
        if not os.path.exists(filename):
            log.debug("Unable to find file: %s skipping", filename)
            return (None, None)
        with open(filename) as file_handle:
            content = file_handle.read()

    if content is None:
        return (None, None)

    return (content, format_type)

def validate_yaml(content):
    """ Try to load yaml to see if it passes basic validation."""
    log = logging.getLogger(__name__)
    try:
        yam = yaml.load(content)
        if not yam.has_key('merge_type'):
            print("Yaml submitted without a merge_type.")
            return "Missing merge_type:"
    except yaml.parser.ParserError as ex:
        log.exception("Problem validating yaml: %s", ex)
        return ex
    except UnboundLocalError as ex:
        log.exception("Exception validating yaml: %s", ex)
    return None
