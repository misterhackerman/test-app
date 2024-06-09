import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserIconView

from bs4 import BeautifulSoup
import requests
import re
import os
import threading
import json

from package.downloaderApp import DownloaderApp

# Constants
DECOR = ' ::'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
STATE_FILE = "app_state.json"

# Categories data
categories = {
    'Athar': 'https://msc-mu.com/level/17',
    'Rou7': 'https://msc-mu.com/level/16',
    'Wateen': 'https://msc-mu.com/level/15',
    'Nabed': 'https://msc-mu.com/level/14',
    'Wareed': 'https://msc-mu.com/level/13',
    'Minors': 'https://msc-mu.com/level/10',
    'Majors': 'https://msc-mu.com/level/9'
}

# Load and save application state
def load_state():
    global favorites, dark_mode, download_progress
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            state = json.load(file)
            favorites = state.get("favorites", [])
            dark_mode = state.get("dark_mode", False)
            download_progress = state.get("download_progress", {})
    else:
        favorites = []
        dark_mode = False
        download_progress = {}

def save_state():
    with open(STATE_FILE, 'w') as file:
        state = {
            "favorites": favorites,
            "dark_mode": dark_mode,
            "download_progress": download_progress
        }
        json.dump(state, file)

# Functions
def find_courses(url):
    page = requests.get(url, headers=HEADERS)
    doc = BeautifulSoup(page.text, 'html.parser')
    subject = doc.find_all('h6')
    courses = []
    for x, i in enumerate(subject):
        parent = i.parent.parent.parent
        course_number = re.findall('href="https://msc-mu.com/courses/(.*)">', parent.decode())[0]
        course_name = i.string.strip()
        courses.append([x + 1, course_name, course_number])
    return courses

def create_nav_links_dictionary(soup):
    navigate_dict = {}
    nav_links = soup.find_all('li', attrs={"class": "nav-item"})
    for navigate_link in nav_links:
        if navigate_link.h5:
            nav_name = navigate_link.h5.text.strip()
            nav_number = navigate_link.a.get('aria-controls')
            navigate_dict[nav_number] = nav_name
    return navigate_dict

def make_course_folder(folder, course_name):
    new_folder = os.path.join(folder, course_name)
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)
    return new_folder

def find_files_paths_and_links(navigation_dict, soup, file_types):
    file_tags = []
    for file_type in file_types:
        file_tags.extend(soup.find_all('a', string=lambda text: text and file_type in text))

    files_list = []
    path = []
    associated_nav_link_id = ''
    for file_tag in file_tags:
        current_tag = file_tag
        if not current_tag:
            print('No files found for the selected extensions!')
            quit()
        while True:
            current_tag = current_tag.parent
            if current_tag.name == 'div' and 'mb-3' in current_tag.get('class', []):
                path.append(current_tag.h6.text.strip())
            if current_tag.name == 'div' and 'tab-pane' in current_tag.get('class', []):
                associated_nav_link_id = current_tag.get('id')
            if not current_tag.parent:
                break
        path.append(navigation_dict[associated_nav_link_id])
        path.reverse()
        basename = file_tag.text
        file_path = "/".join(path) + os.path.sep
        path.clear()

        file_link = file_tag.get('href')
        files_list.append([file_path, file_link, basename])
    return files_list

def download_from_dict(path_link_dict, folder, progress_bar):
    counter = 0
    total_files = len(path_link_dict)

    for path, link, name in path_link_dict:
        counter += 1
        count = f' ({counter}/{total_files})'
        full_path = os.path.join(folder, path)

        if os.path.isfile(os.path.join(full_path, name)):
            print('[ Already there! ] ' + name + count)
            # Add your GUI logic for already downloaded files
            continue

        if not os.path.isdir(full_path):
            os.makedirs(full_path)

        response = requests.get(link, headers=HEADERS)
        with open(os.path.join(full_path, name), 'wb') as file:
            file.write(response.content)
        print(DECOR + ' Downloaded ' + name + count)
        # Add your GUI logic for downloaded files

        # Update the progress bar
        progress = counter / total_files
        progress_bar.value = progress
