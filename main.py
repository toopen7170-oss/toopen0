import os, sys, traceback, json
from datetime import datetime

# [예방 1]: 핵심 모듈 선제 고정 (NoTransition으로 IndexError 원천 차단)
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color
from kivy.utils import platform

# [환경 설정 및 블랙박스 시스템]
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
DATA_FILE = os.path.join(DOWNLOAD_PATH, "PT_Data_v109.json")
BLACKBOX_LOG = os.path.join(DOWNLOAD_PATH, "PT_BlackBox.txt")

def write_blackbox(msg):
    """팅김 전 상황을 기록하는 블랙박스 시스템"""
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(BLACKBOX_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except: pass

# [강제 생존]: 시스템 예외 발생 시 블랙박스 즉시 기록 후 생존
sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [물리 봉쇄]: Pre-Init 단계 폰트 등록
try:
    font_p = os.path.join(DOWNLOAD_PATH, "font.ttf")
    if os.path.exists(font_p):
        LabelBase.register(name="korean", fn_regular=font_p)
        write_blackbox("System: Pre-Init Font Registration Success")
except Exception as e: write_blackbox(f"Font Error: {e}")

# [예방 2]: 자가 치유 베이스 스크린 (배경 유실 대비)
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self._draw_bg, pos=self._draw_bg)

    def _draw_bg(self, *args):
        try:
            self.canvas.before.clear()
            with self.canvas.before:
                bg_p = os.path.join(DOWNLOAD_PATH, "bg.png")
                Color(1, 1, 1, 1)
                if os.path.exists(bg_p): Rectangle(source=bg_p, pos=self.pos, size=self.size)
                else:
                    Color(0.05, 0.1, 0.2, 1); Rectangle(pos=self.pos, size=self.size)
        except Exception as e: write_blackbox(f"BG Drawing Error: {e}")

# [세부 목록]: 18종 정보 + 11종 장비 필드 완벽 복구
INFO_KEYS = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','비고']
EQUIP_KEYS = ['한손무기','두손무기','갑옷','방패','장갑','부츠','암릿','링1','링2','아뮬랫','기타']

class MainScreen(BaseScreen):
    def on_enter(self): Clock.schedule_once(lambda dt: self.refresh(), 0.05)
    def refresh(self, search=""):
        try:
            self.ids.acc_list.clear_widgets()
            accs = App.get_running_app().user_data.get("accounts", {})
            for aid in accs:
                if search.lower() in aid.lower():
                    row = BoxLayout(size_hint_y=None, height="60dp", spacing="5dp")
                    btn = Button(text=f"ID: {aid}", background_color=(0.2, 0.4, 0.6, 1))
                    btn.bind(on_release=lambda x, a=aid: self.select_acc(a))
                    del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
                    del_btn.bind(on_release=lambda x, a=aid: self.delete_pop(a))
                    row.add_widget(btn); row.add_widget(del_btn)
                    self.ids.acc_list.add_widget(row)
        except Exception as e: write_blackbox(f"Main Refresh Error: {e}")

    def select_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def delete_pop(self, aid):
        pop = Popup(title="계정 삭제", size_hint=(0.8, 0.4))
        cnt = BoxLayout(orientation='vertical', padding=10, spacing=10)
        cnt.add_widget(Label(text=f"{aid} 삭제하시겠습니까?"))
        btn_r = BoxLayout(size_hint_y=0.4, spacing=10)
        btn_r.add_widget(Button(text="삭제", on_release=lambda x: self.do_del(aid, pop)))
        btn_r.add_widget(Button(text="취소", on_release=pop.dismiss))
        cnt.add_widget(btn_r); pop.content=cnt; pop.open()

    def do_del(self, aid, pop):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
        pop.dismiss()

    def create_acc(self):
        new_id = datetime.now().strftime('%m%d_%H%M%S')
        app = App.get_running_app()
        app.user_data["accounts"][new_id] = {str(i): {"info":{}, "equip":{}, "inv":{}, "photo":{}, "storage":{}} for i in range(1,7)}
        app.save_data(); self.refresh()

class CharSelectScreen(BaseScreen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", background_color=(0.2, 0.6, 0.3, 0.7))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen): pass

class DataEntryScreen(BaseScreen):
    keys = []; data_type = ""
    def on_enter(self):
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()
            acc_data = app.user_data["accounts"].get(app.cur_acc, {})
            slot_data = acc_data.get(app.cur_slot, {})
            current_values = slot_data.get(self.data_type, {})
            self.inputs = {}
            for k in self.keys:
                row = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
                row.add_widget(Label(text=k, size_hint_x=0.3))
                ti = TextInput(text=str(current_values.get(k, "")), multiline=False)
                self.inputs[k] = ti
                row.add_widget(ti)
                self.ids.container.add_widget(row)
        except Exception as e: write_blackbox(f"DataEntry Error: {e}")

    def save(self):
        try:
            app = App.get_running_app()
            new_v = {k: ti.text for k, ti in self.inputs.items()}
            app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type] = new_v
            app.save_data(); self.manager.current = 'slot_menu'
        except Exception as e: write_blackbox(f"Save Failure: {e}")

class InfoScreen(DataEntryScreen): keys = INFO_KEYS; data_type = "info"
class EquipScreen(DataEntryScreen): keys = EQUIP_KEYS; data_type = "equip"
class InventoryScreen(DataEntryScreen): keys = ['아이템 목록/수량']; data_type = "inv"
class PhotoScreen(DataEntryScreen): keys = ['사진 메모/설명']; data_type = "photo"
class StorageScreen(DataEntryScreen): keys = ['보관소 위치/내용']; data_type = "storage"

# [예방 1-KV]: NoTransition 및 세미콜론 제거된 정규 문법
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<Label>, <Button>, <TextInput>:
    font_name: 'korean' if app.font_exists else 'Roboto'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: "PT Manager v109 [BlackBox]"
            size_hint_y: 0.1
        TextInput:
            hint_text: "계정 검색..."
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
            text: "캐릭터 슬롯 선택 (1~6)"
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
        padding: 15
        spacing: 8
        Button:
            text: "1. 캐릭터 정보 (18종)"
            on_release: root.manager.current = 'info'
        Button:
            text: "2. 캐릭터 장비 (11종)"
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
            text: "이전으로"
            on_release: root.manager.current = 'char_select'

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
            size_hint_y: 0.15
            spacing: 10
            Button:
                text: "데이터 저장"
                on_release: root.save()
            Button:
                text: "취소"
                on_release: root.manager.current = 'slot_menu'

ScreenManager:
    transition: NoTransition()
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

class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""
    font_exists = os.path.exists(os.path.join(DOWNLOAD_PATH, "font.ttf"))

    def build(self):
        self.load_data()
        try:
            return Builder.load_string(KV)
        except Exception as e:
            write_blackbox(f"KV Load Failure: {e}")
            return Label(text="KV Load Error Check BlackBox")

    def load_data(self):
        # [예방 3]: 데이터 강제 생존 로직
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
            else: self.user_data = {"accounts": {}}
        except Exception as e:
            write_blackbox(f"Load Error: {e}")
            self.user_data = {"accounts": {}}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e: write_blackbox(f"Save Failure: {e}")

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions
                request_permissions(['android.permission.READ_EXTERNAL_STORAGE', 
                                    'android.permission.WRITE_EXTERNAL_STORAGE',
                                    'android.permission.MANAGE_EXTERNAL_STORAGE'])
            except: pass

if __name__ == "__main__":
    PristonApp().run()
