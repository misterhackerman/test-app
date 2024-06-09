from kivy.app import App

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

