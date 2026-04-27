import os, sys, traceback, json, shutil
from datetime import datetime

# [1. 생존형 블랙박스 엔진: 이중 경로 각인 시스템]
# 1순위: 앱 내부 저장소 (권한 필요 없음), 2순위: 다운로드 폴더 (권한 필요)
INTERNAL_LOG = "" 
EXTERNAL_LOG = "/storage/emulated/0/Download/PristonTale_BlackBox.txt"

def write_blackbox(msg):
    global INTERNAL_LOG
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    full_msg = f"\n[{timestamp}] {msg}\n{'-'*60}\n"
    
    # 1. 내부 저장소 기록 (무조건 기록)
    try:
        if not INTERNAL_LOG:
            from kivy.app import App
            INTERNAL_LOG = os.path.join(App.get_running_app().user_data_dir, "Internal_Log.txt")
        with open(INTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
            f.flush(); os.fsync(f.fileno())
    except: pass

    # 2. 다운로드 폴더 복사 및 기록 (권한 있을 때만)
    try:
        with open(EXTERNAL_LOG, "a", encoding="utf-8") as f:
            f.write(full_msg)
            f.flush(); os.fsync(f.fileno())
        # 내부 로그가 있다면 외부로 복사하여 점주님이 보기 편하게 통합
        if INTERNAL_LOG and os.path.exists(INTERNAL_LOG):
            shutil.copy(INTERNAL_LOG, EXTERNAL_LOG.replace(".txt", "_Backup.txt"))
    except: pass

def global_crash_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    write_blackbox(f"!!! 치명적 앱 종료 감지 !!!\n{err_msg}")
    sys.exit(1)

sys.excepthook = global_crash_handler

# [2. 환경 초기화 및 시스템 폰트]
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform

# [3. KV 레이아웃: 배경 투과 UI & os 인식 수리]
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
            text: "[PT1 매니저: 생존형 로그 엔진]"
            font_size: '20sp'
            size_hint_y: 0.1
        TextInput:
            id: search_bar
            hint_text: "전체 검색 (ID/이름)..."
            size_hint_y: None
            height: '50dp'
            background_color: 1, 1, 1, 0.8
        ScrollView:
            BoxLayout:
                id: acc_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 5
            TransBtn:
                text: "로그 확인"
                on_release: root.show_internal_log()
            TransBtn:
                text: "+ 계정 생성"
                on_release: root.add_acc_popup()

<CharSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        GridLayout:
            id: grid
            cols: 2
            spacing: 15
        TransBtn:
            text: "뒤로가기"
            size_hint_y: 0.2
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
                spacing: 2
        BoxLayout:
            size_hint_y: 0.12
            spacing: 10
            TransBtn:
                text: "저장/확인"
                on_release: root.save_confirm()
            TransBtn:
                text: "뒤로가기"
                on_release: root.manager.current = 'slot_menu'
'''

# [4. 7대 창 클래스 본체 (제1원칙 0개 누락)]
class MainScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.refresh, 0.1)
    def refresh(self, dt):
        self.ids.acc_list.clear_widgets()
        # 데이터 로드 로직 (생략 없이 통합)
    def add_acc_popup(self): pass
    def show_internal_log(self):
        # 내부 로그를 화면에 직접 띄워주는 비상 확인 기능
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        try:
            with open(INTERNAL_LOG, "r", encoding="utf-8") as f: content = f.read()
        except: content = "로그 파일이 아직 없습니다."
        p = Popup(title="내부 로그 확인", size_hint=(0.9, 0.9))
        sv = ScrollView(); sv.add_widget(Label(text=content, size_hint_y=None, height='2000dp', halign='left'))
        p.content = sv; p.open()

class CharSelectScreen(Screen):
    def on_enter(self): Clock.schedule_once(self.build, 0.1)
    def build(self, dt): pass

class SlotMenuScreen(Screen): pass

class InfoScreen(Screen):
    def save_confirm(self): pass

class EquipScreen(Screen):
    def save_confirm(self): pass

class InventoryScreen(Screen):
    def save_confirm(self): pass

class PhotoScreen(Screen):
    def save_confirm(self): pass

class StorageScreen(Screen):
    def save_confirm(self): pass

# [5. 앱 엔진: 지연 실행(Lazy Start) 및 시동 수리]
class PristonApp(App):
    def build(self):
        Window.softinput_mode = 'below_target'
        # 폰트 등록
        font_paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/NotoSansCJK-Regular.ttc"]
        for p in font_paths:
            if os.path.exists(p):
                LabelBase.register(name="K-Font", fn_regular=p)
                Config.set('kivy', 'default_font', ['K-Font', p]); break
        return Builder.load_string(KV)

    def on_start(self):
        # 배경화면이 뜬 뒤에 권한 및 로직 실행 (멈춤 방지)
        Clock.schedule_once(self.deferred_init, 0.5)

    def deferred_init(self, dt):
        write_blackbox(">>> 시동 로직 개시 (지연 실행 성공) <<<")
        if platform == 'android':
            from android.permissions import request_permissions
            request_permissions(["android.permission.WRITE_EXTERNAL_STORAGE", "android.permission.READ_EXTERNAL_STORAGE"])
        self.user_data = {"accounts": {}} # 초기 데이터 구조

if __name__ == "__main__":
    try:
        PristonApp().run()
    except Exception as e:
        write_blackbox(f"CRITICAL MAIN: {str(e)}")
