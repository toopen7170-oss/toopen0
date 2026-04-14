[buildozer]
log_level = 2
warn_on_root = 1

[app]
title = toopen0
package.name = toopen0
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.23

# 핵심 라이브러리 및 권한 (S26 울트라 최적화)
requirements = python3,kivy==2.3.0,android,pyjnius,pillow
orientation = portrait
android.permissions = INTERNET,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,MANAGE_EXTERNAL_STORAGE

# 빌드 타겟 및 SDK 환경 고정
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# 빌드 안정성 설정
android.enable_androidx = True
android.logcat_filters = *:S python:D
android.add_activities = org.kivy.android.PythonActivity

