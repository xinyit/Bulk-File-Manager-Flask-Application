from flask import render_template, request
import os
from pathlib import Path
import re
import datetime
from shutil import copy

from app import app
from helper import *

@app.route('/')
def index():
    return render_template('index.html')

# ENDPOINT - provide frontend with list of file information for display
@app.route('/list_files', methods=['POST'])
def list_files():
    data = request.get_json()
    selected_directory = data.get('selected_directory')
    regex_string_filter = data.get('regex_string_filter')
    to_include_subdirectories = data.get('to_include_subdirectories')

    filepaths = get_filepaths(selected_directory, to_include_subdirectories, regex_string_filter)
    all_file_info = get_file_info(filepaths)
    
    return {'files': all_file_info}


# ENDPOINT - get filepaths as JSON / dictionary
@app.route('/get_filepaths_json', methods = ["POST"])
def get_filepaths_json():
    data = request.get_json()
    filepaths = get_filepaths(data["selected_directory"], data["to_include_subdirectories"], data["regex_string_filter"])
    return {'filepaths': filepaths}


# ENDPOINT - change file extension to user specified extension and return JSON / dictionary of new filepaths
@app.route('/change_file_extension', methods = ['POST'])
def change_file_extension():
    data = request.get_json()
    new_extension = data.get('new_extension')
    original_filepaths = data.get('filepaths')

    if original_filepaths == None:
        raise Exception("Original filepaths cannot be of Nonetype")
    
    new_filepaths = []
    for original_filepath in original_filepaths:
        pre, ext = os.path.splitext(original_filepath)
        new_filepath = pre + new_extension
        new_filepaths.append(new_filepath)

    return {'filepaths': new_filepaths}

# ENDPOINT - remove double spaces and return JSON / dictionary of new filepaths
@app.route('/remove_double_spaces', methods = ['POST'])
def remove_double_spaces():
    data = request.get_json()
    original_filepaths = data.get('filepaths')

    if original_filepaths == None:
        raise Exception("Original filepaths cannot be of Nonetype")

    new_filepaths = []
    for original_filepath in original_filepaths:
        original_filename = original_filepath.split('/')[-1]
        
        new_filename = re.sub('\s{2}', ' ', original_filename)
        new_filepaths.append(new_filename)

    return {'filepaths': new_filepaths}


# ENDPOINT - append today's date to filename and return JSON / dictionary of new filepaths
@app.route('/append_today_date', methods = ['POST'])
def append_today_date():
    data = request.get_json()
    original_filepaths = data.get('filepaths')

    if original_filepaths == None:
        raise Exception("Original filepaths cannot be of Nonetype")

    new_filepaths = []
    for original_filepath in original_filepaths:
        filename_without_extension = Path(original_filepath).stem
        file_extension = Path(original_filepath).suffix
        new_filename = filename_without_extension + " " + datetime.datetime.now().strftime('%Y-%m-%d') + file_extension
        new_filepaths.append(new_filename)

    return {'filepaths': new_filepaths}

# ENDPOINT - find using user specified regex string and replace with user specified string and return JSON / dictionary of new filepaths
@app.route('/regex_edit', methods = ['POST'])
def regex_edit():
    data = request.get_json()
    try:
        original_filepaths = data.get('filepaths')
        regex_from = data.get('regex_from')
        regex_to = data.get('regex_to')
    except:
        render_template('400.html')
            
    new_filepaths = []
    for original_filepath in original_filepaths:
        filename_without_extension = Path(original_filepath).stem
        file_extension = Path(original_filepath).suffix
        new_filename = re.sub(regex_from, regex_to, filename_without_extension)
        new_filepaths.append(new_filename + file_extension)
    
    return {'filepaths': new_filepaths}

# ENDPOINT - apply modifications, calls apply_modifications() for each file
@app.route('/apply_modifications', methods = ["POST"])
def call_apply_modifications():
    data = request.get_json()
    selected_directory = data.get('selected_directory')
    to_modify_original = data.get('to_modify_original')
    original_filepaths = data.get('original_filepaths')
    new_filepaths = data.get("new_filepaths")

    try:
        for i in range(len(new_filepaths)):
            new_filename = new_filepaths[i].split('/')[-1]
            apply_modifications(original_filepaths[i], new_filename, selected_directory, to_modify_original)
        return "applied modifications", 200
    except Exception as e:
        print(e)
        return f"error applying modifications {e}", 500