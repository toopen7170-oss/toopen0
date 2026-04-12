import os
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

# [과제 1, 2 유지] 파일명 소문자 및 폰트 설정
BG_IMAGE = 'images.jpeg' 
FONT_FILE = 'font.ttf'

def safe_font():
    paths = [os.path.join(os.getcwd(), FONT_FILE), FONT_FILE, "/sdcard/Download/font.ttf"]
    for p in paths:
        if os.path.exists(p): return p
    return None

class BackgroundScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.15, 0.15, 0.15, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# --- [3번 과제] 캐릭터 세부 정보 화면 ---
class CharDetailScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 이름 입력 영역
        top = BoxLayout(size_hint_y=None, height=120, spacing=10)
        top.add_widget(Label(text="캐릭터명:", font_name=f, size_hint_x=0.3, font_size='18sp'))
        self.name_in = TextInput(text="캐릭터 이름", font_name=f, multiline=False)
        top.add_widget(self.name_in)
        layout.add_widget(top)

        # 장비 카테고리 (스크롤)
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=8)
        grid.bind(minimum_height=grid.setter('height'))
        
        cats = ["직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for cat in cats:
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            btn = Button(text=cat, font_name=f, size_hint_x=0.3, background_color=(0.2, 0.5, 0.7, 1))
            row.add_widget(btn)
            row.add_widget(TextInput(hint_text=f"{cat} 정보 입력", font_name=f))
            grid.add_widget(row)
        
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # 화면 전환 버튼 (인벤토리로 이동)
        btns = BoxLayout(size_hint_y=None, height=140, spacing=10)
        inv_btn = Button(text="인벤토리 열기", font_name=f, background_color=(0.9, 0.5, 0.1, 1))
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        
        save_btn = Button(text="정보 저장", font_name=f, background_color=(0.1, 0.7, 0.3, 1))
        
        btns.add_widget(inv_btn)
        btns.add_widget(save_btn)
        layout.add_widget(btns)
        self.add_widget(layout)

# --- [3번 과제] 인벤토리 전용 화면 ---
class InventoryScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="[ 캐릭터 인벤토리 ]", font_name=f, size_hint_y=None, height=80, font_size='22sp'))

        # 아이템 리스트 (스크롤)
        self.scroll_view = ScrollView()
        self.item_list = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.item_list.bind(minimum_height=self.item_list.setter('height'))
        
        for _ in range(5): self.add_item_row() # 초기 5줄
            
        self.scroll_view.add_widget(self.item_list)
        layout.add_widget(self.scroll_view)

        # 하단 조작부
        btns = BoxLayout(size_hint_y=None, height=130, spacing=10)
        add_btn = Button(text="+ 줄 추가", font_name=f, background_color=(0.1, 0.6, 0.9, 1))
        add_btn.bind(on_release=lambda x: self.add_item_row())
        
        back_btn = Button(text="뒤로 (세부내용)", font_name=f, background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        
        btns.add_widget(add_btn)
        btns.add_widget(back_btn)
        layout.add_widget(btns)
        self.add_widget(layout)

    def add_item_row(self):
        f = safe_font()
        row = BoxLayout(size_hint_y=None, height=120, spacing=5)
        row.add_widget(TextInput(hint_text="아이템 이름...", font_name=f))
        del_btn = Button(text="삭제", font_name=f, size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.item_list.remove_widget(row))
        row.add_widget(del_btn)
        self.item_list.add_widget(row)

class PT1App(App):
    def build(self):
        try:
            Window.softinput_mode = "below_target" # 자동 스크롤 적용
            sm = ScreenManager(transition=FadeTransition())
            sm.add_widget(CharDetailScreen(name='detail'))
            sm.add_widget(InventoryScreen(name='inventory'))
            
            # [시작점 설정] 세부 정보 화면을 최우선으로 보여줌
            sm.current = 'detail'
            return sm
        except Exception:
            return Label(text=traceback.format_exc(), color=(1,0,0,1))

if __name__ == '__main__':
    PT1App().run()
