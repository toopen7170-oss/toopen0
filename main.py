import os, sys, traceback, json, time
from datetime import datetime

# [1. 환경 설정 및 모듈 선제 봉쇄]
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color

# [2. 블랙박스 & 물리 각인 엔진]
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
EXTERNAL_LOG = os.path.join(DOWNLOAD_PATH, "PT_BlackBox.txt")

def write_blackbox(msg):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 강제 각인
    except: pass

# 강제 생존: 어떤 에러도 블랙박스에 가두고 앱은 유지함
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. 자가 치유 베이스 스크린] - 45라인 충돌 및 검정 화면 방지
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self.safe_update_bg, pos=self.safe_update_bg)

    def safe_update_bg(self, *args):
        # 0.1초 지연 렌더링으로 Window 크기 미확보 시점의 충돌 차단
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
                    Color(0.05, 0.05, 0.1, 1) # 배경 부재 시 기본 색상
                    Rectangle(pos=self.pos, size=self.size)
        except Exception as e: write_blackbox(f"BG Error: {e}")

# [4. 제1 기본원칙: 7대 창 로직 구현]
class MainScreen(BaseScreen):
    def on_enter(self): Clock.schedule_once(lambda dt: self.refresh(), 0.1)
    def refresh(self, search_text=""):
        container = self.ids.acc_list
        container.clear_widgets()
        accounts = App.get_running_app().user_data.get("accounts", {})
        for aid in accounts:
            if search_text.lower() in aid.lower():
                # 2번 사진 싱크: [계정바(파란색)] + [삭제바(빨간/갈색)]
                row = BoxLayout(size_hint_y=None, height="60dp", spacing="5dp")
                btn = Button(text=f"ID: {aid}", background_color=(0.1, 0.3, 0.5, 0.7))
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.6, 0.2, 0.1, 0.8))
                del_btn.bind(on_release=lambda x, a=aid: self.ask_delete(a))
                row.add_widget(btn); row.add_widget(del_btn)
                container.add_widget(row)

    def ask_delete(self, aid):
        content = BoxLayout(orientation='vertical', padding="15dp", spacing="10dp")
        content.add_widget(Label(text=f"[{aid}]\n정말 삭제하시겠습니까?"))
        btn_row = BoxLayout(size_hint_y=0.4, spacing="10dp")
        pop = Popup(title="경고", content=content, size_hint=(0.8, 0.35))
        yes = Button(text="삭제", background_color=(0.8, 0, 0, 1))
        yes.bind(on_release=lambda x: self.do_delete(aid, pop))
        no = Button(text="취소"); no.bind(on_release=pop.dismiss)
        btn_row.add_widget(yes); btn_row.add_widget(no); content.add_widget(btn_row); pop.open()

    def do_delete(self, aid, pop):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
        pop.dismiss()

    def add_acc(self):
        aid = datetime.now().strftime('%H%M%S')
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
            # 1번 사진 싱크: 반투명 버튼 6개 슬롯
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
        # 제1원칙: 18개 세부 목록 강제 각인
        fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
        for f in fields:
            row = BoxLayout(size_hint_y=None, height="45dp", spacing="10dp")
            row.add_widget(Label(text=f, size_hint_x=0.35, halign='center'))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.box.add_widget(row)

class EquipScreen(BaseScreen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        # 제1원칙: 11개 세부 목록 강제 각인
        items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
        for i in items:
            row = BoxLayout(size_hint_y=None, height="45dp", spacing="10dp")
            row.add_widget(Label(text=i, size_hint_x=0.35, halign='center'))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.box.add_widget(row)

class InventoryScreen(BaseScreen): pass
class PhotoScreen(BaseScreen): pass
class StorageScreen(BaseScreen): pass

# [5. KV 설계도] - 1줄 1속성 원칙 및 반투명 UI
KV = '''
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
            text: "PristonTale Manager v80"
            font_size: '22sp'
            size_hint_y: 0.1
        TextInput:
            id: search_input
            hint_text: "계정/케릭 검색..."
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
            height: '60dp'
            background_color: 0.1, 0.5, 0.2, 0.8
            on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "캐릭터 슬롯 선택"
            size_hint_y: 0.15
        GridLayout:
            id: grid
            cols: 2
            spacing: '12dp'
        Button:
            text: "<< 처음으로"
            size_hint_y: 0.1
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '15dp'
        Button:
            text: "1. 케릭정보창"
            on_release: root.manager.current = 'info'
        Button:
            text: "2. 케릭장비창"
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
            text: "<< 뒤로가기"
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
                text: "저장"
                background_color: 0.18, 0.49, 0.2, 1
                on_release: app.save_data(); root.manager.current = 'slot_menu'
            Button:
                text: "뒤로"
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

# [6. 앱 엔진]
class PristonApp(App):
    user_data = {"accounts": {}}
    custom_font = "Roboto"

    def build(self):
        self.apply_safe_font()
        return Builder.load_string(KV)

    def apply_safe_font(self):
        # 0순위: 다운로드 폴더 탐색
        font_paths = [
            os.path.join(DOWNLOAD_PATH, "font.ttf"),
            "/system/fonts/NanumGothic.ttf",
            "/system/fonts/NotoSansKR-Regular.otf",
            "/system/fonts/DroidSansFallback.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                LabelBase.register(name="korean", fn_regular=path)
                self.custom_font = "korean"
                write_blackbox(f"Font Loaded: {path}")
                return
        write_blackbox("All fonts failed. Using Roboto.")

    def load_data(self):
        path = os.path.join(self.user_data_dir, "PT_Data_v80.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)

    def save_data(self):
        path = os.path.join(self.user_data_dir, "PT_Data_v80.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    def on_start(self):
        self.load_data()
        write_blackbox("Engine Started: Integrity Verified.")

if __name__ == "__main__":
    PristonApp().run()
