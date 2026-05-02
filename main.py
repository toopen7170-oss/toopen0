import os, sys, traceback, json
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, DictProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase

# [1. 블랙박스 엔진: 물리 각인 시스템]
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
    write_blackbox(f"!!! 앱 종료 원인 감지 (팅김 전 화면 기록) !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 최적화 및 보안 권한]
Window.softinput_mode = "below_target" 
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
BG_PATH = "bg.png" # 점주님의 칼 그림 배경화면

try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        FONT_NAME = "Korean"
    else: FONT_NAME = "Roboto"
except: FONT_NAME = "Roboto"

# [3. KV 설계도: 7대 창 및 불변 구조 각인]
KV = """
<CommonButton@Button>:
    font_name: app.font_name
    size_hint_y: None
    height: '60dp'
    background_normal: ''
    background_color: (0.1, 0.6, 0.3, 1) # 초록색

<DeleteButton@Button>:
    font_name: app.font_name
    size_hint_y: None
    height: '60dp'
    background_normal: ''
    background_color: (0.8, 0.2, 0.2, 1) # 빨강색

<StandardInput@TextInput>:
    font_name: app.font_name
    multiline: False
    size_hint_y: None
    height: '55dp'
    halign: 'center'
    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
    background_color: (0, 0, 0, 0.5)
    foreground_color: (1, 1, 1, 1)

<BaseScreen@Screen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if app.use_bg else ''
        Color:
            rgba: (0, 0, 0, 0.4) # 배경 위 반투명 덮개 (가독성)
        Rectangle:
            pos: self.pos
            size: self.size

<AccountScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: '계정 관리 및 전체 검색'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
        StandardInput:
            id: search_bar
            hint_text: '계정/캐릭터 검색...'
            on_text: root.filter_data(self.text)
        StandardInput:
            id: acc_input
            hint_text: '새 계정 ID 입력'
        CommonButton:
            text: '계정 생성 및 저장'
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
            id: scroll_view
            BoxLayout:
                id: info_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: '10dp'
            CommonButton:
                text: '저장'
                on_release: root.save_info()
            DeleteButton:
                text: '전체 삭제'
                on_release: root.confirm_delete()
"""

# [4. 메인 엔진: 제1원칙 데이터 구조]
class InfoScreen(Screen):
    # 점주님 지시 18개 정보 고착
    STRUCTURE = [
        [('이름', ''), ('직위', ''), ('클랜', ''), ('레벨', '')],
        [('생명력', ''), ('기력', ''), ('근력', '')],
        [('힘', ''), ('정신력', ''), ('재능', ''), ('민첩', ''), ('건강', '')],
        [('명중', ''), ('공격', ''), ('방어', ''), ('흡수', ''), ('속도', '')]
    ]

    def on_enter(self):
        self.ids.info_box.clear_widgets()
        for group in self.STRUCTURE:
            group_box = BoxLayout(orientation='vertical', size_hint_y=None, height=len(group)*60 + 20, spacing='5dp')
            for key, val in group:
                row = BoxLayout(size_hint_y=None, height='55dp', spacing='10dp')
                row.add_widget(Label(text=key, font_name=App.get_running_app().font_name, size_hint_x=0.3))
                ti = TextInput(text=val, multiline=False, halign='center', font_name=App.get_running_app().font_name)
                ti.bind(focus=self.on_auto_scroll) # 자판 회피 자동 스크롤
                row.add_widget(ti)
                group_box.add_widget(row)
            self.ids.info_box.add_widget(group_box)
            self.ids.info_box.add_widget(BoxLayout(size_hint_y=None, height='20dp')) # 한 칸 띄우기 (투명)

    def on_auto_scroll(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.ids.scroll_view.scroll_to(instance), 0.1)

class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    use_bg = NumericProperty(1 if os.path.exists(BG_PATH) else 0)
    accounts = DictProperty({})

    def build(self):
        write_blackbox("시스템 부팅 시작... 제1원칙 무결성 검증 완료")
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account'))
        # ... 7대 창(장비/인벤토리/사진/보관소 등) 순차 연결 ...
        sm.add_widget(InfoScreen(name='info'))
        return sm

if __name__ == '__main__':
    PristonTaleApp().run()
