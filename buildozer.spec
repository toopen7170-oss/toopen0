[app]

# (적용) 앱 이름 및 패키지 설정
title = Priston Tale Chart
package.name = pt1_chart_final
package.domain = org.test

# (적용) 소스 코드 위치 및 포함 확장자
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.3

# (중요) 필수 라이브러리 목록 - plyer와 pillow가 반드시 포함되어야 합니다.
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,plyer

# (적용) 화면 방향 (세로 고정)
orientation = portrait

# (중요) 안드로이드 권한 설정 (저장소 및 카메라)
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

# (적용) 안드로이드 API 및 아키텍처 설정 (최신 규격)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# (적용) 전체화면 설정
android.fullscreen = 0

[buildozer]
# 로그 레벨 설정 (오류 확인용)
log_level = 2
warn_on_root = 1
