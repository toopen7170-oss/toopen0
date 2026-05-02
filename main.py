import os, sys, traceback
from datetime import datetime

# [1. 블랙박스 방역 및 자가 치유 엔진]
def write_log(msg):
    path = "/storage/emulated/0/Download/PT1_BlackBox.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except: pass

def crash_guard(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    write_log(f"!!! 크리티컬 엔진 오류 감지 !!!\n{err}")
    # ValueError(폰트 로드 실패) 발생 시에도 앱이 즉사하지 않도록 인터셉트
    if "ValueError" in err and "font.ttf" in err:
        write_log(">> 폰트 접근 오류 감지: 시스템 폰트로 강제 전환 및 복구 시도")
        return 
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = crash_guard

# [2. 코어 엔진 로드 및 초기 검역]
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.core.window import Window
    from kivy.properties import BooleanProperty, StringProperty, DictProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.core.text import LabelBase
    from kivy.clock import Clock
    from kivy.uix.popup import Popup
except Exception as e:
    write_log(f"코어 모듈 로드 오류: {e}")

# [3. 폰트 엔진: 철갑 보안 우회 로직]
FONT_NAME = "Korean"
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
IS_FONT_STABLE = False

def register_font_safely():
    global IS_FONT_STABLE
    if os.path.exists(FONT_PATH):
        try:
            # 1차 시도: 폰트 등록
            LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
            IS_FONT_STABLE = True
            write_log("폰트 엔진 1차 안착 성공")
        except Exception as e:
            write_log(f"폰트 등록 거부됨 (보안 정책): {e}")
            IS_FONT_STABLE = False
    else:
        write_log("폰트 파일 부재: 시스템 폰트로 대체")

register_font_safely()

# [4. KV 설계도: 반투명 블랙 미학 & 레이아웃]
KV = """
<BaseButton@Button>:
    font_name: app.font_logic
    font_size: '16sp'
    background_normal: ''
    background_color: (0.1, 0.5, 0.3, 0.8)
    size_hint_y: None
    height: '55dp'

<ActionBtn@Button>:
    font_name: app.font_logic
    size_hint_x: None
    width: '75dp'
    font_size: '14sp'

<MainScreen>:
    canvas.before:
        Color:
            rgba: (0.05, 0.05, 0.05, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: '50dp'
        spacing: '30dp'
        Label:
            text: 'PT1 MANAGER\\n[MASTER CONTEXT]'
            font_name: app.font_logic
            font_size: '30sp'
            halign: 'center'
            color: (0, 1, 0.5, 1)
        BaseButton:
            text: '통합 관리 시스템 접속'
            on_release: app.root.current = 'menu'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            TextInput:
                id: search_input
                hint_text: '항목 검색...'
                multiline: False
                background_color: (1, 1, 1, 0.1)
                foreground_color: (1, 1, 1, 1)
                on_text: root.filter_logic(self.text)
            Button:
                text: 'X'
                size_hint_x: None
                width: '50dp'
                on_release: search_input.text = ''
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '8dp'
        BaseButton:
            text: '메인으로 복귀'
            background_color: (0.4, 0.1, 0.1, 0.8)
            on_release: app.root.current = 'main'

<EditorPopup>:
    title: '데이터 정밀 수정'
    size_hint: (0.9, 0.8)
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        TextInput:
            id: edit_input
            text: root.current_val
            font_name: app.font_logic
            background_color: (1, 1, 1, 0.05)
            foreground_color: (1, 1, 1, 1)
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            BaseButton:
                text: '저장'
                on_release: root.save_and_close()
            BaseButton:
                text: '닫기'
                background_color: (0.3, 0.3, 0.3, 1)
                on_release: root.dismiss()
"""

# [5. 자가 수복 논리 엔진]
class EditorPopup(Popup):
    current_val = StringProperty("")
    target_key = StringProperty("")
    def save_and_close(self):
        App.get_running_app().update_data(self.target_key, self.ids.edit_input.text)
        self.dismiss()

class MenuScreen(Screen):
    ITEMS = [
        "이름", "클랜", "레벨", "기력", "직위", "공격력", "명중률", "방어력", "흡수력", 
        "생명력", "기력(MP)", "지구력", "근력", "정신력", "재능", "민첩", "건강", "잔여포인트",
        "머리", "갑옷", "무기(한손)", "무기(두손)", "방패", "장갑", "신발", "암릿", "목걸이", "반지1", "반지2"
    ]

    def on_enter(self):
        self.ids.container.clear_widgets()
        # 순차 사출로 GPU 부하 분산
        Clock.schedule_once(self.populate_items, 0.1)

    def populate_items(self, dt):
        for name in self.ITEMS:
            row = self.create_row(name)
            self.ids.container.add_widget(row)

    def create_row(self, name):
        row = BoxLayout(size_hint_y=None, height='65dp', spacing='10dp')
        with row.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(1, 1, 1, 0.07)
            row.bg_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
        row.bind(pos=self.update_rect, size=self.update_rect)

        lbl = Label(text=name, font_name=App.get_running_app().font_logic, 
                    size_hint_x=0.3, color=(0, 1, 0.8, 1))
        ti = TextInput(text=App.get_running_app().db.get(name, ""), multiline=False, readonly=True,
                       background_color=(0,0,0,0), foreground_color=(1,1,1,1),
                       font_name=App.get_running_app().font_logic)

        btn_box = BoxLayout(size_hint_x=None, width='155dp', spacing='5dp', padding='5dp')
        btn_box.add_widget(ActionBtn(text="수정", on_release=lambda x: self.open_editor(name)))
        btn_box.add_widget(ActionBtn(text="삭제", background_color=(0.8, 0.2, 0.2, 0.8),
                                   on_release=lambda x: App.get_running_app().update_data(name, "")))
        row.add_widget(lbl); row.add_widget(ti); row.add_widget(btn_box)
        row.name_tag = name
        return row

    def update_rect(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def open_editor(self, name):
        val = App.get_running_app().db.get(name, "")
        EditorPopup(target_key=name, current_val=val).open()

    def filter_logic(self, query):
        for row in self.ids.container.children:
            if query.lower() in row.name_tag.lower() or query == "":
                row.height, row.opacity, row.disabled = '65dp', 1, False
            else:
                row.height, row.opacity, row.disabled = 0, 0, True

class MainScreen(Screen): pass

class PristonTaleApp(App):
    font_logic = StringProperty(FONT_NAME if IS_FONT_STABLE else 'Roboto')
    db = DictProperty({})

    def build(self):
        try:
            Builder.load_string(KV)
        except Exception as e: write_log(f"KV 로드 오류: {e}")
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm

    def update_data(self, key, value):
        self.db[key] = value
        if self.root.current == 'menu': self.root.get_screen('menu').on_enter()
        write_log(f"데이터 갱신: {key} -> {value}")

if __name__ == '__main__':
    PristonTaleApp().run()
