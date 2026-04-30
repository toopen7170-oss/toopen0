import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 시스템: 물리 각인형]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except: return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{ts}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! CRITICAL CRASH !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox("Engine: PristonTale Manager v112 Initialization Success")

# [2. Kivy 모듈 선제 봉쇄]
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

# [3. 경로 및 데이터 상단 고정]
DOWNLOAD_PATH = "/storage/emulated/0/Download/"
DATA_FILE = os.path.join(DOWNLOAD_PATH, "PT_Data_v112.json")
FONT_FILE = os.path.join(DOWNLOAD_PATH, "font.ttf")
BG_FILE = os.path.join(DOWNLOAD_PATH, "bg.png")

# 폰트 강제 각인
if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="korean", fn_regular=FONT_FILE)
    except: pass

# [제1 기본원칙: 세부 목록 정의]
INFO_STRUCTURE = [
    ['이름', '직위', '클랜', '레벨'],
    ['생명력', '기력', '근력'],
    ['힘', '정신력', '재능', '민첩', '건강'],
    ['명중', '공격', '방어', '흡수', '속도']
]
EQUIP_KEYS = ['한손무기', '두손무기', '갑옷', '방패', '장갑', '부츠', '암릿', '링1', '링2', '아뮬랫', '기타']

# [4. 화면 클래스 정의]
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self._draw_bg, pos=self._draw_bg)

    def _draw_bg(self, *args):
        try:
            self.canvas.before.clear()
            with self.canvas.before:
                if os.path.exists(BG_FILE):
                    Color(1, 1, 1, 1)
                    Rectangle(source=BG_FILE, pos=self.pos, size=self.size)
                else:
                    Color(0.05, 0.1, 0.2, 1)
                    Rectangle(pos=self.pos, size=self.size)
        except: pass

class MainScreen(BaseScreen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    def refresh(self, search=""):
        try:
            self.ids.acc_list.clear_widgets()
            app = App.get_running_app()
            accs = app.user_data.get("accounts", {})
            for aid in accs:
                # 검색바 로직: 계정 ID 혹은 캐릭터 이름 포함 여부 확인
                found = search.lower() in aid.lower()
                if not found:
                    for s_idx in accs[aid]:
                        char_name = accs[aid][s_idx].get("info", {}).get("이름", "")
                        if search.lower() in char_name.lower():
                            found = True; break
                
                if found:
                    row = BoxLayout(size_hint_y=None, height="60dp", spacing="10dp")
                    btn = Button(text=f"ID: {aid}", background_color=(0.18, 0.49, 0.2, 1)) # 초록색
                    btn.bind(on_release=lambda x, a=aid: self.select_acc(a))
                    del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.77, 0.15, 0.15, 1)) # 빨간색
                    del_btn.bind(on_release=lambda x, a=aid: self.confirm_pop(a, "삭제", self.do_del))
                    row.add_widget(btn); row.add_widget(del_btn)
                    self.ids.acc_list.add_widget(row)
        except Exception as e: write_blackbox(f"Main Refresh Error: {e}")

    def confirm_pop(self, target, mode, callback):
        pop = Popup(title="알림", size_hint=(0.8, 0.3))
        cnt = BoxLayout(orientation='vertical', padding=10, spacing=10)
        cnt.add_widget(Label(text=f"{target}을(를) {mode}하시겠습니까?"))
        btns = BoxLayout(size_hint_y=0.4, spacing=10)
        btn_ok = Button(text="확인", on_release=lambda x: [callback(target), pop.dismiss()])
        btn_no = Button(text="취소", on_release=pop.dismiss)
        btns.add_widget(btn_ok); btns.add_widget(btn_no); cnt.add_widget(btns)
        pop.content = cnt; pop.open()

    def do_del(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh()

    def select_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def create_acc(self):
        new_id = self.ids.new_acc_id.text.strip()
        if not new_id: return
        app = App.get_running_app()
        if new_id not in app.user_data["accounts"]:
            app.user_data["accounts"][new_id] = {str(i): {"info":{}, "equip":{}, "inv":[], "photo":[], "storage":[]} for i in range(1,7)}
            app.save_data(); self.refresh(); self.ids.new_acc_id.text = ""

class CharSelectScreen(BaseScreen):
    def on_enter(self):
        try:
            self.ids.grid.clear_widgets()
            app = App.get_running_app()
            acc_data = app.user_data["accounts"].get(app.cur_acc, {})
            for i in range(1, 7):
                char_name = acc_data.get(str(i), {}).get("info", {}).get("이름", f"슬롯 {i}")
                btn = Button(text=char_name, background_color=(0.18, 0.49, 0.2, 1))
                btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
                self.ids.grid.add_widget(btn)
        except Exception as e: write_blackbox(f"CharSelect Error: {e}")

    def go_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen): pass

class InfoScreen(BaseScreen):
    def on_enter(self):
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()
            cur_data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("info", {})
            self.inputs = {}
            for group in INFO_STRUCTURE:
                row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
                for key in group:
                    box = BoxLayout(orientation='vertical', spacing=2)
                    box.add_widget(Label(text=key, font_size='12sp', size_hint_y=0.4))
                    ti = TextInput(text=str(cur_data.get(key, "")), multiline=False, halign='center', padding_y=[10,0])
                    self.inputs[key] = ti
                    box.add_widget(ti)
                    row.add_widget(box)
                self.ids.container.add_widget(row)
                self.ids.container.add_widget(BoxLayout(size_hint_y=None, height="15dp")) # 한칸 띄어주기
        except Exception as e: write_blackbox(f"Info Load Error: {e}")

    def save(self):
        try:
            app = App.get_running_app()
            new_info = {k: ti.text for k, ti in self.inputs.items()}
            app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"] = new_info
            app.save_data(); self.manager.current = 'slot_menu'
        except: pass

    def delete_all(self):
        for ti in self.inputs.values(): ti.text = ""

class EquipScreen(BaseScreen):
    def on_enter(self):
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()
            cur_data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("equip", {})
            self.inputs = {}
            for key in EQUIP_KEYS:
                row = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
                row.add_widget(Label(text=key, size_hint_x=0.3, halign='center'))
                ti = TextInput(text=str(cur_data.get(key, "")), multiline=False, halign='center', padding_y=[10,0])
                self.inputs[key] = ti
                row.add_widget(ti)
                self.ids.container.add_widget(row)
        except: pass

    def save(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"] = {k: ti.text for k, ti in self.inputs.items()}
        app.save_data(); self.manager.current = 'slot_menu'

class ListScreen(BaseScreen):
    data_type = ""
    def on_enter(self):
        self.refresh()

    def refresh(self):
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()
            items = app.user_data["accounts"][app.cur_acc][app.cur_slot].get(self.data_type, [])
            for idx, text in enumerate(items):
                row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
                btn = Button(text=text[:20] + "...", background_color=(0.2, 0.2, 0.3, 1))
                btn.bind(on_release=lambda x, t=text, i=idx: self.detail_pop(t, i))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.77, 0.15, 0.15, 1))
                del_btn.bind(on_release=lambda x, i=idx: self.delete_item(i))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.container.add_widget(row)
        except: pass

    def detail_pop(self, text, idx):
        pop = Popup(title="상세보기/수정", size_hint=(0.9, 0.6))
        cnt = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text=text, multiline=True)
        btn = Button(text="저장하시겠습니까?", size_hint_y=0.2, background_color=(0.18, 0.49, 0.2, 1))
        btn.bind(on_release=lambda x: [self.save_item(idx, ti.text), pop.dismiss()])
        cnt.add_widget(ti); cnt.add_widget(btn); pop.content=cnt; pop.open()

    def add_item(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type].append("새 데이터")
        app.save_data(); self.refresh()

    def save_item(self, idx, text):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx] = text
        app.save_data(); self.refresh()

    def delete_item(self, idx):
        app = App.get_running_app()
        del app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx]
        app.save_data(); self.refresh()

class InventoryScreen(ListScreen): data_type = "inv"
class StorageScreen(ListScreen): data_type = "storage"
class PhotoScreen(BaseScreen): pass # 사진창은 권한 및 미디어 라이브러리 연동 필요

# [5. KV 설계도: 1줄 1속성 및 중앙 정렬]
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<Label>, <Button>, <TextInput>:
    font_name: 'korean' if app.font_exists else 'Roboto'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "PristonTale Manager v112"
            size_hint_y: 0.1
            font_size: '20sp'
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 5
            TextInput:
                id: new_acc_id
                hint_text: "새 계정 ID 입력"
                multiline: False
            Button:
                text: "계정생성"
                size_hint_x: 0.3
                background_color: (0.18, 0.49, 0.2, 1)
                on_release: root.create_acc()
        TextInput:
            id: search_bar
            hint_text: "계정 또는 캐릭터 검색..."
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
                spacing: 10

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
            spacing: 15
        Button:
            text: "계정화면으로"
            size_hint_y: 0.15
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
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
            text: "슬롯선택으로"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        ScrollView:
            do_scroll_x: False
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
                text: "추가/저장"
                background_color: (0.18, 0.49, 0.2, 1)
                on_release: root.save() if hasattr(root, 'save') else root.add_item()
            Button:
                text: "전체/줄 삭제"
                background_color: (0.77, 0.15, 0.15, 1)
                on_release: root.delete_all() if hasattr(root, 'delete_all') else None
            Button:
                text: "이전으로"
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
    StorageScreen:
        name: 'storage'
    PhotoScreen:
        name: 'photo'
'''

class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""
    font_exists = os.path.exists(FONT_FILE)

    def build(self):
        self.load_data()
        return Builder.load_string(KV)

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except: self.user_data = {"accounts": {}}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except: pass

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions
                request_permissions([
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE',
                    'android.permission.MANAGE_EXTERNAL_STORAGE',
                    'android.permission.READ_MEDIA_IMAGES',
                    'android.permission.INTERNET'
                ])
            except: pass

if __name__ == "__main__":
    PristonApp().run()
