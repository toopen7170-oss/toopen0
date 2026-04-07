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

# 필요한 라이브러리
requirements = python3,kivy==2.3.0,pillow,android,pyjnius

# 아키텍처
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# API 버전 (GitHub 서버에 기본으로 깔린 34 사용)
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b

# 경로 설정 (비워두면 Buildozer가 시스템 경로를 자동으로 찾습니다)
android.sdk_path = 
android.ndk_path = 

android.skip_update = False
android.accept_sdk_license = True
android.log_level = 2
android.warn_on_root = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
