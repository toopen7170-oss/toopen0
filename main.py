import os, sys, traceback, json, time
from datetime import datetime

# [블랙박스 엔진: PristonTale 물리 각인형 시스템 - 절대 보존/수정 금지]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        if not os.path.exists(os.path.dirname(path)): return "PristonTale_BlackBox.txt"
        with open(path, "a", encoding="utf-8") as f: pass
        return path
    except: return "PristonTale_BlackBox.txt"

LOG_FILE = get_download_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 물리적 강제 저장
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> 시스템 엔진 가동 <<<")

# [안드로이드 5대 권한 수리 버전]
from kivy.utils import platform
if platform == 'android':
    from android.permissions import request_permissions
    # AttributeError 방지를 위해 직접 문자열로 권한 요청
    perms = [
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.MANAGE_EXTERNAL_STORAGE",
        "android.permission.INTERNET"
    ]
    request_permissions(perms)
    write_blackbox("권한 요청 리스트 전송 완료")

# [Kivy 환경 최적화]
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'maxfps', '60')
Config.set('kivy', 'keyboard_mode', 'systemanddock')

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
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# 폰트 등록
if os.path.exists("font.ttf"):
    LabelBase.register(name="KFont", fn_regular="font.ttf")

# [데이터 매니저]
class DataStore:
    FILE = "PristonTale_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"accounts": {}}
    @staticmethod
    def save(data):
        with open(DataStore.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush(); os.fsync(f.fileno())

# [팝업 시스템]
def show_confirm(title, msg, on_yes):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=msg, font_name='KFont' if os.path.exists("font.ttf") else None))
    btns = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
    y_btn = Button(text="예", background_color=get_color_from_hex("#2E7D32"))
    n_btn = Button(text="아니오", background_color=get_color_from_hex("#C62828"))
    btns.add_widget(y_btn); btns.add_widget(n_btn)
    content.add_widget(btns)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    y_btn.bind(on_release=lambda x: [on_yes(), popup.dismiss()])
    n_btn.bind(on_release=popup.dismiss)
    popup.open()

# [7대 화면 클래스 - 제1원칙 준수]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.2)
    def refresh(self, dt):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        search_text = self.ids.search_bar.text.lower()
        for aid in data:
            if search_text in aid.lower():
                row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
                btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"), halign='center')
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
                del_btn.bind(on_release=lambda x, a=aid: show_confirm("삭제", f"'{a}'를 삭제하시겠습니까?", lambda: self.del_acc(a)))
                row.add_widget(btn); row.add_widget(del_btn)
                self.ids.acc_list.add_widget(row)
    def add_acc(self):
        aid = self.ids.new_acc.text.strip()
        if aid: show_confirm("저장", f"'{aid}' 계정을 생성하시겠습니까?", lambda: self._add(aid))
    def _add(self, aid):
        app = App.get_running_app()
        if aid not in app.user_data["accounts"]:
            app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
            app.save_data(); self.refresh(0)
    def del_acc(self, aid):
        del App.get_running_app().user_data["accounts"][aid]
        App.get_running_app().save_data(); self.refresh(0)
    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build, 0.2)
    def build(self, dt):
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#2E7D32"), halign='center')
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    structure = [['이름','직위','클랜','레벨'],['생명력','기력','근력'],['힘','정신력','재능','민첩','건강'],['명중','공격','방어','흡수','속도']]
    def on_enter(self): Clock.schedule_once(self.build, 0.2)
    def build(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for i, gp in enumerate(self.structure):
            for f in gp:
                row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
                row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists("font.ttf") else None))
                inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center', padding_y=(15, 15))
                inp.bind(text=lambda inst, v, f=f: self.update(f, v))
                row.add_widget(inp); self.ids.cont.add_widget(row)
            if i < len(self.structure)-1:
                self.ids.cont.add_widget(BoxLayout(size_hint_y=None, height="30dp"))
    def update(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        if f == "이름": pass # 케릭선택창 자동 반영은 로드 시 수행됨
        App.get_running_app().save_data()
    def clear_all(self):
        show_confirm("삭제", "전체 내용을 삭제하시겠습니까?", self._clear)
    def _clear(self):
        App.get_running_app().get_cur_data()["info"] = {}; App.get_running_app().save_data(); self.build(0)

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build, 0.2)
    def build(self, dt):
        self.ids.cont.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name="KFont" if os.path.exists("font.ttf") else None))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center', padding_y=(15, 15))
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.cont.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()
    def clear_all(self):
        show_confirm("삭제", "장비 정보를 전체 삭제하시겠습니까?", lambda: [App.get_running_app().get_cur_data().update({"equip":{}}), App.get_running_app().save_data(), self.build(0)])

class InventoryScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.2)
    def refresh(self, dt):
        self.ids.list.clear_widgets()
        items = App.get_running_app().get_cur_data()["inv"]
        for i, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="60dp")
            btn = Button(text=val[:20], background_color=get_color_from_hex("#2E7D32"), halign='center')
            btn.bind(on_release=lambda x, v=val, idx=i: self.detail(v, idx))
            row.add_widget(btn); self.ids.list.add_widget(row)
    def add_item(self):
        App.get_running_app().get_cur_data()["inv"].append("새 항목")
        App.get_running_app().save_data(); self.refresh(0)
    def detail(self, v, idx):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(text=v, halign='center')
        btns = BoxLayout(size_hint_y=0.3, spacing=10)
        s_btn = Button(text="저장", background_color=get_color_from_hex("#2E7D32"))
        d_btn = Button(text="삭제", background_color=get_color_from_hex("#C62828"))
        btns.add_widget(s_btn); btns.add_widget(d_btn)
        content.add_widget(inp); content.add_widget(btns)
        pop = Popup(title="상세보기", content=content, size_hint=(0.9, 0.6))
        s_btn.bind(on_release=lambda x: show_confirm("저장", "저장하시겠습니까?", lambda: [self.save(idx, inp.text), pop.dismiss()]))
        d_btn.bind(on_release=lambda x: show_confirm("삭제", "삭제하시겠습니까?", lambda: [self.delete(idx), pop.dismiss()]))
        pop.open()
    def save(self, idx, text):
        App.get_running_app().get_cur_data()["inv"][idx] = text
        App.get_running_app().save_data(); self.refresh(0)
    def delete(self, idx):
        App.get_running_app().get_cur_data()["inv"].pop(idx)
        App.get_running_app().save_data(); self.refresh(0)

class PhotoScreen(Screen): pass
class StorageScreen(InventoryScreen):
    def refresh(self, dt):
        self.ids.list.clear_widgets()
        items = App.get_running_app().get_cur_data()["storage"]
        for i, val in enumerate(items):
            row = BoxLayout(size_hint_y=None, height="60dp")
            btn = Button(text=val[:20], background_color=get_color_from_hex("#2E7D32"), halign='center')
            btn.bind(on_release=lambda x, v=val, idx=i: self.detail(v, idx))
            row.add_widget(btn); self.ids.list.add_widget(row)
    def add_item(self):
        App.get_running_app().get_cur_data()["storage"].append("보관 항목")
        App.get_running_app().save_data(); self.refresh(0)
    def save(self, idx, text):
        App.get_running_app().get_cur_data()["storage"][idx] = text
        App.get_running_app().save_data(); self.refresh(0)
    def delete(self, idx):
        App.get_running_app().get_cur_data()["storage"].pop(idx)
        App.get_running_app().save_data(); self.refresh(0)

# [KV 레이아웃 - 제1원칙 고정]
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
    InventoryScreen:
        name: 'inv'
    PhotoScreen:
        name: 'photo'
    StorageScreen:
        name: 'storage'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "PristonTale"
            font_size: '40sp'
            size_hint_y: 0.15
            font_name: 'KFont' if exists('font.ttf') else None
        TextInput:
            id: search_bar
            hint_text: "전체 검색 (계정/케릭)"
            size_hint_y: None
            height: '50dp'
            halign: 'center'
            on_text: root.refresh(0)
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            TextInput:
                id: new_acc
                hint_text: "새 계정 ID"
                halign: 'center'
            Button:
                text: "생성"
                background_color: 0.18, 0.49, 0.2, 1
                on_release: root.add_acc()

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        Button:
            text: "케릭정보창"
            background_color: 0.18, 0.49, 0.2, 1
            on_release: root.manager.current = 'info'
        Button:
            text: "케릭장비창"
            background_color: 0.18, 0.49, 0.2, 1
            on_release: root.manager.current = 'equip'
        Button:
            text: "인벤토리창"
            background_color: 0.18, 0.49, 0.2, 1
            on_release: root.manager.current = 'inv'
        Button:
            text: "사진선택창"
            background_color: 0.18, 0.49, 0.2, 1
            on_release: root.manager.current = 'photo'
        Button:
            text: "저장보관소"
            background_color: 0.18, 0.49, 0.2, 1
            on_release: root.manager.current = 'storage'
        Button:
            text: "뒤로"
            background_color: 0.78, 0.16, 0.16, 1
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        ScrollView:
            BoxLayout:
                id: cont
                id: list
                id: grid
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Button:
                text: "전체삭제" if root.name in ['info','equip'] else "추가"
                background_color: 0.78, 0.16, 0.16, 1 if root.name in ['info','equip'] else 0.18, 0.49, 0.2, 1
                on_release: root.clear_all() if root.name in ['info','equip'] else root.add_item()
            Button:
                text: "뒤로"
                background_color: 0.5, 0.5, 0.5, 1
                on_release: root.manager.current = 'slot_menu'

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "캐릭터 선택"
            size_hint_y: 0.1
            font_name: 'KFont' if exists('font.ttf') else None
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "뒤로"
            size_hint_y: 0.15
            on_release: root.manager.current = 'main'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        Window.softinput_mode = 'below_target' # 자판 대응 자동 스크롤
        return Builder.load_string(KV)
    def get_cur_data(self): return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self): DataStore.save(self.user_data)

if __name__ == "__main__":
    PristonApp().run()
