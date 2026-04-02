[app]
# (str) Title of your application
title = toopen0

# (str) Package name
package.name = toopenapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (가장 중요한 부분: ttf 추가 완료)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 0.1

# (list) Application requirements
# 필요한 라이브러리들을 적습니다.
requirements = python3,kivy,pillow

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (list) List of Java .jar files to add to the libs dir
# android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) Android AAR archives to add
# android.add_aars =

# (list) Gradle dependencies
# android.gradle_dependencies =

# (bool) Enable AndroidX support
android.enable_androidx = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 0
