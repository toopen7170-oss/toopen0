import os, json, sys, traceback
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
from kivy.clock import Clock

# [S26 울트라 최적화: 키보드 대응]
Window.softinput_mode = "below_target"

# [폰트 및 배경음 설정]
FONT_FILE = "font.ttf"
USE_FONT = None
if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_FILE)
        USE_FONT = "KFont"
    except: pass

# [자가 진단 시스템]
def global_exception_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    content = BoxLayout(orientation='vertical', padding=10)
    content.add_widget(TextInput(text=err_msg, readonly=True, font_size='12sp'))
    btn = Button(text="닫기", size_hint_y=0.2)
    pop = Popup(title="[시스템 진단 오류]", content=content, size_hint=(0.9, 0.8))
    btn.bind(on_release=pop.dismiss); content.add_widget(btn); pop.open()

sys.excepthook = global_exception_handler

# [데이터 엔진]
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

# [커스텀 입력창: 중앙 정렬 및 고정]
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        if USE_FONT: self.font_name = USE_FONT
        self.multiline = False
        self.size_hint_y = None
        self.height = "65dp"
        self.halign = "center"
        self.padding_y = [self.height / 2 - (self.line_height / 2), 0]
        self.write_tab = False

# --- 제1 기본원칙: 7개 화면 클래스 (절대 사수) ---

class MainScreen(Screen): # 1. 계정생성창
    def on_enter(self): self.refresh()
    def refresh(self, q=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            # 검색 로직 (계정명 + 캐릭터명 통합 검색)
            match = q.lower() in aid.lower()
            if not match:
                for slot in data[aid]:
                    if q.lower() in data[aid][slot]["info"].get("이름", "").lower():
                        match = True; break
            
            if match:
                row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
                btn = Button(text=aid, font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.9, 0.1, 0.1, 1), font_name=USE_FONT)
                del_b.bind(on_release=lambda x, a=aid: App.get_running_app().confirm_pop(f"'{a}'를 삭제하시겠습니까?", lambda: self.do_del(a)))
                row.add_widget(btn); row.add_widget(del_b); self.ids.acc_list.add_widget(row)

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
        self.inp = SInput(hint_text="새 계정 이름을 입력하세요")
        btn = Button(text="계정 저장", font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1), size_hint_y=None, height="65dp")
        c.add_widget(self.inp); c.add_widget(btn)
        pop = Popup(title="계정 생성", content=c, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: App.get_running_app().confirm_pop("계정을 저장하시겠습니까?", lambda: self.save_acc(pop)))
        pop.open()

    def save_acc(self, pop):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(); pop.dismiss()

class CharSelectScreen(Screen): # 2. 케릭선택창 (6슬롯)
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

class SlotMenuScreen(Screen): # 슬롯 클릭 시 5개 버튼 화면
    pass

class InfoScreen(Screen): # 3. 케릭정보창 (18개 목록 사수)
    groups = [
        ['이름', '직위', '클랜', '레벨'],
        ['생명력', '기력', '근력'],
        ['힘', '정신력', '재능', '민첩', '건강'],
        ['명중', '공격', '방어', '흡수', '속도']
    ]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"]
        for gp in self.groups:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
                inp = SInput(text=str(data.get(f, "")))
                inp.bind(text=lambda inst, v, f=f: self.save_val(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(Label(size_hint_y=None, height="40dp")) # 한칸 띄우기 (투명)
    def save_val(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"][f] = v
        App.get_running_app().save_data()
    def clear_all(self):
        App.get_running_app().confirm_pop("정보창의 모든 내용을 삭제하시겠습니까?", self.do_clear)
    def do_clear(self):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["info"] = {}
        App.get_running_app().save_data(); self.on_enter()

class EquipScreen(Screen): # 4. 케릭장비창 (11개 목록 사수)
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
            row.add_widget(Label(text=f, font_name=USE_FONT, size_hint_x=0.3))
            inp = SInput(text=str(data.get(f, "")))
            inp.bind(text=lambda inst, v, f=f: self.save_val(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def save_val(self, f, v):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"][f] = v
        App.get_running_app().save_data()
    def clear_all(self):
        App.get_running_app().confirm_pop("장비창의 모든 내용을 삭제하시겠습니까?", self.do_clear)
    def do_clear(self):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot]["equip"] = {}
        App.get_running_app().save_data(); self.on_enter()

class ListEditScreen(Screen): # 5 & 7. 인벤토리 및 저장보관소
    mode = "inv"
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.cont.clear_widgets()
        items = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode]
        for idx, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="75dp", spacing=10)
            btn = Button(text=val[:20] + "...", font_name=USE_FONT)
            btn.bind(on_release=lambda x, i=idx, v=val: self.show_edit(i, v))
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.9, 0.1, 0.1, 1), font_name=USE_FONT)
            del_b.bind(on_release=lambda x, i=idx: App.get_running_app().confirm_pop("이 줄을 삭제하시겠습니까?", lambda: self.do_del(i)))
            row.add_widget(btn); row.add_widget(del_b); self.ids.cont.add_widget(row)
    def show_edit(self, idx, val):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(text=val, font_name=USE_FONT, size_hint_y=0.7)
        btn = Button(text="수정 완료", size_hint_y=0.3, background_color=(0, 0.6, 0.3, 1), font_name=USE_FONT)
        c.add_widget(inp); c.add_widget(btn)
        p = Popup(title="내용 수정", content=c, size_hint=(0.9, 0.5))
        btn.bind(on_release=lambda x: [self.save_item(idx, inp.text), p.dismiss()]); p.open()
    def save_item(self, i, t):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode][i] = t
        App.get_running_app().save_data(); self.refresh()
    def do_del(self, i):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].pop(i)
        App.get_running_app().save_data(); self.refresh()
    def add_item(self):
        App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc][App.get_running_app().cur_slot][self.mode].append("새 항목")
        App.get_running_app().save_data(); self.refresh()

class PhotoScreen(Screen): # 6. 사진선택창
    def on_enter(self):
        # 안드로이드 권한 요청 시뮬레이션 및 UI 초기화
        pass

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
        SInput: id: search; hint_text: "계정 또는 케릭 이름 검색"; on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
        Button: text: "+ 새 계정 생성"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; background_color:(0, 0.6, 0.3, 1); on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20; spacing: 20
    Label: text: "캐릭터 선택"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '60dp'
    GridLayout: id: grid; cols: 2; spacing: 15
    Button: text: "뒤로가기"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 40; spacing: 15
        Button: text: "케릭정보창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'info'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "케릭장비창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'equip'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "인벤토리창"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("inv"); background_color:(0, 0.5, 0.7, 1)
        Button: text: "사진선택창"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'photo'; background_color:(0, 0.5, 0.7, 1)
        Button: text: "저장보관소"; font_name: 'KFont' if USE_FONT else None; on_release: app.set_mode("storage"); background_color:(0, 0.5, 0.7, 1)
        Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; background_color: (0.5, 0.5, 0.5, 1); on_release: app.root.current = 'char_select'

<InfoScreen>, <EquipScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
    BoxLayout:
        size_hint_y: None; height: '70dp'; spacing: 10
        Button: text: "전체 삭제"; font_name: 'KFont' if USE_FONT else None; background_color:(0.9, 0.1, 0.1, 1); on_release: root.clear_all()
        Button: text: "완료"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'slot_menu'; background_color:(0, 0.6, 0.3, 1)

<ListEditScreen>:
    BoxLayout: orientation: 'vertical'; padding: 10
    ScrollView:
        BoxLayout: id: cont; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 10
    BoxLayout:
        size_hint_y: None; height: '70dp'; spacing: 10
        Button: text: "항목 추가"; font_name: 'KFont' if USE_FONT else None; background_color:(0, 0.6, 0.3, 1); on_release: root.add_item()
        Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; on_release: app.root.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout: orientation: 'vertical'; padding: 20; spacing: 20
    Label: text: "사진 관리 (준비 중)"; font_name: 'KFont' if USE_FONT else None
    Button: text: "파일 선택 (여러장)"; font_name: 'KFont' if USE_FONT else None; height: '80dp'; size_hint_y: None
    Button: text: "뒤로"; font_name: 'KFont' if USE_FONT else None; size_hint_y: None; height: '70dp'; on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.icon = "icon.png"
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        return Builder.load_string(KV)

    def save_data(self): DataStore.save(self.user_data)
    
    def set_mode(self, m):
        self.root.get_screen('list_edit').mode = m
        self.root.current = 'list_edit'

    def confirm_pop(self, msg, yes_func):
        c = BoxLayout(orientation='vertical', padding=20, spacing=20)
        c.add_widget(Label(text=msg, font_name=USE_FONT))
        b = BoxLayout(size_hint_y=None, height="60dp", spacing=15)
        y_btn = Button(text="확인", font_name=USE_FONT, background_color=(0, 0.6, 0.3, 1))
        n_btn = Button(text="취소", font_name=USE_FONT)
        b.add_widget(y_btn); b.add_widget(n_btn); c.add_widget(b)
        pop = Popup(title="알림", content=c, size_hint=(0.8, 0.35))
        y_btn.bind(on_release=lambda x: [yes_func(), pop.dismiss()])
        n_btn.bind(on_release=pop.dismiss); pop.open()

if __name__ == "__main__":
    PristonApp().run()
