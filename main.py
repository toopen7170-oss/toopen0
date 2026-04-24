import os, sys, traceback, json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [블랙박스 및 환경 설정]
LOG_PATH = "/storage/emulated/0/Download/PristonTale_BlackBox_Log.txt"
def write_log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[INFO] {msg}")
    except: pass

# 폰트 등록 (한글 깨짐 방지)
FONT_NAME = "font.ttf"
if os.path.exists(FONT_NAME):
    LabelBase.register(name="KFont", fn_regular=FONT_NAME)

# 윈도우 키보드 대응
Window.softinput_mode = "below_target"

class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            with open(DataStore.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"accounts": {}}
    @staticmethod
    def save(data):
        with open(DataStore.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# [커스텀 위젯 - 상하 중앙 정렬 및 폰트 적용]
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = "KFont" if os.path.exists(FONT_NAME) else None
        self.multiline = False
        self.size_hint_y = None
        self.height = "60dp"
        self.halign = "center"
        self.padding_y = [self.height/2 - 18, 0] # 중앙 정렬 계산

class ConfirmPopup(Popup):
    def __init__(self, text, on_confirm, **kw):
        super().__init__(**kw)
        self.title = "확인"
        self.size_hint = (0.8, 0.3)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=text, font_name="KFont" if os.path.exists(FONT_NAME) else None))
        btns = BoxLayout(spacing=10, size_hint_y=None, height="50dp")
        yes = Button(text="확인", background_color=get_color_from_hex("#2E7D32"))
        no = Button(text="취소", background_color=get_color_from_hex("#C62828"))
        yes.bind(on_release=lambda x: [on_confirm(), self.dismiss()])
        no.bind(on_release=self.dismiss)
        btns.add_widget(yes); btns.add_widget(no)
        layout.add_widget(btns); self.content = layout

# [화면 클래스 정의]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=5)
                btn = Button(text=aid, font_name="KFont" if os.path.exists(FONT_NAME) else None, background_color=get_color_from_hex("#2E7D32"))
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
                del_btn.bind(on_release=lambda x, a=aid: ConfirmPopup(f"'{a}'를 삭제하시겠습니까?", lambda: self.delete_acc(a)).open())
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)
    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def add_acc(self):
        aid = self.ids.new_acc_name.text.strip()
        if aid:
            ConfirmPopup(f"'{aid}'를 저장하시겠습니까?", lambda: self.save_acc(aid)).open()
    def save_acc(self, aid):
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
        app.save_data(); self.ids.new_acc_name.text = ""; self.refresh()
    def delete_acc(self, aid):
        del App.get_running_app().user_data["accounts"][aid]
        App.get_running_app().save_data(); self.refresh()

class CharSelectScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.grid.clear_widgets()
        acc_data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc_data[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name="KFont" if os.path.exists(FONT_NAME) else None, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 제1 기본원칙 18개 목록 고정
    structure = [
        ['이름', '직위', '클랜', '레벨'],
        ['생명력', '기력', '근력'],
        ['힘', '정신력', '재능', '민첩', '건강'],
        ['명중', '공격', '방어', '흡수', '속도']
    ]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for group in self.structure:
            for field in group:
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                lbl = Label(text=field, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_NAME) else None)
                inp = SInput(text=str(data.get(field, "")))
                inp.bind(text=lambda inst, v, f=field: self.auto_save(f, v))
                row.add_widget(lbl); row.add_widget(inp)
                self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(BoxLayout(size_hint_y=None, height="30dp")) # 한 칸 띄우기 (투명)
    def auto_save(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()
    def clear_all(self):
        ConfirmPopup("정보창 전체 내용을 삭제하시겠습니까?", self.do_clear).open()
    def do_clear(self):
        App.get_running_app().get_cur_data()["info"] = {}
        App.get_running_app().save_data(); self.build_ui(0)

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
            lbl = Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_NAME) else None)
            inp = SInput(text=str(data.get(f, "")))
            inp.bind(text=lambda inst, v, f=f: self.auto_save(f, v))
            row.add_widget(lbl); row.add_widget(inp)
            self.ids.cont.add_widget(row)
    def auto_save(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

class ListScreen(Screen):
    mode = "inv" # or "storage"
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().get_cur_data()[self.mode]
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=5)
            inp = SInput(text=val)
            inp.bind(text=lambda inst, v, i=idx: self.update_item(i, v))
            del_btn = Button(text="X", size_hint_x=0.15, background_color=get_color_from_hex("#C62828"))
            del_btn.bind(on_release=lambda x, i=idx: ConfirmPopup("삭제하시겠습니까?", lambda: self.delete_item(i)).open())
            row.add_widget(inp); row.add_widget(del_btn)
            self.ids.cont.add_widget(row)
    def add_item(self):
        App.get_running_app().get_cur_data()[self.mode].append("")
        App.get_running_app().save_data(); self.refresh()
    def update_item(self, i, v):
        App.get_running_app().get_cur_data()[self.mode][i] = v
        App.get_running_app().save_data()
    def delete_item(self, i):
        App.get_running_app().get_cur_data()[self.mode].pop(i)
        App.get_running_app().save_data(); self.refresh()

class PhotoScreen(Screen): pass

# [무결성 KV 설계도]
KV = '''
#:import exists os.path.exists
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Screen>:
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            source: 'bg.png' if exists('bg.png') else None
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
    ListScreen:
        name: 'list_edit'
    PhotoScreen:
        name: 'photo'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "PristonTale"
            font_size: '45sp'
            font_name: 'KFont' if exists('font.ttf') else None
            size_hint_y: None
            height: '100dp'
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: 10
            SInput:
                id: new_acc_name
                hint_text: "계정 ID 입력"
            Button:
                text: "저장"
                size_hint_x: 0.3
                background_color: 0, 0.6, 0.3, 1
                on_release: root.add_acc()
        SInput:
            id: search_bar
            hint_text: "계정 전체 검색"
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
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "뒤로가기"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        Button:
            text: "케릭정보창"
            on_release: app.root.current = 'info'
        Button:
            text: "케릭장비창"
            on_release: app.root.current = 'equip'
        Button:
            text: "인벤토리창"
            on_release: app.set_list_mode("inv")
        Button:
            text: "사진선택창"
            on_release: app.root.current = 'photo'
        Button:
            text: "저장보관소"
            on_release: app.set_list_mode("storage")
        Button:
            text: "뒤로가기"
            size_hint_y: None
            height: '70dp'
            background_color: 0.5, 0.5, 0.5, 1
            on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        ScrollView:
            BoxLayout:
                id: cont
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '70dp'
            spacing: 10
            Button:
                text: "전체삭제"
                background_color: 0.8, 0.2, 0.2, 1
                on_release: root.clear_all() if hasattr(root, 'clear_all') else None
            Button:
                text: "뒤로가기"
                on_release: app.root.current = 'slot_menu'

<ListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        ScrollView:
            BoxLayout:
                id: cont
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '70dp'
            spacing: 10
            Button:
                text: "추가"
                background_color: 0, 0.6, 0.3, 1
                on_release: root.add_item()
            Button:
                text: "닫기"
                on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "사진 선택 (권한 필요)"
            font_name: 'KFont' if exists('font.ttf') else None
        Button:
            text: "갤러리 열기"
            size_hint_y: None
            height: '100dp'
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'slot_menu'

<Button>:
    font_name: 'KFont' if exists('font.ttf') else None
    font_size: '18sp'
    background_normal: ''
    background_color: 0.1, 0.4, 0.6, 1
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        return Builder.load_string(KV)
    
    def get_cur_data(self):
        return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    
    def save_data(self):
        DataStore.save(self.user_data)
        
    def set_list_mode(self, m):
        screen = self.root.get_screen('list_edit')
        screen.mode = m
        self.root.current = 'list_edit'

if __name__ == "__main__":
    PristonApp().run()
