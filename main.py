import os, sys, traceback, json, shutil
from datetime import datetime

# [1. 물리 봉쇄: 클래스 및 UI 구성 요소 사전 로드]
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 블랙박스 엔진]
INTERNAL_LOG = ""
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and not INTERNAL_LOG:
            INTERNAL_LOG = os.path.join(app.user_data_dir, "Internal_Log.txt")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"
        if INTERNAL_LOG:
            with open(INTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
        try:
            with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
        except: pass
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. Kivy 환경 설정]
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import platform

# [4. KV 레이아웃: 모든 텍스트에 KFont 강제 적용]
KV = '''
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

<Button>:
    font_name: 'KFont'

<TextInput>:
    font_name: 'KFont'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: "[PT1 매니저: 다운로드 폰트 적용]"
            font_size: '22sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "계정/캐릭터 검색..."
            size_hint_y: None
            height: '50dp'
            multiline: False
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Button:
                text: "비상 로그"
                on_release: root.show_internal_log()
            Button:
                text: "+ 새 계정"
                on_release: root.add_acc_popup()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        Label:
            id: title_label
            text: "캐릭터 선택"
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "처음으로"
            size_hint_y: 0.2
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 10
        Button:
            text: "케릭정보창"
            on_release: root.manager.current = 'info'
        Button:
            text: "케릭장비창"
            on_release: root.manager.current = 'equip'
        Button:
            text: "뒤로가기"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "저장 및 뒤로가기"
            size_hint_y: 0.12
            on_release: root.manager.current = 'slot_menu'

ScreenManager:
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
'''

# [5. 기능 로직 구현]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            btn = Button(text=f"계정: {aid}", size_hint_y=None, height="65dp")
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            self.ids.acc_list.add_widget(btn)
    def add_acc_popup(self):
        aid = f"toopen_{datetime.now().strftime('%M%S')}"
        App.get_running_app().user_data["accounts"][aid] = {str(i): {} for i in range(1, 7)}
        App.get_running_app().save_data(); self.refresh(0)
    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def show_internal_log(self):
        try:
            with open(INTERNAL_LOG, "r", encoding="utf-8") as f: content = f.read()[-500:]
        except: content = "No Log"
        from kivy.uix.popup import Popup
        Popup(title="Log", content=Label(text=content), size_hint=(0.9, 0.8)).open()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.title_label.text = f"[{App.get_running_app().cur_acc}] 캐릭터 선택"
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}")
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass

class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # [강제 생존 폰트 봉쇄]: 다운로드 폴더의 font.ttf를 최우선 탐색
        download_font = "/storage/emulated/0/Download/font.ttf"
        
        if os.path.exists(download_font):
            LabelBase.register(name="KFont", fn_regular=download_font)
            write_blackbox(">>> 다운로드 폴더에서 font.ttf 로드 성공 <<<")
        else:
            # 파일이 없을 경우를 대비한 시스템 폰트 백업
            backup_font = "/system/fonts/NotoSansCJK-Regular.ttc"
            if os.path.exists(backup_font):
                LabelBase.register(name="KFont", fn_regular=backup_font)
            else:
                LabelBase.register(name="KFont", fn_regular="Roboto-Regular.ttf")
            write_blackbox("!!! 다운로드 폴더에 font.ttf가 없어 백업 폰트 사용 !!!")

        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_once(self.deferred_init, 0.5)

    def deferred_init(self, dt):
        if platform == 'android':
            from android.permissions import request_permissions, check_permission
            perms = ["android.permission.WRITE_EXTERNAL_STORAGE", "android.permission.READ_EXTERNAL_STORAGE"]
            request_permissions(perms)
        
        try:
            if os.path.exists("PT1_Data.json"):
                with open("PT1_Data.json", "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except: pass

    def save_data(self):
        try:
            with open("PT1_Data.json", "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except: pass

if __name__ == "__main__":
    PristonApp().run()
