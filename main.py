import os, sys, traceback, json
from datetime import datetime

# [1. 물리적 선제 봉쇄]: 모든 클래스 및 모듈 선행 각인
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

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 이중 블랙박스 엔진]: os.fsync 물리 각인
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_msg = f"[{ts}] {msg}\n"
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
            f.flush()
            os.fsync(f.fileno())
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. KV 레이아웃]: 1줄 1속성 원칙 및 반투명 UI 적용
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
    outline_width: 1
    outline_color: 0, 0, 0, 1

<Button>:
    font_name: 'KFont'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.6
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.2
        Line:
            width: 1
            rectangle: self.x, self.y, self.width, self.height

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "PristonTale Manager v47"
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
            spacing: '10dp'
        Button:
            text: "<< 계정 목록"
            size_hint_y: 0.1
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '12dp'
        Button:
            text: "1. 케릭정보창 (18개 목록)"
            on_release: root.manager.current = 'info'
        Button:
            text: "2. 케릭장비창 (11개 목록)"
            on_release: root.manager.current = 'equip'
        Button:
            text: "3. 인벤토리창 (상세관리)"
            on_release: root.manager.current = 'inv'
        Button:
            text: "4. 사진선택창 (다중업로드)"
            on_release: root.manager.current = 'photo'
        Button:
            text: "5. 저장보관소 (데이터)"
            on_release: root.manager.current = 'storage'
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
                text: "저장하시겠습니까?"
                on_release: root.save_confirm()
            Button:
                text: "뒤로가기"
                background_color: 0.4, 0.4, 0.4, 0.7
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

# [4. 앱 엔진: 시동 순서 격리 (Boot Isolation)]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # 폰트 우선 탐색 (점주님 지정 경로)
        f_path = "/storage/emulated/0/Download/font.ttf"
        target = f_path if os.path.exists(f_path) else "Roboto"
        LabelBase.register(name="KFont", fn_regular=target)
        return Builder.load_string(KV)

    def on_start(self):
        # 2초 뒤에 권한 및 데이터 로드 진행 (UI 먼저 안착)
        Clock.schedule_once(self.deferred_boot, 2.0)

    def deferred_boot(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.MANAGE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES
                ])
            except: pass
        self.load_data()

    def load_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v47.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except: pass

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v47.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except: pass

# [5. 스크린 로직: 제1원칙 사수]
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
        app.user_data["accounts"][aid] = {str(i):{"info":{}, "equip":{}, "photo":[]} for i in range(1,7)}
        app.save_data()
        self.refresh()
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
    # 18개 목록 물리 각인
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=f, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text=f"{f} 입력"))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class EquipScreen(Screen):
    # 11개 목록 물리 각인
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for i in self.items:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=i, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text="장비 정보"))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class InventoryScreen(Screen):
    def save_confirm(self): self.manager.current = 'slot_menu'

class PhotoScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Button(text="다중 사진 업로드", size_hint_y=None, height="60dp"))
        self.ids.box.add_widget(Button(text="사진 삭제", size_hint_y=None, height="60dp", background_color=(0.7, 0.1, 0.1, 0.8)))
    def save_confirm(self): self.manager.current = 'slot_menu'

class StorageScreen(Screen):
    def save_confirm(self): self.manager.current = 'slot_menu'

if __name__ == "__main__":
    PristonApp().run()
