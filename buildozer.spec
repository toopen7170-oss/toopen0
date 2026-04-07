[app]

# (기본 정보)
title = PT1 Chart App
package.name = pt1chart
package.domain = org.toopen

# (소스 및 폰트 포함 설정)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
# font.ttf가 포함되도록 ttf 확장자가 들어있어야 합니다.

version = 1.2

# (필요 라이브러리)
requirements = python3,kivy==2.3.0,pillow,android,pyjnius

# [핵심 수정] 화면 방향을 세로로 고정합니다.
orientation = portrait

# (안드로이드 설정)
osx.python_version = 3
osx.kivy_version = 1.9.1

fullscreen = 0

# [핵심 수정] 안드로이드 권한 (인터넷 및 사진첩 접근)
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# (빌드 설정)
android.accept_sdk_license = True
android.skip_update = False
android.setup_py = False

[buildozer]
log_level = 2
warn_on_root = 1
