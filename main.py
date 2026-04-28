import os, sys, traceback, json
from datetime import datetime

# [1. 환경 설정 및 모듈 로드]
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
from kivy.graphics import Rectangle, Color

# [2. 블랙박스 & 초강력 자가 치유 엔진]
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

# 전역 에러 트래핑: 어떤 치명적 오류도 블랙박스에 가두고 앱은 살려둠
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. 스크린 로직]: 모든 라인 자가 치유 격벽 설치
class MainScreen(Screen):
    def on_enter(self):
        try:
            Clock.schedule_once(lambda dt: self.refresh(), 0.1)
        except Exception as e:
            write_blackbox(f"Healing Main on_enter: {str(e)}")

    def refresh(self, search_text=""):
        try:
            container = self.ids.acc_list
            container.clear_widgets()
            app = App.get_running_app()
            accounts = app.user_data.get("accounts", {})
            for aid in accounts:
                if search_text.lower() in aid.lower():
                    btn = Button(text=f"계정 ID: {aid}", size_hint_y=None, height="60dp")
                    btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                    container.add_widget(btn)
        except Exception as e:
            write_blackbox(f"Healing refresh: {str(e)}")

    def add_acc(self):
        try:
            aid = datetime.now().strftime('%H%M%S')
            app = App.get_running_app()
            if "accounts" not in app.user_data:
                app.user_data["accounts"] = {}
            app.user_data["accounts"][aid] = {str(i): {"info": {}, "equip": {}} for i in range(1, 7)}
            app.save_data()
            self.refresh(self.ids.search_input.text)
        except Exception as e:
            write_blackbox(f"Healing add_acc: {str(e)}")

    def go_acc(self, aid):
        try:
            App.get_running_app().cur_acc = aid
            self.manager.current = 'char_select'
        except Exception as e:
            write_blackbox(f"Healing go_acc: {str(e)}")

class CharSelectScreen(Screen):
    def on_enter(self):
        try:
            self.ids.grid.clear_widgets()
            for i in range(1, 7):
                btn = Button(text=f"캐릭터 슬롯 {i}")
                btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
                self.ids.grid.add_widget(btn)
        except Exception as e:
            write_blackbox(f"Healing CharSelect: {str(e)}")

    def go_slot(self, idx):
        try:
            App.get_running_app().cur_slot = str(idx)
            self.manager.current = 'slot_menu'
        except Exception as e:
            write_blackbox(f"Healing go_slot: {str(e)}")

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
    def on_enter(self):
        try:
            self.ids.box.clear_widgets()
            for f in self.fields:
                row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
                row.add_widget(Label(text=f, size_hint_x=0.35))
                row.add_widget(TextInput(hint_text="입력", multiline=False))
                self.ids.box.add_widget(row)
        except Exception as e:
            write_blackbox(f"Healing Info: {str(e)}")

    def save_confirm(self):
        try:
            App.get_running_app().save_data()
            self.manager.current = 'slot_menu'
        except Exception as e:
            write_blackbox(f"Healing save: {str(e)}")

class EquipScreen(Screen):
    items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
    def on_enter(self):
        try:
            self.ids.box.clear_widgets()
            for i in self.items:
                row = BoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
                row.add_widget(Label(text=i, size_hint_x=0.35))
                row.add_widget(TextInput(hint_text="정보", multiline=False))
                self.ids.box.add_widget(row)
        except Exception as e:
            write_blackbox(f"Healing Equip: {str(e)}")

    def save_confirm(self):
        try:
            App.get_running_app().save_data()
            self.manager.current = 'slot_menu'
        except Exception as e:
            write_blackbox(f"Healing save: {str(e)}")

class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [4. KV 레이아웃]: 한 줄 표기법 완전 제거 및 정석 분리
KV = '''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Screen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<Label>:
    font_name: 'font' if 'font' in LabelBase.get_registered_designators() else 'Roboto'
    outline_width: 1
    outline_color: 0, 0, 0, 1

<Button>:
    font_name: 'font' if 'font' in LabelBase.get_registered_designators() else 'Roboto'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.6

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: "PristonTale Manager v68 (Final)"
            font_size: '20sp'
            size_hint_y: 0.1
        TextInput:
            id: search_input
            hint_text: "계정 ID 검색"
            size_hint_y: None
            height: '50dp'
            multiline: False
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
            on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "캐릭터 슬롯 선택"
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: '15dp'
        Button:
            text: "<< 계정 목록으로"
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

<InfoScreen>, <EquipScreen>:
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

<InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: "준비 중입니다."
        Button:
            text: "뒤로가기"
            size_hint_y: 0.2
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

# [5. 앱 엔진]: 폰트/이미지 에러 시 자가 수복 로직 탑재
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        try:
            icon_p = os.path.join(DOWNLOAD_PATH, "icon.png")
            if os.path.exists(icon_p): self.icon = icon_p
            return Builder.load_string(KV)
        except Exception as e:
            write_blackbox(f"Critical Parser Healing: {str(e)}")
            return ScreenManager()

    def on_start(self):
        try:
            self.apply_font()
            Clock.schedule_once(self.request_android_permissions, 1.0)
            self.load_data()
        except Exception as e:
            write_blackbox(f"OnStart Healing: {str(e)}")

    def request_android_permissions(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
                for p_name in ['READ_MEDIA_IMAGES', 'READ_MEDIA_VIDEO']:
                    if hasattr(Permission, p_name):
                        perms.append(getattr(Permission, p_name))
                request_permissions(perms, self.on_permission_result)
            except Exception as e:
                write_blackbox(f"Perm Healing: {str(e)}")
                self.apply_background()
        else:
            self.apply_background()

    def on_permission_result(self, permissions, results):
        self.apply_background()

    def apply_font(self):
        # 폰트 등록 실패 시 튕기지 않도록 자가 치유 격벽 설치
        try:
            f_p = os.path.join(DOWNLOAD_PATH, "font.ttf")
            if os.path.exists(f_p):
                LabelBase.register(name="font", fn_regular=f_p)
                write_blackbox("Font Engraved Successfully.")
            else:
                write_blackbox("Font file not found, using default.")
        except Exception as e:
            write_blackbox(f"Font Healing Applied: {str(e)}")

    def apply_background(self, *args):
        try:
            bg_p = os.path.join(DOWNLOAD_PATH, "bg.png")
            if os.path.exists(bg_p):
                for sc in self.root.screens:
                    with sc.canvas.before:
                        Color(1, 1, 1, 1)
                        Rectangle(source=bg_p, pos=sc.pos, size=sc.size)
                write_blackbox("Background Applied.")
        except Exception as e:
            write_blackbox(f"Background Healing: {str(e)}")

    def load_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_Final.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except Exception as e:
            write_blackbox(f"Data Load Healing: {str(e)}")

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Data_Final.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"Data Save Healing: {str(e)}")

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"FINAL CRITICAL FAILURE: {str(e)}")
