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

# [과제 1 해결] 저장소 파일명과 대소문자 일치 (소문자 images.jpeg)
BG_IMAGE = 'images.jpeg' 
FONT_FILE = 'font.ttf'

def safe_font():
    """[과제 2 해결] 한글 깨짐 방지를 위한 폰트 탐색 로직"""
    paths = [
        os.path.join(os.getcwd(), FONT_FILE),
        FONT_FILE,
        "/sdcard/Download/font.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

class BackgroundScreen(Screen):
    """배경 이미지를 공통으로 적용하는 클래스"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.15, 0.15, 0.15, 1) # 이미지 없을 시 어두운 배경
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# --- [과제 3 해결] 캐릭터 세부 정보 화면 (화면 분리) ---
class CharDetailScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 상단 이름 영역
        top = BoxLayout(size_hint_y=None, height=120, spacing=10)
        top.add_widget(Label(text="캐릭터명:", font_name=f, size_hint_x=0.3, font_size='18sp'))
        self.name_input = TextInput(text="기본 캐릭터", font_name=f, multiline=False, font_size='18sp')
        top.add_widget(self.name_input)
        layout.add_widget(top)

        # 중앙: 장비 카테고리 12종 리스트 (스크롤 적용)
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=8)
        grid.bind(minimum_height=grid.setter('height'))
        
        categories = ["직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for cat in categories:
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            # 버튼마다 고유 색상 느낌 부여
            btn = Button(text=cat, font_name=f, size_hint_x=0.3, background_color=(0.2, 0.5, 0.7, 1))
            row.add_widget(btn)
            row.add_widget(TextInput(hint_text=f"{cat} 정보 입력", font_name=f))
            grid.add_widget(row)
        
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # 하단 버튼: 인벤토리 이동 및 저장
        btns = BoxLayout(size_hint_y=None, height=140, spacing=10)
        inv_btn = Button(text="인벤토리 열기", font_name=f, background_color=(0.9, 0.5, 0.1, 1))
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        
        save_btn = Button(text="정보 저장", font_name=f, background_color=(0.1, 0.7, 0.3, 1))
        
        btns.add_widget(inv_btn)
        btns.add_widget(save_btn)
        layout.add_widget(btns)
        
        self.add_widget(layout)

# --- [과제 3 해결] 인벤토리 화면 (별도 분리) ---
class InventoryScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="[ 캐릭터 인벤토리 ]", font_name=f, size_hint_y=None, height=80, font_size='22sp'))

        # 무한 아이템 리스트 영역
        self.scroll_view = ScrollView()
        self.item_list = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.item_list.bind(minimum_height=self.item_list.setter('height'))
        
        # 초기 입력창 5개 생성
        for _ in range(5): self.add_item_row()
            
        self.scroll_view.add_widget(self.item_list)
        layout.add_widget(self.scroll_view)

        # 하단 버튼부
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
        row.add_widget(TextInput(hint_text="아이템 정보...", font_name=f))
        del_btn = Button(text="삭제", font_name=f, size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.item_list.remove_widget(row))
        row.add_widget(del_btn)
        self.item_list.add_widget(row)

class PT1App(App):
    def build(self):
        try:
            # [자동 스크롤] 입력 시 키보드가 글자를 가리지 않게 설정
            Window.softinput_mode = "below_target"
            
            sm = ScreenManager(transition=FadeTransition())
            
            # 화면 등록
            sm.add_widget(CharDetailScreen(name='detail'))
            sm.add_widget(InventoryScreen(name='inventory'))
            
            # [시작 화면 설정] 세부 정보 화면을 먼저 띄움
            sm.current = 'detail'
            
            return sm
        except Exception:
            # 에러 발생 시 빨간 글씨로 로그 출력
            return Label(text=traceback.format_exc(), color=(1,0,0,1))

if __name__ == '__main__':
    PT1App().run()
