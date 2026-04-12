import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

# 폰트 및 이미지 설정 (파일이 반드시 폴더 내에 있어야 함)
KOREAN_FONT = "NanumGothic.ttf" if os.path.exists("NanumGothic.ttf") else "DroidSansFallback.ttf"
BG_IMAGE = 'Images.jpeg'

class BackgroundScreen(Screen):
    """배경 이미지를 공통으로 사용하는 베이스 클래스"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.1, 0.1, 0.1, 1) # 이미지 없을 시 어두운 배경
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BackgroundScreen):
    """[1번, 5번] 메인 화면: 검색 및 계정 생성"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 상단 타이틀
        layout.add_widget(Label(text="[PT1 통합 매니저]", font_size='28sp', font_name=KOREAN_FONT, size_hint_y=0.1))
        
        # 검색창
        search_box = BoxLayout(size_hint_y=0.08, spacing=5)
        self.search_in = TextInput(hint_text="계정/캐릭터 검색...", font_name=KOREAN_FONT, multiline=False)
        search_btn = Button(text="검색", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.1, 0.2, 0.4, 1))
        search_box.add_widget(self.search_in)
        search_box.add_widget(search_btn)
        layout.add_widget(search_box)
        
        # 계정 생성 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=KOREAN_FONT, size_hint_y=0.1, background_color=(0.1, 0.6, 0.3, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)
        
        # 계정 리스트 (7번 삭제 기능 포함)
        self.acc_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        self.add_account_row("계정: to")
        layout.add_widget(self.acc_list)
        
        layout.add_widget(Widget()) # 빈 공간 채우기
        self.add_widget(layout)

    def add_account_row(self, name):
        row = BoxLayout(size_hint_y=None, height=60, spacing=5)
        btn = Button(text=name, font_name=KOREAN_FONT, background_color=(0.2, 0.2, 0.2, 0.8))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.5, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.confirm_delete(name, row))
        
        row.add_widget(btn)
        row.add_widget(del_btn)
        self.acc_list.add_widget(row)

    def show_create_popup(self, *args):
        """[2번] 큰 입력창 팝업"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        id_input = TextInput(hint_text="ID 입력", font_name=KOREAN_FONT, font_size='22sp', size_hint_y=0.6)
        gen_btn = Button(text="생성", font_name=KOREAN_FONT, size_hint_y=0.4, background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(id_input)
        content.add_widget(gen_btn)
        
        pop = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.4))
        gen_btn.bind(on_release=pop.dismiss)
        pop.open()

    def confirm_delete(self, name, row_widget):
        """[7번] 삭제 확인 멘트"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=20)
        content.add_widget(Label(text=f"'{name}'을 삭제할까요?", font_name=KOREAN_FONT))
        
        btns = BoxLayout(spacing=10, size_hint_y=0.4)
        no_b = Button(text="취소", font_name=KOREAN_FONT)
        yes_b = Button(text="확인", font_name=KOREAN_FONT, background_color=(0.6, 0.1, 0.1, 1))
        
        btns.add_widget(no_b)
        btns.add_widget(yes_b)
        content.add_widget(btns)
        
        pop = Popup(title="삭제 확인", content=content, size_hint=(0.7, 0.3))
        yes_b.bind(on_release=lambda x: (self.acc_list.remove_widget(row_widget), pop.dismiss()))
        no_b.bind(on_release=pop.dismiss)
        pop.open()

class CharSelectScreen(BackgroundScreen):
    """[3번, 6번] 캐릭터 선택창"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="[to] 캐릭터 선택", font_name=KOREAN_FONT, size_hint_y=0.1))
        
        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.7)
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", font_name=KOREAN_FONT, background_color=(0.3, 0.3, 0.6, 0.6))
            btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        back = Button(text="처음으로", font_name=KOREAN_FONT, size_hint_y=0.1, background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)
        self.add_widget(layout)

class InventoryScreen(Screen):
    """[4번] 인벤토리 시스템"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='horizontal')
        
        # 카테고리 메뉴
        side = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=1)
        cats = ["양손무기", "한손무기", "갑옷", "ローブ", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for c in cats:
            side.add_widget(Button(text=c, font_name=KOREAN_FONT, background_color=(0,0,0,1), font_size='12sp'))
        main_layout.add_widget(side)
        
        # 인벤토리 리스트
        right = BoxLayout(orientation='vertical', size_hint_x=0.75, padding=5)
        scroll = ScrollView()
        self.item_grid = GridLayout(cols=1, size_hint_y=None, spacing=3)
        self.item_grid.bind(minimum_height=self.item_grid.setter('height'))
        
        # 초기 5줄 생성
        for _ in range(5): self.add_item_row()
        
        scroll.add_widget(self.item_grid)
        right.add_widget(scroll)
        
        # 하단 버튼
        bottom = BoxLayout(size_hint_y=0.1, spacing=5)
        add_b = Button(text="+ 추가", font_name=KOREAN_FONT, background_color=(0.1, 0.4, 0.7, 1))
        add_b.bind(on_release=self.add_item_row)
        back_b = Button(text="뒤로", font_name=KOREAN_FONT, background_color=(0.3, 0.3, 0.3, 1))
        back_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        bottom.add_widget(add_b)
        bottom.add_widget(back_b)
        right.add_widget(bottom)
        
        main_layout.add_widget(right)
        self.add_widget(main_layout)

    def add_item_row(self, *args):
        row = BoxLayout(size_hint_y=None, height=55, spacing=2)
        tin = TextInput(font_name=KOREAN_FONT, multiline=False, size_hint_x=0.6)
        s_btn = Button(text="저장", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.1, 0.5, 0.2, 1))
        d_btn = Button(text="삭제", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.6, 0.1, 0.1, 1))
        d_btn.bind(on_release=lambda x: self.item_grid.remove_widget(row))
        
        row.add_widget(tin)
        row.add_widget(s_btn)
        row.add_widget(d_btn)
        self.item_grid.add_widget(row)

class PT1ManagerApp(App):
    def build(self):
        # [1번] 아이콘 설정
        if os.path.exists(BG_IMAGE):
            self.icon = BG_IMAGE
            
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(InventoryScreen(name='inventory'))
        return sm

if __name__ == '__main__':
    PT1ManagerApp().run()
