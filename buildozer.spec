[app]
title = Priston Tale Chart
package.name = pristontale_chart_v7
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 2.2

# plyer 라이브러리 필수
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,plyer

orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
