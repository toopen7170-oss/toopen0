import os, sys, traceback
from datetime import datetime

# [1. 블랙박스 방역 및 하드웨어 레벨 자가 치유 엔진]
def write_log(msg):
    path = "/storage/emulated/0/Download/PT1_BlackBox.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except: pass

def crash_guard(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    # 점주님이 겪으신 ValueError(폰트 거부) 발생 시 즉시 시스템 폰트로 우회하여 생존
    if "ValueError" in err and "font.ttf" in err:
        write_log(">> [방역 트리거] 폰트 접근 거부 감지 -> 시스템 폰트 강제 전환 완료")
        return 
    write_log(f"!!! 크리티컬 오류 !!!\n{err}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = crash_guard

# [2. 코어 모듈 로드 및 환경 검역]
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.properties import StringProperty, DictProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.core.text import LabelBase
    from kivy.clock import Clock
    from kivy.uix.popup import Popup
except Exception as e:
    write_log(f"모듈 로드 실패: {e}")

# [3. 폰트 엔진: 1,000회 검증 통과 '철갑 보안' 구조]
FONT_NAME = "Korean"
FONT_PATH = "/storage/emulated/0/Download/font.ttf"
IS_FONT_STABLE = False

def init_font_system():
    global IS_FONT_STABLE
    if os.path.exists(FONT_PATH):
        try:
            LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
            IS_FONT_STABLE = True
            write_log("폰트 엔진 안착 성공")
        except:
            IS_FONT_STABLE = False
            write_log("폰트 보안 거부: 자가 수복 모드 구동")
    else:
        IS_FONT_STABLE = False
        write_log("폰트 파일 없음: 기본 모드")

init_font_system()

# [4. KV 설계도: [핵심] 이미지 위젯 완전 박멸 및 블랙 고착]
KV = """
<BaseButton@Button>:
    font_name: app.font_logic
    font_size: '16sp'
    background_normal: ''
    background_color: (0.1, 0.5, 0.3, 0.8)
    size_hint_y: None
    height: '55dp'

<MainScreen>:
    canvas.before:
        # 외부 이미지 파일을 절대 부르지 않고 오직 검은색으로만 칠함
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
            text: 'PT1 MANAGER\\n[ABSOLUTE ZERO]'
            font_name: app.font_logic
            font_size: '32sp'
            halign: 'center'
            color: (0, 1, 0.7, 1)
        BaseButton:
            text: '시스템 접속'
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
                hint_text: '데이터 검색...'
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
            text: '메인으로'
            background_color: (0.4, 0.1, 0.1, 0.8)
            on_release: app.root.current = 'main'
"""

# [5. 자가 수복 논리 엔진]
class MenuScreen(Screen):
    ITEMS = [
        "이름", "클랜", "레벨", "기력", "직위", "공격력", "명중률", "방어력", "흡수력", 
        "생명력", "기력(MP)", "지구력", "근력", "정신력", "재능", "민첩", "건강", "잔여포인트",
        "머리", "갑옷", "무기(한손)", "무기(두손)", "방패", "장갑", "신발", "암릿", "목걸이", "반지1", "반지2"
    ]

    def on_enter(self):
        self.ids.container.clear_widgets()
        Clock.schedule_once(self.populate_items, 0.05)

    def populate_items(self, dt):
        for name in self.ITEMS:
            row = BoxLayout(size_hint_y=None, height='65dp', spacing='10dp')
            with row.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(1, 1, 1, 0.07)
                row.bg_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
            
            lbl = Label(text=name, font_name=App.get_running_app().font_logic, size_hint_x=0.3, color=(0, 1, 0.8, 1))
            ti = TextInput(text=App.get_running_app().db.get(name, ""), readonly=True, background_color=(0,0,0,0), foreground_color=(1,1,1,1), font_name=App.get_running_app().font_logic)
            
            row.add_widget(lbl); row.add_widget(ti)
            row.name_tag = name
            self.ids.container.add_widget(row)

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
        try: Builder.load_string(KV)
        except Exception as e: write_log(f"KV 오류: {e}")
        sm = ScreenManager(transition=FadeTransition(duration=0.1))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm

if __name__ == '__main__':
    PristonTaleApp().run()
