[app]

# (str) 앱 제목
title = PT1 Manager

# (str) 패키지 명
package.name = pt1manager

# (str) 패키지 도메인
package.domain = org.toopen

# (str) 소스 코드 위치
source.dir = .

# (list) 포함할 파일 확장자 (한글 폰트 ttf 및 데이터 json 필수 포함)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) 앱 버전
version = 1.0.0

# (list) 필수 라이브러리 (최신 Kivy 버전 고정 및 최적화)
requirements = python3,kivy==2.3.0,pillow

# (str) 화면 방향 (세로 모드 고정)
orientation = portrait

# (list) 안드로이드 권한 (사진 접근 및 저장소)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, INTERNET

# (int) 타겟 API 레벨 (갤럭시 S26 울트라 안드로이드 14 대응)
android.api = 34

# (int) 최소 지원 API
android.minapi = 21

# (str) NDK 버전 (안정적인 25b 버전 추천)
android.ndk = 25b

# (bool) 내부 저장소 사용 여부
android.private_storage = True

# (str) 엔트리 포인트
android.entrypoint = org.kivy.android.PythonActivity

# (list) 빌드 제외 확장자
android.exclude_exts = spec

# (str) CPU 아키텍처 (S26 울트라 최적화: 64비트 전용)
android.archs = arm64-v8a

# (bool) 자동 백업 허용
android.allow_backup = True

[buildozer]

# (int) 로그 레벨 (오류 추적을 위해 2로 설정)
log_level = 2

# (int) 루트 실행 경고
warn_on_root = 1

# (str) 결과물 저장 경로
# bin_dir = ./bin
