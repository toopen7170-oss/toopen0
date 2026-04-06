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
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Application requirements
requirements = python3,kivy,pillow,android,pyjnius

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
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# (int) Android API to use 
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# [중요] GitHub 서버의 실제 SDK/NDK 경로를 강제로 지정합니다.
# 이 경로 설정이 없으면 sdkmanager를 엉뚱한 곳에서 찾다가 실패합니다.
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724
android.ndk = 25b

# (bool) Use --private data storage (Internal storage)
android.private_storage = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) The Android arch to build for.
android.archs = arm64-v8a, armeabi-v7a

# (bool) Skip SDK/NDK update (이미 서버에 설치된 것을 쓰므로 업데이트를 건너뜁니다)
android.skip_update = True

# (bool) Accept SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
