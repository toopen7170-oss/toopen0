[app]
title = PristonTale
package.name = pristontale
package.domain = org.toopen8
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
version = 1.0
requirements = python3,kivy==2.3.1,pillow,pyjnius
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.0
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
