[app]
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.8

# [중요] plyer 라이브러리 필수 포함
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,plyer

orientation = portrait

# [중요] 안드로이드 권한 보강
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
