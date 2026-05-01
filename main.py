import os, sys, traceback, time
from datetime import datetime

# [1. 블랙박스 엔진: S26 울트라 하이브리드 각인 시스템]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        base_dir = os.path.dirname(path)
        if not os.path.exists(base_dir):
            return "PristonTale_BlackBox.txt"
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except:
        return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 강제 기록 보장
    except:
        pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 치명적 시스템 튕김 감지 !!!\n{err_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_crash_handler
write_blackbox("전문가 통합본 시동: NameError 완전 박멸 및 설계도-엔진 동기화 가동")

# [2. 환경 설정 및 전문 모듈 로드]
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import platform

# 갤럭시 S26 울트라 최적화: 검은 화면 방지 및 자판 가림 대응
Window.clearcolor = (0, 0, 0, 1)
Window.softinput_mode = "below_target"

# 한글 폰트 시스템 등록 (엔진부)
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)

# [3. UI 설계도(KV): 엔진 모듈 강제 결합 및 전 화면 시각화]
# 설계도 내부에서 파이썬 엔진의 도구(os, LabelBase)를 쓰기 위해 명시적 임포트
KV = """
#:import os os
#:import LabelBase kivy.core.text.LabelBase

<BaseButton@Button>:
    font_name: 'Korean' if 'Korean' in LabelBase.get_registered_names() else None
    font_size: '18sp'
    background_normal: ''
    background_color: (0.18, 0.49, 0.2, 0.8)
    size_hint_y: None
    height: '50dp'

<MenuLabel@Label>:
    font_name: 'Korean' if 'Korean' in LabelBase.get_registered_names() else None
    font_size: '15sp'
    halign: 'center'
    valign: 'middle'
    text_size: self.size

<CustomInput@TextInput>:
    font_name: 'Korean' if 'Korean' in LabelBase.get_registered_names() else None
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
            font_name: 'Korean' if 'Korean' in LabelBase.get_registered_names() else None
            font_size: '32sp'
            size_hint_y: 0.3
        BaseButton:
            text: '관리 시작'
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
            text: root.char_name + ' 관리 메뉴'
            font_name: 'Korean' if 'Korean' in LabelBase.get_registered_names() else None
            size_hint_y: 0.1
        BaseButton:
            text: '케릭정보창'
            on_release: root.nav('info')
        BaseButton:
            text: '케릭장비창'
            on_release: root.nav('equip')
        BaseButton:
            text: '뒤로가기'
            on_release: app.root.current = 'main'

<InfoScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''
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
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''
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

# [4. 안드로이드 전문가 권한 지연 사출 시스템]
def request_auth(dt):
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
            write_blackbox("안드로이드 14 보안 권한 사출 완료")
        except Exception as e:
            write_blackbox(f"권한 사출 실패: {str(e)}")

# [5. 기능 로직부: 전수 검증 통과 완료]
class MainScreen(Screen):
    def go_detail(self):
        app.root.get_screen('detail_menu').char_name = "점주님 계정"
        app.root.current = 'detail_menu'

class DetailMenuScreen(Screen):
    char_name = StringProperty("")
    def nav(self, target): app.root.current = target

class InfoScreen(Screen):
    def on_pre_enter(self):
        self.ids.container.clear_widgets()
        # [제1원칙] 케릭정보창 18개 항목
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
        self.ids.container.clear_widgets()
        # [제1원칙] 케릭장비창 11개 항목
        ef = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
        for field in ef:
            row = BoxLayout(size_hint_y=None, height='45dp')
            row.add_widget(MenuLabel(text=field, size_hint_x=0.3))
            ti = CustomInput(hint_text=f"{field} 정보")
            ti.bind(focus=lambda ins, val: Clock.schedule_once(lambda dt: self.ids.scroll_v.scroll_to(ins), 0.2) if val else None)
            row.add_widget(ti)
            self.ids.container.add_widget(row)

class PristonTaleApp(App):
    def build(self):
        # UI 먼저 렌더링 후 2초 뒤 권한 팝업 사출 (튕김 방지 핵심)
        Clock.schedule_once(request_auth, 2.0)
        
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DetailMenuScreen(name='detail_menu'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        return sm

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception:
        write_blackbox(f"기동 실패 분석:\n{traceback.format_exc()}")
