import sys
from distutils.core import setup

import cloudscheduler.__version__ as version

setup(name = "cloudscheduler",
      version = version.version,
      license = "'GPL3' or 'Apache 2'",
      install_requires = [
          "boto3",
          "botocore",
          "pyyaml",
          "urllib3",
          "python-novaclient",
          "python-neutronclient",
          ],
      description = "A cloud-enabled distributed resource manager for batch jobs",
      author = "Michael Paterson, Colson Driemel",
      author_email = "mhp@uvic.ca",
      url = "http://github.com/hep-gc/cloudscheduler",
      packages = [ 'cloudscheduler', 'attribute_mapper' ],
      scripts = [ "csmain", "csstatus", "csadmin" ]
)
