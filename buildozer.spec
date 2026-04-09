[app]
title = Priston Tale
package.name = pristontale
package.domain = org.pt1
source.dir = .
# ttf, png 파일이 확실히 포함되도록 체크
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 2.6

# plyer가 있으면 사진첩 접근이 가능하므로 유지
requirements = python3,kivy==2.3.0,plyer,android,setuptools

orientation = portrait
fullscreen = 0

# 중요: 안드로이드 11 이상 대응을 위한 권한 (공백 주의)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET, CAMERA
android.api = 33
android.minapi = 21
android.window_soft_input_mode = adjustPan
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
