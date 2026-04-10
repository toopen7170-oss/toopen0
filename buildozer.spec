[app]
# (str) 앱의 이름 (바탕화면에 표시될 이름)
title = PT1 Manager

# (str) 패키지 이름 (영문/숫자만 가능)
package.name = pt1manager

# (str) 패키지 도메인
package.domain = org.pt1

# (str) 소스 코드 경로
source.dir = .

# (list) 포함할 파일 확장자
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) 앱 버전
version = 4.0

# (list) 필수 라이브러리 (오류 수정을 위해 plyer 필수 포함)
requirements = python3,kivy,plyer

# (str) 바탕화면 아이콘 파일명 (아까 만드신 icon.png)
icon.filename = icon.png

# (str) 앱 실행 시 로딩 이미지 (bg.png 활용 가능)
presplash.filename = bg.png

# (str) 화면 방향 (세로 모드 고정)
orientation = portrait

# (bool) 전체 화면 모드
fullscreen = 1

# (list) 안드로이드 권한 (사진첩 및 카메라 접근 허용)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

# (int) 안드로이드 API 수준 (S26 Ultra 최신 환경 대응)
android.api = 33
android.minapi = 21
android.sdk = 33

# (str) 안드로이드 아키텍처 (최신 폰은 arm64-v8a 필수)
android.archs = arm64-v8a, armeabi-v7a

# (bool) 앱이 종료되어도 로그를 남길 수 있게 설정
android.logcat_filters = *:S python:D

# (list) 자바 컴파일 시 라이브러리 중복 오류 방지
android.gradle_dependencies = androidx.core:core:1.9.0

# (bool) 앱 빌드 시 디버그 모드 사용
android.debug_artifact = apk

[buildozer]
# (int) 로그 수준 (2로 설정하면 빌드 오류를 자세히 보여줍니다)
log_level = 2

# (int) 빌드 시 경고 무시
warn_on_root = 1
