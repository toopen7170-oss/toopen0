import os
import json
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

# 이전 단계에서 성공한 경로 설정 유지
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

# --- [신규] 캐릭터 세부 정보 화면 (인벤토리와 분리됨) ---
class CharDetailScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 상단 타이틀 및 이름 수정
        top = BoxLayout(size_hint_y=None, height=120, spacing=10)
        top.add_widget(Label(text="캐릭터명:", font_name=f, size_hint_x=0.3))
        self.name_input = TextInput(text="기본이름", font_name=f, multiline=False)
        top.add_widget(self.name_input)
        layout.add_widget(top)

        # 중앙: 캐릭터 기본 정보 (장비 카테고리 12종)
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))
        
        categories = ["직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for cat in categories:
            row = BoxLayout(size_hint_y=None, height=100, spacing=10)
            row.add_widget(Button(text=cat, font_name=f, size_hint_x=0.3, background_color=(0.2, 0.4, 0.6, 1)))
            row.add_widget(TextInput(hint_text=f"{cat} 정보 입력", font_name=f))
            grid.add_widget(row)
        
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # 하단 버튼부: 인벤토리 이동 버튼을 명확히 배치
        btns = BoxLayout(size_hint_y=None, height=130, spacing=10)
        inv_btn = Button(text="인벤토리 열기", font_name=f, background_color=(0.8, 0.5, 0.1, 1))
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        
        save_btn = Button(text="정보 저장", font_name=f, background_color=(0.1, 0.6, 0.3, 1))
        back_btn = Button(text="뒤로가기", font_name=f, background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'test')) # 임시 메인으로
        
        btns.add_widget(inv_btn)
        btns.add_widget(save_btn)
        btns.add_widget(back_btn)
        layout.add_widget(btns)

        self.add_widget(layout)

# --- [신규] 인벤토리 전용 화면 ---
class InventoryScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="[ 캐릭터 인벤토리 ]", font_name=f, size_hint_y=None, height=80, font_size='22sp'))

        # 아이템 리스트 영역
        self.scroll = ScrollView()
        self.item_list = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.item_list.bind(minimum_height=self.item_list.setter('height'))
        
        # 테스트용 초기 줄 3개 추가
        for _ in range(3): self.add_item_row()
            
        self.scroll.add_widget(self.item_list)
        layout.add_widget(self.scroll)

        # 하단 조작부
        btns = BoxLayout(size_hint_y=None, height=120, spacing=10)
        add_btn = Button(text="+ 아이템 추가", font_name=f, background_color=(0.1, 0.5, 0.8, 1))
        add_btn.bind(on_release=lambda x: self.add_item_row())
        
        close_btn = Button(text="닫기 (세부내용으로)", font_name=f, background_color=(0.4, 0.4, 0.4, 1))
        close_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        
        btns.add_widget(add_btn)
        btns.add_widget(close_btn)
        layout.add_widget(btns)

        self.add_widget(layout)

    def add_item_row(self):
        f = safe_font()
        row = BoxLayout(size_hint_y=None, height=110, spacing=5)
        row.add_widget(TextInput(hint_text="아이템 이름 입력", font_name=f))
        del_btn = Button(text="X", font_name=f, size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.item_list.remove_widget(row))
        row.add_widget(del_btn)
        self.item_list.add_widget(row)

class PT1App(App):
    def build(self):
        try:
            Window.softinput_mode = "below_target" # 자동 스크롤(글 작성 시 화면 밀림) 적용
            sm = ScreenManager(transition=FadeTransition())
            
            # 테스트를 위해 세부내용 화면을 먼저 띄우도록 설정
            sm.add_widget(CharDetailScreen(name='detail'))
            sm.add_widget(InventoryScreen(name='inventory'))
            
            # 이전 단계 테스트 화면 (필요시)
            from kivy.uix.screenmanager import Screen
            sm.add_widget(Screen(name='test')) 
            
            return sm
        except Exception:
            return Label(text=traceback.format_exc(), color=(1,0,0,1))

if __name__ == '__main__':
    PT1App().run()
