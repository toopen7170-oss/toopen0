[buildozer]
log_level = 2
warn_on_root = 1

[app]
title = toopen0
package.name = toopen0
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.20

# 라이브러리 및 권한 설정
requirements = python3,kivy==2.3.0,android,pyjnius,pillow
orientation = portrait
android.permissions = INTERNET,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,MANAGE_EXTERNAL_STORAGE

# 안드로이드 빌드 아키텍처 (S26 울트라 최적화)
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# 시스템 및 Gradle 설정
android.enable_androidx = True
android.logcat_filters = *:S python:D
android.add_activities = org.kivy.android.PythonActivity

