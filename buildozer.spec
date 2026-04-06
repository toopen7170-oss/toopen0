[app]
title = toopen0
package.name = toopenapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
requirements = python3,kivy,pillow,android,pyjnius
source.include_patterns = assets/*,*.ttf
version = 0.1
orientation = portrait
fullscreen = 0

# Android specific
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES
android.api = 33
android.minapi = 21

# [수정] 경로를 직접 쓰지 않고 Buildozer가 자동으로 찾게 비워둡니다.
# 대신 skip_update를 False로 해서 필요한 도구를 스스로 받게 합니다.
android.sdk_path = 
android.ndk_path = 
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity
android.enable_androidx = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 0
