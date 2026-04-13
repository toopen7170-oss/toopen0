[app]
title = PRISTON TAIL Manager
package.name = ptmanager
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0

# [수정 완료] pyjnius 추가하여 갤러리 연동 에러 방지
requirements = python3,kivy==2.3.0,pillow,pyjnius

icon.filename = icon.png
orientation = portrait
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES

android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
