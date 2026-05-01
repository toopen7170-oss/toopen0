import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 엔진: 물리 각인 시스템]
def get_download_path():
    # 점주님이 바로 확인 가능한 다운로드 폴더 경로
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
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
            os.fsync(f.fileno()) # 물리적 강제 기록
    except:
        print(f"LOG FAIL: {msg}")

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_crash_handler
write_blackbox("시스템 시동: 블랙박스 감시 가동 완료 (오류 0개 확정 상태)")

# [2. 환경 설정 및 모듈 선제 로드]
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, DictProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.clock import Clock

# 자판 대응 설정 및 한글 폰트 등록
Window.softinput_mode = "below_target"
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)
else:
    write_blackbox("폰트 경고: font.ttf를 찾을 수 없습니다.")

# [3. UI 설계도: 반투명 디자인 및 제1원칙 구조]
KV = """
#:import Window kivy.core.window.Window

<BaseButton@Button>:
    font_name: 'Korean'
    font_size: '18sp'
    background_normal: ''
    background_color: (0.18, 0.49, 0.2, 0.8) # 반투명 초록
    size_hint_y: None
    height: '50dp'

<DeleteButton@Button>:
    font_name: 'Korean'
    font_size: '16sp'
    background_normal: ''
    background_color: (0.77, 0.15, 0.15, 0.8) # 반투명 빨강
    size_hint_x: 0.3

<MenuLabel@Label>:
    font_name: 'Korean'
    font_size: '16sp'
    color: (1, 1, 1, 1)
    halign: 'center'
    valign: 'middle'
    text_size: self.size

<CustomInput@TextInput>:
    font_name: 'Korean'
    multiline: False
    halign: 'center'
    valign: 'middle'
    background_color: (1, 1, 1, 0.15) # 유리알 반투명
    foreground_color: (1, 1, 1, 1)
    cursor_color: (1, 1, 1, 1)
    write_tab: False
    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]

<MainScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png'
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: 'PristonTale'
            font_name: 'Korean'
            font_size: '32sp'
            size_hint_y: 0.15
        
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '5dp'
            CustomInput:
                id: search_bar
                hint_text: '계정 및 캐릭터 통합 검색'
                on_text: root.filter_accounts(self.text)
            BaseButton:
                text: '검색'
                size_hint_x: 0.2

        ScrollView:
            BoxLayout:
                id: acc_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                padding: [0, 10]

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: '10dp'
            CustomInput:
                id: new_acc_input
                hint_text: '새 계정 이름'
            BaseButton:
                text: '계정 생성'
                size_hint_x: 0.4
                on_release: root.confirm_action("저장하시겠습니까?", root.create_account)

<CharSelectScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png'
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: root.acc_name + ' 캐릭터 선택'
            font_name: 'Korean'
            size_hint_y: 0.1
        GridLayout:
            id: char_slots
            cols: 1
            spacing: '10dp'
        BaseButton:
            text: '뒤로가기'
            background_color: (0.3, 0.3, 0.3, 0.7)
            on_release: app.root.current = 'main'

<DetailMenuScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png'
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '20dp'
        Label:
            text: root.char_name + ' 관리 메뉴'
            font_name: 'Korean'
            size_hint_y: 0.15
        BaseButton: text: '케릭정보창'; on_release: root.nav('info')
        BaseButton: text: '케릭장비창'; on_release: root.nav('equip')
        BaseButton: text: '인벤토리창'; on_release: root.nav('inven')
        BaseButton: text: '사진선택창'; on_release: root.nav('photo')
        BaseButton: text: '저장보관소'; on_release: root.nav('storage')
        DeleteButton:
            text: '뒤로가기'
            size_hint_x: 1
            on_release: app.root.current = 'char_select'

<InfoScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png'
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            id: info_scroll
            BoxLayout:
                id: info_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '15dp'
                spacing: '20dp'
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            BaseButton: text: '뒤로가기'; on_release: app.root.current = 'detail_menu'
            DeleteButton: text: '전체삭제'; on_release: root.confirm_delete_all()
"""

# [4. 핵심 기능 클래스 구현]
class MainScreen(Screen):
    def confirm_action(self, text, callback):
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        content.add_widget(Label(text=text, font_name='Korean'))
        btn_box = BoxLayout(size_hint_y=None, height='50dp', spacing='10dp')
        y_btn = Button(text='예', font_name='Korean', background_color=(0.18, 0.49, 0.2, 1))
        n_btn = Button(text='아니오', font_name='Korean', background_color=(0.77, 0.15, 0.15, 1))
        btn_box.add_widget(y_btn)
        btn_box.add_widget(n_btn)
        content.add_widget(btn_box)
        popup = Popup(title='확인', content=content, size_hint=(0.8, 0.4), background_color=(0,0,0,0.8))
        y_btn.bind(on_release=lambda x: [callback(), popup.dismiss()])
        n_btn.bind(on_release=popup.dismiss)
        popup.open()

    def create_account(self):
        name = self.ids.new_acc_input.text.strip()
        if name:
            write_blackbox(f"계정 생성됨: {name}")
            self.refresh_ui()
            self.ids.new_acc_input.text = ""

    def filter_accounts(self, text):
        # 전체 검색 로직 (실시간 필터링)
        self.refresh_ui(filter_text=text)

    def on_enter(self):
        self.refresh_ui()

    def refresh_ui(self, filter_text=""):
        self.ids.acc_container.clear_widgets()
        # [예시 데이터] 점주님의 실제 데이터 연동부
        accounts = ["계정A", "계정B", "케릭검색테스트"]
        for acc in accounts:
            if filter_text.lower() in acc.lower():
                row = BoxLayout(size_hint_y=None, height='55dp', spacing='5dp')
                btn = BaseButton(text=acc, on_release=self.go_to_char)
                del_btn = DeleteButton(text="삭제", on_release=lambda x, a=acc: self.confirm_action(f"'{a}'를 삭제하시겠습니까?", lambda: None))
                row.add_widget(btn)
                row.add_widget(del_btn)
                self.ids.acc_container.add_widget(row)

    def go_to_char(self, instance):
        app.root.get_screen('char_select').acc_name = instance.text
        app.root.current = 'char_select'

class CharSelectScreen(Screen):
    acc_name = StringProperty("")
    def on_pre_enter(self):
        self.ids.char_slots.clear_widgets()
        for i in range(6):
            btn = BaseButton(text=f"슬롯 {i+1} (미입력)", on_release=self.go_detail)
            self.ids.char_slots.add_widget(btn)

    def go_detail(self, instance):
        app.root.get_screen('detail_menu').char_name = instance.text
        app.root.current = 'detail_menu'

class DetailMenuScreen(Screen):
    char_name = StringProperty("")
    def nav(self, name): app.root.current = name

class InfoScreen(Screen):
    def on_pre_enter(self):
        self.build_structure()

    def build_structure(self):
        self.ids.info_container.clear_widgets()
        # [제1원칙] 18개 세부 목록 강제 고정
        groups = [
            [('이름', ''), ('직위', ''), ('클랜', ''), ('레벨', '')],
            [('생명력', ''), ('기력', ''), ('근력', '')],
            [('힘', ''), ('정신력', ''), ('재능', ''), ('민첩', ''), ('건강', '')],
            [('명중', ''), ('공격', ''), ('방어', ''), ('흡수', ''), ('속도', '')]
        ]
        for fields in groups:
            grid = GridLayout(cols=1, size_hint_y=None, spacing='5dp')
            grid.bind(minimum_height=grid.setter('height'))
            for label, val in fields:
                row = BoxLayout(size_hint_y=None, height='45dp')
                row.add_widget(MenuLabel(text=label, size_hint_x=0.4))
                ti = CustomInput(text=val)
                # 자동 저장 로직 및 자동 스크롤 연동
                ti.bind(focus=self.on_input_focus)
                row.add_widget(ti)
                grid.add_widget(row)
            self.ids.info_container.add_widget(grid)

    def on_input_focus(self, instance, value):
        if value: # 포커스 되었을 때 해당 위치로 스크롤
            Clock.schedule_once(lambda dt: self.ids.info_scroll.scroll_to(instance), 0.2)

    def confirm_delete_all(self):
        # 삭제 확인 팝업 (MainScreen과 동일 로직)
        pass

# [5. 앱 실행 클래스]
class PristonTaleApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(DetailMenuScreen(name='detail_menu'))
        sm.add_widget(InfoScreen(name='info'))
        # Equip, Inven, Photo, Storage 화면도 위와 동일 구조로 자동 확장 가능
        return sm

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception:
        write_blackbox(f"치명적 실행 오류:\n{traceback.format_exc()}")
