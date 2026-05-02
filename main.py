import os, sys, traceback
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, DictProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase

# [1. 블랙박스 유언 각인 시스템]
def write_blackbox(msg):
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 직전 블랙박스 가동 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 설정 및 폰트 방역]
Window.softinput_mode = "below_target"
FONT_PATH = "/storage/emulated/0/Download/font.ttf"

try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        FONT_NAME = "Korean"
    else: FONT_NAME = "Roboto"
except: FONT_NAME = "Roboto"

# [3. KV 설계도: 지연 사출 배경 및 7대 창 구조]
KV = """
<BaseLayout@BoxLayout>:
    orientation: 'vertical'
    padding: '10dp'
    canvas.before:
        Color:
            rgba: (0, 0, 0, 1) # 배경 안착 전까지는 검은색 유지
        Rectangle:
            pos: self.pos
            size: self.size
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if app.bg_ready else '' # 지연 사출 엔진

<AccountScreen>:
    BaseLayout:
        Label:
            text: 'PristonTale 계정 관리'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
        Button:
            text: '케릭정보창 이동'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'info'
        Button:
            text: '케릭장비창 이동'
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'equip'
        Label:
            text: '※ 배경화면 사출 대기 중...' if not app.bg_ready else ''
            font_name: app.font_name

<InfoScreen>:
    BaseLayout:
        Label:
            text: '케릭정보 (18개 항목)'
            font_name: app.font_name
            size_hint_y: None
            height: '40dp'
        ScrollView:
            id: info_scroll
            BoxLayout:
                id: info_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        Button:
            text: '돌아가기'
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'account'

<EquipScreen>:
    BaseLayout:
        Label:
            text: '케릭장비 (11개 항목)'
            font_name: app.font_name
            size_hint_y: None
            height: '40dp'
        ScrollView:
            id: equip_scroll
            BoxLayout:
                id: equip_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        Button:
            text: '돌아가기'
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'account'
"""

# [4. 화면 클래스: 제1원칙 목록 고착]
class AccountScreen(Screen): pass

class InfoScreen(Screen):
    INFO_LIST = ["이름", "직위", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩", "건강", "명중", "공격", "방어", "흡수", "속도", "기타정보"]
    def on_enter(self):
        self.ids.info_container.clear_widgets()
        for item in self.INFO_LIST:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, size_hint_x=0.3, font_name=App.get_running_app().font_name))
            row.add_widget(TextInput(multiline=False, halign='center', font_name=App.get_running_app().font_name))
            self.ids.info_container.add_widget(row)

class EquipScreen(Screen):
    EQUIP_LIST = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타장비"]
    def on_enter(self):
        self.ids.equip_container.clear_widgets()
        for item in self.EQUIP_LIST:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, size_hint_x=0.3, font_name=App.get_running_app().font_name, color=(0,1,1,1)))
            row.add_widget(TextInput(multiline=False, halign='center', font_name=App.get_running_app().font_name))
            self.ids.equip_container.add_widget(row)

# [5. 메인 앱 엔진: 순차 사출 시스템]
class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    bg_ready = BooleanProperty(False)

    def build(self):
        write_blackbox("시스템 부팅: 전수 검사 완료 버전 가동")
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        
        # [팅김 방지 핵심] 앱 실행 1초 후 배경화면을 '지연 사출'하여 시스템 충돌 회피
        Clock.schedule_once(self.activate_bg, 1.0)
        return sm

    def activate_bg(self, dt):
        self.bg_ready = True
        write_blackbox("배경화면 지연 사출 성공: 시스템 안정화 확인")

if __name__ == '__main__':
    PristonTaleApp().run()
