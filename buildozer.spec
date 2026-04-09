[app]
# (str) Title of your application
title = PT1_Chart_App

# (str) Package name
package.name = pt1app

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) Application versioning (method 1)
# 빌드할 때마다 이 숫자를 조금씩 올려주세요 (예: 1.5, 1.6 ...)
version = 1.5

# (list) Application requirements
# 필요한 라이브러리들입니다.
requirements = python3,kivy,plyer,android

# (str) Supported orientations
orientation = portrait

# -----------------------------------------------------------------------------
# 안드로이드 설정 (중요!)
# -----------------------------------------------------------------------------

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
# 사진 선택을 위해 저장소 권한이 필요합니다.
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# [핵심 수정] 키보드가 올라올 때 화면을 위로 밀어올리는 설정입니다.
# 앞의 #을 제거하고 adjustPan으로 설정했습니다.
android.window_soft_input_mode = adjustPan

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
