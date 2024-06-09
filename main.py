import kivy
from kivy.app import App
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

class DownloaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.category_label = Label(text="Select Category:")
        self.layout.add_widget(self.category_label)
        
        self.category_spinner = Spinner(
            text='Select a category',
            values=list(categories.keys()),
        )
        self.layout.add_widget(self.category_spinner)
        self.category_spinner.bind(text=self.update_courses_menu)
        
        self.course_label = Label(text="Select Course:")
        self.layout.add_widget(self.course_label)
        
        self.course_spinner = Spinner(text='Select a category first')
        self.layout.add_widget(self.course_spinner)
        
        self.folder_label = Label(text="Select Destination Folder:")
        self.layout.add_widget(self.folder_label)
        
        self.folder_input = TextInput(hint_text='Folder path')
        self.layout.add_widget(self.folder_input)
        
        self.browse_button = Button(text='Browse...', on_press=self.browse_folder)
        self.layout.add_widget(self.browse_button)
        
        self.filetype_label = Label(text="Select File Types:")
        self.layout.add_widget(self.filetype_label)
        
        self.pdf_checkbox = CheckBox(text='PDF')
        self.layout.add_widget(self.pdf_checkbox)
        self.ppt_checkbox = CheckBox(text='PPT')
        self.layout.add_widget(self.ppt_checkbox)
        
        self.start_button = Button(text='Start Download', on_press=self.start_download)
        self.layout.add_widget(self.start_button)
        
        self.progress_bar = ProgressBar()
        self.layout.add_widget(self.progress_bar)
        
        return self.layout
    
    def browse_folder(self, instance):
        filechooser = FileChooserIconView()
        popup = Popup(title="Select Folder", content=filechooser, size_hint=(0.9, 0.9))
        
        def on_selection(instance, selection):
            if selection:
                self.folder_input.text = selection[0]
            popup.dismiss()
        
        filechooser.bind(on_selection=on_selection)
        popup.open()
    
    def update_courses_menu(self, spinner, text):
        if text in categories:
            self.course_spinner.values = [course[1] for course in find_courses(categories[text])]
        else:
            self.course_spinner.values = []
    
    def start_download(self, instance):
        selected_category = self.category_spinner.text
        selected_course = self.course_spinner.text
        download_folder = self.folder_input.text
        selected_file_types = []
        if self.pdf_checkbox.active:
            selected_file_types.append('.pdf')
        if self.ppt_checkbox.active:
            selected_file_types.append('.ppt')
        
        def download_thread():
            try:
                category_url = categories[selected_category]
                courses = find_courses(category_url)
                course_number = next(course[2] for course in courses if course[1] == selected_course)
                course_url = f'https://msc-mu.com/courses/{course_number}'
                course_page = requests.get(course_url, headers=HEADERS)
                soup = BeautifulSoup(course_page.text, 'html.parser')
                print(DECOR + ' Creating navigation links dictionary...')
                nav_dict = create_nav_links_dictionary(soup)
                print(DECOR + ' Finding all files paths and links...')
                paths_links = find_files_paths_and_links(nav_dict, soup, selected_file_types)
                print(DECOR + ' Downloading from dictionary...')
                download_from_dict(paths_links, download_folder, self.progress_bar)
            except Exception as e:
                self.show_popup("Error", f"Failed to download files: {e}")

        threading.Thread(target=download_thread).start()
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text='Close', size_hint=(1, 0.25))
        popup
