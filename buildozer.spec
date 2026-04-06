[app]
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.include_patterns = assets/*,images/*
version = 1.2
orientation = portrait
fullscreen = 0
requirements = python3,kivy==2.3.0,pillow,android,pyjnius
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# ==========================================================
# [중요] GitHub 서버 환경(API 34)에 맞춘 최적화 설정
# ==========================================================
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724

# API 버전을 서버에 존재하는 34로 변경
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 27c

android.skip_update = True
android.accept_sdk_license = True
android.log_level = 2
android.warn_on_root = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
