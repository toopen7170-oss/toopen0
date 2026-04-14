[app]
title = PristonTale
package.name = PristonTale
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
source.include_patterns = assets/*,images/*
version = 0.1

requirements = python3,kivy==2.3.0,pillow,pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# 권한 명시 (데이터 저장 및 이미지 로드용)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.skip_update = False
android.log_level = 2

icon.filename = icon.png
presplash.filename = bg.png

[buildozer]
log_level = 2
warn_on_root = 0
