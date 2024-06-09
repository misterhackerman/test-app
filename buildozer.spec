[app]
# (str) Title of your application
title = CSki

# (str) Package name
package.name = cski

# (str) Package domain (you can use any domain you own or create a placeholder)
package.domain = org.example

# (str) Source code where the main.py file is located
source.dir = .

# (str) Main script file
source.include_exts = py,png,jpg,kv,atlas

# (str) The name of the entry point of your application
main = main.py

# (list) Permissions your app will request
android.permissions = INTERNET

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Application requirements
#requirements = python3,hostpython3,kivy,requests,beautifulsoup4,pillow
requirements = python3==3.7.6,hostpython3==3.7.6,kivy,requests,beautifulsoup4,pillow
osx.python_version=3.7.6
osx.kivy_version=1.9.1

# (str) Application versioning (format: major.minor.patch)
version = 0.1

# (str) Presplash of the application
presplash.filename = brain.png

# (str) Icon of the application
icon.filename = brain.png

# (list) Supported platforms
android.arch = armeabi-v7a

[buildozer]
# (str) Path to the build directory
build_dir = ./build

# (str) Path to buildozer.spec file, default is the current directory
specfile.path = ./buildozer.spec

[app:android]
# (str) Package domain for android
package.domain = org.example.cski

# (str) Application package
package.name = cski

# (str) Package version
version = 0.1

# (list) Permissions required by the application
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[app:ios]
# (str) Package domain for iOS
package.domain = org.example.cski
