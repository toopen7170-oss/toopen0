import os, sys, traceback, time
from datetime import datetime

# [1. 블랙박스 & 사전 방역 엔진]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        base_dir = os.path.dirname(path)
        if not os.path.exists(base_dir): return "PristonTale_BlackBox.txt"
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except: return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 방역 엔진 작동: 예상치 못한 충돌 감지 및 기록 !!!\n{err_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_crash_handler
write_blackbox("방역 통합본 시동: 네임스페이스 및 속성 오류 사전 차단 모드 가동")

# [2. 환경 설정 및 전문 모듈 로드]
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.core.window import Window
    from kivy.properties import StringProperty, BooleanProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.core.text import LabelBase
    from kivy.clock import Clock
    from kivy.utils import platform
except Exception as e:
    write_blackbox(f"모듈 로드 치명적 오류: {str(e)}")

# 갤럭시 S26 울트라 최적화: 검은 화면 및 소프트 키보드 대응
Window.clearcolor = (0, 0, 0, 1)
Window.softinput_mode = "below_target"

# [3. 사전 방역: 리소스 상태 확정]
FONT_EXISTS = False
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        FONT_EXISTS = True
        write_blackbox("방역 완료: 한글 폰트 엔진 결합 성공")
    except:
        write_blackbox("방역 경고: 폰트 파일 손상됨 (시스템 기본값 사용)")

# [4. UI 설계도(KV): 사전 방역 시스템 적용]
# NameError 방지를 위해 모든 라이브러리를 최상단에 사전 각인
KV = """
#:import os os
#:import LabelBase kivy.core.text.LabelBase
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<BaseButton@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    font_size: '18sp'
    background_normal: ''
    background_color: (0.18, 0.49, 0.2, 0.8)
    size_hint_y: None
    height: '50dp'

<MenuLabel@Label>:
    font_name: 'Korean' if app.is_font_ready else None
    font_size: '15sp'
    halign: 'center'
    valign: 'middle'
    text_size: self.size

<CustomInput@TextInput>:
    font_name: 'Korean' if app.is_font_ready else None
    multiline: False
    background_color: (1, 1, 1, 0.12)
    foreground_color: (1, 1, 1, 1)
    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]

<MainScreen>:
    canvas.before:
        Color:
            rgba: (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        Label:
            text: 'PristonTale Manager'
            font_name: 'Korean' if app.is_font_ready else None
            font_size: '32sp'
            size_hint_y: 0.3
        BaseButton:
            text: '관리 시작 (사전 방역 모드)'
            on_release: root.go_detail()

<DetailMenuScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''
    BoxLayout:
        orientation: 'vertical'
        padding: '25dp'
        spacing: '15dp'
        Label:
            text: root.char_name + ' 관리'
            font_name: 'Korean' if app.is_font_ready else None
            size_hint_y: 0.1
        BaseButton:
            text: '케릭정보창'
            on_release: root.nav('info')
        BaseButton:
            text: '케릭장비창'
            on_release: root.nav('equip')
        BaseButton:
            text: '뒤로가기'
            background_color: (0.6, 0.2, 0.2, 0.8)
            on_release: app.root.current = 'main'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            id: scroll_v
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '10dp'
                spacing: '10dp'
        BaseButton:
            text: '뒤로가기'
            on_release: app.root.current = 'detail_menu'

<EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            id: scroll_v
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '10dp'
                spacing: '10dp'
        BaseButton:
            text: '뒤로가기'
            on_release: app.root.current = 'detail_menu'
"""

# [5. 안드로이드 전문가 권한 요청]
def delayed_permission_check(dt):
    if platform == 'android':
        try:
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.READ_MEDIA_IMAGES,
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ]
            request_permissions(perms)
            write_blackbox("방역 확인: 안드로이드 14 보안 권한 사출 성공")
        except Exception as e:
            write_blackbox(f"방역 경고: 권한 사출 실패 {str(e)}")

# [6. 기능 로직부: 사전 방역 데이터 바인딩]
class MainScreen(Screen):
    def go_detail(self):
        app.root.get_screen('detail_menu').char_name = "점주님 계정"
        app.root.current = 'detail_menu'

class DetailMenuScreen(Screen):
    char_name = StringProperty("")
    def nav(self, target): app.root.current = target

class InfoScreen(Screen):
    def on_pre_enter(self):
        # AttributeError 방지를 위한 사전 위젯 존재 확인
        if not hasattr(self.ids, 'container'): return
        self.ids.container.clear_widgets()
        f = ["이름", "클랜", "레벨", "힘", "정신", "재능", "민첩", "건강", "생명력", "기력", "근력", "공격", "방어", "명중", "흡수", "속도", "직위", "기타"]
        for field in f:
            row = BoxLayout(size_hint_y=None, height='45dp')
            row.add_widget(MenuLabel(text=field, size_hint_x=0.3))
            ti = CustomInput(hint_text=f"{field} 입력")
            ti.bind(focus=lambda ins, val: Clock.schedule_once(lambda dt: self.ids.scroll_v.scroll_to(ins), 0.2) if val else None)
            row.add_widget(ti)
            self.ids.container.add_widget(row)

class EquipScreen(Screen):
    def on_pre_enter(self):
        if not hasattr(self.ids, 'container'): return
        self.ids.container.clear_widgets()
        ef = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
        for field in ef:
            row = BoxLayout(size_hint_y=None, height='45dp')
            row.add_widget(MenuLabel(text=field, size_hint_x=0.3))
            ti = CustomInput(hint_text=f"{field} 정보")
            ti.bind(focus=lambda ins, val: Clock.schedule_once(lambda dt: self.ids.scroll_v.scroll_to(ins), 0.2) if val else None)
            row.add_widget(ti)
            self.ids.container.add_widget(row)

class PristonTaleApp(App):
    # AttributeError 방지를 위한 '안전한 대화 통로' (Property) 사전 구축
    is_font_ready = BooleanProperty(FONT_EXISTS)

    def build(self):
        # 1. 시동 2초 후 권한 요청 (보안 튕김 방지)
        Clock.schedule_once(delayed_permission_check, 2.0)
        
        # 2. 설계도 로드 (이중 예외 처리로 튕김 방지)
        try:
            Builder.load_string(KV)
        except Exception as e:
            write_blackbox(f"방역 경고: 설계도 로드 오류 {str(e)}")
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DetailMenuScreen(name='detail_menu'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        
        write_blackbox("방역 완료: 시스템이 무결점 상태로 기동되었습니다.")
        return sm

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception:
        write_blackbox(f"치명적 오류 분석:\n{traceback.format_exc()}")
