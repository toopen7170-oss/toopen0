import os, sys, traceback, json, shutil
from datetime import datetime

# [물리적 선제 봉쇄]: 엔진 로드 전 모든 클래스 및 모듈 선행 각인
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

# 7대 창 클래스 껍데기 물리 선언 (NameError 방지)
class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [이중 블랙박스 엔진]: 내부/외부 이중 기록 시스템
INTERNAL_LOG = ""
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    try:
        if not INTERNAL_LOG:
            try:
                INTERNAL_LOG = os.path.join(App.get_running_app().user_data_dir, "Internal_Log.txt")
            except: INTERNAL_LOG = "Internal_Log.txt"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"

        with open(INTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
        try:
            with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
                f.flush()
                os.fsync(f.fileno()) # 물리적 강제 각인
        except: pass
    except: pass

# 치명적 오류 발생 시 자동 기록
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [KV 레이아웃]: 1줄 1속성 원칙 및 반투명 UI 적용
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
    color: 1, 1, 1, 1
    outline_width: 1
    outline_color: 0, 0, 0, 1

<Button>:
    font_name: 'KFont'
    background_normal: ''
    background_color: 0.1, 0.4, 0.2, 0.7  # 기본 초록 계열
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.3
        Line:
            width: 1.2
            rectangle: self.x, self.y, self.width, self.height

<TextInput>:
    font_name: 'KFont'
    background_color: 1, 1, 1, 0.8
    multiline: False
    write_tab: False

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
            hint_text: "전체 검색 (계정/이름)..."
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
            height: '60dp'
            spacing: 15
            Button:
                text: "비상 로그"
                background_color: 0.4, 0.4, 0.4, 0.8
                on_release: root.show_internal_log()
            Button:
                text: "+ 계정 생성"
                on_release: root.add_acc_popup()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            id: title_label
            text: "캐릭터 선택"
            font_size: '22sp'
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: 20
        Button:
            text: "처음으로"
            size_hint_y: 0.15
            background_color: 0.6, 0.2, 0.2, 0.8
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
        padding: 15
        spacing: 10
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
                text: "저장 (Save)"
                background_color: 0.1, 0.5, 0.1, 0.9
                on_release: root.save_confirm()
            Button:
                text: "뒤로가기"
                background_color: 0.6, 0.2, 0.2, 0.8
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

# [기능 로직]: 제1원칙 사수 및 오류 자가 수복
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        try:
            self.ids.acc_list.clear_widgets()
            data = App.get_running_app().user_data.get("accounts", {})
            for aid in data:
                btn = Button(text=f"ID: {aid}", size_hint_y=None, height="70dp")
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                self.ids.acc_list.add_widget(btn)
        except Exception as e: write_blackbox(f"Refresh Error: {str(e)}")

    def add_acc_popup(self):
        aid = f"User_{datetime.now().strftime('%m%d_%H%M')}"
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "storage":[]} for i in range(1, 7)}
        app.save_data()
        self.refresh(0)

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def show_internal_log(self):
        try:
            with open(INTERNAL_LOG, "r", encoding="utf-8") as f: content = f.read()[-1500:]
        except: content = "기록된 로그가 없습니다."
        Popup(title="BlackBox Emergency Log", content=TextInput(text=content, readonly=True), size_hint=(0.9, 0.8)).open()

class CharSelectScreen(Screen):
    def on_enter(self):
        try:
            self.ids.title_label.text = f"계정 [{App.get_running_app().cur_acc}] 슬롯 선택"
            self.ids.grid.clear_widgets()
            for i in range(1, 7):
                btn = Button(text=f"SLOT {i}\n(대기중)", halign='center')
                btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
                self.ids.grid.add_widget(btn)
        except Exception as e: write_blackbox(f"CharSelect Error: {str(e)}")

    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    fields = ['이름','레벨','힘','민첩','건강','정신','재능','생명력','기력','근력','명중','공격','방어','흡수','속도','클랜','직위','비고']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, halign='right'))
            row.add_widget(TextInput(hint_text=f"{f} 입력"))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class EquipScreen(Screen):
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for i in self.items:
            row = BoxLayout(size_hint_y=None, height="55dp", spacing=10)
            row.add_widget(Label(text=i, size_hint_x=0.3))
            row.add_widget(TextInput(hint_text="아이템 정보"))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class InventoryScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="[인벤토리 시스템]\n데이터 로딩 중...", size_hint_y=None, height="150dp", halign='center'))
    def save_confirm(self): self.manager.current = 'slot_menu'

class PhotoScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="[사진 선택창]\n미디어 권한 확인 필요", size_hint_y=None, height="150dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

class StorageScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="[저장보관소]\n물리 각인 영역", size_hint_y=None, height="150dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

# [앱 메인 엔진]: 시동 격리 및 권한 수복
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # 폰트 우선 탐색 (Download -> System -> Default)
        font_p = "/storage/emulated/0/Download/font.ttf"
        backup_p = "/system/fonts/NotoSansCJK-Regular.ttc"
        target_font = font_p if os.path.exists(font_p) else (backup_p if os.path.exists(backup_p) else "Roboto")
        LabelBase.register(name="KFont", fn_regular=target_font)
        
        write_blackbox(f"Engine Booting: Font used - {target_font}")
        return Builder.load_string(KV)

    def on_start(self):
        # 시동 멈춤 방지: UI 먼저 띄우고 데이터 로드
        Clock.schedule_once(self.deferred_init, 0.6)

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
            except: pass
        
        try:
            data_path = os.path.join(self.user_data_dir, "PT1_Data.json")
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            write_blackbox(">>> Data Load Success <<<")
        except Exception as e:
            write_blackbox(f"Critical Data Load Error: {str(e)}")

    def save_data(self):
        try:
            data_path = os.path.join(self.user_data_dir, "PT1_Data.json")
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
            write_blackbox("Data Saved Successfully")
        except Exception as e:
            write_blackbox(f"Save Error: {str(e)}")

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"FATAL BOOT ERROR: {str(e)}")
