import os, json
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

# [환경 방어] 갤럭시 S26 울트라 최적화 및 폰트 설정
Window.softinput_mode = "below_target"
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
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
        self.font_name = "KFont" if os.path.exists(FONT_FILE) else None
        self.multiline, self.size_hint_y, self.height = False, None, "55dp"
        self.halign = "center"

# --- 화면 로직 (절대 규칙: 총 6개 창) ---

class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        for aid in data.keys():
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                btn = Button(text=f"계정: {aid}", font_name="KFont", background_color=(0, 0.5, 0.2, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1), font_name="KFont")
                del_btn.bind(on_release=lambda x, a=aid: App.get_running_app().confirm_pop(f"[{a}] 삭제?", lambda: self.do_del(a)))
                row.add_widget(btn); row.add_widget(del_btn); self.ids.acc_list.add_widget(row)
    def go_next(self, aid): App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'
    def do_del(self, aid): app = App.get_running_app(); del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
    def show_add(self):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="새 계정 ID")
        btn = Button(text="생성", font_name="KFont", background_color=(0, 0.5, 0.2, 1), size_hint_y=None, height="55dp")
        c.add_widget(self.inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(pop)); pop.open()
    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        acc_data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc_data[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name="KFont", background_color=(0, 0.4, 0.3, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i): App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 절대 규칙: 세부 목록 18개 고정
    fields = [['이름', '직위', '클랜', '레벨'], ['생명력', '기력', '근력'], ['힘', '정신력', '재능', '민첩', '건강'], ['명중', '공격', '방어', '흡수', '속도']]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"]
        for group in self.fields:
            for f in group:
                row = BoxLayout(size_hint_y=None, height="55dp")
                row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.35))
                inp = SInput(text=data.get(f, "")); inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"][f] = v
        app.save_data()

class EquipScreen(Screen):
    # 절대 규칙: 세부 목록 11개 고정
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp")
            row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.35))
            inp = SInput(text=data.get(f, "")); inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"][f] = v
        app.save_data()

KV = '''
ScreenManager:
    transition: FadeTransition()
    MainScreen: name: 'main'
    CharSelectScreen: name: 'char_select'
    SlotMenuScreen: name: 'slot_menu'
    InfoScreen: name: 'info'
    EquipScreen: name: 'equip'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        canvas.before:
            Rectangle: source: 'bg.png'; pos: self.pos; size: self.size
        Label: text: "PristonTale"; font_size: '32sp'; font_name: 'KFont'; size_hint_y: None; height: '70dp'
        SInput: hint_text: "계정 검색..."; on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 8
        Button: text: "+ 새 계정 생성"; font_name: 'KFont'; size_hint_y: None; height: '65dp'; background_color: (0, 0.6, 0.3, 1); on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label: text: "캐릭터 슬롯"; font_name: 'KFont'; size_hint_y: None; height: '60dp'
        GridLayout: id: grid; cols: 2; spacing: 15
        Button: text: "이전 단계"; font_name: 'KFont'; size_hint_y: None; height: '65dp'; on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        Button: text: "케릭정보창"; font_name: 'KFont'; on_release: app.root.current = 'info'
        Button: text: "케릭장비창"; font_name: 'KFont'; on_release: app.root.current = 'equip'
        Button: text: "인벤토리창"; font_name: 'KFont'
        Button: text: "사진선택창"; font_name: 'KFont'
        Button: text: "뒤로가기"; font_name: 'KFont'; size_hint_y: None; height: '65dp'; background_color: (0.5, 0.5, 0.5, 1); on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height
        Button: text: "저장 및 뒤로"; font_name: 'KFont'; size_hint_y: None; height: '65dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data, self.cur_acc, self.cur_slot = DataStore.load(), "", ""
        return Builder.load_string(KV)
    def save_data(self): DataStore.save(self.user_data)
    def confirm_pop(self, msg, yes):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        c.add_widget(Label(text=msg, font_name="KFont", halign="center"))
        b = BoxLayout(size_hint_y=None, height="55dp", spacing=10)
        y, n = Button(text="확인", background_color=(0, 0.5, 0.2, 1), font_name="KFont"), Button(text="취소", font_name="KFont")
        b.add_widget(y); b.add_widget(n); c.add_widget(b)
        p = Popup(title="알림", content=c, size_hint=(0.85, 0.35))
        y.bind(on_release=lambda x: [yes(), p.dismiss()]); n.bind(on_release=p.dismiss); p.open()

if __name__ == "__main__":
    PristonApp().run()
