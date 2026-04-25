import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 엔진: PristonTale 물리 각인형 시스템]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        if not os.path.exists(os.path.dirname(path)): return "PristonTale_BlackBox.txt"
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except: return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 저장 강제
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> 시스템 엔진 가동 (최종 무결점 통합본) <<<")

# [2. 환경 오류 수리: 안드로이드 14 대응]
from kivy.utils import platform
if platform == 'android':
    from android.permissions import request_permissions
    perms = ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE", 
             "android.permission.READ_MEDIA_IMAGES", "android.permission.MANAGE_EXTERNAL_STORAGE"]
    request_permissions(perms)

from kivy.config import Config
Config.set('kivy', 'text', 'sdl2')
Config.set('graphics', 'multisamples', '0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [3. 데이터 매니저]
class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.flush(); os.fsync(f.fileno())
        except Exception as e:
            write_blackbox(f"데이터 저장 실패: {e}")

# [4. 7대 화면 클래스 - 절대 규칙 준수]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.acc_list_box.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
            btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            del_btn = Button(text="X", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
            del_btn.bind(on_release=lambda x, a=aid: self.del_acc(a))
            row.add_widget(btn); row.add_widget(del_btn)
            self.ids.acc_list_box.add_widget(row)
    def add_acc(self):
        aid = self.ids.new_acc_input.text.strip()
        if aid:
            app = App.get_running_app()
            if aid not in app.user_data["accounts"]:
                app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
                app.save_data(); self.refresh(0); self.ids.new_acc_input.text = ""
    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.char_slot_grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.char_slot_grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 18개 세부 목록
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','기타']
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.info_scroll_box.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center', padding_y=(15,15))
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.info_scroll_box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    # 11개 세부 목록
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.equip_scroll_box.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center', padding_y=(15,15))
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.equip_scroll_box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

class InventoryScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.inv_list_box.clear_widgets()
        items = App.get_running_app().get_cur_data()["inv"]
        for val in items:
            btn = Button(text=val[:20], size_hint_y=None, height="60dp", background_color=get_color_from_hex("#2E7D32"))
            self.ids.inv_list_box.add_widget(btn)
    def add_item(self):
        App.get_running_app().get_cur_data()["inv"].append("새 아이템")
        App.get_running_app().save_data(); self.refresh(0)

class PhotoScreen(Screen): pass

class StorageScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.storage_list_box.clear_widgets()
        items = App.get_running_app().get_cur_data()["storage"]
        for val in items:
            btn = Button(text=val[:20], size_hint_y=None, height="60dp", background_color=get_color_from_hex("#455A64"))
            self.ids.storage_list_box.add_widget(btn)
    def add_item(self):
        App.get_running_app().get_cur_data()["storage"].append("보관 항목")
        App.get_running_app().save_data(); self.refresh(0)

# [5. KV 레이아웃 - 모듈 주입 및 ID 충돌 박멸]
KV = '''
#:import os os
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Screen>:
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            source: 'bg.png' if os.path.exists('bg.png') else ''
            pos: self.pos
            size: self.size

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

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "PristonTale"
            font_size: '35sp'
            size_hint_y: 0.15
        ScrollView:
            BoxLayout:
                id: acc_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            TextInput:
                id: new_acc_input
                hint_text: "계정 ID 입력"
                multiline: False
                halign: 'center'
            Button:
                text: "생성"
                size_hint_x: 0.3
                background_color: (0.18, 0.49, 0.2, 1)
                on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "캐릭터 선택"
            size_hint_y: 0.1
            font_size: '20sp'
        GridLayout:
            id: char_slot_grid
            cols: 2
            spacing: 15
        Button:
            text: "뒤로가기"
            size_hint_y: 0.15
            background_color: (0.5, 0.5, 0.5, 1)
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        Button: text: "케릭정보창"; on_release: root.manager.current = 'info'
        Button: text: "케릭장비창"; on_release: root.manager.current = 'equip'
        Button: text: "인벤토리창"; on_release: root.manager.current = 'inv'
        Button: text: "사진선택창"; on_release: root.manager.current = 'photo'
        Button: text: "저장보관소"; on_release: root.manager.current = 'storage'
        Button:
            text: "뒤로가기"
            background_color: (0.7, 0.2, 0.2, 1)
            on_release: root.manager.current = 'char_select'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: info_scroll_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        Button:
            text: "뒤로가기"
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'slot_menu'

<EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: equip_scroll_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        Button:
            text: "뒤로가기"
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'slot_menu'

<InventoryScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: inv_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 10
            Button: text: "추가"; on_release: root.add_item()
            Button: text: "뒤로"; on_release: root.manager.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label: text: "사진 선택 시스템 (준비 중)"
        Button:
            text: "뒤로가기"
            size_hint_y: 0.1
            on_release: root.manager.current = 'slot_menu'

<StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: storage_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 10
            Button: text: "추가"; on_release: root.add_item()
            Button: text: "뒤로"; on_release: root.manager.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        Window.softinput_mode = 'below_target'
        return Builder.load_string(KV)
    def get_cur_data(self):
        return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self):
        DataStore.save(self.user_data)

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception:
        write_blackbox(traceback.format_exc())
