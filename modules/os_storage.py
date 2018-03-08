# coding: utf8
import os
from gluon import *

def get_size(start_path=None):
    '''
        Gets the size of directory including subdirectories starting from
        start_path
    '''
    total_size = 0 # in bytes
    if not start_path is None:
        seen = {}
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    stat = os.stat(fp)
                except OSError:
                    continue

                try:
                    seen[stat.st_ino]
                except KeyError:
                    seen[stat.st_ino] = True
                else:
                    continue

                total_size += stat.st_size
    
    total_mb = total_size/1000/1000
    return total_mb

def uploads_available_space(app_dir):
    '''
        Gets the used space for the uploads directory, returns a dictionairy 
        containing allowed, used and available space.
    '''
    dba = current.globalenv['db']
    row = dba.sys_properties(Property='storage_allowed_space')
    allowed_space = int(row.PropertyValue)
    
    uploads_dir = os.path.join(app_dir, 'uploads')
    used_space = get_size(uploads_dir)
    available_space = allowed_space - used_space
    
    full_message = DIV(BR(),
            B(current.T('Sorry, your OpenStudio storage is full...')), BR(),
            current.T('Please contact your OpenStudio administrator to \
                      increase the allowed storage.'))
    
    return dict(allowed=allowed_space,
                 used=used_space,
                 available=available_space,
                 full_message=full_message)
