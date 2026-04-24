import os, json, sys, traceback

# [블랙박스 가동 시점 최상단 배치]
# 라이브러리 로딩 중 발생하는 오류까지 가로채기 위해 import 문 중간에 배치
def global_exception_handler(exctype, value, tb):
    err_lines = traceback.format_exception(exctype, value, tb)
    full_err_msg = "".join(err_lines)
    
    # 누적 로그 기록 (PristonTale_BlackBox.txt)
    with open("PristonTale_BlackBox.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "!"*10 + " NEW ERROR LOG " + "!"*10 + "\n" + full_err_msg)
    
    # 화면 강제 출력 시스템 (팅기기 전 최후의 수단)
    try:
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        content.add_widget(Label(text="🚨 블랙박스 치명적 오류 감지 🚨", 
                                 color=(1, 0, 0, 1), bold=True, size_hint_y=None, height="50dp"))
        
        # 전체 에러 정보 출력 (점주님 사진 촬영용)
        err_view = TextInput(text=full_err_msg, readonly=True, font_size='12sp',
                             background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        content.add_widget(err_view)
        
        btn = Button(text="확인 후 종료 (사진을 꼭 찍어주세요)", size_hint_y=None, height="70dp",
                     background_color=(0.8, 0.2, 0.2, 1))
        content.add_widget(btn)
        
        pop = Popup(title="BlackBox Diagnostic v2.0", content=content, size_hint=(0.95, 0.95), auto_dismiss=False)
        btn.bind(on_release=lambda x: sys.exit(1))
        pop.open()
    except:
        # Kivy조차 로딩 안 된 경우 콘솔 출력 (로그파일은 이미 생성됨)
        print(full_err_msg)
        sys.exit(1)

sys.excepthook = global_exception_handler

# 이후 나머지 라이브러리 로딩
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock

# [환경 오류 검사 및 최적화]
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

# --- 제1 기본원칙 사수 (생략 없이 통합) ---
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if q.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
                btn = Button(text=aid, font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_b = Button(text="삭제", size_hint_x=0.25, background_color=(0.9, 0.1, 0.1, 1), font_name=USE_FONT)
                del_b.bind(on_release=lambda x, a=aid: App.get_running_app().confirm_pop(f"'{a}' 삭제?", lambda: self.do_del(a)))
                row.add_widget(btn); row.add_widget(del_b); self.ids.acc_list.add_widget(row)
    def go_next(self, aid): App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'
    def do_del(self, aid):
        app = App.get_running_app(); del app.user_data["accounts"][aid]; app.save_data(); self.refresh()
    def show_add(self):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="새 계정 ID"); c.add_widget(self.inp)
        btn = Button(text="저장", font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1), size_hint_y=None, height="65dp")
        c.add_widget(btn); pop = Popup(title="계정 추가", content=c, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: App.get_running_app().confirm_pop("계정 저장?", lambda: self.save_acc(pop))); pop.open()
    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app(); app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name=USE_FONT, background_color=(0, 0.5, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx)); self.ids.grid.add_widget(btn)
    def go_slot(self, i): App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    groups = [['이름', '직위', '클랜', '레벨'], ['생명력', '기력', '근력'], ['힘', '정신력', '재능', '민첩', '건강'], ['명중', '공격', '방어', '흡수', '속도']]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"]
        for gp in self.groups:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
                inp = SInput(text=str(data.get(f, ""))); inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(Label(size_hint_y=None, height="30dp"))
    def save(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"][f] = v
        App.get_running_app().save_data()
    def clear_all(self): App.get_running_app().confirm_pop("전체 삭제?", self.do_clear)
    def do_clear(self): App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"] = {}; App.get_running_app().save_data(); self.on_enter()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
            row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
            inp = SInput(text=str(data.get(f, ""))); inp.bind(text=lambda inst, v, f=f: self.save(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"][f] = v
        App.get_running_app().save_data()
    def clear_all(self): App.get_running_app().confirm_pop("장비 전체 삭제?", self.do_clear)
    def do_clear(self): App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"] = {}; App.get_running_app().save_data(); self.on_enter()

class ListEditScreen(Screen):
    mode = "inv"
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode]
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
            btn = Button(text=val[:25], font_name=USE_FONT); btn.bind(on_release=lambda x, i=idx, v=val: self.show_edit(i, v))
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.9, 0.1, 0.1, 1), font_name=USE_FONT)
            del_b.bind(on_release=lambda x, i=idx: App.get_running_app().confirm_pop("삭제?", lambda: self.do_del(i)))
            row.add_widget(btn); row.add_widget(del_b); self.ids.cont.add_widget(row)
    def show_edit(self, idx, val):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(text=val, font_name=USE_FONT, size_hint_y=0.7); c.add_widget(inp)
        btn = Button(text="수정", size_hint_y=0.3, background_color=(0, 0.6, 0.3, 1), font_name=USE_FONT)
        c.add_widget(btn); p = Popup(title="수정", content=c, size_hint=(0.9, 0.5))
        btn.bind(on_release=lambda x: [self.save_item(idx, inp.text), p.dismiss()]); p.open()
    def save_item(self, i, t): App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode][i] = t; App.get_running_app().save_data(); self.refresh()
    def do_del(self, i): App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].pop(i); App.get_running_app().save_data(); self.refresh()
    def add_item(self): App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].append("새 항목"); App.get_running_app().save_data(); self.refresh()

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
        orientation: 'vertical'; padding: 20; spacing: 15
        canvas.before:
            Rectangle:
                source: 'bg.png' if os.path.exists('bg.png') else ''
                pos: self.pos; size: self.size
        Label: text: "PristonTale"; font_size: '35sp'; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '80dp'
        SInput: id: search; hint_text: "검색 (계정/이름)"; on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
        Button: text: "+ 계정 생성"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; background_color:(0, 0.6, 0.3, 1); on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20; spacing: 20
    Label: text: "캐릭터 선택"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'
    GridLayout: id: grid; cols: 2; spacing: 15
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 40; spacing: 15
        Button: text: "케릭정보창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'info'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "케릭장비창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'equip'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "인벤토리창"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("inv"); background_color:(0, 0.5, 0.7, 1)
        Button: text: "사진선택창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'photo'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "저장보관소"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("storage"); background_color:(0, 0.5, 0.7, 1)
        Button: text: "뒤로가기"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; background_color: (0.5, 0.5, 0.5, 1); on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
    BoxLayout:
        size_hint_y: None; height: '70dp'; spacing: 10
        Button: text: "전체삭제"; font_name: 'KFont' if USE_FONT else None; background_color:(0.9, 0.1, 0.1, 1); on_release: root.clear_all()
        Button: text: "저장완료"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'slot_menu'; background_color:(0, 0.6, 0.3, 1)

<ListEditScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
    BoxLayout:
        size_hint_y: None; height: '70dp'; spacing: 10
        Button: text: "추가"; font_name: 'KFont' if USE_FONT else None; background_color:(0, 0.6, 0.3, 1); on_release: root.add_item()
        Button: text: "닫기"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20; spacing: 20
    Label: text: "사진 관리 시스템"; font_name: 'KFont' if USE_FONT else None
    Button: text: "뒤로가기"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        return Builder.load_string(KV)
    def save_data(self): DataStore.save(self.user_data)
    def set_mode(self, m): self.root.get_screen('list_edit').mode = m; self.root.current = 'list_edit'
    def confirm_pop(self, msg, yes_func):
        c = BoxLayout(orientation='vertical', padding=20, spacing=20)
        c.add_widget(Label(text=msg, font_name=USE_FONT))
        b = BoxLayout(size_hint_y=None, height="60dp", spacing=15)
        y = Button(text="예", font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
        n = Button(text="아니오", font_name=USE_FONT)
        b.add_widget(y); b.add_widget(n); c.add_widget(b)
        p = Popup(title="확인", content=c, size_hint=(0.85, 0.35))
        y.bind(on_release=lambda x: [yes_func(), p.dismiss()])
        n.bind(on_release=p.dismiss); p.open()

if __name__ == "__main__":
    PristonApp().run()
