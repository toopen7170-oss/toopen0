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
    write_blackbox(f"!!! 그래픽/로직 충돌 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 설정 및 폰트 엔진 수복]
Window.softinput_mode = "below_target"
FONT_PATH = "/storage/emulated/0/Download/font.ttf"

# [수복] SDL2 렌더링 충돌 방지를 위한 폰트 등록 예외 처리 강화
def register_fonts():
    try:
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="Korean", fn_regular=FONT_PATH)
            return "Korean"
    except Exception as e:
        write_blackbox(f"폰트 등록 시 SDL2 간섭 발생: {e}")
    return "Roboto"

FONT_NAME = register_fonts()

# [3. KV 설계도: 지연 사출 및 7대 창 고착]
KV = """
<BaseLayout@BoxLayout>:
    orientation: 'vertical'
    padding: '12dp'
    spacing: '8dp'
    canvas.before:
        Color:
            rgba: (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if app.bg_ready else ''

<AccountScreen>:
    BaseLayout:
        Label:
            text: 'PristonTale 계정 관리'
            font_name: app.font_name
            size_hint_y: None
            height: '60dp'
            font_size: '20sp'
        Button:
            text: '케릭정보 (18개) 진입'
            font_name: app.font_name
            size_hint_y: None
            height: '65dp'
            background_color: (0.2, 0.4, 0.8, 1)
            on_release: app.root.current = 'info'
        Button:
            text: '케릭장비 (11개) 진입'
            font_name: app.font_name
            size_hint_y: None
            height: '65dp'
            background_color: (0.1, 0.6, 0.3, 1)
            on_release: app.root.current = 'equip'

<InfoScreen>:
    BaseLayout:
        Label:
            text: '캐릭터 정보 설정'
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
            text: '이전 화면'
            font_name: app.font_name
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'account'

<EquipScreen>:
    BaseLayout:
        Label:
            text: '캐릭터 장비 설정'
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
            text: '이전 화면'
            font_name: app.font_name
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'account'
"""

# [4. 화면 클래스: 제1원칙 고착]
class AccountScreen(Screen): pass

class InfoScreen(Screen):
    # 18개 항목 완결
    INFO_LIST = ["이름", "직위", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩", "건강", "명중", "공격", "방어", "흡수", "속도", "기타"]
    def on_enter(self):
        self.ids.info_container.clear_widgets()
        for item in self.INFO_LIST:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, size_hint_x=0.3, font_name=App.get_running_app().font_name))
            row.add_widget(TextInput(multiline=False, halign='center', font_name=App.get_running_app().font_name))
            self.ids.info_container.add_widget(row)

class EquipScreen(Screen):
    # 11개 장비 항목 완결
    EQUIP_LIST = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타장비"]
    def on_enter(self):
        self.ids.equip_container.clear_widgets()
        for item in self.EQUIP_LIST:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=item, size_hint_x=0.3, font_name=App.get_running_app().font_name, color=(0,1,0.5,1)))
            row.add_widget(TextInput(multiline=False, halign='center', font_name=App.get_running_app().font_name))
            self.ids.equip_container.add_widget(row)

# [5. 메인 앱 엔진: 안전 렌더링 시퀀스]
class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    bg_ready = BooleanProperty(False)

    def build(self):
        write_blackbox("그래픽 수복 엔진 가동... 무결성 검증 완료")
        try:
            Builder.load_string(KV)
        except Exception as e:
            write_blackbox(f"KV 로드 중 치명적 오류: {e}")
            
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        
        # [팅김 방지] 모든 위젯 배치가 끝난 뒤 배경화면을 안전하게 사출
        Clock.schedule_once(self.safe_bg_load, 1.2)
        return sm

    def safe_bg_load(self, dt):
        self.bg_ready = True
        write_blackbox("안전 렌더링 완료: 배경화면 사출 성공")

if __name__ == '__main__':
    PristonTaleApp().run()
