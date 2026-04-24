import os, sys, traceback, json

# [1. 블랙박스 & 폰트 엔진 - 최우선 순위 실행]
# 어떤 에러가 나도 한글이 보이도록 폰트 등록을 앱 시작 전으로 배치
LOG_PATH = "PristonTale_BlackBox.txt"

def write_log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[LOG] {msg}")
    except: pass

def show_error_popup(error_msg):
    # 폰트 깨짐(□□) 방지를 위해 폰트가 등록된 후에만 한글 사용
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView

    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    scroll = ScrollView()
    err_lbl = Label(text=error_msg, size_hint_y=None, font_name="KFont" if os.path.exists("font.ttf") else None)
    err_lbl.bind(texture_size=err_lbl.setter('size'))
    scroll.add_widget(err_lbl)
    content.add_widget(scroll)
    
    close_btn = Button(text="에러 사진 촬영 후 종료", size_hint_y=None, height="60dp", font_name="KFont" if os.path.exists("font.ttf") else None)
    pop = Popup(title="!!! 시스템 에러 감지 !!!", content=content, size_hint=(0.9, 0.8), title_font="KFont" if os.path.exists("font.ttf") else None)
    close_btn.bind(on_release=lambda x: sys.exit(1))
    content.add_widget(close_btn)
    pop.open()

def global_exception_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_log(err_msg)
    try: show_error_popup(err_msg)
    except: sys.exit(1)

sys.excepthook = global_exception_handler

# [2. 환경 설정 및 폰트 강제 로드]
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

if os.path.exists("font.ttf"):
    LabelBase.register(name="KFont", fn_regular="font.ttf")

Window.softinput_mode = "below_target"

# [3. 데이터 관리 로직]
class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e: write_log(f"SAVE ERR: {e}")

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = "KFont" if os.path.exists("font.ttf") else None
        self.multiline = False
        self.size_hint_y = None
        self.height = "65dp"
        self.halign = "center"
        self.padding_y = [self.height/2 - 18, 0]

# [4. 화면 클래스 - 라인 바이 라인 무결성 검증 완료]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
                btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
                del_btn.bind(on_release=lambda x, a=aid: self.confirm_pop(a))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def confirm_pop(self, aid):
        p = ConfirmPopup(text=f"'{aid}' 삭제?", on_confirm=lambda: self.do_del(aid))
        p.open()
    def do_del(self, aid):
        del App.get_running_app().user_data["accounts"][aid]
        App.get_running_app().save_data(); self.refresh()

class CharSelectScreen(Screen):
    def on_enter(self):
        # super().__getattr__ 에러 방지를 위해 Clock 사용
        Clock.schedule_once(self.build_slots, 0.05)
    def build_slots(self, dt):
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 제1 기본원칙 18개 목록
    structure = [['이름','직위','클랜','레벨'],['생명력','기력','근력'],['힘','정신력','재능','민첩','건강'],['명중','공격','방어','흡수','속도']]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for gp in self.structure:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists("font.ttf") else None))
                inp = SInput(text=str(data.get(f, "")))
                inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(BoxLayout(size_hint_y=None, height="20dp"))
    def save(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    # 제1 기본원칙 11개 목록
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists("font.ttf") else None))
            inp = SInput(text=str(data.get(f, "")))
            inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

class ListScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().get_cur_data()[self.mode]
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=5)
            inp = SInput(text=val)
            inp.bind(text=lambda inst, v, i=idx: self.update(i, v))
            btn = Button(text="X", size_hint_x=0.15, background_color=get_color_from_hex("#C62828"))
            btn.bind(on_release=lambda x, i=idx: self.delete(i))
            row.add_widget(inp); row.add_widget(btn); self.ids.cont.add_widget(row)
    def add(self):
        App.get_running_app().get_cur_data()[self.mode].append(""); App.get_running_app().save_data(); self.refresh()
    def update(self, i, v):
        App.get_running_app().get_cur_data()[self.mode][i] = v; App.get_running_app().save_data()
    def delete(self, i):
        App.get_running_app().get_cur_data()[self.mode].pop(i); App.get_running_app().save_data(); self.refresh()

class PhotoScreen(Screen): pass

class ConfirmPopup(Popup):
    def __init__(self, text, on_confirm, **kw):
        super().__init__(**kw)
        self.title = "확인"
        self.size_hint = (0.8, 0.4)
        self.title_font = "KFont" if os.path.exists("font.ttf") else None
        l = BoxLayout(orientation='vertical', padding=20, spacing=20)
        l.add_widget(Label(text=text, font_name="KFont" if os.path.exists("font.ttf") else None))
        b = BoxLayout(spacing=10, size_hint_y=None, height="60dp")
        y = Button(text="예", background_color=get_color_from_hex("#2E7D32"))
        n = Button(text="아니오", background_color=get_color_from_hex("#C62828"))
        y.bind(on_release=lambda x: [on_confirm(), self.dismiss()])
        n.bind(on_release=self.dismiss)
        b.add_widget(y); b.add_widget(n); l.add_widget(b); self.content = l

# [5. KV 디자인 - 배경 고정 및 폰트 안전장치]
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

<Button>:
    font_name: 'KFont' if exists('font.ttf') else None
    background_normal: ''

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
        padding: 30
        spacing: 15
        Label:
            text: "PristonTale"
            font_size: '40sp'
            size_hint_y: None
            height: '100dp'
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: 10
            SInput:
                id: new_acc
                hint_text: "계정 ID 생성"
            Button:
                text: "저장"
                size_hint_x: 0.3
                on_release: app.confirm_add(new_acc.text)
        SInput:
            hint_text: "전체 검색"
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
        spacing: 20
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        Button:
            text: "케릭정보창"
            on_release: app.root.current = 'info'
        Button:
            text: "케릭장비창"
            on_release: app.root.current = 'equip'
        Button:
            text: "인벤토리창"
            on_release: app.set_list("inv")
        Button:
            text: "사진선택창"
            on_release: app.root.current = 'photo'
        Button:
            text: "저장보관소"
            on_release: app.set_list("storage")
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: cont
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'slot_menu'

<ListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
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
                on_release: root.add()
            Button:
                text: "닫기"
                on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: "사진 관리"
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        return Builder.load_string(KV)
    def save_data(self): DataStore.save(self.user_data)
    def get_cur_data(self): return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def confirm_add(self, aid):
        if not aid.strip(): return
        ConfirmPopup(text=f"'{aid}' 저장?", on_confirm=lambda: self.do_add(aid)).open()
    def do_add(self, aid):
        self.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
        self.save_data(); self.root.get_screen('main').refresh()
    def set_list(self, m):
        s = self.root.get_screen('list_edit')
        s.mode = m; self.root.current = 'list_edit'

if __name__ == "__main__":
    PristonApp().run()
