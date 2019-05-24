#!/usr/bin/env python
# -*- coding: utf-8 -*-
#BakirovAR turkin86@mail.ru
import tarfile
import os
import sys
import shutil
import logging
from datetime import datetime
import fnmatch, re

def get_jobs():
    print 'jobs'

def main():
    print('Main')
    logging.basicConfig(level=logging.INFO)
    #Получить все файлы
    root_files = ls_dir("/var/lib/jenkins")
    flist = [] # Список всех файлов
    get_files("/var/lib/jenkins", root_files, db_files=flist)
    #Отфильтровать мусор по регулярке
    fmt_list = filter_files(flist, "/users/:/secrets/:^/nodes/:.xml")
    print fmt_list

def filter_files(db_files, patterns):
    pttrn = patterns.split(':')
    filter_list = []
    for fl in db_files:
        for pt in pttrn:
            pattern = re.compile(pt)
            result = pattern.search(fl)
            if result:
                filter_list.append(fl)

def ls_dir(path):
    return os.listdir(path)

def is_dir(file):
    return os.path.isdir(file)

def get_path(path, file):
    return os.path.join(path, file)

def get_files(root_path, files, db_files=[]):
    for file in files:
        path_file = get_path(root_path, file)
        if is_dir(path_file):
            chld_files = ls_dir(path_file)
            get_files(path_file, chld_files, db_files)
            #logging.info("dir: %s" % (path_file))
        #else:
            #logging.info("file: %s" % (path_file))
        db_files.append(path_file)

if __name__ == "__main__":
    # execute only if run as a script
    print(os.environ.get('JENKON_HOME'))
    program_name = os.path.basename(__file__)
    arguments = sys.argv[1:]
    args_count = range(len(arguments))
    for x in args_count:
        if x == 0:
            fls = arguments[x].split(' ')
            DUMP_PATH = arguments[x]
        elif x == 1:
            SEARC_REGEX_LIST = arguments[x].split(':')
        elif x == 2:
            DUMP_NAME = arguments[x]


    if args_count < 3:
        logging.error("No input arguments")
        logging.error("%s [options] {JENKON_HOME} {TYPE_FILE:FILE:FOLDER:FOLDER/REGEX:PATHS/REGEX:REGEX} {PATH/DUMP_NAME}" % (program_name))
        logging.error("example: %s \"/home/jenkins/ /etc/fstab /usr\" /media/storage my_dump_name" % (program_name))
        sys.exit(1)

    main()
