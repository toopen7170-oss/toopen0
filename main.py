import os, sys, traceback, json, time
from datetime import datetime

# [1. 블랙박스 엔진: 다운로드 폴더 물리 각인 시스템]
def get_download_path():
    # 안드로이드 11 이상 권한 및 보안 대응
    path = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"
    try:
        # 경로 접근 권한 테스트 및 디렉토리 확인
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
        # 파일 열기 -> 쓰기 -> 플러시 -> 물리싱크(os.fsync) -> 닫기
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {msg}\n{'-'*60}\n")
            f.flush()
            os.fsync(f.fileno()) # 튕길 때 로그 유실 방지 핵심 로직
    except:
        print(f"LOG FAIL: {msg}")

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 앱 종료 원인 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler
write_blackbox(">>> 시스템 엔진 가동 (전수검사 완료 최종본) <<<")

# [2. 환경 오류 수리: 5대 필수 권한 및 전역 한글 폰트 적용]
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.config import Config

def init_system():
    if platform == 'android':
        from android.permissions import request_permissions
        # 5대 권한: 읽기, 쓰기, 미디어사진, 전체파일관리, 인터넷
        perms = [
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_MEDIA_IMAGES",
            "android.permission.MANAGE_EXTERNAL_STORAGE",
            "android.permission.INTERNET"
        ]
        request_permissions(perms)
        
        # 시스템 폰트 강제 매핑 (한글 깨짐 방지)
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

# [3. 데이터 매니저]
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
        except: pass

# [4. 7대 창 구조 (제1원칙 절대 준수)]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.acc_list.clear_widgets()
        search = self.ids.search_bar.text.strip().lower()
        data = App.get_running_app().user_data.get("accounts", {})
        for aid in data:
            if search and search not in aid.lower(): continue
            row = BoxLayout(size_hint_y=None, height="70dp", spacing=10)
            btn = Button(text=aid, background_color=get_color_from_hex("#2E7D32"))
            btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
            del_btn = Button(text="삭제", size_hint_x=0.2, background_color=get_color_from_hex("#C62828"))
            del_btn.bind(on_release=lambda x, a=aid: self.ask_confirm("삭제", aid))
            row.add_widget(btn); row.add_widget(del_btn)
            self.ids.acc_list.add_widget(row)

    def ask_confirm(self, mode, target):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text=f"정말 {mode}하시겠습니까? \n대상: {target}"))
        btn_box = BoxLayout(size_hint_y=0.4, spacing=10)
        p = Popup(title=f"{mode} 확인", content=content, size_hint=(0.8, 0.4))
        yes = Button(text="확인", on_release=lambda x: [self.del_acc(target) if mode=="삭제" else None, p.dismiss()])
        no = Button(text="취소", on_release=p.dismiss)
        btn_box.add_widget(yes); btn_box.add_widget(no); content.add_widget(btn_box); p.open()

    def del_acc(self, aid):
        app = App.get_running_app()
        if aid in app.user_data["accounts"]:
            del app.user_data["accounts"][aid]
            app.save_data(); self.refresh(0)

    def add_acc(self):
        aid = self.ids.new_acc_input.text.strip()
        if aid:
            app = App.get_running_app()
            if aid not in app.user_data["accounts"]:
                app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "pics":[], "storage":[]} for i in range(1, 7)}
                app.save_data(); self.refresh(0); self.ids.new_acc_input.text = ""

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.grid.clear_widgets()
        acc = App.get_running_app().user_data["accounts"][App.get_running_app().cur_acc]
        for i in range(1, 7):
            name = acc[str(i)]["info"].get("이름", f"슬롯 {i}")
            btn = Button(text=name, background_color=get_color_from_hex("#1B5E20"))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen):
    pass

class InfoScreen(Screen):
    fields = ['이름','직위','클랜','레벨','생명력','기력','근력','힘','정신력','재능','민첩','건강','명중','공격','방어','흡수','속도','기타']
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.box.clear_widgets()
        data = App.get_running_app().get_cur_data()["info"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, halign='center'))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center')
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["info"][f] = v
        App.get_running_app().save_data()

class EquipScreen(Screen):
    fields = ["한손무기", "두손무기", "갑옷", "방패", "장갑", "부츠", "암릿", "링1", "링2", "아뮬랫", "기타"]
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.box.clear_widgets()
        data = App.get_running_app().get_cur_data()["equip"]
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, halign='center'))
            inp = TextInput(text=str(data.get(f, "")), multiline=False, halign='center')
            inp.bind(text=lambda inst, v, f=f: self.update(f, v))
            row.add_widget(inp); self.ids.box.add_widget(row)
    def update(self, f, v):
        App.get_running_app().get_cur_data()["equip"][f] = v
        App.get_running_app().save_data()

class InventoryScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.list.clear_widgets()
        for item in App.get_running_app().get_cur_data()["inv"]:
            self.ids.list.add_widget(Button(text=item, size_hint_y=None, height="60dp"))
    def add_item(self):
        App.get_running_app().get_cur_data()["inv"].append("새 아이템")
        App.get_running_app().save_data(); self.refresh(0)

class PhotoScreen(Screen):
    def open_gallery(self):
        if platform == 'android':
            from android import activity, intent
            itnt = intent.Intent(); itnt.setAction(intent.ACTION_PICK); itnt.setType("image/*")
            activity.startActivity(itnt)

class StorageScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.list.clear_widgets()
        for item in App.get_running_app().get_cur_data()["storage"]:
            self.ids.list.add_widget(Button(text=item, size_hint_y=None, height="60dp"))
    def add_item(self):
        App.get_running_app().get_cur_data()["storage"].append("보관소 항목")
        App.get_running_app().save_data(); self.refresh(0)

# [5. KV 레이아웃: 배경이미지 전역 적용 및 표준화]
KV = '''
<Screen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.png' if os.path.exists('bg.png') else ''

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
            id: search_bar
            hint_text: "전체 검색 (ID/이름)..."
            size_hint_y: None
            height: '50dp'
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
                id: new_acc_input
                hint_text: "새 계정 ID 입력"
            Button:
                text: "생성"
                on_release: root.add_acc()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        Button:
            text: "뒤로가기"
            size_hint_y: 0.1
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

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                id: box if hasattr(self, 'box') else list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "추가" if root.name in ['inv', 'storage'] else "저장확인"
                on_release: root.add_item() if root.name in ['inv', 'storage'] else None
            Button:
                text: "뒤로가기"
                on_release: root.manager.current = 'slot_menu'

<PhotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        Button:
            text: "갤러리 사진 확인"
            on_release: root.open_gallery()
        Button:
            text: "뒤로가기"
            on_release: root.manager.current = 'slot_menu'
'''

class PristonApp(App):
    def build(self):
        self.user_data = DataStore.load()
        self.cur_acc = ""; self.cur_slot = ""
        # 자동 스크롤: 입력창 포커스 시 자판 위로 이동
        Window.softinput_mode = 'below_target'
        return Builder.load_string(KV)
    def get_cur_data(self):
        return self.user_data["accounts"][self.cur_acc][self.cur_slot]
    def save_data(self):
        DataStore.save(self.user_data)

if __name__ == "__main__":
    PristonApp().run()
