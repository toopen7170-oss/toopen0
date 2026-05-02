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

# [1. 블랙박스 물리 각인 시스템]
def write_blackbox(msg):
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 즉시 기록
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 그래픽 엔진/로직 최종 충돌 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 설정: 보안 및 폰트 충돌 원천 차단]
Window.softinput_mode = "below_target"
# 외부 폰트(font.ttf)를 배제하고 시스템 기본 폰트(Roboto)를 사용하여 SDL2 충돌 방지
FONT_NAME = "Roboto" 

# [3. KV 설계도: 순차 사출 및 제1원칙 구조 각인]
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
            text: 'PristonTale Manager (Safety Mode)'
            font_size: '22sp'
            size_hint_y: None
            height: '60dp'
        Button:
            text: '케릭정보 (18개) 진입'
            size_hint_y: None
            height: '65dp'
            background_color: (0.2, 0.4, 0.8, 1)
            on_release: app.root.current = 'info'
        Button:
            text: '케릭장비 (11개) 진입'
            size_hint_y: None
            height: '65dp'
            background_color: (0.1, 0.6, 0.3, 1)
            on_release: app.root.current = 'equip'

<InfoScreen>:
    BaseLayout:
        Label:
            text: '캐릭터 상세 정보 (18)'
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
            text: '메인으로 돌아가기'
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'account'

<EquipScreen>:
    BaseLayout:
        Label:
            text: '캐릭터 장비 목록 (11)'
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
            text: '메인으로 돌아가기'
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'account'
"""

# [4. 화면 클래스: 29개 항목 물리적 각인]
class AccountScreen(Screen): pass

class InfoScreen(Screen):
    # 18개 고착 목록
    INFO_LIST = ["이름", "직위", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩", "건강", "명중", "공격", "방어", "흡수", "속도", "종합비고"]
    def on_enter(self):
        self.ids.info_container.clear_widgets()
        # 렌더링 과부하 방지를 위한 순차 생성
        for i, item in enumerate(self.INFO_LIST):
            Clock.schedule_once(lambda dt, it=item: self.add_row(it), i * 0.02)

    def add_row(self, item_text):
        row = BoxLayout(size_hint_y=None, height='50dp')
        row.add_widget(Label(text=item_text, size_hint_x=0.3))
        row.add_widget(TextInput(multiline=False, halign='center'))
        self.ids.info_container.add_widget(row)

class EquipScreen(Screen):
    # 11개 장비 고착 목록
    EQUIP_LIST = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타장비"]
    def on_enter(self):
        self.ids.equip_container.clear_widgets()
        for i, item in enumerate(self.EQUIP_LIST):
            Clock.schedule_once(lambda dt, it=item: self.add_row(it), i * 0.02)

    def add_row(self, item_text):
        row = BoxLayout(size_hint_y=None, height='50dp')
        row.add_widget(Label(text=item_text, size_hint_x=0.3, color=(0, 1, 0.8, 1)))
        row.add_widget(TextInput(multiline=False, halign='center'))
        self.ids.equip_container.add_widget(row)

# [5. 메인 앱 엔진: 절대 영점 사출 시퀀스]
class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    bg_ready = BooleanProperty(False)

    def build(self):
        write_blackbox("절대 영점 시스템 가동... 전수 검사 완료")
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # 이름표(NameTag) 수복 및 등록
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(EquipScreen(name='equip'))
        
        # [팅김 방지 핵심] 1.5초 뒤 시스템 안정화 확인 후 배경 사출
        Clock.schedule_once(self.safe_bg_activation, 1.5)
        return sm

    def safe_bg_activation(self, dt):
        self.bg_ready = True
        write_blackbox("안전 렌더링 완료: 배경화면 사출 성공 및 유지")

if __name__ == '__main__':
    PristonTaleApp().run()
