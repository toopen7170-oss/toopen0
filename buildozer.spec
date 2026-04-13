[app]

# (section) Title of your application
title = toopen0

# (section) Package name
package.name = toopen0

# (section) Package domain
package.domain = org.toopen

# (section) Source code where the main.py live
source.dir = .

# (section) Source files to include
source.include_exts = py,png,jpg,kv,ttf,json

# (section) Application version
version = 4.9.1

# (section) Application requirements
# [수정] 빌드 안정성을 위해 android, pyjnius, pillow 순서 최적화
requirements = python3, kivy==2.3.0, android, pyjnius, pillow

# (section) Supported orientations
orientation = portrait

# (section) Android specific
# [수정] 안드로이드 14 대응 필수 권한 세트
android.permissions = INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, MANAGE_EXTERNAL_STORAGE

# (section) Android API Levels
# [수정] S26 울트라 최신 OS 대응
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

# (section) Android Application Allow Backup
android.allow_backup = True

# (section) Android Logcat Filters
android.logcat_filters = *:S python:D

# (section) Services (if any)
android.services = 

# (section) Java classes to add to the manifest
# 갤러리 인텐트 호출을 위한 추가 설정
android.add_activities = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
