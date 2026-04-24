[app]
title = PristonTale
package.name = pristontale
package.domain = org.toopen0
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
version = 1.0
icon.filename = icon.png
presplash.filename = bg.png

# [핵심 수정] 범인 'filetype' 모듈 추가 완료
requirements = python3,kivy==2.3.1,pillow,pyjnius,android,filetype

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# S26 울트라 대응 권한 전수 허용
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO, CAMERA

android.api = 34
android.minapi = 21
android.build_tools_version = 34.0.0
android.ndk = 25b
android.accept_sdk_license = True

# 무료 서버 SDK 경로 고정
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

[buildozer]
log_level = 2
warn_on_root = 0
