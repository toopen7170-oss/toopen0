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

# [갤럭시 S26 울트라 최적화]
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
                    d = json.load(f)
                    if "accounts" not in d: d = {"accounts": {}}
                    return d
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
        self.multiline = False
        self.size_hint_y = None
        self.height = "60dp"
        self.halign = "center"
        self.padding_y = [self.height/2 - (self.line_height/2), 0]
        self.write_tab = False

# --- 제1원칙: 7개 화면 구성 (절대 수정 불가) ---

class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        for aid in data.keys():
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
                btn = Button(text=f"{aid}", font_name="KFont", background_color=(0, 0.6, 0.3, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_btn = Button(text="삭제", size_hint_x=0.25, background_color=(0.9, 0.1, 0.1, 1), font_name="KFont")
                del_btn.bind(on_release=lambda x, a=aid: App.get_running_app().confirm_pop(f"'{a}' 삭제하시겠습니까?", lambda: self.do_del(a)))
                row.add_widget(btn); row.add_widget(del_btn); self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def do_del(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]
            app.save_data(); self.refresh()
    def show_add(self):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="새 계정 ID 입력")
        btn = Button(text="저장", font_name="KFont", background_color=(0, 0.6, 0.3, 1), size_hint_y=None, height="60dp")
        c.add_widget(self.inp); c.add_widget(btn)
        pop = Popup(title="계정 생성", content=c, size_hint=(0.9, 0.4))
        btn.bind(on_release=lambda x: App.get_running_app().confirm_pop("저장하시겠습니까?", lambda: self.save_acc(pop))); pop.open()
    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        acc_data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc_data[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name="KFont", background_color=(0, 0.5, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    # 절대 규칙: 세부 목록 18개 그룹화
    fields = [['이름', '직위', '클랜', '레벨'], ['생명력', '기력', '근력'], ['힘', '정신력', '재능', '민첩', '건강'], ['명중', '공격', '방어', '흡수', '속도']]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"]
        for group in self.fields:
            for f in group:
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.3))
                inp = SInput(text=data.get(f, ""))
                inp.bind(text=lambda inst, v, f=f: self.auto_save(f, v))
                row.add_widget(inp)
                del_b = Button(text="X", size_hint_x=0.15, background_color=(0.9, 0.1, 0.1, 1))
                del_b.bind(on_release=lambda x, i=inp: App.get_running_app().confirm_pop("삭제하시겠습니까?", lambda: self.clear_field(i)))
                row.add_widget(del_b)
                self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(Label(size_hint_y=None, height="20dp")) # 시각적 공백
    def auto_save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"][f] = v
        app.save_data()
    def clear_field(self, inp): inp.text = ""

class EquipScreen(Screen):
    # 절대 규칙: 세부 목록 11개
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
            row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.3))
            inp = SInput(text=data.get(f, ""))
            inp.bind(text=lambda inst, v, f=f: self.auto_save(f, v))
            row.add_widget(inp)
            del_b = Button(text="X", size_hint_x=0.15, background_color=(0.9, 0.1, 0.1, 1))
            del_b.bind(on_release=lambda x, i=inp: App.get_running_app().confirm_pop("삭제하시겠습니까?", lambda: self.clear_field(i)))
            row.add_widget(del_b)
            self.ids.cont.add_widget(row)
    def auto_save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"][f] = v
        app.save_data()
    def clear_field(self, inp): inp.text = ""

class ListEditScreen(Screen):
    mode = "inv" # "inv" or "storage"
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        app = App.get_running_app()
        acc_slot = app.user_data["accounts"][app.cur_acc][app.cur_slot]
        if self.mode not in acc_slot: acc_slot[self.mode] = []
        items = acc_slot[self.mode]
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="65dp", spacing=5)
            btn = Button(text=val[:25], font_name="KFont", halign="center")
            btn.bind(on_release=lambda x, i=idx, v=val: self.show_edit(i, v))
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.9, 0.1, 0.1, 1), font_name="KFont")
            del_b.bind(on_release=lambda x, i=idx: app.confirm_pop("삭제하시겠습니까?", lambda: self.do_del(i)))
            row.add_widget(btn); row.add_widget(del_b); self.ids.cont.add_widget(row)
    def show_edit(self, idx, val):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(text=val, font_name="KFont", size_hint_y=0.7, halign="center")
        btn = Button(text="수정완료", font_name="KFont", size_hint_y=0.3, background_color=(0, 0.6, 0.3, 1))
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="내용 수정", content=c, size_hint=(0.9, 0.6))
        btn.bind(on_release=lambda x: self.save_edit(idx, inp.text, pop)); pop.open()
    def save_edit(self, idx, txt, pop):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.mode][idx] = txt
        app.save_data(); self.refresh(); pop.dismiss()
    def do_del(self, idx):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.mode].pop(idx)
        app.save_data(); self.refresh()
    def add_line(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot][self.mode].append("새 항목")
        app.save_data(); self.refresh()

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
        orientation: 'vertical'
        padding: 15
        spacing: 15
        canvas.before:
            Rectangle: source: 'bg.png'; pos: self.pos; size: self.size
        Label: text: "PristonTale"; font_size: '35sp'; font_name: 'KFont'; size_hint_y: None; height: '80dp'
        SInput: hint_text: "계정 검색..."; on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
        Button: text: "+ 계정 생성"; font_name: 'KFont'; size_hint_y: None; height: '70dp'; background_color: (0, 0.6, 0.3, 1); on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label: text: "캐릭터 선택"; font_name: 'KFont'; size_hint_y: None; height: '60dp'
        GridLayout: id: grid; cols: 2; spacing: 20
        Button: text: "뒤로가기"; font_name: 'KFont'; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        Button: text: "케릭정보창"; font_name: 'KFont'; on_release: app.root.current = 'info'
        Button: text: "케릭장비창"; font_name: 'KFont'; on_release: app.root.current = 'equip'
        Button: text: "인벤토리창"; font_name: 'KFont'; on_release: app.set_list_mode("inv")
        Button: text: "사진선택창"; font_name: 'KFont'; on_release: app.root.current = 'photo'
        Button: text: "저장보관소"; font_name: 'KFont'; on_release: app.set_list_mode("storage")
        Button: text: "이전으로"; font_name: 'KFont'; size_hint_y: None; height: '70dp'; background_color: (0.5, 0.5, 0.5, 1); on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height
        Button: text: "완료 및 뒤로"; font_name: 'KFont'; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'slot_menu'

<ListEditScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
        BoxLayout:
            size_hint_y: None; height: '70dp'; spacing: 10
            Button: text: "+ 줄 추가"; font_name: 'KFont'; background_color: (0, 0.6, 0.3, 1); on_release: root.add_line()
            Button: text: "뒤로"; font_name: 'KFont'; on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label: text: "사진 선택창"; font_name: 'KFont'
        Button: text: "뒤로"; font_name: 'KFont'; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data, self.cur_acc, self.cur_slot = DataStore.load(), "", ""
        return Builder.load_string(KV)
    def save_data(self): DataStore.save(self.user_data)
    def set_list_mode(self, mode):
        self.root.get_screen('list_edit').mode = mode
        self.root.current = 'list_edit'
    def confirm_pop(self, msg, yes):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        c.add_widget(Label(text=msg, font_name="KFont", halign="center"))
        b = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
        y, n = Button(text="확인", background_color=(0, 0.6, 0.3, 1), font_name="KFont"), Button(text="취소", font_name="KFont")
        b.add_widget(y); b.add_widget(n); c.add_widget(b)
        p = Popup(title="알림", content=c, size_hint=(0.85, 0.35))
        y.bind(on_release=lambda x: [yes(), p.dismiss()]); n.bind(on_release=p.dismiss); p.open()

if __name__ == "__main__":
    PristonApp().run()
