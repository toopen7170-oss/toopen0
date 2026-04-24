import os, sys, traceback, json

# [로그 저장 경로 설정 - 갤럭시 Download 폴더]
# 안드로이드 공용 폴더인 Download에 로그를 남겨 점주님이 바로 확인 가능하게 함
LOG_PATH = "/storage/emulated/0/Download/PristonTale_BlackBox_Log.txt"

def write_log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[INFO] {msg}")
            f.flush() # 메모리에 머물지 않고 즉시 파일로 기록
            os.fsync(f.fileno()) # OS 수준에서 강제 쓰기 실행
    except:
        # 권한 문제로 Download 폴더 실패 시 내부 저장소에 시도
        try:
            with open("Internal_Log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[INTERNAL] {msg}")
        except: pass

write_log("=== 앱 부팅 시퀀스 시작 ===")

def global_exception_handler(exctype, value, tb):
    err_lines = traceback.format_exception(exctype, value, tb)
    full_err_msg = "".join(err_lines)
    
    # 팅기기 직전 에러 위치와 원인을 무조건 기록 (빈 파일 방지)
    write_log("!!! 치명적 오류 발생 !!!")
    write_log(full_err_msg)
    
    # 화면 출력 시도 (Kivy 엔진이 살아있을 경우)
    try:
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text="🚨 블랙박스 오류 진단 🚨", color=(1,0,0,1), size_hint_y=None, height="50dp"))
        content.add_widget(TextInput(text=full_err_msg, readonly=True))
        btn = Button(text="확인 후 종료", size_hint_y=None, height="70dp")
        content.add_widget(btn)
        pop = Popup(title="BlackBox Report", content=content, size_hint=(0.9, 0.9), auto_dismiss=False)
        btn.bind(on_release=lambda x: sys.exit(1))
        pop.open()
    except:
        sys.exit(1)

sys.excepthook = global_exception_handler

# [그래픽 엔진 세이프 모드]
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'maxfps', '30')

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

# 환경 설정
Window.softinput_mode = "below_target"
FONT_FILE = "font.ttf"
USE_FONT = "KFont" if os.path.exists(FONT_FILE) else None
if USE_FONT:
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)

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
        write_log("현재 위치: [1번 계정생성창(MainScreen)] 진입")
        self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
                btn = Button(text=aid, font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                row.add_widget(btn); self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def show_add(self):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="ID 입력"); c.add_widget(self.inp)
        btn = Button(text="저장", size_hint_y=None, height="60dp")
        c.add_widget(btn); pop = Popup(title="추가", content=c, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(pop)); pop.open()
    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        write_log("현재 위치: [2번 케릭선택창(CharSelect)] 진입")
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name=USE_FONT, background_color=(0, 0.5, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen):
    def on_enter(self): write_log("현재 위치: [슬롯 메뉴창] 진입")

class InfoScreen(Screen): # 3. 케릭정보창 (18개 목록)
    groups = [['이름', '직위', '클랜', '레벨'], ['생명력', '기력', '근력'], ['힘', '정신력', '재능', '민첩', '건강'], ['명중', '공격', '방어', '흡수', '속도']]
    def on_enter(self):
        write_log("현재 위치: [3번 케릭정보창] 목록 생성 시작")
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

class EquipScreen(Screen): # 4. 케릭장비창 (11개 목록)
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        write_log("현재 위치: [4번 케릭장비창] 목록 생성 시작")
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
    def on_enter(self): 
        write_log(f"현재 위치: [{self.mode} 리스트창] 진입")
        self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode]
        for idx, val in enumerate(items):
            btn = Button(text=val, size_hint_y=None, height="70dp", font_name=USE_FONT)
            self.ids.cont.add_widget(btn)
    def add_item(self):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].append("새 항목")
        App.get_running_app().save_data(); self.refresh()

class PhotoScreen(Screen):
    def on_enter(self): write_log("현재 위치: [사진선택창] 진입")

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
    Label: text: "사진 관리"; font_name: 'KFont' if USE_FONT else None
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        write_log("App Build 과정 시작")
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        return Builder.load_string(KV)
    def save_data(self): DataStore.save(self.user_data)
    def set_mode(self, m): self.root.get_screen('list_edit').mode = m; self.root.current = 'list_edit'

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_log(f"런타임 치명적 오류: {str(e)}")
