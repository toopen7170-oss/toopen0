import os, sys, traceback
from datetime import datetime

# [1. 블랙박스 및 엔진 보호막]
def write_log(msg):
    path = "/storage/emulated/0/Download/PristonTale_Log.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except: pass

def crash_guard(exctype, value, tb):
    write_log(f"!!! 비상 방역 시스템 가동 (튕김 감지) !!!\n{''.join(traceback.format_exception(exctype, value, tb))}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = crash_guard

# [2. Kivy 엔진 선제 최적화]
os.environ['KIVY_NO_ARGS'] = '1' # 인자 충돌 방지
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.core.window import Window
    from kivy.properties import BooleanProperty, StringProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.core.text import LabelBase
    from kivy.clock import Clock
    from kivy.utils import platform
except Exception as e:
    write_log(f"모듈 로드 단계 사전 차단: {e}")

# S26 울트라 고주사율 대응 및 렌더링 고정
Window.clearcolor = (0, 0, 0, 1)

# [3. 폰트 엔진 절대 안전 모드]
FONT_NAME = "Korean"
FONT_READY = False
if os.path.exists("/storage/emulated/0/Download/font.ttf"):
    try:
        LabelBase.register(name=FONT_NAME, fn_regular="/storage/emulated/0/Download/font.ttf")
        FONT_READY = True
    except: write_log("폰트 등록 오류: 기본 폰트로 우회")

# [4. UI 설계도: 렌더링 부하 분산 구조]
KV = """
<BaseButton@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    font_size: '18sp'
    background_normal: ''
    background_color: (0.1, 0.4, 0.2, 0.8)
    size_hint_y: None
    height: '50dp'

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
        Label:
            text: 'PristonTale Manager'
            font_name: 'Korean' if app.is_font_ready else None
            font_size: '30sp'
            size_hint_y: 0.4
        BaseButton:
            text: '관리 시작'
            on_release: app.root.current = 'detail_menu'

<DetailMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        BaseButton:
            text: '케릭정보창 (18)'
            on_release: app.root.current = 'info'
        BaseButton:
            text: '케릭장비창 (11)'
            on_release: app.root.current = 'equip'
        BaseButton:
            text: '메인으로'
            on_release: app.root.current = 'main'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
                padding: '10dp'
        BaseButton:
            text: '뒤로가기'
            on_release: app.root.current = 'detail_menu'

<EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
                padding: '10dp'
        BaseButton:
            text: '뒤로가기'
            on_release: app.root.current = 'detail_menu'
"""

# [5. 기능 로직: 순차적 위젯 사출 (사전 방역 핵심)]
class InfoScreen(Screen):
    def on_enter(self): # 화면이 완전히 뜬 후 실행
        self.ids.container.clear_widgets()
        fields = ["이름", "클랜", "레벨", "힘", "정신", "재능", "민첩", "건강", "생명력", "기력", "근력", "공격", "방어", "명중", "흡수", "속도", "직위", "기타"]
        for i, f in enumerate(fields):
            Clock.schedule_once(lambda dt, name=f: self.add_row(name), i * 0.03)

    def add_row(self, name):
        row = BoxLayout(size_hint_y=None, height='40dp')
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        row.add_widget(Label(text=name, font_name='Korean' if App.get_running_app().is_font_ready else None, size_hint_x=0.3))
        row.add_widget(TextInput(multiline=False))
        self.ids.container.add_widget(row)

class EquipScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
        for i, f in enumerate(fields):
            Clock.schedule_once(lambda dt, name=f: self.add_row(name), i * 0.03)

    def add_row(self, name):
        row = BoxLayout(size_hint_y=None, height='40dp')
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        row.add_widget(Label(text=name, font_name='Korean' if App.get_running_app().is_font_ready else None, size_hint_x=0.3))
        row.add_widget(TextInput(multiline=False))
        self.ids.container.add_widget(row)

class MainScreen(Screen): pass
class DetailMenuScreen(Screen): pass

class PristonTaleApp(App):
    is_font_ready = BooleanProperty(FONT_READY)
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DetailMenuScreen(name='detail_menu'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        return sm

if __name__ == '__main__':
    PristonTaleApp().run()
