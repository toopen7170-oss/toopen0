import os, sys, traceback, json
from datetime import datetime

# [1. 물리적 선행 각인]
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
from kivy.graphics import Rectangle, Color

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 블랙박스 엔진]
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
EXTERNAL_LOG = os.path.join(DOWNLOAD_PATH, "PristonTale_BlackBox.txt")

def write_blackbox(msg):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. KV 레이아웃]: 외부 경로(Download) 참조 코드를 모두 제거 (보안 핵심)
KV = '''
#:import LabelBase kivy.core.text.LabelBase
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Screen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            id: bg_rect
            pos: self.pos
            size: self.size
            # source를 여기서 비워둡니다 (Python에서 권한 확인 후 주입)

<Label>:
    font_name: 'KFont' if 'KFont' in LabelBase.font_manager.fonts else 'Roboto'
    outline_width: 1
    outline_color: 0, 0, 0, 1

<Button>:
    font_name: 'KFont' if 'KFont' in LabelBase.font_manager.fonts else 'Roboto'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.6

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "PristonTale Manager v51"
            font_size: '28sp'
            size_hint_y: 0.15
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        Button:
            text: "+ 새 계정 생성"
            size_hint_y: None
            height: '60dp'
            on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            id: title_label
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: '15dp'
        Button:
            text: "<< 계정 목록"
            size_hint_y: 0.12
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '12dp'
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
            text: "<< 캐릭터 선택으로"
            background_color: 0.4, 0.4, 0.4, 0.7
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
                spacing: '8dp'
        BoxLayout:
            size_hint_y: 0.12
            spacing: '10dp'
            Button:
                text: "저장하기"
                on_release: root.save_confirm()
            Button:
                text: "뒤로가기"
                background_color: 0.4, 0.4, 0.4, 0.7
                on_release: root.manager.current = 'slot_menu'

ScreenManager:
    transition: FadeTransition()
    MainScreen: name: 'main'
    CharSelectScreen: name: 'char_select'
    SlotMenuScreen: name: 'slot_menu'
    InfoScreen: name: 'info'
    EquipScreen: name: 'equip'
    InventoryScreen: name: 'inv'
    PhotoScreen: name: 'photo'
    StorageScreen: name: 'storage'
'''

# [4. 앱 엔진: 권한 획득 후 리소스 순차 주입]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # 1. 빌드 시점엔 아이콘만 설정 (앱 번들 내부에 있는 경우만)
        return Builder.load_string(KV)

    def on_start(self):
        # 2. 강제 딜레이 후 권한 요청
        Clock.schedule_once(self.deferred_boot, 1.5)

    def deferred_boot(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.MANAGE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES
                ], self.on_permission_result)
            except: pass
        else:
            self.apply_resources()
        self.load_data()

    def on_permission_result(self, permissions, results):
        # 3. 권한이 승인된 이 '순간'부터 파일을 읽기 시작합니다.
        if any(results):
            write_blackbox("Permissions granted. Applying resources...")
            self.apply_resources()

    def apply_resources(self):
        # [폰트 적용]
        f_path = os.path.join(DOWNLOAD_PATH, "font.ttf")
        if os.path.exists(f_path):
            try:
                LabelBase.register(name="KFont", fn_regular=f_path)
                write_blackbox("Font loaded.")
            except: pass

        # [배경화면 실시간 주입]
        bg_path = os.path.join(DOWNLOAD_PATH, "bg.png")
        if os.path.exists(bg_path):
            try:
                for sc in self.root.screens:
                    with sc.canvas.before:
                        # 기존 캔버스를 덮어쓰며 이미지를 강제 주입
                        Color(1, 1, 1, 1)
                        Rectangle(source=bg_path, pos=sc.pos, size=sc.size)
                write_blackbox("Background image applied after permission.")
            except Exception as e:
                write_blackbox(f"BG Apply Error: {e}")

    def load_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v51.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except: pass

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v51.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except: pass

# [5. 기능 로직 (동일)]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.acc_list.clear_widgets()
        for aid in App.get_running_app().user_data.get("accounts", {}):
            btn = Button(text=f"ID: {aid}", size_hint_y=None, height="60dp")
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            self.ids.acc_list.add_widget(btn)
    def add_acc(self):
        aid = datetime.now().strftime('%H%M%S')
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i):{"info":{}, "equip":{}} for i in range(1,7)}
        app.save_data(); self.refresh()
    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}")
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=f, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text="입력", multiline=False))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data(); self.manager.current = 'slot_menu'

class EquipScreen(Screen):
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for i in self.items:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=i, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text="장비 정보", multiline=False))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data(); self.manager.current = 'slot_menu'

class InventoryScreen(Screen):
    def save_confirm(self): self.manager.current = 'slot_menu'
class PhotoScreen(Screen):
    def save_confirm(self): self.manager.current = 'slot_menu'
class StorageScreen(Screen):
    def save_confirm(self): self.manager.current = 'slot_menu'

if __name__ == "__main__":
    PristonApp().run()
