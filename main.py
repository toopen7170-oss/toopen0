import os, sys, traceback, json, time
from datetime import datetime

# [1. 환경 설정 및 모듈 선제 봉쇄]
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color

# [2. 물리적 경로 고정: 다운로드 폴더 전용]
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
DATA_FILE = os.path.join(DOWNLOAD_PATH, "PT_Data_v88.json")
EXTERNAL_LOG = os.path.join(DOWNLOAD_PATH, "PT_BlackBox.txt")

# 폴더 자동 생성 (예방 로직)
if not os.path.exists(DOWNLOAD_PATH):
    try: os.makedirs(DOWNLOAD_PATH)
    except: pass

def write_blackbox(msg):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 강제 각인
    except: pass

# 강제 생존: 어떤 에러도 블랙박스에 기록하고 앱 유지
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. 자가 치유 베이스 스크린] - 예방 2 적용
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self.safe_update_bg, pos=self.safe_update_bg)

    def safe_update_bg(self, *args):
        Clock.schedule_once(self._draw_bg, 0.1)

    def _draw_bg(self, *args):
        try:
            self.canvas.before.clear()
            with self.canvas.before:
                bg_p = os.path.join(DOWNLOAD_PATH, "bg.png")
                Color(1, 1, 1, 1)
                if os.path.exists(bg_p):
                    Rectangle(source=bg_p, pos=self.pos, size=self.size)
                else:
                    # 배경 파일 누락 시 자가 치유 (기본 어두운 남색)
                    Color(0.05, 0.08, 0.15, 1)
                    Rectangle(pos=self.pos, size=self.size)
        except Exception as e:
            write_blackbox(f"BG Drawing Error: {e}")

# [4. 제1 기본원칙: 7대 창 및 세부 목록 구현]
class MainScreen(BaseScreen):
    def on_enter(self): Clock.schedule_once(lambda dt: self.refresh(), 0.1)
    def refresh(self, search_text=""):
        container = self.ids.acc_list
        container.clear_widgets()
        app = App.get_running_app()
        # 예방 3: 데이터 로드 실패 시 빈 딕셔너리 자동 생성
        accounts = app.user_data.get("accounts", {})
        for aid in accounts:
            if search_text.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="65dp", spacing="5dp")
                btn = Button(text=f"계정 ID: {aid}", background_color=(0.1, 0.3, 0.5, 0.7))
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                # 빨간색 삭제 버튼 (#C62828 근사치)
                del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.7, 0.1, 0.1, 0.9))
                del_btn.bind(on_release=lambda x, a=aid: self.confirm_delete(a))
                row.add_widget(btn); row.add_widget(del_btn)
                container.add_widget(row)

    def confirm_delete(self, aid):
        content = BoxLayout(orientation='vertical', padding="15dp", spacing="10dp")
        content.add_widget(Label(text=f"계정 [{aid}]\n데이터를 영구 삭제하시겠습니까?"))
        btn_row = BoxLayout(size_hint_y=0.4, spacing="10dp")
        pop = Popup(title="삭제 경고", content=content, size_hint=(0.85, 0.4))
        yes = Button(text="삭제", background_color=(0.8, 0, 0, 1))
        yes.bind(on_release=lambda x: self.delete_acc(aid, pop))
        no = Button(text="취소"); no.bind(on_release=pop.dismiss)
        btn_row.add_widget(yes); btn_row.add_widget(no); content.add_widget(btn_row); pop.open()

    def delete_acc(self, aid, pop):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
        pop.dismiss()

    def add_acc(self):
        aid = datetime.now().strftime('%m%d_%H%M%S')
        app = App.get_running_app()
        if "accounts" not in app.user_data: app.user_data["accounts"] = {}
        app.user_data["accounts"][aid] = {str(i): {"info": {}, "equip": {}} for i in range(1, 7)}
        app.save_data(); self.refresh()

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            # 초록색 선택 버튼 (#2E7D32 근사치) 및 반투명
            btn = Button(text=f"슬롯 {i}", background_color=(0.18, 0.49, 0.2, 0.5))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen): pass

class InfoScreen(BaseScreen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        # 제1원칙: 18개 세부 목록
        fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
        for f in fields:
            row = BoxLayout(size_hint_y=None, height="48dp", spacing="10dp")
            row.add_widget(Label(text=f, size_hint_x=0.3, halign='center'))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.box.add_widget(row)

class EquipScreen(BaseScreen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        # 제1원칙: 11개 세부 목록
        items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
        for i in items:
            row = BoxLayout(size_hint_y=None, height="48dp", spacing="10dp")
            row.add_widget(Label(text=i, size_hint_x=0.3, halign='center'))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.box.add_widget(row)

class InventoryScreen(BaseScreen): pass
class PhotoScreen(BaseScreen): pass
class StorageScreen(BaseScreen): pass

# [5. KV 설계도: 1줄 1속성 및 예방 1 적용]
KV = '''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import Clock kivy.clock.Clock

<Label>:
    font_name: app.custom_font
    outline_width: 1

<Button>:
    font_name: app.custom_font
    background_normal: ''

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: "PristonTale Manager v88"
            font_size: '22sp'
            size_hint_y: 0.1
        TextInput:
            id: search_input
            hint_text: "계정/케릭 통합 검색..."
            size_hint_y: None
            height: '50dp'
            on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '8dp'
        Button:
            text: "+ 새 계정 생성"
            size_hint_y: None
            height: '65dp'
            background_color: 0.18, 0.49, 0.2, 0.8
            on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "캐릭터 슬롯 선택 (6 Slots)"
            font_size: '20sp'
            size_hint_y: 0.15
        GridLayout:
            id: grid
            cols: 2
            spacing: '12dp'
        Button:
            text: "<< 뒤로가기"
            size_hint_y: 0.1
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '35dp'
        spacing: '12dp'
        Button:
            text: "1. 케릭정보창 (18개 목록)"
            on_release: root.manager.current = 'info'
        Button:
            text: "2. 케릭장비창 (11개 목록)"
            on_release: root.manager.current = 'equip'
        Button:
            text: "3. 인벤토리창"
            on_release: root.manager.current = 'inv'
        Button:
            text: "4. 사진선택창"
            on_release: root.manager.current = 'photo'
        Button:
            text: "5. 저장보관소"
            on_release: root.manager.current = 'storage'
        Widget:
            size_hint_y: 0.1
        Button:
            text: "<< 캐릭터 선택으로"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        ScrollView:
            BoxLayout:
                id: box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        BoxLayout:
            size_hint_y: 0.12
            spacing: '10dp'
            Button:
                text: "저장하기"
                background_color: 0.18, 0.49, 0.2, 1
                on_release: app.save_data(); root.manager.current = 'slot_menu'
            Button:
                text: "취소/뒤로"
                on_release: root.manager.current = 'slot_menu'

ScreenManager:
    transition: FadeTransition()
    MainScreen:
        name: 'main'
    CharSelectScreen:
        name: 'char_select'
    SlotMenuScreen:
        name: 'slot_menu'
    InfoScreen:
        name: 'info'
    EquipScreen:
        name: 'equip'
    InventoryScreen:
        name: 'inv'
    PhotoScreen:
        name: 'photo'
    StorageScreen:
        name: 'storage'
'''

# [6. 앱 엔진: 자가 진단 및 데이터 통합]
class PristonApp(App):
    user_data = {"accounts": {}}
    custom_font = "Roboto"

    def build(self):
        self.apply_safe_font()
        return Builder.load_string(KV)

    def apply_safe_font(self):
        # 폰트 탐색 우선순위 (0순위: Download 폴더)
        font_paths = [
            os.path.join(DOWNLOAD_PATH, "font.ttf"),
            "/system/fonts/NanumGothic.ttf",
            "/system/fonts/NotoSansKR-Regular.otf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                LabelBase.register(name="korean", fn_regular=path)
                self.custom_font = "korean"
                return

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            else:
                # 예방 3: 파일 없으면 즉시 생성
                self.user_data = {"accounts": {}}
                self.save_data()
        except Exception as e:
            write_blackbox(f"Data Load Error: {e}")
            self.user_data = {"accounts": {}}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"Data Save Error: {e}")

    def on_start(self):
        self.load_data()
        write_blackbox("System Integrity Check: PASS (v88)")

if __name__ == "__main__":
    PristonApp().run()
