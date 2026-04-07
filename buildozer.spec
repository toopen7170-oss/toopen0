[app]
# 앱 이름 및 패키지 설정
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.6

# --- 핵심 수정 사항: 필요한 라이브러리 추가 ---
# 사진 선택을 위한 plyer와 이미지 처리를 위한 pillow 추가
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,plyer

# 세로 화면 고정
orientation = portrait

# --- 핵심 수정 사항: 안드로이드 권한 설정 ---
# 사진첩 접근 및 저장소 권한 (안드로이드 13 이상 대응 포함)
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

# 서비스 및 하드웨어 가속
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# (선택 사항) 앱 아이콘이 있다면 아래 주석을 해제하고 파일명을 적으세요
# icon.filename = %(source.dir)s/icon.png

# (선택 사항) 시작 화면(스플래시) 이미지가 있다면 설정하세요
# presplash.filename = %(source.dir)s/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
