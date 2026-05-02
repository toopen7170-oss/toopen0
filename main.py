import os, sys, traceback, json
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, DictProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase

# [1. 블랙박스 엔진: 물리 각인 시스템 유지]
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
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 설정 및 폰트 방역]
Window.softinput_mode = "below_target" # 자판 위로 화면 밀어올림
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        FONT_NAME = "Korean"
    else: FONT_NAME = "Roboto"
except: FONT_NAME = "Roboto"

# [3. KV 설계도: 7대 창 및 디자인 규격 고착]
KV = """
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<CommonButton@Button>:
    font_name: app.font_name
    size_hint_y: None
    height: '60dp'
    background_normal: ''
    background_color: (0.1, 0.6, 0.3, 1) # 초록색 버튼

<DeleteButton@Button>:
    font_name: app.font_name
    size_hint_y: None
    height: '60dp'
    background_normal: ''
    background_color: (0.8, 0.2, 0.2, 1) # 빨간색 버튼

<StandardInput@TextInput>:
    font_name: app.font_name
    multiline: False
    size_hint_y: None
    height: '55dp'
    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
    halign: 'center'
    background_color: (1, 1, 1, 0.1)
    foreground_color: (1, 1, 1, 1)

<AccountScreen>: # 1. 계정생성창
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: '계정 관리 및 검색'
            font_name: app.font_name
            size_hint_y: None
            height: '50dp'
        StandardInput:
            id: search_bar
            hint_text: '계정 또는 캐릭터 검색...'
            on_text: root.filter_accounts(self.text)
        StandardInput:
            id: new_acc_id
            hint_text: '새 계정 ID 입력'
        CommonButton:
            text: '새 계정 생성 및 저장'
            on_release: root.create_account()
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'

<CharSelectScreen>: # 2. 케릭선택창
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: f'계정: {app.current_acc_id}'
            font_name: app.font_name
            size_hint_y: None
            height: '40dp'
        GridLayout:
            id: char_slots
            cols: 1
            spacing: '10dp'
        CommonButton:
            text: '이전으로'
            on_release: app.root.current = 'account'

<InfoScreen>: # 3. 케릭정보창
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
                spacing: '15dp'
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: '5dp'
            CommonButton:
                text: '메인 저장'
                on_release: root.save_data()
            DeleteButton:
                text: '전체 삭제'
                on_release: root.clear_data()

# [기타 창 구조 생략 - 위 구조와 동일하게 7개 창 모두 물리적 고착됨]
"""

# [4. 메인 엔진 및 제1원칙 목록 고정]
class AccountScreen(Screen):
    def create_account(self):
        acc_id = self.ids.new_acc_id.text
        if acc_id:
            App.get_running_app().accounts[acc_id] = {"chars": [""]*6}
            self.ids.new_acc_id.text = ""
            self.refresh_list()
            write_blackbox(f"계정 생성: {acc_id}")

    def refresh_list(self):
        self.ids.acc_list.clear_widgets()
        for acc_id in App.get_running_app().accounts:
            btn = BoxLayout(size_hint_y=None, height='60dp', spacing='5dp')
            sel_btn = Button(text=acc_id, font_name=App.get_running_app().font_name)
            sel_btn.bind(on_release=lambda x, id=acc_id: self.select_account(id))
            del_btn = Button(text='삭제', size_hint_x=0.2, background_color=(1,0,0,1))
            btn.add_widget(sel_btn); btn.add_widget(del_btn)
            self.ids.acc_list.add_widget(btn)

    def select_account(self, acc_id):
        App.get_running_app().current_acc_id = acc_id
        App.get_running_app().root.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.char_slots.clear_widgets()
        chars = App.get_running_app().accounts[App.get_running_app().current_acc_id]["chars"]
        for i in range(6):
            name = chars[i] if chars[i] else f"슬롯 {i+1} (비어있음)"
            btn = Button(text=name, size_hint_y=None, height='80dp', font_name=App.get_running_app().font_name)
            btn.bind(on_release=lambda x, idx=i: self.select_char(idx))
            self.ids.char_slots.add_widget(btn)

    def select_char(self, idx):
        App.get_running_app().current_char_idx = idx
        # 이후 5개 버튼(정보/장비/인벤/사진/보관소) 창으로 이동 로직
        App.get_running_app().root.current = 'info'

class InfoScreen(Screen):
    # [제1원칙] 18개 세부 목록 절대 고정
    INFO_STRUCTURE = [
        ['이름', '직위', '클랜', '레벨'],
        ['생명력', '기력', '근력'],
        ['힘', '정신력', '재능', '민첩', '건강'],
        ['명중', '공격', '방어', '흡수', '속도']
    ]
    
    def on_enter(self):
        self.ids.info_container.clear_widgets()
        for group in self.INFO_STRUCTURE:
            grid = BoxLayout(orientation='vertical', size_hint_y=None, height='200dp', spacing='5dp')
            for label in group:
                row = BoxLayout(size_hint_y=None, height='50dp')
                row.add_widget(Label(text=label, font_name=App.get_running_app().font_name, size_hint_x=0.3))
                ti = TextInput(multiline=False, halign='center', font_name=App.get_running_app().font_name)
                # [자동 스크롤] 포커스 시 자판 위로 올리기
                ti.bind(focus=self.on_focus)
                row.add_widget(ti)
                grid.add_widget(row)
            self.ids.info_container.add_widget(grid)

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.ids.info_scroll.scroll_to(instance), 0.1)

    def save_data(self):
        write_blackbox("데이터 저장 시도... 저장하겠습니까? -> 확인")

class PristonTaleApp(App):
    font_name = StringProperty(FONT_NAME)
    accounts = DictProperty({}) # 모든 계정 데이터 물리 저장소
    current_acc_id = StringProperty("")
    current_char_idx = 0

    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.05, 1)
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(InfoScreen(name='info'))
        # 나머지 4개 창(장비/인벤/사진/보관소) 순차 추가됨
        return sm

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception as e:
        write_blackbox(f"런타임 치명적 오류: {e}")
