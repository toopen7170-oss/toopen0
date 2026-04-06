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
# [수정] 폰트(ttf)와 데이터(json) 파일이 누락되지 않도록 포함 설정
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Application requirements
# [수정] 안드로이드 시스템 기능을 제어하기 위해 android와 pyjnius를 추가했습니다.
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
# [수정] 카메라 및 안드로이드 13 대응 최신 미디어 접근 권한 추가
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# (int) Android API to use 
# [수정] 최신 기기 호환성을 위해 API 33으로 설정
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

# (int) Log level (2 = 오류 발생 시 상세 로그 확인 가능)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
