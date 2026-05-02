import os, sys, traceback
from datetime import datetime

# [1. 블랙박스 및 엔진 방역 시스템]
def write_log(msg):
    path = "/storage/emulated/0/Download/PristonTale_Log.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except: pass

def crash_guard(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    write_log(f"!!! 시스템 붕괴 감지 !!!\n{err}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = crash_guard

# [2. Kivy 환경 설정 및 사전 방역]
os.environ['KIVY_NO_ARGS'] = '1'
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.core.window import Window
    from kivy.properties import BooleanProperty, StringProperty, ListProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.core.text import LabelBase
    from kivy.clock import Clock
    from kivy.uix.popup import Popup
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
except Exception as e:
    write_log(f"모듈 로드 실패: {e}")

Window.clearcolor = (0, 0, 0, 1)

# [3. 폰트 엔진 보호막 - 경로 직접 타격]
FONT_NAME = "Korean"
FONT_READY = False
# 점주님 확인 경로: 내장 저장공간 > Download > font.ttf
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
BG_PATH = "/storage/emulated/0/Download/bg.png"

if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
        FONT_READY = True
        write_log("폰트 엔진 정상 로드 완료")
    except: 
        write_log("폰트 등록 실패: 권한 또는 파일 손상")

# [4. KV 설계도: 튕김 원천 봉쇄 및 시각 최적화]
KV = f"""
#:import os os

<BaseButton@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    font_size: '16sp'
    background_normal: ''
    background_color: (0.1, 0.4, 0.2, 0.9)
    size_hint_y: None
    height: '50dp'

<ActionBtn@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    size_hint_x: None
    width: '70dp'
    font_size: '14sp'

<MainScreen>:
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
            source: '{BG_PATH}' if os.path.exists('{BG_PATH}') else ''
    BoxLayout:
        orientation: 'vertical'
        padding: '40dp'
        Widget:
            size_hint_y: 0.7
        BaseButton:
            text: '통합 관리 시스템 접속'
            on_release: app.root.current = 'menu'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '8dp'
        
        # 전체 검색바 (전 지역 적용)
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            TextInput:
                id: search_input
                hint_text: '검색 (캐릭터명, 아이템 등...)'
                multiline: False
                on_text: root.filter_items(self.text)
            BaseButton:
                text: '초기화'
                width: '80dp'
                size_hint_x: None
                on_release: search_input.text = ''

        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
        
        BaseButton:
            text: '메인 화면으로'
            on_release: app.root.current = 'main'

<EditorPopup>:
    title: '전체화면 편집기'
    size_hint: (0.95, 0.9)
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        TextInput:
            id: edit_box
            text: root.content
            multiline: True
            font_name: 'Korean' if app.is_font_ready else None
        BoxLayout:
            size_hint_y: None
            height: '55dp'
            spacing: '10dp'
            BaseButton:
                text: '저장'
                on_release: root.do_save()
            BaseButton:
                text: '삭제'
                background_color: (0.8, 0.2, 0.2, 1)
                on_release: root.do_delete()
            BaseButton:
                text: '닫기'
                on_release: root.dismiss()
"""

# [5. 데이터 및 팝업 로직]
class EditorPopup(Popup):
    content = StringProperty("")
    item_name = StringProperty("")

    def do_save(self):
        App.get_running_app().show_toast(f"[{self.item_name}] 데이터가 저장되었습니다.")
        self.dismiss()

    def do_delete(self):
        App.get_running_app().show_toast(f"[{self.item_name}] 데이터가 삭제되었습니다.")
        self.dismiss()

class MenuScreen(Screen):
    # 18개 정보 + 11개 장비 (총 29개 항목 전수 명시)
    INFO_ITEMS = ["이름", "클랜", "레벨", "기력", "직위", "공격력", "명중률", "방어력", "흡수력", "생명력", "기력(MP)", "지구력", "근력", "정신력", "재능", "민첩", "건강", "잔여포인트"]
    EQUIP_ITEMS = ["머리", "갑옷", "무기(한손)", "무기(두손)", "방패", "장갑", "신발", "암릿", "목걸이", "반지1", "반지2"]
    
    def on_enter(self):
        self.build_list()

    def build_list(self):
        self.ids.container.clear_widgets()
        all_list = self.INFO_ITEMS + self.EQUIP_ITEMS
        for i, name in enumerate(all_list):
            Clock.schedule_once(lambda dt, n=name: self.add_item_row(n), i * 0.02)

    def add_item_row(self, name):
        row = BoxLayout(size_hint_y=None, height='60dp', spacing='5dp')
        
        # 항목 레이블 (더블클릭 지원)
        lbl = Label(text=name, font_name='Korean' if App.get_running_app().is_font_ready else None, size_hint_x=0.4)
        lbl.bind(on_touch_down=lambda obj, touch: self.check_double_tap(obj, touch, name))
        
        # 입력창 (요약본)
        ti = TextInput(text="", multiline=False, font_name='Korean' if App.get_running_app().is_font_ready else None)
        
        # 수정/삭제 버튼
        btn_box = BoxLayout(size_hint_x=None, width='145dp', spacing='5dp')
        btn_box.add_widget(ActionBtn(text="저장", on_release=lambda x: App.get_running_app().show_toast(f"{name} 저장 완료")))
        btn_box.add_widget(ActionBtn(text="삭제", background_color=(0.7, 0.1, 0.1, 1), on_release=lambda x: App.get_running_app().show_toast(f"{name} 삭제 완료")))
        
        row.add_widget(lbl)
        row.add_widget(ti)
        row.add_widget(btn_box)
        self.ids.container.add_widget(row)

    def check_double_tap(self, obj, touch, name):
        if touch.is_double_tap and obj.collide_point(*touch.pos):
            EditorPopup(item_name=name, content=f"{name}의 세부 내용을 입력하세요.").open()

    def filter_items(self, query):
        # 전체 검색 필터 로직
        for row in self.ids.container.children:
            if query.lower() in row.children[2].text.lower() or query == "":
                row.height = '60dp'
                row.opacity = 1
            else:
                row.height = 0
                row.opacity = 0

class MainScreen(Screen): pass

class PristonTaleApp(App):
    is_font_ready = BooleanProperty(FONT_READY)

    def build(self):
        try:
            Builder.load_string(KV)
        except Exception as e:
            write_log(f"KV 로드 실패: {e}")
            
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm

    def show_toast(self, text):
        write_log(f"알림: {text}")
        # 안드로이드 화면 하단 출력 시뮬레이션
        print(f"[시스템 알림] {text}")

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception:
        write_log(f"기동 실패 상세:\n{traceback.format_exc()}")
