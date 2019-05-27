#!/usr/bin/env python
# -*- coding: utf-8 -*-
#BakirovAR turkin86@mail.ru
import tarfile
import os
import sys
import shutil
import logging
from datetime import datetime
import re

def get_jobs():
    print 'jobs'

def main():
    logging.basicConfig(level=logging.INFO)
    
    argvs = "/var/lib/jenkins"
    #depth = 3
    files_pattern = "/nodes:/users"
    archive_file = "/opt/arv.tar.gz"

    flist = [] # Список всех файлов

    #Получть список файлов в корневом катологе
    root_files = []
    get_files(argvs, db_files=root_files)
    print("root_files: %s" %(root_files))
    #Отфильтровать файлы в корневом катологе
    root_files = filter_files(root_files, files_pattern)
    #Получить путь всех файлов в корневом катологе
    get_files(argvs, list_files=root_files, db_files=flist, recursive=True)
    #Отфильтровать мусор по регулярке
    flist = filter_files(flist, files_pattern)
    #Архивирование данных
    create_archive(archive_file, flist)

def create_archive(file_path, files):
    archive_file = tarfile.open(file_path, "w:gz")
    for f in files:
        archive_file.add(f)
        logging.info("archive add file: %s" % (f))
    archive_file.close()

def filter_files(db_files, patterns):
    pattern_list = patterns.split(':')
    filter_list = []
    for fl in db_files:
        for pt in pattern_list:
            pattern = re.compile(os.path.normpath(pt))
            result = pattern.search(fl)
            if result and fl not in filter_list:
                filter_list.append(fl)
    return sorted(filter_list)

def get_files(path, list_files=None, db_files=[], recursive=False):
    #depth
    if isinstance(list_files, list):
        files = list_files
    else:    
        files = ls_dir(path)
    src_path = os.path.normpath(path)
    for file in files:
        path_file = get_path(src_path, file)
        #recursive block
        if recursive and is_dir(path_file):
            chld_files = ls_dir(path_file)
            get_files(path_file, list_files=chld_files, db_files=db_files, recursive=true)
            #logging.info("dir: %s" % (path_file))
        #else:
            #logging.info("file: %s" % (path_file))
        db_files.append(path_file)

def ls_dir(path):
    return os.listdir(path)

def is_dir(file):
    return os.path.isdir(file)

def get_path(path, file):
    return os.path.join(path, file)

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
