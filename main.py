import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 엔진: 물리 각인 및 시동 로그]
def get_log_path():
    p = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        with open(p, "a", encoding="utf-8") as f: pass
        return p
    except: return "BlackBox_PT.txt"

LOG_FILE = get_log_path()

def write_blackbox(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{ts}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_sentinel(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! CRITICAL STOP !!!\n{err}")
    sys.exit(1)

sys.excepthook = global_crash_sentinel
write_blackbox("Engine: v116 Zero-Error Build Initialized")

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

# [3. 제1 기본원칙: 성역 데이터 박제]
DL_PATH = "/storage/emulated/0/Download/"
DATA_FILE = os.path.join(DL_PATH, "PT_Data_v116.json")
FONT_FILE = os.path.join(DL_PATH, "font.ttf")
BG_FILE = os.path.join(DL_PATH, "bg.png")

if os.path.exists(FONT_FILE):
    try: LabelBase.register(name="korean", fn_regular=FONT_FILE)
    except: pass

# 정보창 18종 / 장비창 11종 (절대 성역)
INFO_COLS = [
    ['이름', '직위', '클랜', '레벨'],
    ['생명력', '기력', '근력'],
    ['힘', '정신력', '재능', '민첩', '건강'],
    ['명중', '공격', '방어', '흡수', '속도']
]
EQUIP_KEYS = ['한손무기', '두손무기', '갑옷', '방패', '장갑', '부츠', '암릿', '링1', '링2', '아뮬랫', '기타']

# [4. UI 컴포넌트: 논리 격리 설계]

class BaseScreen(Screen):
    """엔진 충돌 방지를 위한 독립형 배경 렌더러"""
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self.bg_color = Color(0.06, 0.08, 0.12, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if os.path.exists(BG_FILE):
            self.bg_rect.source = BG_FILE
            self.bg_color.rgba = (1, 1, 1, 1)

class MainScreen(BaseScreen):
    """1. 계정생성창: ID 생성 및 전체검색"""
    def on_enter(self):
        Clock.schedule_once(self.refresh_acc_list, 0.1)

    def refresh_acc_list(self, query=""):
        if not isinstance(query, str): query = self.ids.search_bar.text
        self.ids.acc_box.clear_widgets()
        app = App.get_running_app()
        for aid, data in app.user_data.get("accounts", {}).items():
            match = query.lower() in aid.lower()
            if not match:
                for s in data:
                    if query.lower() in data[s].get("info", {}).get("이름", "").lower():
                        match = True; break
            if match:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                btn = Button(text=f"ID: {aid}", background_color=(0.18, 0.5, 0.2, 1))
                btn.bind(on_release=lambda x, a=aid: self.enter_acc(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1))
                del_btn.bind(on_release=lambda x, a=aid: self.confirm_pop(a, "삭제", self.delete_acc))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_box.add_widget(row)

    def create_acc(self):
        aid = self.ids.new_id.text.strip()
        if not aid: return
        app = App.get_running_app()
        if aid not in app.user_data["accounts"]:
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "photo":[], "storage":[]} for i in range(1,7)}
            app.save_data(); self.refresh_acc_list(); self.ids.new_id.text = ""

    def confirm_pop(self, target, mode, callback):
        pop = Popup(title="알림", size_hint=(0.8, 0.3))
        cnt = BoxLayout(orientation='vertical', padding=15, spacing=10)
        cnt.add_widget(Label(text=f"[{target}]을 {mode}하시겠습니까?"))
        bs = BoxLayout(size_hint_y=0.4, spacing=10)
        bs.add_widget(Button(text="확인", on_release=lambda x: [callback(target), pop.dismiss()]))
        bs.add_widget(Button(text="취소", on_release=pop.dismiss))
        cnt.add_widget(bs); pop.content=cnt; pop.open()

    def delete_acc(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]; app.save_data(); self.refresh_acc_list()

    def enter_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    """2. 케릭선택창: 6개 슬롯 기반"""
    def on_enter(self):
        self.ids.slot_grid.clear_widgets()
        app = App.get_running_app()
        acc_data = app.user_data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            name = acc_data.get(str(i), {}).get("info", {}).get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=(0.2, 0.4, 0.3, 0.8))
            btn.bind(on_release=lambda x, idx=i: self.select_slot(idx))
            self.ids.slot_grid.add_widget(btn)

    def select_slot(self, idx):
        App.get_running_app().cur_slot = str(idx)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(BaseScreen): pass

class InfoScreen(BaseScreen):
    """3. 케릭정보창: 18종 목록 중앙 정렬"""
    def on_enter(self):
        self.ids.view_box.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("info", {})
        self.inputs = {}
        for group in INFO_COLS:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=5)
            for k in group:
                cell = BoxLayout(orientation='vertical', spacing=2)
                cell.add_widget(Label(text=k, font_size='11sp', size_hint_y=0.4))
                ti = TextInput(text=str(data.get(k, "")), multiline=False, halign='center')
                self.inputs[k] = ti
                cell.add_widget(ti)
                row.add_widget(cell)
            self.ids.view_box.add_widget(row)
            self.ids.view_box.add_widget(BoxLayout(size_hint_y=None, height="10dp"))

    def save(self):
        app = App.get_running_app()
        new_info = {k: v.text for k, v in self.inputs.items()}
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"] = new_info
        app.save_data(); self.manager.current = 'slot_menu'

class EquipScreen(BaseScreen):
    """4. 케릭장비창: 11종 목록 고정"""
    def on_enter(self):
        self.ids.view_box.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot].get("equip", {})
        self.inputs = {}
        for k in EQUIP_KEYS:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=10, padding=[5,0])
            row.add_widget(Label(text=k, size_hint_x=0.3))
            ti = TextInput(text=str(data.get(k, "")), multiline=False, halign='center')
            self.inputs[k] = ti
            row.add_widget(ti)
            self.ids.view_box.add_widget(row)

    def save(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"] = {k: v.text for k, v in self.inputs.items()}
        app.save_data(); self.manager.current = 'slot_menu'

class UniversalListScreen(BaseScreen):
    """5. 인벤토리 / 7. 저장보관소 공통 구조"""
    data_type = ""
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.view_box.clear_widgets()
        app = App.get_running_app()
        items = app.user_data["accounts"][app.cur_acc][app.cur_slot].get(self.data_type, [])
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
            btn = Button(text=val[:20], background_color=(0.2, 0.3, 0.5, 0.9))
            btn.bind(on_release=lambda x, i=idx, v=val: self.show_detail(i, v))
            del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1))
            del_btn.bind(on_release=lambda x, i=idx: self.delete_row(i))
            row.add_widget(btn); row.add_widget(del_btn)
            self.ids.view_box.add_widget(row)

    def show_detail(self, idx, val):
        p = Popup(title="내용 수정", size_hint=(0.9, 0.5))
        b = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text=val, multiline=True)
        btn = Button(text="저장", size_hint_y=0.3, background_color=(0.18, 0.5, 0.2, 1))
        btn.bind(on_release=lambda x: [self.save_row(idx, ti.text), p.dismiss()])
        b.add_widget(ti); b.add_widget(btn); p.content=b; p.open()

    def add_row(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type].append("새 항목")
        app.save_data(); self.refresh()

    def save_row(self, idx, val):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx] = val
        app.save_data(); self.refresh()

    def delete_row(self, idx):
        app = App.get_running_app()
        del app.user_data["accounts"][app.cur_acc][app.cur_slot][self.data_type][idx]
        app.save_data(); self.refresh()

class InventoryScreen(UniversalListScreen): data_type = "inv"
class StorageScreen(UniversalListScreen): data_type = "storage"
class PhotoScreen(BaseScreen): pass

# [5. KV 설계도: 1줄 1속성 표준화]
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
            text: "PristonTale Manager v116"
            size_hint_y: 0.1
            font_size: '22sp'
            bold: True
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            spacing: 10
            TextInput:
                id: new_id
                hint_text: "신규 ID 입력"
                multiline: False
            Button:
                text: "생성"
                size_hint_x: 0.25
                background_color: (0.18, 0.5, 0.2, 1)
                on_release: root.create_acc()
        TextInput:
            id: search_bar
            hint_text: "전체 검색 (ID/캐릭터)..."
            size_hint_y: None
            height: '50dp'
            on_text: root.refresh_acc_list(self.text)
        ScrollView:
            BoxLayout:
                id: acc_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 8

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: "캐릭터 선택"
            size_hint_y: 0.1
        GridLayout:
            id: slot_grid
            cols: 2
            spacing: 15
        Button:
            text: "메인으로"
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
            text: "뒤로가기"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: view_box
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
                background_color: (0.18, 0.5, 0.2, 1)
                on_release: root.save() if hasattr(root, 'save') else root.add_row()
            Button:
                text: "이전으로"
                on_release: root.manager.current = 'slot_menu'

ScreenManager:
    transition: NoTransition()
'''

class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""
    font_exists = os.path.exists(FONT_FILE)

    def build(self):
        self.load_data()
        self.sm = ScreenManager()
        # 시동 시퀀스 분리: 화면 등록
        screens = [
            MainScreen(name='main'), CharSelectScreen(name='char_select'),
            SlotMenuScreen(name='slot_menu'), InfoScreen(name='info'),
            EquipScreen(name='equip'), InventoryScreen(name='inv'),
            StorageScreen(name='storage'), PhotoScreen(name='photo')
        ]
        for s in screens: self.sm.add_widget(s)
        return self.sm

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
        # 최종 시동: 0.5초 뒤에 메인 화면 활성화 (교착 방지)
        Clock.schedule_once(lambda dt: setattr(self.sm, 'current', 'main'), 0.5)
        if platform == 'android':
            try:
                from android.permissions import request_permissions
                request_permissions(['android.permission.READ_EXTERNAL_STORAGE', 
                                   'android.permission.WRITE_EXTERNAL_STORAGE', 
                                   'android.permission.MANAGE_EXTERNAL_STORAGE',
                                   'android.permission.READ_MEDIA_IMAGES'])
            except: pass

if __name__ == "__main__":
    Builder.load_string(KV)
    PristonApp().run()
