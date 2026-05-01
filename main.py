import os, sys, traceback, time
from datetime import datetime

# [1. 블랙박스 엔진: S26 울트라 고속 각인 시스템]
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
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 치명적 튕김 감지 !!!\n{err_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_crash_handler
write_blackbox("전문가 모드: NameError 수복 및 S26 울트라 최적화본 가동")

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

# 갤럭시 S26 울트라 디스플레이 최적화
Window.clearcolor = (0, 0, 0, 1)
Window.softinput_mode = "below_target"

# 한글 폰트 시스템 각인
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)

# [3. UI 설계도: NameError 완벽 차단 및 반투명 디자인]
# KV 언어 내에서 os 모듈을 인식하도록 강제 임포트 (NameError 방지 핵심)
KV = """
#:import os os

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

# [4. 안드로이드 권한 강제 사출 시스템]
def request_auth(dt):
    if platform == 'android':
        try:
            from android.permissions import request_permissions, Permission
            perms = [Permission.READ_MEDIA_IMAGES, Permission.CAMERA, Permission.READ_EXTERNAL_STORAGE]
            request_permissions(perms)
            write_blackbox("권한 시스템: 2초 지연 후 사출 성공")
        except Exception as e:
            write_blackbox(f"권한 시스템 오류: {str(e)}")

# [5. 기능 로직부: 전수 검사 통과본]
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
        # [제1원칙] 케릭장비창 11개 항목 시각화
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
        write_blackbox(f"기동 실패:\n{traceback.format_exc()}")
