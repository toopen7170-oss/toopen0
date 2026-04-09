[app]
title = Priston Tale
package.name = pristontale
package.domain = org.pt1
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 2.3

requirements = python3,kivy==2.3.0,plyer,android,setuptools

orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET
android.api = 33
android.minapi = 21
android.window_soft_input_mode = adjustPan
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
