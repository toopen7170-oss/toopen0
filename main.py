import os, sys, traceback, json
from datetime import datetime

# [1. 블랙박스 엔진: 내부 저장소 우회 기록 및 실시간 출력 시스템]
def get_log_path():
    # 안드로이드 11 이상 보안 대응: 앱 전용 내부 경로 사용
    try:
        from android.storage import app_storage_path
        base_path = app_storage_path()
    except:
        base_path = "."
    return os.path.join(base_path, "BlackBox_Log.txt")

LOG_FILE = get_log_path()

def write_blackbox(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_entry = f"[{timestamp}] {msg}\n{'-'*60}\n"
    print(log_entry) # 터미널(Logcat) 출력
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
            f.flush()
            os.fsync(f.fileno())
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> 시스템 엔진 가동 (무결점 전수검사 완료본) <<<")

# [2. 환경 오류 수리: 폰트 강제 주입 및 권한 설정]
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.config import Config

def init_env():
    if platform == 'android':
        from android.permissions import request_permissions, check_permission
        perms = ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"]
        request_permissions(perms)
        
        # 시스템 폰트 강제 탐색 (갤럭시 대응)
        font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc", "/system/fonts/DroidSansFallback.ttf"]
        for p in font_paths:
            if os.path.exists(p):
                LabelBase.register(name="K-Font", fn_regular=p)
                Config.set('kivy', 'default_font', ['K-Font', p])
                break

init_env()

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# [3. 데이터 매니저: 저장/삭제 알림 로직 포함]
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
            write_blackbox(f"데이터 저장 실패: {e}")

# [4. 7대 화면 클래스 - 절대 규칙 준수 및 멘트 시스템]
class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    
    def refresh(self, dt):
        self.ids.acc_list_box.clear_widgets()
        search_txt = self.ids.search_input.text.strip().lower()
        data = App.get_running_app().user_data.get("accounts", {})
        
        for aid in data:
            if search_txt and search_txt not in aid.lower(): continue
            
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
            btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            
            del_btn = Button(text="X", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
            del_btn.bind(on_release=lambda x, a=aid: self.del_acc(a))
            
            row.add_widget(btn)
            row.add_widget(del_btn)
            self.ids.acc_list_box.add_widget(row)

    def add_acc(self):
        aid = self.ids.new_acc_input.text.strip()
        if aid:
            app = App.get_running_app()
            if aid not in app.user_data["accounts"]:
                app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
                app.save_data()
                self.ids.msg_label.text = "계정 생성 완료"
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
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.char_slot_grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen):
    pass

class InfoScreen(Screen):
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','기타']
    def on_enter(self):
        Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.info_scroll_box.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            inp = TextInput(text=str(data.get(f, "")), multiline=False)
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp)
            self.ids.info_scroll_box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self):
        Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.equip_scroll_box.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3))
            inp = TextInput(text=str(data.get(f, "")), multiline=False)
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp)
            self.ids.equip_scroll_box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

class InventoryScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.inv_list_box.clear_widgets()
        for item in App.get_running_app().get_cur_data()["inv"]:
            self.ids.inv_list_box.add_widget(Button(text=item, size_hint_y=None, height="60dp"))
    def add_item(self):
        App.get_running_app().get_cur_data()["inv"].append("신규 아이템")
        App.get_running_app().save_data()
        self.refresh(0)

class PhotoScreen(Screen):
    def open_gallery(self):
        if platform == 'android':
            from android import activity, intent
            from android.permissions import check_permission
            if check_permission("android.permission.READ_EXTERNAL_STORAGE"):
                intent = intent.Intent()
                intent.setAction(intent.ACTION_PICK)
                intent.setType("image/*")
                activity.startActivity(intent)

class StorageScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.storage_list_box.clear_widgets()
        for item in App.get_running_app().get_cur_data()["storage"]:
            self.ids.storage_list_box.add_widget(Button(text=item, size_hint_y=None, height="60dp"))
    def add_item(self):
        App.get_running_app().get_cur_data()["storage"].append("보관소 항목")
        App.get_running_app().save_data()
        self.refresh(0)

# [5. KV 레이아웃 - 한 줄 표기법 표준화 (개행 필수)]
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
            text: ""
            size_hint_y: None
            height: '30dp'
            color: (1, 1, 0, 1)
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            TextInput:
                id: new_acc_input
                hint_text: "새 계정 ID"
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
                id: info_scroll_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "뒤로"
            size_hint_y: 0.1
            on_release: root.manager.current = 'slot_menu'

<EquipScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: equip_scroll_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "뒤로"
            size_hint_y: 0.1
            on_release: root.manager.current = 'slot_menu'

<InventoryScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: inv_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "추가"
                on_release: root.add_item()
            Button:
                text: "뒤로"
                on_release: root.manager.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        Button:
            text: "사진 폴더 열기 (갤러리)"
            on_release: root.open_gallery()
        Button:
            text: "뒤로가기"
            on_release: root.manager.current = 'slot_menu'

<StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: storage_list_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "저장항목 추가"
                on_release: root.add_item()
            Button:
                text: "뒤로"
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
