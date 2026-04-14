[buildozer]
log_level = 2
warn_on_root = 1

[app]
title = toopen0
package.name = toopen0
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.24

# 핵심 라이브러리 및 권한 (S26 Ultra 최적화)
requirements = python3,kivy==2.3.0,android,pyjnius,pillow
orientation = portrait
android.permissions = INTERNET,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,MANAGE_EXTERNAL_STORAGE

# 빌드 환경 강제 동기화 (경로 충돌 해결용)
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False
android.auto_google_update = True

# 시스템 및 Gradle 설정
android.enable_androidx = True
android.logcat_filters = *:S python:D
android.add_activities = org.kivy.android.PythonActivity

