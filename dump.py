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
    root_path = os.path.abspath(path)
    len_depth = get_len_depth(root_path, depth)
    patterns_list = init_patterns(items)
    #Получть список файлов в корневом катологе
    # logging.info("Get root files")
    # logging.info("def load depth: %d" % depth)
    get_files(root_path, db_files=root_files, patterns=patterns_list)
    #Отфильтровать файлы в корневом катологе
    # root_files = filter_files(root_files, patterns_list)
    #Получить путь всех файлов в корневом катологе
    logging.info("Get chield files:")
    print root_files
    get_files(root_path, list_files=root_files, db_files=flist, recursive=recursive, depth=len_depth, patterns=patterns_list)
    logging.info("Chield files:")
    print flist
    #Отфильтровать по глубине
    # logging.info("Get filter depth files")
    # flist = filter_depth(flist, len_depth)
    #Отфильтровать мусор по регулярке и вернуть новый список
    #return filter_files(flist, patterns_list)
    return flist

def get_len_depth(path, depth, sep=os.sep):
    return len(path.split(sep)[1:]) + depth

def filter_depth(files, depth):
    filter_list = []
    for f in files:
        if check_depth(f, depth):
            filter_list.append(f)
    return filter_list

def check_depth(path, depth=0, sep=os.sep):
    len_path = get_len_depth(path, depth)
    if len_path <= depth or depth == 0:
        # logging.info("check depth: depth: %d len_path: %d path: %s" % (depth, len_path, path))
        return True

    return False

def main(data):
    logging.basicConfig(level=logging.INFO)
    
    argvs = "/var/lib/jenkins"
    #depth = 3
    files_pattern = "/nodes/:/users/"
    flist = load(argvs, files_pattern, depth=2, recursive=True)
    #Архивирование данных
    archive_file = "/opt/arv.tar.gz"
    create_archive(archive_file, flist)

def create_archive(name, files, recursive=False, archive_type="gz"):
    archive = tarfile.open(name, ":".join(["w", archive_type]))
    if files:
        for f in files:
            archive.add(f, recursive=recursive)
            logging.info("archive add file: %s" % (f))
    archive.close()

def is_duplicate(item, data_list):
    if item not in data_list:
        return True
    return False

def filter_files(db_files, patterns, normalize_pattern=False, sort=False):
    filter_list = []
    if not normalize_pattern:
        pattern_list = patterns
    else:
        pattern_list = init_patterns(patterns)
    #Нужно немного оптимизировать фильтрацию
    if pattern_list:
        for fl in db_files:
            if is_patterns(fl, pattern_list) and is_duplicate(fl, filter_list):
                filter_list.append(fl)
    if sort:
        filter_list = sorted(filter_list)
    return filter_list

def init_patterns(patterns_list, sep=':'):
    plist = []
    if isinstance(patterns_list, basestring):
        pattern = re.compile(sep)
        if pattern.search(patterns_list):
            patterns = patterns_list.split(sep)
            for pts in patterns:
                if pts: 
                    plist.append(os.path.normpath(pts))
        elif patterns_list:
            plist.append(os.path.normpath(patterns_list))
    elif isinstance(patterns_list, list) and len(patterns_list):
        for pts in patterns_list:
            if pts: 
                plist.append(os.path.normpath(pts))
    if plist:
        return plist       
    return None

def is_patterns(path, patterns):
    #os.path.splitext('*.ta')
    if patterns:
        # logging.debug("Is patterns path: %s" % (path))
        for pattern in patterns:
            #os.path.splitext('*.ta')
            pattern = os.path.normpath(pattern)
            re_pattern = re.compile(pattern)
            if re_pattern.search(path):
                return True
    elif not patterns:
        return True

    return False

def get_files(path, list_files=None, db_files=[], recursive=False, depth=0, patterns=None):
    if isinstance(list_files, list):
        files = list_files
    else:    
        files = ls_dir(path)
    src_path = os.path.normpath(path)
    path_file = None
    for file in files:
        if os.path.isabs(file):
            re_pattern = re.compile(path)
            if re_pattern.search(file):
                path_file = file
            else:
                path_file = get_path(src_path, file)
        else:
            path_file = get_path(src_path, file)

        if check_depth(path_file, depth=depth):
            #recursive block
            if recursive and is_dir(path_file):
                chld_files = ls_dir(path_file)
                get_files(path_file, list_files=chld_files, db_files=db_files, recursive=True, depth=depth)
                logging.info("dir: %s" % (path_file))
            else:
                logging.info("file: %s" % (path_file))
            if is_patterns(path_file, patterns) and is_duplicate(path_file, db_files):
                db_files.append(path_file)
                logging.info("add file: %s" % (path_file))

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
