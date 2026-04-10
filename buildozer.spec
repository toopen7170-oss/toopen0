[app]
title = PT1 Manager
package.name = pt1manager
package.domain = org.pt1
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.0
requirements = python3,kivy,plyer

# 아이콘을 만들기 전까지는 아래 두 줄 앞에 #을 붙여두세요.
# 만드신 후에 #을 지우고 icon.png 파일을 폴더에 넣으면 됩니다.
# icon.filename = icon.png
# presplash.filename = bg.png

orientation = portrait
fullscreen = 1
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA
android.api = 33
android.minapi = 21
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.gradle_dependencies = androidx.core:core:1.9.0

[buildozer]
log_level = 2
warn_on_root = 1
