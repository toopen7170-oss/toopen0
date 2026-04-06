[app]
# 앱 기본 정보
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.include_patterns = assets/*,images/*

# 버전 및 아이콘
version = 1.2
orientation = portrait
fullscreen = 0

# 필수 라이브러리 (kivy 버전 고정으로 안정성 확보)
requirements = python3,kivy==2.3.0,pillow,android,pyjnius

# 안드로이드 아키텍처 (최신 폰 호환)
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# ==========================================================
# [중요] GitHub Actions 무료 빌드 최적화 경로 설정
# ==========================================================

# 1. 시스템에 이미 설치된 SDK/NDK 경로 강제 지정 (다운로드 에러 방지)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724

# 2. API 버전 및 NDK 버전 고정
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 27c

# 3. 빌드 안정성 설정 (자동 업데이트 끄고 라이선스 자동 승인)
android.skip_update = True
android.accept_sdk_license = True
android.log_level = 2
android.warn_on_root = 0

# 4. 앱 권한 (인터넷 및 저장소)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (기타 설정)
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
