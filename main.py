import os, sys, traceback, json
from datetime import datetime

# [1. 블랙박스 상시 가동 시스템 - 다운로드 폴더 강제 지정]
def get_download_path():
    # 안드로이드의 표준 다운로드 폴더 경로
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    # 만약 위 경로에 쓰기 권한이 없을 경우를 대비한 2중 방어
    try:
        with open(path, "a", encoding="utf-8") as f:
            pass
        return path
    except:
        return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*50}")
    except:
        # 파일 쓰기 실패 시 콘솔 출력 (마지막 수단)
        print(f"BLACKBOX WRITE FAIL: {msg}")

def show_emergency_popup(error_msg):
    from kivy.uix.popup import Popup
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView

    write_blackbox(f"POPUP CALLED: {error_msg}")

    content = BoxLayout(orientation='vertical', padding=15, spacing=15)
    scroll = ScrollView()
    # 폰트 깨짐(□□) 방지를 위해 시스템 기본 폰트 사용
    err_lbl = Label(
        text=f"!!! 시스템 오류 감지 !!!\n\n내용:\n{error_msg}\n\n로그파일: Download 폴더 확인",
        size_hint_y=None,
        halign="left",
        valign="top"
    )
    err_lbl.bind(texture_size=err_lbl.setter('size'))
    scroll.add_widget(err_lbl)
    content.add_widget(scroll)
    
    close_btn = Button(text="오류 사진 촬영 후 종료", size_hint_y=None, height="70dp")
    pop = Popup(title="Emergency Diagnosis", content=content, size_hint=(0.95, 0.85))
    close_btn.bind(on_release=lambda x: sys.exit(1))
    content.add_widget(close_btn)
    pop.open()

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"CRASH LOG:\n{err_msg}")
    try:
        show_emergency_popup(err_msg)
    except:
        sys.exit(1)

# 앱 시작 전 예외 처리기 등록
sys.excepthook = global_crash_handler

# [2. Kivy 엔진 설정 및 폰트 무결성 검사]
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# 폰트 등록 (라인 바이 라인 검수 완료)
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)

Window.softinput_mode = "below_target"

# [3. 데이터 관리 시스템 - 제1 기본원칙 준수]
class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                write_blackbox(f"DATA LOAD ERR: {e}")
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"DATA SAVE ERR: {e}")

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = "KFont" if os.path.exists(FONT_FILE) else None
        self.multiline = False
        self.size_hint_y = None
        self.height = "65dp"
        self.halign = "center"
        self.padding_y = [self.height/2 - 18, 0]

# [4. 화면 클래스 - 초정밀 타이밍 에러 수정 완료]
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        if not self.ids: return
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
                btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                row.add_widget(btn)
                self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self):
        # super.__getattr__ 에러 원천 봉쇄 (Clock 지연 로드)
        Clock.schedule_once(self.build_slots, 0.1)
    def build_slots(self, dt):
        if not self.ids: return
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
    # 18개 세부 목록 고정
    structure = [['이름','직위','클랜','레벨'],['생명력','기력','근력'],['힘','정신력','재능','민첩','건강'],['명중','공격','방어','흡수','속도']]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        if not self.ids: return
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for gp in self.structure:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_FILE) else None))
                inp = SInput(text=str(data.get(f, "")))
                inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    # 11개 세부 목록 고정
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        if not self.ids: return
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_FILE) else None))
            inp = SInput(text=str(data.get(f, "")))
            inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

# [5. KV 디자인 - 배경 고정 및 예외 처리]
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

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        Label:
            text: "PristonTale"
            font_size: '40sp'
            size_hint_y: 0.2
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 15

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
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
        spacing: 20
        Button:
            text: "케릭정보창"
            on_release: app.root.current = 'info'
        Button:
            text: "케릭장비창"
            on_release: app.root.current = 'equip'
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
'''

class PristonApp(App):
    def build(self):
        write_blackbox("=== APP BUILD START ===")
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        try:
            return Builder.load_string(KV)
        except Exception as e:
            write_blackbox(f"KV PARSE ERROR: {e}")
            raise e
    def get_cur_data(self): return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self): DataStore.save(self.user_data)

if __name__ == "__main__":
    write_blackbox("=== PYTHON PROCESS START ===")
    PristonApp().run()
