#!/usr/bin/env python
# -*- coding: utf-8 -*-
#BakirovAR turkin86@mail.ru
import tarfile
import os
import sys
import logging
import re
import json
import argparse

def get_config_files(path, patterns="*.conf"):
    depth=1
    return load(get_path(path, 'etc/'), patterns, depth=depth)

def load(path, items, depth=0, recursive=False):
    flist = [] # Список всех файлов
    root_files = []
    root_path = os.path.abspath(path)
    len_depth = get_len_depth(root_path, depth)
    patterns_list = init_patterns(items)
    #Получть список файлов в корневом катологе
    get_files(root_path, db_files=flist, recursive=recursive, depth=len_depth, patterns=patterns_list)
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
    len_path =len(path.split(sep)[1:])
    if len_path <= depth or depth == 0:
        return True
    return False

def load_data(data):
    pass

def main(data):
    logging.basicConfig(level=logging.INFO)
    dp = data.get("dump")
    archive_file = ''.join([dp.get('path'), dp.get('name'),'.', dp.get('type')])
    items = dp.get('items')
    files_list = []
    for item in items:
        path = item.get('path')
        depth = item.get('depth') or 0
        recursive = item.get('recursive') or False
        patterns = item.get('items')
        flist = load(path, patterns, depth=depth, recursive=recursive)
        if flist:
            files_list = files_list + flist
    #Архивирование данных
    create_archive(archive_file, files_list)

def create_archive(name, files, recursive=False, archive_type="gz"):
    archive = tarfile.open(name, ":".join(["w", archive_type]))
    if files:
        for f in files:
            archive.add(f, recursive=recursive)
            logging.info("archive add file: %s" % (f))
    archive.close()

def is_duplicate(item, data_list):
    return item not in data_list

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
        for pattern in patterns:
            pattern = os.path.normpath(pattern)
            root_path, extension = os.path.splitext(pattern)
            root_path = os.path.normpath(root_path)
            #/path_pattern/*.extension
            if root_path != '*' and root_path and extension:
                root_pattern = re.compile(root_path)
                extension_pattern = re.compile(''.join([extension, '$']))
                if root_pattern.search(path) and extension_pattern.search(path):
                    logging.debug("root_path extension  path: %s" % (path))
                    return True
            #*.extension        
            elif root_path == '*' and extension:
                #head, tail = os.path.split(root_path)
                re_pattern = re.compile(''.join(['/.*\w+', extension, '$']))
                if re_pattern.search(path):
                    logging.debug("File extension by pattern: %s" % (path))
                    return True              
            #/path_pattern/*
            else:
                re_pattern = re.compile(pattern)
                if re_pattern.search(path):
                    logging.debug("This is the right path pattern: %s, %s" % (pattern, path))
                    return True
    elif not patterns:
        return True
    else:
        return False

def is_it_possible_add(path, patterns, files=[]):
    return is_patterns(path, patterns) and is_duplicate(path, files)

def get_dir_files(path, files=None):
    fls = None
    if isinstance(files, list):
        fls = files
    elif is_dir(path):    
        ls = ls_dir(path)
        if not ls:
            return path
        fls = ls
    return fls

def get_files(path, list_files=None, db_files=[], recursive=False, depth=0, patterns=None):
    files = get_dir_files(path, files=list_files);
    if isinstance(files, basestring) and is_it_possible_add(files, patterns, files=db_files):
        db_files.append(files)
    elif files:
        for file in files:
            path_file = None
            if os.path.isabs(file):
                re_pattern = re.compile(path)
                if re_pattern.search(file):
                    path_file = file
                else:
                    path_file = get_path(path, file)
            else:
                path_file = get_path(path, file)

            if check_depth(path_file, depth=depth):
                #recursive block
                if recursive and is_dir(path_file):
                    chld_files = ls_dir(path_file)
                    if chld_files:
                        get_files(path_file, list_files=chld_files, db_files=db_files, recursive=True, depth=depth, patterns=patterns)
                        logging.debug("This is directory: %s" % (path_file))
                # else:
                #     logging.info("file: %s" % (path_file))
                if is_it_possible_add(path_file, patterns, files=db_files):
                    db_files.append(path_file)
                    logging.debug("Add file to internal list: %s" % (path_file))
    else:
        logging.error("File: %s not found." % (path))

def ls_dir(path):
    src_path = os.path.normpath(path)
    if not is_dir(src_path):
        logging.error("%s" % (e))
        return []
    return os.listdir(src_path)

def is_dir(path):
    src_path = os.path.normpath(path)
    return os.path.isdir(src_path)

def get_path(path, file):
    if file and file[0] == os.sep:
        return os.path.join(path, file[1:])
    return os.path.join(path, file)

def load_configs(path):
    try:
        fconfig = open(path, 'r')
        return json.load(fconfig)
    except IOError:
        logging.error("File: %s not found." % (path))
   
if __name__ == "__main__":
    program_name = os.path.basename(__file__)
    app_path = os.path.dirname(os.path.abspath(__file__))
    config_default = get_config_files(app_path)
    #parser arguments
    parser = argparse.ArgumentParser(description='Files dump')
    parser.add_argument('--config', help='/your/path/json/config/file', default=config_default[:1])
    arguments = parser.parse_args(sys.argv[1:])
    configs = load_configs(arguments.config)
    if configs:
        main(configs)
