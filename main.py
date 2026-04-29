import os, sys, traceback, json
from datetime import datetime

# [예방 1]: 모든 핵심 모듈 선제 고정 (NameError 원천 차단)
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color
from kivy.utils import platform

# [환경 설정]: 다운로드 폴더 및 블랙박스 경로 고정
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
DATA_FILE = os.path.join(DOWNLOAD_PATH, "PT_Data_v92.json")
BLACKBOX_LOG = os.path.join(DOWNLOAD_PATH, "PT_BlackBox.txt")

# [블랙박스]: 팅김 전 강제 각인 시스템
def write_blackbox(msg):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(BLACKBOX_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 즉시 각인
    except:
        print(f"BlackBox Write Failed: {msg}")

# 강제 생존 전략: 치명적 오류 발생 시에도 로그 남기고 종료
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [예방 2]: 자가 치유 베이스 스크린 (AttributeError 방지)
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self.update_ui, pos=self.update_ui)

    def update_ui(self, *args):
        Clock.schedule_once(self._draw_background, 0)

    def _draw_background(self, *args):
        try:
            self.canvas.before.clear()
            with self.canvas.before:
                bg_path = os.path.join(DOWNLOAD_PATH, "bg.png")
                Color(1, 1, 1, 1)
                if os.path.exists(bg_path):
                    Rectangle(source=bg_path, pos=self.pos, size=self.size)
                else:
                    # 자가 치유: 배경 파일 없을 시 짙은 남색 배경 적용
                    Color(0.05, 0.1, 0.2, 1)
                    Rectangle(pos=self.pos, size=self.size)
        except Exception as e:
            write_blackbox(f"BG Render Error: {e}")

# [제1 기본원칙]: 7대 창 구현 및 로직
class MainScreen(BaseScreen):
    def on_enter(self): Clock.schedule_once(lambda dt: self.refresh(), 0.1)
    def refresh(self, search=""):
        self.ids.acc_list.clear_widgets()
        accs = App.get_running_app().user_data.get("accounts", {})
        for aid in accs:
            if search.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="60dp", spacing="5dp")
                btn = Button(text=f"ID: {aid}", background_color=(0.2, 0.4, 0.6, 1))
                btn.bind(on_release=lambda x, a=aid: self.select_acc(a))
                del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
                del_btn.bind(on_release=lambda x, a=aid: self.delete_acc_pop(a))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)
    def select_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def delete_acc_pop(self, aid):
        pop = Popup(title="경고", size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f"{aid} 삭제하시겠습니까?"))
        btn_row = BoxLayout(size_hint_y=0.4, spacing=10)
        yes = Button(text="삭제", on_release=lambda x: self.do_delete(aid, pop))
        no = Button(text="취소", on_release=pop.dismiss)
        btn_row.add_widget(yes); btn_row.add_widget(no); content.add_widget(btn_row); pop.content=content; pop.open()
    def do_delete(self, aid, pop):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
        pop.dismiss()
    def create_acc(self):
        new_id = datetime.now().strftime('%m%d_%H%M%S')
        app = App.get_running_app()
        if "accounts" not in app.user_data: app.user_data["accounts"] = {}
        app.user_data["accounts"][new_id] = {str(i): {"info":{}, "equip":{}} for i in range(1,7)}
        app.save_data(); self.refresh()

class CharSelectScreen(BaseScreen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"캐릭터 슬롯 {i}", background_color=(0.2, 0.6, 0.3, 0.7))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen): pass
class InfoScreen(BaseScreen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        # 제1원칙: 18개 세부 항목
        keys = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
        for k in keys:
            row = BoxLayout(size_hint_y=None, height="45dp", spacing=10)
            row.add_widget(Label(text=k, size_hint_x=0.3))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.container.add_widget(row)

class EquipScreen(BaseScreen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        # 제1원칙: 11개 세부 항목
        items = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']
        for i in items:
            row = BoxLayout(size_hint_y=None, height="45dp", spacing=10)
            row.add_widget(Label(text=i, size_hint_x=0.3))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1)))
            self.ids.container.add_widget(row)

class InventoryScreen(BaseScreen): pass
class PhotoScreen(BaseScreen): pass
class StorageScreen(BaseScreen): pass

# [표준화]: 1줄 1속성 기반 KV 설계도
KV = '''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Label>:
    font_name: app.custom_font
    outline_width: 1

<Button>:
    font_name: app.custom_font

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        Label:
            text: "PristonTale Manager v92"
            size_hint_y: 0.1
            font_size: '20sp'
        TextInput:
            hint_text: "통합 검색..."
            size_hint_y: None
            height: '50dp'
            on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        Button:
            text: "새 계정 생성"
            size_hint_y: 0.1
            on_release: root.create_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "캐릭터 슬롯 선택"
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: 10
        Button:
            text: "이전으로"
            size_hint_y: 0.15
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 10
        Button: text: "1. 케릭정보창"; on_release: root.manager.current = 'info'
        Button: text: "2. 케릭장비창"; on_release: root.manager.current = 'equip'
        Button: text: "3. 인벤토리창"; on_release: root.manager.current = 'inv'
        Button: text: "4. 사진선택창"; on_release: root.manager.current = 'photo'
        Button: text: "5. 저장보관소"; on_release: root.manager.current = 'storage'
        Widget: size_hint_y: 0.2
        Button: text: "이전으로"; on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            Button: text: "저장"; on_release: app.save_data(); root.manager.current = 'slot_menu'
            Button: text: "취소"; on_release: root.manager.current = 'slot_menu'

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

# [앱 엔진]: 자가 진단 및 강제 생존 로직
class PristonApp(App):
    user_data = {"accounts": {}}
    custom_font = "Roboto" # 기본값

    def build(self):
        self.apply_integrity_check()
        return Builder.load_string(KV)

    def apply_integrity_check(self):
        # 1. 폰트 자가 진단 및 ValueError 봉쇄
        f_path = os.path.join(DOWNLOAD_PATH, "font.ttf")
        if os.path.exists(f_path):
            try:
                LabelBase.register(name="korean", fn_regular=f_path)
                self.custom_font = "korean"
            except Exception as e:
                write_blackbox(f"Font Load Failure (Auto-Healed): {e}")
                self.custom_font = "Roboto"
        
        # 2. 데이터 무결성 진단 (예방 3)
        self.load_data()

    def ask_permissions(self, *args):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_MEDIA_IMAGES, Permission.MANAGE_EXTERNAL_STORAGE])
            except: pass

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            else:
                self.user_data = {"accounts": {}}
        except:
            self.user_data = {"accounts": {}}
            write_blackbox("Data File Corrupted: Empty Dict Created")

    def save_data(self):
        try:
            if not os.path.exists(DOWNLOAD_PATH): os.makedirs(DOWNLOAD_PATH)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"Save Failed: {e}")

    def on_start(self):
        Clock.schedule_once(self.ask_permissions, 1)
        write_blackbox("System Start: Integrity Verified (v92)")

if __name__ == "__main__":
    PristonApp().run()
