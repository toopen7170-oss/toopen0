[app]
title = toopen0
package.name = toopenapp
package.domain = org.test
source.dir = .
# ttf 포함 확인
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0
# 사진 기능 필수 권한 추가 완료
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
