import os, sys, traceback, json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [1. 실시간 에러 경고 시스템]
def show_error_popup(error_msg):
    # 팅기기 직전에 에러를 화면에 강제로 띄움
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    scroll = ScrollView()
    err_lbl = Label(text=error_msg, size_hint_y=None, color=(1, 0, 0, 1))
    err_lbl.bind(texture_size=err_lbl.setter('size'))
    scroll.add_widget(err_lbl)
    content.add_widget(scroll)
    
    close_btn = Button(text="사진 찍은 후 닫기 (앱 종료)", size_hint_y=None, height="60dp")
    pop = Popup(title="!!! 시스템 에러 감지 !!!", content=content, size_hint=(0.9, 0.8))
    close_btn.bind(on_release=lambda x: sys.exit(1))
    content.add_widget(close_btn)
    pop.open()

def global_exception_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    # 메인 루프에서 에러 발생 시 팝업 시도
    try:
        show_error_popup(err_msg)
    except:
        # 팝업조차 못 띄울 상황이면 콘솔 출력
        print(err_msg)
        sys.exit(1)

sys.excepthook = global_exception_handler

# [2. 환경 및 폰트 설정]
FONT_FILE = "font.ttf"
HAS_FONT = os.path.exists(FONT_FILE)
if HAS_FONT:
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    except Exception as e:
        HAS_FONT = False

Window.softinput_mode = "below_target"

class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                Clock.schedule_once(lambda dt: show_error_popup(f"데이터 로드 실패: {e}"), 0.5)
        return {"accounts": {}}
    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            show_error_popup(f"데이터 저장 실패: {e}")

# [3. 제1 기본원칙 입력창 - 중앙 정렬 및 자동 스크롤 대응]
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = "KFont" if HAS_FONT else None
        self.multiline = False
        self.size_hint_y = None
        self.height = "65dp"
        self.halign = "center"
        self.padding_y = [self.height/2 - 18, 0]
        self.background_color = (1, 1, 1, 0.9)

# [화면 클래스 - 라인 바이 라인 검수 완료]
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
                del_btn.bind(on_release=lambda x, a=aid: self.confirm_pop(f"'{a}' 삭제?", lambda: self.do_del(a)))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)
    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'
    def confirm_pop(self, text, on_yes):
        p = ConfirmPopup(text=text, on_confirm=on_yes)
        p.open()
    def do_del(self, aid):
        del App.get_running_app().user_data["accounts"][aid]
        App.get_running_app().save_data(); self.refresh()

class CharSelectScreen(Screen):
    def on_enter(self):
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
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for gp in self.structure:
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if HAS_FONT else None))
                inp = SInput(text=str(data.get(f, "")))
                inp.bind(text=lambda inst, v, f=f: self.save(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
            self.ids.cont.add_widget(BoxLayout(size_hint_y=None, height="30dp"))
    def save(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build_ui, 0.1)
    def build_ui(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if HAS_FONT else None))
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
        l = BoxLayout(orientation='vertical', padding=20, spacing=20)
        l.add_widget(Label(text=text, font_name="KFont" if HAS_FONT else None))
        b = BoxLayout(spacing=10, size_hint_y=None, height="60dp")
        y = Button(text="예", background_color=get_color_from_hex("#2E7D32"))
        n = Button(text="아니오", background_color=get_color_from_hex("#C62828"))
        y.bind(on_release=lambda x: [on_confirm(), self.dismiss()])
        n.bind(on_release=self.dismiss)
        b.add_widget(y); b.add_widget(n); l.add_widget(b); self.content = l

# [4. KV 설계도 - 고정 배경 및 스타일]
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
    background_color: (0.1, 0.4, 0.6, 1)

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
            text: "사진 선택창 (준비 중)"
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
        try:
            return Builder.load_string(KV)
        except Exception as e:
            show_error_popup(f"KV 로드 실패: {e}")
    
    def save_data(self): DataStore.save(self.user_data)
    def get_cur_data(self): return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    
    def confirm_add(self, aid):
        if not aid.strip(): return
        p = ConfirmPopup(text=f"'{aid}' 저장?", on_confirm=lambda: self.do_add(aid))
        p.open()
    def do_add(self, aid):
        self.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
        self.save_data(); self.root.get_screen('main').refresh()
    
    def set_list(self, m):
        s = self.root.get_screen('list_edit')
        s.mode = m; self.root.current = 'list_edit'

if __name__ == "__main__":
    PristonApp().run()
