[app]
title = PT1 Manager
package.name = pt1manager
package.domain = org.pt1
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 4.0
requirements = python3,kivy,plyer

# 아이콘 파일이 생기면 주석(#)을 제거하세요
# icon.filename = icon.png

orientation = portrait
fullscreen = 1
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.gradle_dependencies = androidx.core:core:1.9.0

[buildozer]
log_level = 2
warn_on_root = 1
