[app]
title = PT1 Manager
package.name = ptmanager
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 2.8.0

requirements = python3,kivy==2.3.0,pillow==10.2.0,pyjnius

icon.filename = icon.png
orientation = portrait
android.permissions = INTERNET, READ_MEDIA_IMAGES, MANAGE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
