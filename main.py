import os, sys, traceback
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.text import LabelBase

# [1. 블랙박스 및 자가 진단 각인 엔진]
def write_blackbox(msg):
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 시스템 비상 종료 (자가 진단 실패) !!!\n{err_msg}")
    # 점주님 폰 화면에 마지막 오류 표시 시도
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 오류 방역: 한글 폰트 수복]
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)
    DEFAULT_FONT = "Korean"
else:
    DEFAULT_FONT = "Roboto"

# [3. KV 설계도: 자가 진단 인터페이스 및 5단계 계층]
KV = """
<BaseLayout@BoxLayout>:
    orientation: 'vertical'
    padding: '12dp'
    spacing: '8dp'
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if app.bg_ready else ''

<AccountScreen>:
    BaseLayout:
        Label:
            text: '1. 계정 접속'
            font_name: app.font_name
            size_hint_y: None
            height: '60dp'
        Button:
            text: '테스트 계정 진입'
            font_name: app.font_name
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'char_select'

<CharSelectScreen>:
    BaseLayout:
        Label:
            text: '2. 캐릭터 선택'
            font_name: app.font_name
            size_hint_y: None
            height: '60dp'
        Button:
            text: '전사(Fighter) Lv.100'
            font_name: app.font_name
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'char_menu'

<CharMenuScreen>:
    BaseLayout:
        Label:
            text: '3. 캐릭터 관리 메뉴'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
        GridLayout:
            cols: 1
            spacing: '10dp'
            Button:
                text: '▶ 케릭정보창 (18개)'
                font_name: app.font_name
                on_release: app.root.current = 'info'
            Button:
                text: '▶ 케릭장비창 (11개)'
                font_name: app.font_name
                on_release: app.root.current = 'equip'
            Button:
                text: '▶ 인벤토리창'
                font_name: app.font_name
            Button:
                text: '▶ 사진선택창'
                font_name: app.font_name
            Button:
                text: '▶ 저장보관소'
                font_name: app.font_name
        Button:
            text: '캐릭터 선택으로'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'char_select'

<InfoScreen>:
    BaseLayout:
        Label:
            id: info_title
            text: ''
            font_name: app.font_name
            size_hint_y: None
            height: '40dp'
        ScrollView:
            BoxLayout:
                id: info_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        Button:
            text: '저장 및 복귀'
            font_name: app.font_name
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'char_menu'

<EquipScreen>:
    BaseLayout:
        Label:
            id: equip_title
            text: ''
            font_name: app.font_name
            size_hint_y: None
            height: '40dp'
        ScrollView:
            BoxLayout:
                id: equip_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        Button:
            text: '저장 및 복귀'
            font_name: app.font_name
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'char_menu'
"""

# [4. 자가 치유 로직: 지연 사출 및 무결성 검증]
class InfoScreen(Screen):
    ITEMS = ["이름", "직위", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩", "건강", "명중", "공격", "방어", "흡수", "속도", "종합"]
    def on_enter(self):
        self.ids.info_box.clear_widgets()
        write_blackbox("정보창 자가 치유 사출 시작")
        Clock.schedule_once(self._build_items, 0.2)

    def _build_items(self, dt):
        self.ids.info_title.text = "케릭정보 (18항목)"
        for item in self.ITEMS:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, font_name=App.get_running_app().font_name, size_hint_x=0.35))
            row.add_widget(TextInput(multiline=False, halign='center'))
            self.ids.info_box.add_widget(row)

class EquipScreen(Screen):
    ITEMS = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타장비"]
    def on_enter(self):
        self.ids.equip_box.clear_widgets()
        write_blackbox("장비창 자가 치유 사출 시작")
        Clock.schedule_once(self._build_items, 0.2)

    def _build_items(self, dt):
        self.ids.equip_title.text = "케릭장비 (11항목)"
        for item in self.ITEMS:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, font_name=App.get_running_app().font_name, size_hint_x=0.35, color=(0,1,1,1)))
            row.add_widget(TextInput(multiline=False, halign='center'))
            self.ids.equip_box.add_widget(row)

class AccountScreen(Screen): pass
class CharSelectScreen(Screen): pass
class CharMenuScreen(Screen): pass

# [5. 메인 시스템: 자가 진단 및 사출 엔진]
class PristonTaleApp(App):
    font_name = StringProperty(DEFAULT_FONT)
    bg_ready = BooleanProperty(False)

    def build(self):
        write_blackbox("시스템 부팅 - 자가 진단 개시")
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharMenuScreen(name='char_menu'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        
        # 배경 사출 1.5초 지연 (팅김 방역)
        Clock.schedule_once(lambda dt: setattr(self, 'bg_ready', True), 1.5)
        return sm

if __name__ == '__main__':
    PristonTaleApp().run()
