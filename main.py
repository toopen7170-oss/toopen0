import os, sys, traceback, json, time
from datetime import datetime

# [블랙박스 엔진: 다운로드 폴더 물리 각인 시스템 - 절대 보존 영역]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        if not os.path.exists(os.path.dirname(path)): return "PristonTale_BlackBox.txt"
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except:
        return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 저장 강제 명령 (팅김 대비 핵심)
    except:
        pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! CRASH DETECTED !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> PYTHON ENGINE START <<<")

# [Kivy 설정 및 그래픽 안정화]
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'maxfps', '30')

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

# 폰트 안전 등록
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)

# [데이터 매니저]
class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                write_blackbox(f"DATA LOAD ERROR: {e}")
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            write_blackbox(f"DATA SAVE ERROR: {e}")

# [화면 클래스 - 0.5초 지연 로딩]
class MainScreen(Screen):
    def on_enter(self):
        write_blackbox("MainScreen on_enter")
        Clock.schedule_once(self.deferred_refresh, 0.5)

    def deferred_refresh(self, dt):
        try:
            if not self.ids: return
            self.ids.acc_list.clear_widgets()
            data = App.get_running_app().user_data.get("accounts", {})
            for aid in data:
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
                btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                row.add_widget(btn)
                self.ids.acc_list.add_widget(row)
            write_blackbox("MainScreen UI Build Done")
        except Exception as e:
            write_blackbox(f"MAIN UI ERROR: {e}")

    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build_slots, 0.2)
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
    structure = [['이름','직위','클랜','레벨'],['생명력','기력','근력'],['힘','정신력','재능','민첩','건강'],['명중','공격','방어','흡수','속도']]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.2)
    def build_ui(self, dt):
        if not self.ids: return
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for gp in self.structure:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_FILE) else None))
                inp = TextInput(text=str(data.get(f, "")), multiline=False, font_name="KFont" if os.path.exists(FONT_FILE) else None)
                inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.2)
    def build_ui(self, dt):
        if not self.ids: return
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists(FONT_FILE) else None))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, font_name="KFont" if os.path.exists(FONT_FILE) else None)
            inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

# [KV 디자인 - FadeTransition 임포트 추가 완료]
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

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        Label:
            text: "PristonTale"
            font_size: '40sp'
            size_hint_y: 0.2
            font_name: 'KFont' if exists('font.ttf') else None
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 15

<CharSelectScreen>, <SlotMenuScreen>, <InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        ScrollView:
            BoxLayout:
                id: cont
                id: grid
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "뒤로"
            size_hint_y: None
            height: '70dp'
            font_name: 'KFont' if exists('font.ttf') else None
            on_release: app.root.current = 'main' if root.name == 'char_select' else 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        write_blackbox("--- APP BUILD START ---")
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
    try:
        write_blackbox("=== SYSTEM STARTING ===")
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"RUNTIME FATAL: {e}")
