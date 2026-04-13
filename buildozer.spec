[app]
title = toopen0
package.name = toopen0
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.0.0

requirements = python3,kivy==2.3.0,pillow,pyjnius

orientation = portrait
android.permissions = READ_MEDIA_IMAGES, INTERNET, MANAGE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
