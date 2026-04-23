import os
import json
import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase

# [자가 진단] 로그 시스템 활성화
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PristonManager")

# [검수] S26 울트라 최적화 설정
Window.softinput_mode = "below_target"
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)

# --- 데이터 무결성 보호 레이어 ---
class DataStore:
    FILE = "PristonTale.json"
    
    @staticmethod
    def get_default_structure():
        # [절대 규칙] 6개 창 및 세부 목록 18개/11개 초기값 고정
        return {
            "info_fields": ['이름', '직위', '클랜', '레벨', '생명력', '기력', '근력', '힘', '정신력', '재능', '민첩', '건강', '명중', '공격', '방어', '흡수', '속도'],
            "equip_fields": ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"],
            "accounts": {}
        }

    @staticmethod
    def load():
        try:
            if os.path.exists(DataStore.FILE):
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Data Load Error: {e}")
        return DataStore.get_default_structure()

    @staticmethod
    def save(data):
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Data Save Error: {e}")

# --- 공통 스타일 (중앙 정렬 고정) ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = "KFont" if os.path.exists(FONT_FILE) else None
        self.multiline = False
        self.size_hint_y = None
        self.height = "55dp"
        self.halign = "center"
        self.write_tab = False

# --- 각 화면 구성 (절대 규칙 준수) ---
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def refresh(self, query=""):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        for aid in data.keys():
            if query.lower() in aid.lower():
                row = BoxLayout(size_hint_y=None, height="65dp", spacing=10)
                btn = Button(text=f"ID: {aid}", font_name="KFont", background_color=(0, 0.5, 0.2, 1))
                btn.bind(on_release=lambda x, a=aid: self.go_next(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1), font_name="KFont")
                del_btn.bind(on_release=lambda x, a=aid: self.ask_del(a))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)

    def go_next(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def ask_del(self, aid):
        App.get_running_app().confirm_pop(f"[{aid}] 계정을\\n정말 삭제하시겠습니까?", lambda: self.do_del(aid))

    def do_del(self, aid):
        app = App.get_running_app()
        del app.user_data["accounts"][aid]
        app.save_data(); self.refresh()

    def show_add(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.inp = SInput(hint_text="새 계정 ID 입력")
        btn = Button(text="계정 저장", font_name="KFont", background_color=(0, 0.5, 0.2, 1), size_hint_y=None, height="55dp")
        content.add_widget(self.inp); content.add_widget(btn)
        self.pop = Popup(title="계정 생성", content=content, size_hint=(0.85, 0.4))
        btn.bind(on_release=lambda x: App.get_running_app().confirm_pop("새 계정을 저장하시겠습니까?", self.save_acc))
        self.pop.open()

    def save_acc(self):
        aid = self.inp.text.strip()
        if aid:
            app = App.get_running_app()
            if aid not in app.user_data["accounts"]:
                app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[]} for i in range(1, 7)}
                app.save_data(); self.refresh(); self.pop.dismiss()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.grid.clear_widgets()
        app = App.get_running_app()
        acc_data = app.user_data["accounts"][app.cur_acc]
        for i in range(1, 7):
            name = acc_data[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, font_name="KFont", background_color=(0, 0.4, 0.3, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen):
    pass

class InfoScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"]
        fields = app.user_data["info_fields"]
        
        # [검수] 시각적 편의를 위한 그룹화 출력
        groups = [fields[0:4], fields[4:7], fields[7:12], fields[12:17]]
        for group in groups:
            for f in group:
                row = BoxLayout(size_hint_y=None, height="55dp", spacing=5)
                row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.35))
                inp = SInput(text=data.get(f, ""))
                inp.bind(text=lambda instance, v, field=f: self.auto_save(field, v))
                row.add_widget(inp)
                self.ids.container.add_widget(row)
            self.ids.container.add_widget(Label(size_hint_y=None, height="15dp")) # 보이지 않는 칸 띄움

    def auto_save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"][f] = v
        app.save_data()

    def ask_clear(self):
        App.get_running_app().confirm_pop("이 정보창의 내용을\\n전체 삭제하시겠습니까?", self.do_clear)

    def do_clear(self):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["info"] = {}
        app.save_data(); self.on_enter()

class EquipScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        app = App.get_running_app()
        data = app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"]
        fields = app.user_data["equip_fields"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=5)
            row.add_widget(Label(text=f, font_name="KFont", size_hint_x=0.35))
            inp = SInput(text=data.get(f, ""))
            inp.bind(text=lambda instance, v, field=f: self.auto_save(field, v))
            row.add_widget(inp)
            self.ids.container.add_widget(row)

    def auto_save(self, f, v):
        app = App.get_running_app()
        app.user_data["accounts"][app.cur_acc][app.cur_slot]["equip"][f] = v
        app.save_data()

# [전수 검수] KV 디자인 레이아웃
KV = '''
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
        padding: 15
        spacing: 12
        canvas.before:
            Rectangle:
                source: 'bg.png'
                pos: self.pos
                size: self.size
        Label:
            text: "PristonTale"
            font_size: '32sp'
            font_name: 'KFont'
            size_hint_y: None
            height: '70dp'
        SInput:
            hint_text: "전체 계정 검색..."
            on_text: root.refresh(self.text)
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
        Button:
            text: "+ 새 계정 생성"
            font_name: 'KFont'
            size_hint_y: None
            height: '65dp'
            background_color: (0, 0.6, 0.3, 1)
            on_release: root.show_add()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: "캐릭터 슬롯 선택"
            font_name: 'KFont'
            font_size: '26sp'
            size_hint_y: None
            height: '60dp'
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "이전 화면으로"
            font_name: 'KFont'
            size_hint_y: None
            height: '65dp'
            on_release: app.root.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        Button:
            text: "케릭정보창"
            font_name: 'KFont'
            on_release: app.root.current = 'info'
        Button:
            text: "케릭장비창"
            font_name: 'KFont'
            on_release: app.root.current = 'equip'
        Button:
            text: "인벤토리창"
            font_name: 'KFont'
        Button:
            text: "사진선택창"
            font_name: 'KFont'
        Button:
            text: "뒤로가기"
            font_name: 'KFont'
            size_hint_y: None
            height: '65dp'
            background_color: (0.5, 0.5, 0.5, 1)
            on_release: app.root.current = 'char_select'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '65dp'
            spacing: 10
            Button:
                text: "내용 전체삭제"
                font_name: 'KFont'
                background_color: (0.8, 0, 0, 1)
                on_release: root.ask_clear()
            Button:
                text: "저장 및 뒤로"
                font_name: 'KFont'
                on_release: app.root.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""
        self.cur_slot = ""
        return Builder.load_string(KV)

    def save_data(self):
        DataStore.save(self.user_data)

    def confirm_pop(self, msg, yes_func):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text=msg, font_name="KFont", halign="center"))
        btns = BoxLayout(size_hint_y=None, height="55dp", spacing=15)
        y_btn = Button(text="확인", background_color=(0, 0.5, 0.2, 1), font_name="KFont")
        n_btn = Button(text="취소", font_name="KFont")
        btns.add_widget(y_btn); btns.add_widget(n_btn)
        content.add_widget(btns)
        pop = Popup(title="알림", content=content, size_hint=(0.85, 0.4))
        y_btn.bind(on_release=lambda x: [yes_func(), pop.dismiss()])
        n_btn.bind(on_release=pop.dismiss)
        pop.open()

if __name__ == "__main__":
    PristonApp().run()
