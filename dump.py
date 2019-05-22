#!/usr/bin/env python
# -*- coding: utf-8 -*-
#BakirovAR turkin86@mail.ru
import tarfile
import os
import sys
import shutil
import logging
from datetime import datetime

def get_jobs():
    print 'jobs'
def main():
    print 'hello'

if __name__ == "__main__":
    # execute only if run as a script
    print(os.environ.get('JENKON_HOME'))
    arguments = sys.argv[1:]
    args_count = len(arguments)
    if args_count < 3:
        logging.error("No input arguments")
        logging.error("%s {JENKON_HOME} {TYPE_FILE:FILES:FOLDER:PATHS:PATHS/REGEX:REGEX} {PATH/DUMP_NAME}" % (program_name))
        logging.error("example: %s \"/home/jenkins/ /etc/fstab /usr\" /media/storage my_dump_name" % (program_name))
        sys.exit(1)

    main()
