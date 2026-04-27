import os, sys, traceback, json, shutil
from datetime import datetime

# [1. 물리 봉쇄: 모든 클래스 선행 각인]
# KV가 로드되기 전 모든 클래스가 존재해야 ParserException이 발생하지 않습니다.
from kivy.uix.screenmanager import Screen

class MainScreen(Screen): pass
class CharSelectScreen(Screen): pass
class SlotMenuScreen(Screen): pass
class InfoScreen(Screen): pass
class EquipScreen(Screen): pass
class InventoryScreen(Screen): pass
class PhotoScreen(Screen): pass
class StorageScreen(Screen): pass

# [2. 생존형 블랙박스: 이중 경로 시스템]
INTERNAL_LOG = ""
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and not INTERNAL_LOG:
            INTERNAL_LOG = os.path.join(app.user_data_dir, "Internal_Log.txt")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"

        if INTERNAL_LOG:
            with open(INTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
                f.flush(); os.fsync(f.fileno())

        try:
            with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
                f.write(full_msg)
                f.flush(); os.fsync(f.fileno())
        except: pass
    except: pass

sys.excepthook = lambda t, v, tb: write_blackbox("".join(traceback.format_exception(t, v, tb)))

# [3. Kivy 시스템 초기화]
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform

# [4. KV 레이아웃: 문법 오류 물리 봉쇄 (1줄 1속성 원칙)]
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
    font_size: '16sp'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: "[PT1 매니저: 강제 생존 시스템]"
            font_size: '22sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "전체 검색 (ID/이름)..."
            size_hint_y: None
            height: '50dp'
            multiline: False
            background_color: 1, 1, 1, 0.8
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
            TransBtn:
                text: "비상 로그"
                on_release: root.show_internal_log()
            TransBtn:
                text: "+ 계정 추가"
                on_release: root.add_acc_popup()

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
            size_hint_y: 0.2
            on_release: root.manager.current = 'main'

<SlotMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 10
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

<InfoScreen>, <EquipScreen>, <InventoryScreen>, <PhotoScreen>, <StorageScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            BoxLayout:
                id: box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: 0.12
            spacing: 10
            TransBtn:
                text: "데이터 저장"
                on_release: root.save_confirm()
            TransBtn:
                text: "뒤로가기"
                on_release: root.manager.current = 'slot_menu'

ScreenManager:
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
'''

# [5. 기능 로직: 제1원칙 기반 7대 창 구현]
class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh, 0.1)
    
    def refresh(self, dt):
        try:
            self.ids.acc_list.clear_widgets()
            data = App.get_running_app().user_data.get("accounts", {})
            for aid in data:
                btn = Button(text=f"계정: {aid}", size_hint_y=None, height="65dp", background_color=(0.1, 0.4, 0.7, 0.7))
                btn.bind(on_release=lambda x, a=aid: self.go_acc(a))
                self.ids.acc_list.add_widget(btn)
        except Exception as e:
            write_blackbox(f"Refresh Error: {str(e)}")

    def add_acc_popup(self):
        aid = f"User_{datetime.now().strftime('%M%S')}"
        app = App.get_running_app()
        app.user_data["accounts"][aid] = {str(i): {"info":{}, "equip":{}, "inv":[], "storage":[]} for i in range(1, 7)}
        app.save_data()
        self.refresh(0)

    def go_acc(self, aid):
        App.get_running_app().cur_acc = aid
        self.manager.current = 'char_select'

    def show_internal_log(self):
        try:
            with open(INTERNAL_LOG, "r", encoding="utf-8") as f:
                content = f.read()[-1000:]
        except:
            content = "기록된 로그가 없습니다."
        from kivy.uix.popup import Popup
        Popup(title="내부 블랙박스 (최근 1000자)", content=Label(text=content), size_hint=(0.9, 0.8)).open()

class CharSelectScreen(Screen):
    def on_enter(self):
        self.ids.title_label.text = f"[{App.get_running_app().cur_acc}] 케릭 선택"
        Clock.schedule_once(self.build_slots, 0.1)

    def build_slots(self, dt):
        self.ids.grid.clear_widgets()
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", background_color=(0.2, 0.2, 0.3, 0.7))
            btn.bind(on_release=lambda x, idx=i: self.go_slot(idx))
            self.ids.grid.add_widget(btn)

    def go_slot(self, i):
        App.get_running_app().cur_slot = str(i)
        self.manager.current = 'slot_menu'

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    fields = ['이름','레벨','힘','민첩','건강','정신','재능','생명력','기력','근력','명중','공격','방어','흡수','속도','클랜','직위','기타']
    def on_enter(self):
        self.ids.box.clear_widgets()
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
            row.add_widget(Label(text=f, size_hint_x=0.4))
            row.add_widget(TextInput(multiline=False, background_color=(1,1,1,0.8)))
            self.ids.box.add_widget(row)
    def save_confirm(self):
        App.get_running_app().save_data()

class EquipScreen(Screen):
    def save_confirm(self): App.get_running_app().save_data()
class InventoryScreen(Screen):
    def save_confirm(self): pass
class PhotoScreen(Screen):
    def save_confirm(self): pass
class StorageScreen(Screen):
    def save_confirm(self): pass

# [6. 앱 메인 엔진: 시동 격리 및 강제 생존]
class PristonApp(App):
    user_data = {"accounts": {}}
    cur_acc = ""
    cur_slot = ""

    def build(self):
        Window.softinput_mode = 'below_target'
        # 시스템 폰트 강제 매핑
        font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc"]
        for p in font_paths:
            if os.path.exists(p):
                LabelBase.register(name="K-Font", fn_regular=p)
                Config.set('kivy', 'default_font', ['K-Font', p])
                break
        return Builder.load_string(KV)

    def on_start(self):
        # 시동 멈춤 봉쇄: UI 로드 0.5초 후 권한 및 데이터 처리
        Clock.schedule_once(self.deferred_init, 0.5)

    def deferred_init(self, dt):
        write_blackbox(">>> 강제 생존 엔진: 시동 완료 <<<")
        if platform == 'android':
            from android.permissions import request_permissions
            request_permissions(["android.permission.WRITE_EXTERNAL_STORAGE", "android.permission.READ_EXTERNAL_STORAGE"])
        
        try:
            if os.path.exists("PT1_Data.json"):
                with open("PT1_Data.json", "r", encoding="utf-8") as f:
                    self.user_data = json.load(f)
        except Exception as e:
            write_blackbox(f"Init Error: {str(e)}")

    def save_data(self):
        try:
            with open("PT1_Data.json", "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            write_blackbox(f"Save Error: {str(e)}")

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        # 최후의 보루: 실행 단계에서 팅길 시 콘솔 기록
        print(f"FATAL ERROR: {str(e)}")
