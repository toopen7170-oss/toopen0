[app]
title = PristonTale
package.name = pristontale
package.domain = org.toopen0
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt,json
version = 1.0
icon.filename = icon.png
presplash.filename = bg.png

# S26 울트라 대응 필수 요구사항 보강
requirements = python3,kivy==2.3.1,pillow,pyjnius,android

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# 안드로이드 14(API 34) 대응 미디어 권한 전수 추가
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO, CAMERA

# API 레벨 상향 (중요: S26 울트라 호환성)
android.api = 34
android.minapi = 21
android.build_tools_version = 34.0.0
android.ndk = 25b
android.accept_sdk_license = True

# SDK 경로 (무료 서버 환경 고정)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

[buildozer]
log_level = 2
warn_on_root = 0
