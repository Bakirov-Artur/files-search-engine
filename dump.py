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
import json
import argparse

def get_jobs():
    print 'jobs'

def get_default_configs(path):
    return get_path(path, 'etc/files_dump.conf')

def main():
    logging.basicConfig(level=logging.INFO)
    
    argvs = "/var/lib/jenkins"
    #depth = 3
    files_pattern = "/nodes/:/users/"
    archive_file = "/opt/arv.tar.gz"

    flist = [] # Список всех файлов

    #Получть список файлов в корневом катологе
    root_files = []
    get_files(argvs, db_files=root_files)
    #Отфильтровать файлы в корневом катологе
    root_files = filter_files(root_files, files_pattern)
    #Получить путь всех файлов в корневом катологе
    get_files(argvs, list_files=root_files, db_files=flist, recursive=True)

    #Отфильтровать по глубине
    #depth = 3

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
            get_files(path_file, list_files=chld_files, db_files=db_files, recursive=True)
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

def load_config_data(path):
    try:
        fconfig = open(path, 'r')
        return json.load(fconfig)
    except IOError:
        logging.error("file: %s not found." % (path))


   

if __name__ == "__main__":
    program_name = os.path.basename(__file__)
    app_path = os.path.dirname(os.path.abspath(__file__))
    config_default = get_default_configs(app_path)
    #parser arguments
    parser = argparse.ArgumentParser(description='Files dump')
    parser.add_argument('--config', help='/your/path/json/config', default=config_default)
    arguments = parser.parse_args(sys.argv[1:])
    print arguments
    config_data = load_config_data(arguments.config)
    print config_data
    #main()
