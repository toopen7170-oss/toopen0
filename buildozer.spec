[app]
title = toopen0
package.name = toopen0
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt
source.include_patterns = assets/*,images/*
version = 0.1

requirements = python3,kivy==2.3.0,pillow,pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# 서버 환경 고착 방지용 고정 버전
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
