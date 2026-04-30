import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 시스템: 물리 각인 및 초기화 보호]
def get_log_path():
    p = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        with open(p, "a", encoding="utf-8") as f: pass
        return p
    except: return "BlackBox_Internal.txt"

LOG_FILE = get_log_path()

def write_blackbox(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{ts}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 강제 각인
    except: pass

def crash_sentinel(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! SYSTEM CRASH DETECTED !!!\n{err}")
    sys.exit(1)

sys.excepthook = crash_sentinel

# [2. Kivy 엔진 선제 봉쇄 및 초기화]
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

# [3. 경로 및 제1원칙 데이터 박제]
DL_PATH = "/storage/emulated/0/Download/"
DATA_PATH = os.path.join(DL_PATH, "PT_Data_v113.json")
FONT_PATH = os.path.join(DL_PATH, "font.ttf")
BG_PATH = os.path.join(DL_PATH, "bg.png")

# 폰트 등록
if os.path.exists(FONT_PATH):
    try: LabelBase.register(name="korean", fn_regular=FONT_PATH)
    except: pass

# 케릭정보 18종 / 케릭장비 11종 (절대 고정)
INFO_COLS = [
    ['이름', '직위', '클랜', '레벨'],
    ['생명력', '기력', '근력'],
    ['힘', '정신력', '재능', '민첩', '건강'],
    ['명중', '공격', '방어', '흡수', '속도']
]
EQUIP_LIST = ['한손무기', '두손무기', '갑옷', '방패', '장갑', '부츠', '암릿', '링1', '링2', '아뮬랫', '기타']

# [4. UI 컴포넌트: 초기화된 뼈대]

class BaseScreen(Screen):
    """모든 창의 근간: 배경화면 자가 치유 및 투명 레이아웃 적용"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(size=self._apply_bg, pos=self._apply_bg)

    def _apply_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if os.path.exists(BG_PATH):
                Color(1, 1, 1, 1)
                Rectangle(source=BG_PATH, pos=self.pos, size=self.size)
            else:
                Color(0.05, 0.08, 0.15, 1) # 권한 거부 시 대비용 남색 배경
                Rectangle(pos=self.pos, size=self.size)

class MainScreen(BaseScreen):
    """1. 계정생성창: ID 생성 및 전체검색바"""
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.1)

    def refresh_list(self, query=""):
        self.ids.acc_container.clear_widgets()
        app = App.get_running_app()
        for aid, data in app.user_data.get("accounts", {}).items():
            # 계정 ID 검색 또는 캐릭터 이름 검색
            show = query.lower() in aid.lower()
            if not show:
                for s in data:
                    if query.lower() in data[s].get("info", {}).get("이름", "").lower():
                        show = True; break
            
            if show:
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10, padding=[5,5])
                btn = Button(text=f"ID: {aid}", background_color=(0.18, 0.49, 0.2, 0.9), font_size='16sp')
                btn.bind(on_release=lambda x, a=aid: self.enter_acc(a))
                del_btn = Button(text="삭제", size_hint_x=0.25, background_color=(0.77, 0.15, 0.15, 1))
                del_btn.bind(on_release=lambda x, a=aid: self.ask_delete(a))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_container.add_widget(row)

    def create_acc(self):
        aid = self.ids.acc_input.text.strip()
        if not aid: return
        app = App.get_running_app()
        if aid not in app.user_data["accounts"]:
            # 계정 당 6개 슬롯 초기화
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "photo":[], "storage":[]} for i in range(1,7)}
            app.save_data(); self.refresh_list(); self.ids.acc_input.text = ""

    def ask_delete(self, aid):
        pop = Popup(title="경고", size_hint=(0.8, 0.35))
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        box.add_widget(Label(text=f"계정 [{aid}]를\n삭제하시겠습니까?"))
        btn_box = BoxLayout(size_hint_y=0.5, spacing=10)
        btn_box.add_widget(Button(text="삭제(빨강)", background_color=(0.77, 0.15, 0.15, 1), 
                                  on_release=lambda x: [self.do_delete(aid), pop.dismiss()]))
        btn_box.add_widget(Button(text="취소", on_release=pop.dismiss))
        box.add_widget(btn_box); pop.content = box; pop.open()

    def do_delete(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh_list()

    def enter_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    """2. 케릭선택창: 6개 슬롯 기반 구조"""
    def on_enter(self):
        self.ids.slot_grid.clear_widgets()
        app = App.get_running_app()
        acc_data = app.user_data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            name = acc_data.get(str(i), {}).get("info", {}).get("이름", f"비어있음 (슬롯 {i})")
            btn = Button(text=name, background_color=(0.18, 0.49, 0.2, 0.8), font_size='15sp')
            btn.bind(on_release=lambda x, idx=i: self.select_slot(idx))
            self.ids.slot_grid.add_widget(btn)

    def select_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen):
    """슬롯 진입 후 5대 기능 버튼 창"""
    pass

class InfoScreen(BaseScreen):
    """3. 케릭정보창: 18종 세부 목록 고정"""
    def on_enter(self):
        self.ids.scroll_box.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("info", {})
        self.inputs = {}
        for group in INFO_COLS:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=8)
            for key in group:
                item_box = BoxLayout(orientation='vertical', spacing=2)
                item_box.add_widget(Label(text=key, font_size='11sp', size_hint_y=0.4))
                ti = TextInput(text=str(data.get(key, "")), multiline=False, halign='center', 
                               background_color=(1,1,1,0.1), foreground_color=(1,1,1,1))
                self.inputs[key] = ti
                item_box.add_widget(ti)
                row.add_widget(item_box)
            self.ids.scroll_box.add_widget(row)
            self.ids.scroll_box.add_widget(BoxLayout(size_hint_y=None, height="10dp")) # 투명 간격

    def save(self):
        app = App.get_running_app()
        new_info = {k: ti.text for k, ti in self.inputs.items()}
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"] = new_info
        app.save_data()
        self.manager.current = 'slot_menu'

    def clear_all(self):
        for ti in self.inputs.values(): ti.text = ""

class EquipScreen(BaseScreen):
    """4. 케릭장비창: 11종 세부 목록 고정"""
    def on_enter(self):
        self.ids.scroll_box.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("equip", {})
        self.inputs = {}
        for key in EQUIP_LIST:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=15, padding=[10,0])
            row.add_widget(Label(text=key, size_hint_x=0.3, halign='center'))
            ti = TextInput(text=str(data.get(key, "")), multiline=False, halign='center')
            self.inputs[key] = ti
            row.add_widget(ti)
            self.ids.scroll_box.add_widget(row)

    def save(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"] = {k: ti.text for k, ti in self.inputs.items()}
        app.save_data()
        self.manager.current = 'slot_menu'

class ListManagerScreen(BaseScreen):
    """5. 인벤토리 / 7. 저장보관소 공통 구조"""
    data_type = ""
    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.ids.scroll_box.clear_widgets()
        app = App.get_running_app()
        items = app.user_data["accounts"][app.cur_acc][app.cur_slot].get(self.data_type, [])
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
            btn = Button(text=val[:25], background_color=(0.2, 0.3, 0.4, 0.8))
            btn.bind(on_release=lambda x, i=idx, v=val: self.open_detail(i, v))
            del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.77, 0.15, 0.15, 1))
            del_btn.bind(on_release=lambda x, i=idx: self.delete_row(i))
            row.add_widget(btn); row.add_widget(del_btn)
            self.ids.scroll_box.add_widget(row)

    def open_detail(self, idx, val):
        pop = Popup(title="내용 수정", size_hint=(0.9, 0.5))
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text=val, multiline=True)
        btn = Button(text="저장하시겠습니까?", size_hint_y=0.25, background_color=(0.18, 0.49, 0.2, 1))
        btn.bind(on_release=lambda x: [self.save_row(idx, ti.text), pop.dismiss()])
        box.add_widget(ti); box.add_widget(btn); pop.content = box; pop.open()

    def save_row(self, idx, text):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx] = text
        app.save_data(); self.refresh()

    def add_row(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type].append("새 데이터 입력")
        app.save_data(); self.refresh()

    def delete_row(self, idx):
        app = App.get_running_app()
        del app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx]
        app.save_data(); self.refresh()

class InventoryScreen(ListManagerScreen): data_type = "inv"
class StorageScreen(ListManagerScreen): data_type = "storage"
class PhotoScreen(BaseScreen): 
    """6. 사진선택창: 다중 선택 및 권한 베이스"""
    pass

# [5. KV 설계도: 물리 격리 및 1줄 1속성]
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<Label>, <Button>, <TextInput>:
    font_name: 'korean' if app.font_exists else 'Roboto'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 12
        Label:
            text: "PristonTale Manager v113"
            size_hint_y: 0.08
            font_size: '22sp'
            bold: True
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            spacing: 8
            TextInput:
                id: acc_input
                hint_text: "신규 계정 ID"
                multiline: False
            Button:
                text: "생성"
                size_hint_x: 0.25
                background_color: (0.18, 0.49, 0.2, 1)
                on_release: root.create_acc()
        TextInput:
            hint_text: "전체 검색 (계정/캐릭터)..."
            size_hint_y: None
            height: '50dp'
            on_text: root.refresh_list(self.text)
        ScrollView:
            BoxLayout:
                id: acc_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 8

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 25
        spacing: 20
        Label:
            text: "캐릭터 슬롯 (1~6)"
            size_hint_y: 0.1
        GridLayout:
            id: slot_grid
            cols: 2
            spacing: 15
        Button:
            text: "메인으로 돌아가기"
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
            text: "이전 슬롯 화면"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: scroll_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            padding: 5
            Button:
                text: "저장/추가"
                background_color: (0.18, 0.49, 0.2, 1)
                on_release: root.save() if hasattr(root, 'save') else root.add_row()
            Button:
                text: "삭제"
                background_color: (0.77, 0.15, 0.15, 1)
                on_release: root.clear_all() if hasattr(root, 'clear_all') else None
            Button:
                text: "뒤로"
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
    font_exists = os.path.exists(FONT_PATH)

    def build(self):
        self.load_data()
        return Builder.load_string(KV)

    def load_data(self):
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except: self.user_data = {"accounts": {}}

    def save_data(self):
        try:
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e: write_blackbox(f"Save Error: {e}")

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions
                request_permissions([
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE',
                    'android.permission.MANAGE_EXTERNAL_STORAGE',
                    'android.permission.READ_MEDIA_IMAGES'
                ])
            except: pass

if __name__ == "__main__":
    PristonApp().run()
