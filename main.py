import os, sys, traceback, json
from datetime import datetime

# [1. 물리적 선행 각인]: 모든 모듈과 클래스 선언
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

# 각 스크린 클래스 개별 정의 (다중 선언 파싱 에러 방지)
class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 블랙박스 & 환경 설정]
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

# 치명적 오류 발생 시 블랙박스에 유언 남기기
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. KV 레이아웃]: 1줄 1속성 엄격 준수 및 외부 리소스 참조 완전 격리
KV = '''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Screen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            id: bg_rect
            pos: self.pos
            size: self.size

<Label>:
    font_name: 'KFont'
    outline_width: 1
    outline_color: 0, 0, 0, 1

<Button>:
    font_name: 'KFont'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.6

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "PristonTale Manager v56"
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
            background_color: 0.4, 0.4, 0.4, 0.7
            on_release: root.manager.current = 'char_select'

<InfoScreen>:
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
                on_release: root.manager.current = 'slot_menu'

<EquipScreen>:
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
                on_release: root.manager.current = 'slot_menu'

<InventoryScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: "인벤토리 준비 중 (뒤로가기)"
            on_release: root.manager.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: "사진선택 준비 중 (뒤로가기)"
            on_release: root.manager.current = 'slot_menu'

<StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: "저장보관소 준비 중 (뒤로가기)"
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

# [4. 앱 엔진: 권한 및 리소스 지연 주입]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""
    cur_slot = ""

    def build(self):
        # 아이콘 로드 (빌드 타임 안전성 확보)
        icon_path = os.path.join(DOWNLOAD_PATH, "icon.png")
        if os.path.exists(icon_path):
            self.icon = icon_path
        return Builder.load_string(KV)

    def on_start(self):
        # 부팅 1.5초 후 권한 요청 (안드로이드 OS 준비 대기)
        Clock.schedule_once(self.request_android_permissions, 1.5)

    def request_android_permissions(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                perms = [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.MANAGE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES
                ]
                request_permissions(perms, self.on_permission_result)
            except:
                self.apply_resources()
        else:
            self.apply_resources()
            self.load_data()

    def on_permission_result(self, permissions, results):
        write_blackbox(f"Permissions: {results}")
        self.apply_resources()
        self.load_data()

    def apply_resources(self):
        # [폰트 수복]
        f_path = os.path.join(DOWNLOAD_PATH, "font.ttf")
        if os.path.exists(f_path):
            try:
                LabelBase.register(name="KFont", fn_regular=f_path)
                write_blackbox("KFont Registered.")
            except: pass

        # [배경화면 실시간 각인]
        bg_path = os.path.join(DOWNLOAD_PATH, "bg.png")
        if os.path.exists(bg_path):
            for sc in self.root.screens:
                with sc.canvas.before:
                    Color(1, 1, 1, 1)
                    Rectangle(source=bg_path, pos=sc.pos, size=sc.size)
            write_blackbox("Background Applied.")

    def load_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v56.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            write_blackbox("Data Loaded.")
        except: pass

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_v56.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except: pass

# [5. 스크린 기능 로직]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            btn = Button(text=f"ID: {aid}", size_hint_y=None, height="60dp")
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            self.ids.acc_list.add_widget(btn)
    def add_acc(self):
        aid = datetime.now().strftime('%H%M%S')
        app = App.get_running_app()
        if "accounts" not in app.user_data: app.user_data["accounts"] = {}
        app.user_data["accounts"][aid] = {str(i):{"info":{}, "equip":{}} for i in range(1,7)}
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
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=f, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text="입력", multiline=False))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class EquipScreen(Screen):
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for i in self.items:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
            row.add_widget(Label(text=i, size_hint_x=0.35))
            row.add_widget(TextInput(hint_text="정보 입력", multiline=False))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'

class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

if __name__ == "__main__":
    PristonApp().run()
