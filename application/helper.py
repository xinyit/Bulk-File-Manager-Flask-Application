import os
from pathlib import Path
import math
import re
import datetime
import pytz
from shutil import copy

# HELPER FUNCTION - get all the filepaths as a list of strings
def get_filepaths(selected_directory, to_include_subdirectories, regex_string_filter):
    # get list of filepaths
    # if user selected option to include subdirectories
    if to_include_subdirectories:
        filepaths = []
        for root, dirs, files in os.walk(selected_directory):
            for file in files:
                filepath = os.path.join(root, file)
                filepaths.append(filepath)
    else:
        filenames = os.listdir(selected_directory)
        paths = [selected_directory + '/' + filename for filename in filenames]
        filepaths = [path for path in paths if os.path.isfile(path)]

    #filter files using user's input for regex filter
    if regex_string_filter is not None:
        regex_filter = re.compile(regex_string_filter)
        filepaths = [filepath for filepath in filepaths if regex_filter.match(filepath.split('/')[-1])]
    
    return filepaths


# HELPER FUNCTION - get file info (filename, extension, date modified, size)
def get_file_info(filepaths):
    try:
        all_file_info = []

        for filepath in filepaths:
            # filename
            filename_without_extension = Path(filepath).stem
            # file size
            file_size = (os.path.getsize(filepath))
            formatted_file_size = format_file_size(file_size)
            # datetime modified
            file_modified_dt_unix = os.path.getmtime(filepath)
            file_modified_dt = datetime.datetime.fromtimestamp(file_modified_dt_unix, tz = pytz.timezone('Asia/Singapore'))
            formatted_file_modified_dt = file_modified_dt.strftime("%d %B %Y %H:%M:%S")
            # file extension
            file_extension = Path(filepath).suffix

            file_info= {'filename': filename_without_extension, 'file_size': formatted_file_size, 'file_modified_dt': formatted_file_modified_dt, 'file_extension': file_extension}
            all_file_info.append(file_info)

        return all_file_info
    except Exception as e:
        raise e


# HELPER FUNCTION - readable file size string (using appropriate units)
def format_file_size(size):
    if size <= 0:
        return 0
    
    units = ["B", "kB", "MB", "GB", "TB"]
    digits = int(math.log10(size)//math.log10(1024))
    formatted_file_size = "{:.2f}".format(size/math.pow(1024, digits)) + " " + units[digits]
    
    return formatted_file_size


# HELPER FUNCTION - make modification
def apply_modifications(original_filepath, new_filename, selected_directory, apply_to_original):
    try:
        subdir = '/'.join(original_filepath[len(selected_directory):].split('/')[:-1]) + '/'
        
        if apply_to_original:
            os.rename(original_filepath, selected_directory + subdir + new_filename)
        else:
            new_directory = '/renamed_files/'
            if not os.path.exists(selected_directory + new_directory):
                os.mkdir(selected_directory + new_directory)
            copy(original_filepath, selected_directory + new_directory + new_filename)
        return
    except Exception as e:
        raise e
