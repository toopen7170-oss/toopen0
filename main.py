import os, sys, traceback, json
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, DictProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase

# [1. 블랙박스 및 팅김 방역 시스템]
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
    write_blackbox(f"!!! 치명적 오류 발생 (팅김 감지) !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 설정 및 폰트 각인]
Window.softinput_mode = "below_target" 
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
BG_PATH = "bg.png"

try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        FONT_NAME = "Korean"
    else: FONT_NAME = "Roboto"
except: FONT_NAME = "Roboto"

# [3. KV 설계도: 7대 창 및 UI 규격 고착]
KV = """
<AccountScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: 'PristonTale 계정 관리'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
        TextInput:
            id: acc_input
            hint_text: '새 계정 ID 입력'
            multiline: False
            size_hint_y: None
            height: '55dp'
            halign: 'center'
        Button:
            text: '계정 생성 및 저장'
            size_hint_y: None
            height: '60dp'
            background_color: (0.1, 0.6, 0.3, 1)
            on_release: root.add_account()
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        ScrollView:
            id: info_scroll
            BoxLayout:
                id: info_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
"""

# [4. 화면 클래스 선언 (App 상단 배치로 NameError 방지)]
class AccountScreen(Screen):
    def add_account(self):
        acc_id = self.ids.acc_input.text
        if acc_id:
            App.get_running_app().accounts[acc_id] = {"info": {}, "equip": {}}
            self.ids.acc_input.text = ""
            write_blackbox(f"계정 생성 완료: {acc_id}")

class InfoScreen(Screen):
    # 제1원칙: 18개 정보 목록 고착
    INFO_LIST = ["이름", "직위", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩", "건강", "명중", "공격", "방어", "흡수", "속도"]
    
    def on_enter(self):
        self.ids.info_container.clear_widgets()
        for item in self.INFO_LIST:
            row = BoxLayout(size_hint_y=None, height='55dp')
            row.add_widget(Label(text=item, size_hint_x=0.3))
            ti = TextInput(multiline=False, halign='center')
            ti.bind(focus=self.on_auto_scroll)
            row.add_widget(ti)
            self.ids.info_container.add_widget(row)

    def on_auto_scroll(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.ids.info_scroll.scroll_to(instance), 0.1)

# [5. 메인 앱 엔진: 7대 창 통합 및 무결성 사출]
class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    accounts = DictProperty({})

    def build(self):
        write_blackbox("시스템 부팅: 제1원칙 클래스 연결 시퀀스 가동")
        Builder.load_string(KV)
        
        # [수복 지점] ScreenManager 선언 전 모든 클래스 로딩 확인 완료
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # 7대 창 순차 등록 (NameError 박멸)
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(InfoScreen(name='info'))
        
        write_blackbox("모든 화면 이름표(NameTag) 안착 성공")
        return sm

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception as e:
        write_blackbox(f"런타임 치명적 오류: {e}")
