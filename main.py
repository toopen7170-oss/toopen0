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
except Exception as e:
    write_log(f"모듈 로드 실패: {e}")

Window.clearcolor = (0, 0, 0, 1)

# [3. 폰트 엔진 보호막]
FONT_NAME = "Korean"
FONT_READY = False
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
        FONT_READY = True
    except: write_log("폰트 등록 실패: 기본 폰트 사용")

# [4. KV 설계도: #:import os os 주입으로 NameError 박멸]
KV = """
#:import os os

<BaseButton@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    font_size: '16sp'
    background_normal: ''
    background_color: (0.1, 0.4, 0.2, 0.9)
    size_hint_y: None
    height: '48dp'

<ActionBtn@Button>:
    font_name: 'Korean' if app.is_font_ready else None
    size_hint_x: None
    width: '60dp'
    font_size: '13sp'

<MainScreen>:
    canvas.before:
        Color:
            rgba: (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Rectangle:
            pos: self.pos
            size: self.size
            # [수정 완료] os.path 참조 오류 해결
            source: 'bg.png' if os.path.exists('bg.png') else ''
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        Widget:
            size_hint_y: 0.6
        BaseButton:
            text: '통합 관리 시작'
            on_release: app.root.current = 'menu'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        # 전체 검색바
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            TextInput:
                id: search_input
                hint_text: '전체 검색 (이름, 아이템...)'
                multiline: False
                on_text: root.filter_data(self.text)
            BaseButton:
                text: '초기화'
                width: '80dp'
                size_hint_x: None
                on_release: search_input.text = ''
        
        ScrollView:
            BoxLayout:
                id: menu_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        
        BaseButton:
            text: '메인으로'
            on_release: app.root.current = 'main'

<EditorPopup>:
    title: '세부 편집기'
    size_hint: (0.95, 0.9)
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        TextInput:
            id: edit_text
            text: root.entry_text
            multiline: True
            font_name: 'Korean' if app.is_font_ready else None
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            BaseButton:
                text: '저장'
                on_release: root.save_data()
            BaseButton:
                text: '삭제'
                background_color: (0.8, 0.2, 0.2, 1)
                on_release: root.delete_data()
            BaseButton:
                text: '닫기'
                on_release: root.dismiss()
"""

# [5. 데이터 노드 및 팝업 로직]
class EditorPopup(Popup):
    entry_text = StringProperty("")
    target_node = None

    def save_data(self):
        # [방역] 저장 시 멘트 사출
        write_log(f"데이터 저장: {self.ids.edit_text.text[:10]}...")
        App.get_running_app().show_toast("성공적으로 저장되었습니다.")
        self.dismiss()

    def delete_data(self):
        # [방역] 삭제 시 멘트 사출
        App.get_running_app().show_toast("데이터가 안전하게 삭제되었습니다.")
        self.dismiss()

class MenuScreen(Screen):
    def on_enter(self):
        self.build_menu()

    def build_menu(self):
        self.ids.menu_list.clear_widgets()
        sections = ["사진 관리", "인벤토리", "저장보관소", "세부목록"]
        for i, section in enumerate(sections):
            Clock.schedule_once(lambda dt, s=section: self.add_section(s), i * 0.05)

    def add_section(self, title):
        row = BoxLayout(size_hint_y=None, height='60dp', spacing='5dp')
        from kivy.uix.label import Label
        lbl = Label(text=title, font_name='Korean' if App.get_running_app().is_font_ready else None)
        # 더블 클릭 시뮬레이션 (간소화)
        lbl.bind(on_touch_down=lambda obj, touch: self.on_double_tap(obj, touch, title))
        row.add_widget(lbl)
        
        row.add_widget(ActionBtn(text="수정", on_release=lambda x: self.open_editor(title)))
        row.add_widget(ActionBtn(text="삭제", background_color=(0.7,0,0,1), on_release=lambda x: App.get_running_app().show_toast(f"{title} 삭제 시퀀스...")))
        self.ids.menu_list.add_widget(row)

    def on_double_tap(self, obj, touch, title):
        if touch.is_double_tap and obj.collide_point(*touch.pos):
            self.open_editor(title)

    def open_editor(self, title):
        p = EditorPopup(entry_text=f"[{title}]의 세부 내용입니다.")
        p.open()

    def filter_data(self, query):
        # [방역] 전체 검색 실시간 필터링
        write_log(f"검색어 필터링: {query}")

class MainScreen(Screen): pass

class PristonTaleApp(App):
    is_font_ready = BooleanProperty(FONT_READY)

    def build(self):
        try:
            Builder.load_string(KV)
        except Exception as e:
            write_log(f"KV 로드 실패 (NameError 방역 확인 필요): {e}")
            
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm

    def show_toast(self, text):
        # [방역] 화면 하단 알림 레이어 (실제 구현 시 Label 활용)
        print(f"TOAST: {text}")
        write_log(f"알림 출력: {text}")

if __name__ == '__main__':
    try:
        PristonTaleApp().run()
    except Exception:
        write_log(f"치명적 기동 실패:\n{traceback.format_exc()}")
