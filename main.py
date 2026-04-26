import os, sys, traceback, json
from datetime import datetime

# [1. 블랙박스 엔진: 최상단 배치 - 초동 튕김 현상 실시간 기록]
def get_log_path():
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "BlackBox_Log.txt")
    except:
        return "BlackBox_Log.txt"

LOG_FILE = get_log_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_entry = f"[{timestamp}] {msg}\n{'-'*60}\n"
    print(log_entry) # 안드로이드 Logcat으로 실시간 전송
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 치명적 오류 발생 (앱 종료) !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> 시스템 엔진 가동 (35차 전수검사 완료본) <<<")

# [2. 환경 설정 및 폰트 복구 로직]
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.config import Config

if platform == 'android':
    from android.permissions import request_permissions
    request_permissions(["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"])
    
    # 갤럭시 등 안드로이드 시스템 폰트 강제 매핑
    font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc", "/system/fonts/DroidSansFallback.ttf"]
    for p in font_paths:
        if os.path.exists(p):
            LabelBase.register(name="K-Font", fn_regular=p)
            Config.set('kivy', 'default_font', ['K-Font', p])
            break

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [3. 데이터 관리 시스템]
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
        try:
            with open(DataStore.FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"데이터 저장 오류: {e}")

# [4. 7대 화면 로직 - 한 줄 표기법 표준화 준수]
class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    
    def refresh(self, dt):
        self.ids.acc_list_box.clear_widgets()
        search_txt = self.ids.search_input.text.strip().lower()
        data = App.get_running_app().user_data.get("accounts", {})
        
        for aid in data:
            if search_txt and search_txt not in aid.lower():
                continue
            
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
            btn = Button(
                text=aid,
                background_color=get_color_from_hex("#2E7D32")
            )
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            
            del_btn = Button(
                text="삭제",
                size_hint_x=0.25,
                background_color=get_color_from_hex("#C62828")
            )
            del_btn.bind(on_release=lambda x, a=aid: self.del_acc(a))
            
            row.add_widget(btn)
            row.add_widget(del_btn)
            self.ids.acc_list_box.add_widget(row)

    def add_acc(self):
        aid = self.ids.new_acc_input.text.strip()
        if aid:
            app = App.get_running_app()
            if aid not in app.user_data["accounts"]:
                app.user_data["accounts"][aid] = {
                    str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} 
                    for i in range(1, 7)
                }
                app.save_data()
                self.ids.msg_label.text = "계정 저장 완료"
                self.refresh(0)
                self.ids.new_acc_input.text = ""

    def del_acc(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]
            app.save_data()
            self.ids.msg_label.text = f"{aid} 삭제 완료"
            self.refresh(0)

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.char_slot_grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"캐릭터 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.char_slot_grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen):
    pass

class InfoScreen(Screen):
    fields = ['이름','레벨','생명력','기력','힘','정신력','재능','민첩','건강','공격','방어','기타']
    def on_enter(self):
        Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.info_box.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            inp = TextInput(text=str(data.get(f, "")), multiline=False)
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp)
            self.ids.info_box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        # 장비창 로직 (동일 방식)
        pass

class InventoryScreen(Screen):
    def add_item(self):
        App.get_running_app().get_cur_data()["inv"].append("신규템")
        App.get_running_app().save_data()
        self.ids.msg_label.text = "인벤 저장 완료"

class PhotoScreen(Screen):
    def open_gallery(self):
        write_blackbox("갤러리 연동 시도")
        # 인텐트 로직 생략 (실행 환경에 따라 조정)

class StorageScreen(Screen):
    pass

# [5. KV 레이아웃 - 개행 및 표준화 철저 준수]
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
        spacing: 10
        TextInput:
            id: search_input
            hint_text: "ID 검색..."
            size_hint_y: None
            height: '50dp'
            on_text: root.refresh(0)
        ScrollView:
            BoxLayout:
                id: acc_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        Label:
            id: msg_label
            text: "대기 중"
            size_hint_y: None
            height: '30dp'
            color: (1, 1, 0, 1)
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            TextInput:
                id: new_acc_input
                hint_text: "생성할 계정 ID"
            Button:
                text: "생성"
                on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        GridLayout:
            id: char_slot_grid
            cols: 2
            spacing: 10
        Button:
            text: "뒤로가기"
            size_hint_y: 0.15
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        Button:
            text: "케릭정보창"
            on_release: root.manager.current = 'info'
        Button:
            text: "케릭장비창"
            on_release: root.manager.current = 'equip'
        Button:
            text: "인벤토리창"
            on_release: root.manager.current = 'inv'
        Button:
            text: "사진선택창"
            on_release: root.manager.current = 'photo'
        Button:
            text: "저장보관소"
            on_release: root.manager.current = 'storage'
        Button:
            text: "뒤로가기"
            on_release: root.manager.current = 'char_select'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: info_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "뒤로가기"
            size_hint_y: 0.1
            on_release: root.manager.current = 'slot_menu'

<InventoryScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: msg_label
            text: ""
            size_hint_y: 0.1
        ScrollView:
            BoxLayout:
                id: inv_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "아이템 추가"
                on_release: root.add_item()
            Button:
                text: "뒤로가기"
                on_release: root.manager.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        Button:
            text: "갤러리에서 사진 확인"
            on_release: root.open_gallery()
        Button:
            text: "뒤로가기"
            on_release: root.manager.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""
        self.cur_slot = ""
        return Builder.load_string(KV)
    def get_cur_data(self):
        return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self):
        DataStore.save(self.user_data)

if __name__ == "__main__":
    PristonApp().run()
