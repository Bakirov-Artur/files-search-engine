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

def load(path, items, depth=0, recursive=False):
    flist = [] # Список всех файлов
    root_files = []
    root_path = os.path.normpath(path)
    #Получть список файлов в корневом катологе
    get_files(root_path, db_files=root_files)
    #Отфильтровать файлы в корневом катологе
    root_files = filter_files(root_files, items)
    #Получить путь всех файлов в корневом катологе
    get_files(root_path, list_files=root_files, db_files=flist, recursive=recursive)

    #Отфильтровать по глубине
    if depth > 0:
        count = len(os.path.split(root_path)) + depth
        flist = filter_depth(count, flist)
    #Отфильтровать мусор по регулярке и вернуть новый список
    return filter_files(flist, items)

def filter_depth(depth, files):
    filter_list = []
    for f in files:
        sf  = os.path.split(f)
        logging.info("filter_depth sf: %s", % (sf))
        count = len(sf)
        if count < depth:
            logging.info("filter_depth: depth: %d file: %s" % (count, f))
            filter_list.append(f)
    return filter_list

def main(data):
    logging.basicConfig(level=logging.INFO)
    
    argvs = "/var/lib/jenkins"
    #depth = 3
    files_pattern = "/nodes/:/users/"
    flist = load(argvs, files_pattern, depth=2, recursive=True)
    #Архивирование данных
    archive_file = "/opt/arv.tar.gz"
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

def load_configs(path):
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
    parser.add_argument('--config', help='/your/path/json/config/file', default=config_default)
    arguments = parser.parse_args(sys.argv[1:])
    configs = load_configs(arguments.config)
    if configs:
        main(configs)
