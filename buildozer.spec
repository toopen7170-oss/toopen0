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

# 필수 라이브러리
requirements = python3,kivy==2.3.0,pillow,android,pyjnius

# 아키텍처 설정
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# ==========================================================
# [최종 수정] 경로 자동 감지 및 API 버전 고정
# ==========================================================
# 경로를 비워두면 Buildozer가 시스템(GitHub) 경로를 더 잘 찾아냅니다.
android.sdk_path = 
android.ndk_path = 

# GitHub Ubuntu 22.04 서버 기준 최적 버전
android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.skip_update = False

# 권한 설정
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
