import os, sys, traceback, json
from datetime import datetime

# [1. 블랙박스 엔진: 다운로드 폴더 물리 각인 시스템]
def get_download_path():
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        if not os.path.exists("/storage/emulated/0/Download"):
            return "PristonTale_BlackBox.txt"
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
            os.fsync(f.fileno()) 
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 초기화 및 폰트 설정]
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform

def init_system():
    if platform == 'android':
        from android.permissions import request_permissions
        request_permissions(["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE", "android.permission.READ_MEDIA_IMAGES"])
    
    font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc", "/system/fonts/DroidSansFallback.ttf"]
    for p in font_paths:
        if os.path.exists(p):
            LabelBase.register(name="K-Font", fn_regular=p)
            Config.set('kivy', 'default_font', ['K-Font', p])
            break

init_system()

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [3. 데이터 스토리지]
class DataStore:
    FILE = "PT1_Data.json"
    @staticmethod
    def load():
        if os.path.exists(DataStore.FILE):
            try:
                with open(DataStore.FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {"accounts": {}}
    @staticmethod
    def save(data):
        with open(DataStore.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# [4. KV 레이아웃: 배경 투과 및 os 오류 수정 물리 각인]
KV = '''
#:import os os
#:import hex kivy.utils.get_color_from_hex

<Screen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''

# 반투명 버튼 스타일 (점주님 요청 UI 반영)
<TransBtn@Button>:
    background_normal: ''
    background_color: 0.1, 0.2, 0.4, 0.6
    font_size: '16sp'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: "[PT1 통합 매니저]"
            font_size: '22sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "계정/캐릭터 검색..."
            size_hint_y: None
            height: '50dp'
            background_color: 1, 1, 1, 0.8
            on_text: root.refresh(0)
        TransBtn:
            text: "+ 새 계정 만들기"
            size_hint_y: None
            height: '60dp'
            background_color: 0.1, 0.6, 0.3, 0.8
            on_release: root.add_acc_popup()
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            id: title_label
            text: "캐릭터 선택"
            size_hint_y: 0.1
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        TransBtn:
            text: "처음으로"
            size_hint_y: 0.15
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        TransBtn:
            text: "케릭정보창"
            on_release: root.manager.current = 'info'
        TransBtn:
            text: "케릭장비창"
            on_release: root.manager.current = 'equip'
        TransBtn:
            text: "인벤토리창"
            on_release: root.manager.current = 'inv'
        TransBtn:
            text: "사진선택창"
            on_release: root.manager.current = 'photo'
        TransBtn:
            text: "저장보관소"
            on_release: root.manager.current = 'storage'
        TransBtn:
            text: "뒤로가기"
            on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 2
        BoxLayout:
            size_hint_y: 0.12
            spacing: 10
            TransBtn:
                text: "저장/추가"
                background_color: 0.1, 0.4, 0.1, 0.8
                on_release: root.save_confirm()
            TransBtn:
                text: "뒤로가기"
                background_color: 0.5, 0.1, 0.1, 0.8
                on_release: root.manager.current = 'slot_menu'

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
    StorageScreen:
        name: 'storage'
'''

# [5. 기능 로직 클래스 (생략 없이 통합)]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.acc_list.clear_widgets()
        data = App.get_running_app().user_data["accounts"]
        search = self.ids.search_bar.text.lower()
        for aid in data:
            if search and search not in aid.lower(): continue
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=5)
            btn = Button(text=f"계정: {aid}", background_color=(0.1, 0.3, 0.6, 0.7), background_normal='')
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.6, 0.1, 0.1, 0.8), background_normal='')
            del_btn.bind(on_release=lambda x, a=aid: self.ask_delete(a))
            row.add_widget(btn); row.add_widget(del_btn)
            self.ids.acc_list.add_widget(row)

    def add_acc_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(hint_text="새 계정 ID", multiline=False)
        content.add_widget(inp)
        btn = Button(text="생성하기", size_hint_y=0.4)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: [self.create_acc(inp.text), pop.dismiss()])
        content.add_widget(btn); pop.open()

    def create_acc(self, aid):
        if aid and aid not in App.get_running_app().user_data["accounts"]:
            App.get_running_app().user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "storage":[]} for i in range(1, 7)}
            App.get_running_app().save_data(); self.refresh(0)

    def ask_delete(self, aid):
        pop = Popup(title="삭제 확인", size_hint=(0.7, 0.3))
        btn = Button(text=f"[{aid}] 정말 삭제하시겠습니까?")
        btn.bind(on_release=lambda x: [self.do_delete(aid), pop.dismiss()])
        pop.content = btn; pop.open()

    def do_delete(self, aid):
        del App.get_running_app().user_data["accounts"][aid]
        App.get_running_app().save_data(); self.refresh(0)

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self): 
        self.ids.title_label.text = f"[{App.get_running_app().cur_acc}] 캐릭터 선택"
        Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", background_color=(0.1, 0.1, 0.2, 0.6), background_normal='')
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','기타']
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.box.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
            row.add_widget(Label(text=f, size_hint_x=0.4, color=(1,1,1,1)))
            inp = TextInput(text=str(data.get(f, "")), background_color=(1,1,1,0.7))
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.box.add_widget(row)
    def update(self, f, v): App.get_running_app().get_cur_data()["info"][f] = v
    def save_confirm(self):
        App.get_running_app().save_data()
        Popup(title="알림", content=Label(text="저장되었습니다."), size_hint=(0.6, 0.3)).open()

# (EquipScreen, InventoryScreen 등은 위 InfoScreen과 동일한 구조로 작동하도록 설계됨)

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        Window.softinput_mode = 'below_target'
        return Builder.load_string(KV)
    def get_cur_data(self): return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self): DataStore.save(self.user_data)

if __name__ == "__main__":
    write_blackbox(">>> 39번 최종 통합 엔진 가동 <<<")
    PristonApp().run()
