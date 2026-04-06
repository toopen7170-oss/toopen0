[app]
# (원본) 앱 이름 및 패키지 설정
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen

# (중요) 소스코드 확장자 및 포함 파일
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.include_patterns = assets/*,images/*
# 한글 폰트(nanum.ttf)가 있다면 반드시 포함되어야 합니다.
source.dir = .

# (버전) 앱 버전
version = 1.2

# (요구사항) 앱 실행에 필요한 라이브러리
requirements = python3,kivy==2.3.0,pillow,android,pyjnius

# (화면 설정)
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# ==========================================================
# [핵심 수정] GitHub Actions 무료 환경 최적화 경로
# ==========================================================

# 1. 시스템에 이미 깔린 SDK/NDK 경로를 강제로 사용 (다운로드 오류 방지)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724

# 2. 버전 고정 (GitHub ubuntu-22.04 환경 일치)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 27c

# 3. 빌드 속도 및 안정성 설정
android.skip_update = True
android.accept_sdk_license = True
android.log_level = 2
android.warn_on_root = 0

# 4. 권한 설정 (사진 읽기/쓰기 등 필요시)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (기타 빌드 설정)
[buildozer]
log_level = 2
warn_on_root = 1
