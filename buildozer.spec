[app]
# 1. 앱 정보 (이미지 3번 반영)
title = PRISTON TAIL Manager
package.name = ptmanager
package.domain = org.toopen

# 2. 소스 및 확장자
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0

# 3. 필수 라이브러리 (GitHub Actions 빌드 최적화)
requirements = python3,kivy==2.3.0,pillow,pyjnius

# 4. 아이콘 설정 (저장소에 icon.png가 있어야 함)
icon.filename = icon.png

# 5. 화면 및 권한 (S26 울트라 최신 갤러리 대응)
orientation = portrait
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES

# 6. 안드로이드 시스템 설정 (API 34 - 안드로이드 14 대응)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

# 7. 네이티브 빌드 설정
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
