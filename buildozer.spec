[app]
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
# [중요] ttf 확장자가 반드시 포함되어야 합니다!
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.2

requirements = python3,kivy==2.3.0,pillow,android,pyjnius

android.archs = arm64-v8a, armeabi-v7a
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b

# 폰트 파일이 루트에 있으므로 경로 비워둠
android.sdk_path = 
android.ndk_path = 

android.accept_sdk_license = True
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
