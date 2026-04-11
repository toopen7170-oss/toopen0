[app]
# (section) 앱 기본 정보
title = PRISTON TALE MANAGER
package.name = pt1manager
package.domain = org.toopen

# 🎯 에러 해결: 앱 버전 정보를 명시합니다.
version = 1.1

# (section) 소스 코드 및 포함 파일 설정
# png, jpg, jpeg, ttf, json 파일을 모두 포함합니다.
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,json
source.include_patterns = assets/*,images/*

# (section) 앱 아이콘 설정
# 점주님의 단풍 아이콘(icon.png)을 적용합니다.
icon.filename = icon.png

# (section) 화면 방향 및 요구 사양
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0

# (section) 필수 라이브러리 (이미지 처리를 위해 pillow 필수)
requirements = python3,kivy==2.1.0,pillow

# (section) 안드로이드 전용 설정
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 🎯 사진첩 접근 및 저장 권한 (사진 안 보이는 문제 해결)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, INTERNET, MANAGE_EXTERNAL_STORAGE

# (section) 안드로이드 API 수준 (최신 폰 대응)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# (section) 빌드 최적화 및 라이선스 동의
android.skip_update = False
android.accept_sdk_license = True

# (section) 로그 출력 설정
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
