[app]

# (str) Title of your application
title = toopen0

# (str) Package name
package.name = toopenapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (ttf, json 누락 방지)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Application requirements
# [필수] android와 pyjnius가 있어야 갤러리 호출 및 권한 설정이 가능합니다.
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
# 최신 안드로이드(API 33) 대응 권한을 모두 포함했습니다.
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# (int) Android API to use 
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# [에러 해결 포인트] 
# 특정 NDK 버전을 강제하거나 경로를 지정하면 GitHub 서버 환경과 충돌합니다.
# 버전을 비워두거나 시스템 기본값(25b)을 쓰되, 경로는 비워두어 자동 탐색하게 합니다.
android.ndk = 25b
android.ndk_path = 

# (bool) Use --private data storage (Internal storage)
android.private_storage = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) The Android arch to build for.
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (상세한 에러 확인을 위해 2로 설정)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
