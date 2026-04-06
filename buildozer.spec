[app]

# (str) Title of your application
title = toopen0

# (str) Package name
package.name = toopenapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include 
# ttf와 json이 누락되지 않도록 확실히 포함했습니다.
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Application requirements
requirements = python3,kivy,pillow

# (str) Custom source folders for assets
source.include_patterns = assets/*,*.ttf

# (str) Application version
version = 0.1

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# -----------------------------------------------------------------------------
# Android specific
# -----------------------------------------------------------------------------

# (list) Permissions 
# 사진 기능을 위한 핵심 권한(CAMERA, STORAGE)을 모두 추가했습니다.
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, CAMERA

# (int) Android API to use 
# 최신 기기 대응을 위해 API 33으로 상향 조정했습니다.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (Internal storage)
android.private_storage = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) The Android arch to build for.
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (2 = 오류 추적을 위한 디버그 모드)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
