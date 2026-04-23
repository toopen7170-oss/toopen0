[app]
title = PristonTale
package.name = pristontale
package.domain = org.toopen0
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
version = 1.0

# [제1원칙] 리소스 설정
icon.filename = icon.png
presplash.filename = bg.png

requirements = python3,kivy==2.3.1,pillow,pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
# [권한 정밀 주입]
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, CAMERA

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.0
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
