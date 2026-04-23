[app]
title = PristonTale
package.name = pristontale
package.domain = org.toopen8
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
version = 1.0

requirements = python3,kivy==2.3.0,pillow,pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# 사진 및 미디어 권한 추가
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
icon.filename = icon.png
presplash.filename = bg.png
