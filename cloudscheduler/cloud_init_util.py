import sys
import urllib3
import yaml

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def build_multi_mime_message(file_type_pairs):
    """file_type_pairs - list of strings in path : mime-type format"""
    combined_message = MIMEMultipart()
    for i in file_type_pairs:
        (contents, format_type) = read_file_type_pairs(i)
        if contents == None or format_type == None:
            return None
        sub_message = MIMEText(contents, format_type, sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (i))
        combined_message.attach(sub_message)
    #for i in content_type_pairs:
    #    sub_message = MIMEText(i[0], i[1].strip(), sys.getdefaultencoding())
    #    if len(i) <= 3:
    #        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (i[2].strip()))
    #    else:
    #        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % ("cs-cloud-init.yaml"))
    #    combined_message.attach(sub_message)

    return str(combined_message)

def read_file_type_pairs(file_type_pair):
    """
    :param file_type_pair: string in filepath:mimetype format - may be http:// based
    :return: tuple with content of the file, and content mime type
    """
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
            content = urllib3.urlopen(http_loc).read()
        except Exception as e:
            print("Unable to read url: %s" % http_loc)
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
            print("Unable to find file: %s skipping" % filename)
            return (None, None)
        with open(filename) as fh:
            content = fh.read()

    if len(content) == 0:
        return (None, None)

    return (content, format_type)

def validate_yaml(content):
    """ Try to load yaml to see if it passes basic validation."""
    try:
        y = yaml.load(content)
        if not y.has_key('merge_type'):
            print("Yaml submitted without a merge_type.")
            return "Missing merge_type:"
    except yaml.YAMLError as e:
        print("Problem validating yaml: %s" % e)
        return ' '.join(['Line: ', str(e.problem_mark.line), ' Col: ', str(e.problem_mark.column)]) # use e.problem_mark.[name,column,line]
    except UnboundLocalError as e:
        print("Caught an exception trying to validate yaml. Is the pyyaml module installed?")
    return None
