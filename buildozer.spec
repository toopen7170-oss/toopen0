[app]
# (section) 앱 기본 정보
title = PT1 Manager
package.name = pt1manager
package.domain = org.toopen

# (section) 소스 코드 및 포함 파일 설정
# 점주님 저장소의 py, png, jpg, jpeg, ttf, json 파일을 모두 포함합니다
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,json
source.include_patterns = assets/*,images/*

# (section) 앱 버전 및 아이콘
version = 1.1
# 아이콘 파일이 icon.png로 있다면 아래 주석을 해제하세요
# icon.filename = icon.png

# (section) 화면 방향 및 요구 사양
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0

# (section) 파이썬 라이브러리 (Kivy 필수)
requirements = python3,kivy==2.1.0,pillow

# (section) 안드로이드 전용 설정 (가장 중요!)
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 🎯 사진첩 접근 및 저장 권한 강제 허용
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, INTERNET

# (section) 안드로이드 API 수준 (최신 폰 대응)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# (section) 빌드 최적화
android.skip_update = False
android.accept_sdk_license = True

# (section) 로그 출력 설정
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
