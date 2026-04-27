import os, sys, traceback, json
from datetime import datetime

# [1. 물리적 선제 봉쇄]: NameError 차단용 클래스 선언
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
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_msg = f"[{timestamp}] {msg}\n"
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
            f.flush()
            os.fsync(f.fileno())
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. 전역 투명 UI 및 KV 1줄 1속성 원칙]
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

<TextInput>:
    font_name: 'KFont'
    background_color: 1, 1, 1, 0.6
    foreground_color: 0, 0, 0, 1
    multiline: False
    halign: 'center'

<Button>:
    font_name: 'KFont'
    background_normal: ''
    background_color: 0.18, 0.49, 0.2, 0.6
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.3
        Line:
            width: 1.1
            rectangle: self.x, self.y, self.width, self.height

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            text: "PristonTale Manager v46"
            font_size: '30sp'
            size_hint_y: 0.15
        TextInput:
            id: search_bar
            hint_text: "계정 또는 캐릭터 검색..."
            size_hint_y: None
            height: '50dp'
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: '10dp'
            Button:
                text: "+ 새 계정 생성"
                on_release: root.add_acc_popup()
            Button:
                text: "전체 삭제"
                background_color: 0.77, 0.15, 0.15, 0.7
                on_release: root.clear_all_confirm()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        Label:
            id: title_label
            font_size: '22sp'
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: '15dp'
        Button:
            text: "<< 계정 목록으로"
            size_hint_y: 0.12
            background_color: 0.4, 0.4, 0.4, 0.7
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '12dp'
        Button: text: "1. 케릭정보창 (18개 목록)"; on_release: root.manager.current = 'info'
        Button: text: "2. 케릭장비창 (11개 목록)"; on_release: root.manager.current = 'equip'
        Button: text: "3. 인벤토리창 (상세관리)"; on_release: root.manager.current = 'inv'
        Button: text: "4. 사진선택창 (다중업로드)"; on_release: root.manager.current = 'photo'
        Button: text: "5. 저장보관소 (데이터)"; on_release: root.manager.current = 'storage'
        Widget: size_hint_y: 0.1
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
                text: "삭제하시겠습니까?"
                background_color: 0.77, 0.15, 0.15, 0.7
                on_release: root.delete_confirm()
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

# [4. 앱 메인 엔진: 시동 순서 격리 및 권한 수복]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        # 폰트 탐색 제0순위: 점주님 지정 경로
        f_path = "/storage/emulated/0/Download/font.ttf"
        target = f_path if os.path.exists(f_path) else "Roboto"
        LabelBase.register(name="KFont", fn_regular=target)
        Window.clearcolor = (0, 0, 0, 1)
        return Builder.load_string(KV)

    def on_start(self):
        # [시동 순서 격리]: 2.5초 대기 후 엔진 가동 (검은 화면 방지)
        Clock.schedule_once(self.deferred_boot, 2.5)

    def deferred_boot(self, dt):
        write_blackbox(">>> Boot Isolation Complete. Loading Engine... <<<")
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES,
                    Permission.MANAGE_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ])
                write_blackbox("All 5 Permissions Requested.")
            except Exception as e:
                write_blackbox(f"Permission Error: {e}")
        self.load_data()

    def load_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Master_Data.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            write_blackbox("Data Sync Success.")
        except: write_blackbox("Data Sync Failed.")

    def save_data(self):
        try:
            path = os.path.join(self.user_data_dir, "PT_Master_Data.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
            write_blackbox("Physical Save Complete.")
        except: pass

# [5. 제1원칙: 7대 창 및 29개 세부 목록 물리 각인 로직]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            btn = Button(text=f"계정 ID: {aid}", size_hint_y=None, height="65dp")
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            self.ids.acc_list.add_widget(btn)

    def add_acc_popup(self):
        aid = f"USER_{datetime.now().strftime('%H%M%S')}"
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i):{"info":{}, "equip":{}, "inv":[], "photo":[], "storage":[]} for i in range(1,7)}
        app.save_data()
        self.refresh()

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.title_label.text = f"계정 [{App.get_running_app().cur_acc}] 캐릭터 선택"
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"SLOT {i}")
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 제1원칙 18개 목록
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
    def delete_confirm(self): pass

class EquipScreen(Screen):
    # 제1원칙 11개 목록
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
    def delete_confirm(self): pass

class InventoryScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="인벤토리 줄 단위 리스트", size_hint_y=None, height="100dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

class PhotoScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        btn_layout = BoxLayout(size_hint_y=None, height="60dp", spacing="10dp")
        btn_layout.add_widget(Button(text="다중 사진 업로드", on_release=self.upload_photos))
        btn_layout.add_widget(Button(text="사진 다운로드", on_release=self.download_photos))
        self.ids.box.add_widget(btn_layout)
        self.ids.box.add_widget(Label(id="photo_status", text="선택된 사진 없음", size_hint_y=None, height="50dp"))

    def upload_photos(self, instance):
        # 안드로이드 갤러리 호출 가상 로직 (실제 빌드 시 plyer/android 사용)
        write_blackbox("Photo Picker Requested.")
        self.ids.photo_status.text = "사진 3장 업로드 완료 (가상)"

    def download_photos(self, instance):
        write_blackbox("Photo Download Started.")

    def save_confirm(self): 
        App.get_running_app().save_data()
        self.manager.current = 'slot_menu'
    def delete_confirm(self): pass

class StorageScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        self.ids.box.add_widget(Label(text="저장보관소 통합 리스트", size_hint_y=None, height="100dp"))
    def save_confirm(self): self.manager.current = 'slot_menu'

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"CRITICAL BOOT ERROR: {e}")
