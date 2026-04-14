[app]
title = PristonTale
package.name = PristonTale
package.domain = org.test
source.dir = .
# [검토 완료] json 포함
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
source.include_patterns = assets/*,images/*
version = 0.1

requirements = python3,kivy==2.3.0,pillow,pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# [검토 완료] 안드로이드 권한 명시
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
