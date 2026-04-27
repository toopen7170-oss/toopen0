import os, sys, traceback, json, shutil
from datetime import datetime

# [물리 봉쇄 1순위: 모든 클래스 사전 선언]
# 엔진이 레이아웃을 읽기 전, 클래스 존재 여부로 인한 팅김을 방지합니다.
from kivy.uix.screenmanager import Screen

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [물리 봉쇄 2순위: 이중 각인 블랙박스 엔진]
INTERNAL_LOG = ""
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    try:
        from kivy.app import App
        if not INTERNAL_LOG:
            INTERNAL_LOG = os.path.join(App.get_running_app().user_data_dir, "Internal_Log.txt")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"

        # 내부 저장소 강제 기록
        with open(INTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
            f.flush(); os.fsync(f.fileno())

        # 외부 다운로드 폴더 복사 시도
        try:
            with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
                f.flush(); os.fsync(f.fileno())
        except: pass
    except:
        print(f"CRITICAL LOG FAIL: {msg}")

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [환경 초기화 및 폰트]
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform

# [KV 레이아웃: 배경 투과 UI & os 물리 각인]
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

<TransBtn@Button>:
    background_normal: ''
    background_color: 0.1, 0.2, 0.4, 0.6
    font_name: 'K-Font' if os.path.exists('/system/fonts/NanumGothic.ttf') else 'Roboto'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: "[PT1 강제 생존 엔진]"
            font_size: '20sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "검색어를 입력하세요..."
            size_hint_y: None
            height: '50dp'
            background_color: 1, 1, 1, 0.8
        ScrollView:
            BoxLayout: id: acc_list; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 5
        BoxLayout:
            size_hint_y: None; height: '60dp'; spacing: 5
            TransBtn: text: "비상 로그"; on_release: root.show_internal_log()
            TransBtn: text: "+ 계정 생성"; on_release: root.add_acc_popup()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 30
        GridLayout: id: grid; cols: 2; spacing: 15
        TransBtn: text: "뒤로가기"; size_hint_y: 0.2; on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 40; spacing: 15
        TransBtn: text: "케릭정보창"; on_release: root.manager.current = 'info'
        TransBtn: text: "케릭장비창"; on_release: root.manager.current = 'equip'
        TransBtn: text: "인벤토리창"; on_release: root.manager.current = 'inv'
        TransBtn: text: "사진선택창"; on_release: root.manager.current = 'photo'
        TransBtn: text: "저장보관소"; on_release: root.manager.current = 'storage'
        TransBtn: text: "뒤로가기"; on_release: root.manager.current = 'char_select'

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'; padding: 10
        ScrollView:
            BoxLayout: id: box; orientation: 'vertical'; size_hint_y: None; height: self.minimum_height; spacing: 2
        BoxLayout:
            size_hint_y: 0.12; spacing: 10
            TransBtn: text: "저장/확인"; on_release: root.save_confirm()
            TransBtn: text: "뒤로가기"; on_release: root.manager.current = 'slot_menu'

ScreenManager:
    MainScreen: name: 'main'
    CharSelectScreen: name: 'char_select'
    SlotMenuScreen: name: 'slot_menu'
    InfoScreen: name: 'info'
    EquipScreen: name: 'equip'
    InventoryScreen: name: 'inv'
    PhotoScreen: name: 'photo'
    StorageScreen: name: 'storage'
'''

# [기능 로직 구현: 제1원칙 7대 창 본체]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        try:
            self.ids.acc_list.clear_widgets()
            data = App.get_running_app().user_data.get("accounts", {})
            for aid in data:
                btn = Button(text=f"계정: {aid}", size_hint_y=None, height="60dp", background_color=(0.1, 0.3, 0.6, 0.7))
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                self.ids.acc_list.add_widget(btn)
        except Exception as e: write_blackbox(f"Refresh Error: {str(e)}")

    def add_acc_popup(self):
        App.get_running_app().user_data["accounts"]["NewAcc"] = {str(i): {"info":{}, "equip":{}, "inv":[], "storage":[]} for i in range(1, 7)}
        App.get_running_app().save_data(); self.refresh(0)

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid; self.manager.current = 'char_select'

    def show_internal_log(self):
        try:
            with open(INTERNAL_LOG, "r", encoding="utf-8") as f: content = f.read()
        except: content = "기록된 로그가 없습니다."
        from kivy.uix.popup import Popup
        Popup(title="내부 블랙박스 확인", content=Label(text=content[-500:]), size_hint=(0.9, 0.8)).open()

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", background_color=(0.1, 0.1, 0.2, 0.6))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)
    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i); self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    def on_enter(self):
        self.ids.box.clear_widgets()
        fields = ['이름','레벨','힘','민첩','건강','정신','재능','...기타 18종']
        for f in fields:
            row = BoxLayout(size_hint_y=None, height="50dp")
            row.add_widget(Label(text=f, size_hint_x=0.4))
            row.add_widget(TextInput(background_color=(1,1,1,0.7), multiline=False))
            self.ids.box.add_widget(row)
    def save_confirm(self): App.get_running_app().save_data()

class EquipScreen(Screen):
    def save_confirm(self): App.get_running_app().save_data()
class InventoryScreen(Screen):
    def save_confirm(self): pass
class PhotoScreen(Screen):
    def save_confirm(self): pass
class StorageScreen(Screen):
    def save_confirm(self): pass

# [물리 봉쇄 3순위: 시동 순서 격리 엔진]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""; cur_slot = ""

    def build(self):
        Window.softinput_mode = 'below_target'
        # 폰트 선제적 매핑
        font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc"]
        for p in font_paths:
            if os.path.exists(p):
                LabelBase.register(name="K-Font", fn_regular=p)
                Config.set('kivy', 'default_font', ['K-Font', p]); break
        return Builder.load_string(KV)

    def on_start(self):
        # 배경화면 출력 후 0.5초 뒤 로직 실행 (프리징 봉쇄)
        Clock.schedule_once(self.deferred_init, 0.5)

    def deferred_init(self, dt):
        write_blackbox(">>> 강제 생존 엔진 시동 성공 <<<")
        if platform == 'android':
            from android.permissions import request_permissions
            request_permissions(["android.permission.WRITE_EXTERNAL_STORAGE", "android.permission.READ_EXTERNAL_STORAGE"])
        # 데이터 로드 시도
        try:
            if os.path.exists("PT1_Data.json"):
                with open("PT1_Data.json", "r", encoding="utf-8") as f: self.user_data = json.load(f)
        except Exception as e: write_blackbox(f"Data Load Error: {str(e)}")

    def save_data(self):
        try:
            with open("PT1_Data.json", "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e: write_blackbox(f"Save Error: {str(e)}")

if __name__ == "__main__":
    PristonApp().run()
