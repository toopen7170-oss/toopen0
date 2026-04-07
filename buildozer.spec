[app]
# 앱의 기본 정보
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.7

# --- [권한 및 라이브러리 보강] ---
# 사진 선택을 위한 plyer와 이미지 처리를 위한 pillow를 반드시 포함해야 합니다.
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,plyer

# 화면 방향 (세로 고정)
orientation = portrait

# --- [안드로이드 권한 설정] ---
# 인터넷, 저장소 읽기/쓰기, 카메라 권한을 모두 허용합니다.
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

# 안드로이드 API 설정 (최신 기기 대응)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# --- [기타 설정] ---
fullscreen = 0
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
