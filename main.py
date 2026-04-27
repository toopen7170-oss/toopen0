import os, sys, traceback, json
from datetime import datetime

# [1. 물리적 선제 봉쇄]: 모든 클래스 선행 각인 (NameError 원천 차단)
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 이중 블랙박스 엔진]: os.fsync 물리 각인
INTERNAL_LOG = ""
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"
        # 외부 저장소 강제 각인
        try:
            with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
                f.flush()
                os.fsync(f.fileno())
        except: pass
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. KV 레이아웃]: 제1원칙 투명 UI 및 1줄 1속성 원칙
KV = '''
#:import os os

<Screen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''

<Label>:
    font_name: 'KFont'
    halign: 'center'
    valign: 'middle'

<Button>:
    font_name: 'KFont'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.7
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.2
        Line:
            width: 1
            rectangle: self.x, self.y, self.width, self.height

<TextInput>:
    font_name: 'KFont'
    background_color: 1, 1, 1, 0.8
    multiline: False

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "PristonTale Manager"
            font_size: '28sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "계정/캐릭터 검색..."
            size_hint_y: None
            height: '50dp'
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: 15
            Button:
                text: "비상 로그"
                background_color: 0.3, 0.3, 0.3, 0.8
                on_release: root.show_log()
            Button:
                text: "+ 계정 생성"
                on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            id: title_label
            font_size: '22sp'
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "처음으로"
            size_hint_y: 0.15
            background_color: 0.77, 0.15, 0.15, 0.8
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 12
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
        Button:
            text: "<< 뒤로가기"
            background_color: 0.5, 0.5, 0.5, 0.8
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
        BoxLayout:
            size_hint_y: 0.12
            spacing: 15
            Button:
                text: "저장하시겠습니까?"
                background_color: 0.18, 0.49, 0.2, 0.9
                on_release: root.save_confirm()
            Button:
                text: "뒤로가기"
                background_color: 0.77, 0.15, 0.15, 0.8
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

# [4. 제1원칙: 7대 창 기능 및 29개 세부 목록 물리 주입]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        try:
            self.ids.acc_list.clear_widgets()
            data = App.get_running_app().user_data.get("accounts", {})
            for aid in data:
                btn = Button(text=f"ID: {aid}", size_hint_y=None, height="65dp")
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                self.ids.acc_list.add_widget(btn)
        except Exception as e: write_blackbox(f"Main Refresh Error: {e}")

    def add_acc(self):
        aid = f"PT_{datetime.now().strftime('%H%M%S')}"
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "photo":[], "storage":[]} for i in range(1, 7)}
        app.save_data()
        self.refresh()

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def show_log(self):
        try:
            with open(EXTERNAL_LOG, "r", encoding="utf-8") as f:
                content = f.read()[-2000:]
        except: content = "로그 없음"
        from kivy.uix.popup import Popup
        Popup(title="BlackBox Log", content=TextInput(text=content, readonly=True), size_hint=(0.9, 0.8)).open()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.title_label.text = f"계정 [{App.get_running_app().cur_acc}] 캐릭터 선택"
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}")
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 제1원칙 18개 세부 목록
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            row.add_widget(TextInput(hint_text=f"{f} 입력", halign='center'))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class EquipScreen(Screen):
    # 제1원칙 11개 세부 목록
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for i in self.items:
            row = BoxLayout(size_hint_y=None, height="55dp", spacing=10)
            row.add_widget(Label(text=i, size_hint_x=0.3))
            row.add_widget(TextInput(hint_text="장비 정보"))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class InventoryScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="인벤토리 줄 단위 관리 대기 중", size_hint_y=None, height="100dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

class PhotoScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="사진 선택 및 업로드 대기 중", size_hint_y=None, height="100dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

class StorageScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="저장보관소 리스트 대기 중", size_hint_y=None, height="100dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

# [5. 앱 메인 엔진]: 시동 순서 격리 및 권한 수복
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # 폰트 탐색 제0순위
        f_path = "/storage/emulated/0/Download/font.ttf"
        target = f_path if os.path.exists(f_path) else "Roboto"
        LabelBase.register(name="KFont", fn_regular=target)
        return Builder.load_string(KV)

    def on_start(self):
        # 검은 화면 방지: UI 먼저 띄우고 1.5초 뒤 데이터/권한 처리
        write_blackbox(">>> UI Rendered. Initializing Boot Isolation (1.5s) <<<")
        Clock.schedule_once(self.deferred_init, 1.5)

    def deferred_init(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES,
                    Permission.MANAGE_EXTERNAL_STORAGE
                ])
                write_blackbox("Permissions Requested.")
            except Exception as e:
                write_blackbox(f"Permission Error: {e}")
        
        try:
            path = os.path.join(self.user_data_dir, "PT_Final_Data.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            write_blackbox("Data Engine Loaded.")
        except Exception as e:
            write_blackbox(f"Load Error: {e}")

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Final_Data.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
            write_blackbox("Data Saved.")
        except: pass

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"CRITICAL BOOT ERROR: {e}")
