import os, sys, traceback

# [최하층 네이티브 로그 시스템]
# Kivy가 로딩되기 전부터 작동하며, 화면에 안 뜨더라도 파일로 흔적을 남깁니다.
def write_native_log(msg):
    with open("PristonTale_Native_Log.txt", "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

write_native_log("--- APP START CHECK ---")

def global_exception_handler(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    write_native_log("!!! CRITICAL ERROR !!!\n" + err)
    # 화면 출력 시도
    try:
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text="🚨 블랙박스 진단 시스템 🚨", color=(1,0,0,1), bold=True))
        content.add_widget(TextInput(text=err, readonly=True))
        btn = Button(text="종료 (사진 촬영 필수)", size_hint_y=None, height="80dp")
        content.add_widget(btn)
        pop = Popup(title="Error Log", content=content, size_hint=(0.95, 0.95))
        btn.bind(on_release=lambda x: sys.exit(1))
        pop.open()
    except:
        sys.exit(1)

sys.excepthook = global_exception_handler

# [그래픽 엔진 강제 안정화 설정]
# 최신 기기에서 충돌을 일으키는 텍스처 로딩 방식을 가장 안정적인 구형 방식으로 고정
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'maxfps', '30') # S26의 초고주사율과 충돌 방지

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.text import LabelBase

# 폰트 및 환경 설정
Window.softinput_mode = "below_target"
FONT_FILE = "font.ttf"
USE_FONT = "KFont" if os.path.exists(FONT_FILE) else None
if USE_FONT:
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)

# 데이터 관리 로직
import json
class DataStore:
    FILE = "PristonTale.json"
    @staticmethod
    def load():
        try:
            if os.path.exists(DataStore.FILE):
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except: pass
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        if USE_FONT: self.font_name = USE_FONT
        self.multiline = False; self.size_hint_y = None; self.height = "65dp"
        self.halign = "center"; self.write_tab = False
        self.padding_y = [self.height/2 - 18, 0]

# --- 제1 기본원칙 사수 (7개 창 구조) ---
class MainScreen(Screen):
    def on_enter(self): 
        write_native_log("MainScreen Entered")
        self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
                btn = Button(text=aid, font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                row.add_widget(btn)
                self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def show_add(self):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="ID 입력"); c.add_widget(self.inp)
        btn = Button(text="저장", size_hint_y=None, height="60dp")
        c.add_widget(btn); pop = Popup(title="계정 추가", content=c, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(pop)); pop.open()
    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name=USE_FONT, background_color=(0, 0.5, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    groups = [['이름', '직위', '클랜', '레벨'], ['생명력', '기력', '근력'], ['힘', '정신력', '재능', '민첩', '건강'], ['명중', '공격', '방어', '흡수', '속도']]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"]
        for gp in self.groups:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp")
                row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
                inp = SInput(text=str(data.get(f, "")))
                inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp")
            row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
            inp = SInput(text=str(data.get(f, "")))
            inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"][f] = v
        App.get_running_app().save_data()

class ListEditScreen(Screen):
    mode = "inv"
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode]
        for idx, val in enumerate(items):
            btn = Button(text=val, size_hint_y=None, height="70dp", font_name=USE_FONT)
            self.ids.cont.add_widget(btn)
    def add_item(self):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].append("새 항목")
        App.get_running_app().save_data(); self.refresh()

class PhotoScreen(Screen): pass

KV = '''
ScreenManager:
    transition: FadeTransition()
    MainScreen: name: 'main'
    CharSelectScreen: name: 'char_select'
    SlotMenuScreen: name: 'slot_menu'
    InfoScreen: name: 'info'
    EquipScreen: name: 'equip'
    ListEditScreen: name: 'list_edit'
    PhotoScreen: name: 'photo'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 20; spacing: 10
        # 배경화면 일시 비활성화 (안정성 테스트용)
        Label: text: "PristonTale"; font_size: '40sp'; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '100dp'
        SInput: id: search; hint_text: "검색"; on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
        Button: text: "+ 계정 추가"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20; spacing: 10
    GridLayout: id: grid; cols: 2; spacing: 10
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 30; spacing: 15
        Button: text: "정보"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'info'
        Button: text: "장비"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'equip'
        Button: text: "인벤토리"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("inv")
        Button: text: "사진"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'photo'
        Button: text: "보관소"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("storage")
        Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'slot_menu'

<ListEditScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
    Button: text: "추가"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: root.add_item()
    Button: text: "닫기"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20
    Label: text: "사진창 (테스트 중)"; font_name: 'KFont' if USE_FONT else None
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        write_native_log("App Build Start")
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        try:
            return Builder.load_string(KV)
        except Exception as e:
            write_native_log("KV Load Error: " + str(e))
            raise e
    def save_data(self): DataStore.save(self.user_data)
    def set_mode(self, m): self.root.get_screen('list_edit').mode = m; self.root.current = 'list_edit'

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_native_log("Run Error: " + str(e))
