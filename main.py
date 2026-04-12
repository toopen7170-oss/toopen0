import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

# 한글 폰트 설정 (안드로이드 환경 고려)
KOREAN_FONT = "/system/fonts/NanumGothic.ttf" if os.path.exists("/system/fonts/NanumGothic.ttf") else "DroidSansFallback.ttf"

class BackgroundScreen(Screen):
    """배경 이미지가 포함된 기본 스크린 클래스"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source='Images.jpeg', pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BackgroundScreen):
    """1번, 5번: 메인 화면 및 검색/계정 생성"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 상단 타이틀
        layout.add_widget(Label(text="[PT1 통합 매니저]", font_size='24sp', font_name=KOREAN_FONT, size_hint_y=0.1))
        
        # 검색창 영역
        search_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        self.search_input = TextInput(hint_text="계정/캐릭터 검색...", font_name=KOREAN_FONT, multiline=False)
        search_btn = Button(text="검색", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.1, 0.2, 0.4, 1))
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        layout.add_widget(search_layout)
        
        # 새 계정 만들기 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=KOREAN_FONT, size_hint_y=0.1, background_color=(0.1, 0.6, 0.3, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)
        
        # 계정 리스트 예시 (7번 삭제 기능 포함)
        self.acc_list = BoxLayout(orientation='vertical', spacing=5)
        self.add_account_row("계정: to")
        layout.add_widget(self.acc_list)
        layout.add_widget(Widget()) # 스페이서
        
        self.add_widget(layout)

    def add_account_row(self, name):
        row = BoxLayout(size_hint_y=None, height=50)
        btn = Button(text=name, font_name=KOREAN_FONT, background_color=(0.2, 0.2, 0.2, 0.8))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.5, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.confirm_delete(name))
        row.add_widget(btn)
        row.add_widget(del_btn)
        self.acc_list.add_widget(row)

    def show_create_popup(self, *args):
        """2번: 큰 입력창 팝업"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.id_input = TextInput(hint_text="ID 입력", font_name=KOREAN_FONT, font_size='20sp')
        gen_btn = Button(text="생성", font_name=KOREAN_FONT, size_hint_y=0.3, background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(self.id_input)
        content.add_widget(gen_btn)
        
        self.popup = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.5))
        gen_btn.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def confirm_delete(self, name):
        """7번: 삭제 확인 멘트 팝업"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=20)
        content.add_widget(Label(text=f"'{name}'을 삭제할까요?", font_name=KOREAN_FONT))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.4)
        yes_btn = Button(text="확인", font_name=KOREAN_FONT, background_color=(0.5, 0.1, 0.1, 1))
        no_btn = Button(text="취소", font_name=KOREAN_FONT)
        
        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        content.add_widget(btn_layout)
        
        pop = Popup(title="삭제 확인", content=content, size_hint=(0.7, 0.3))
        no_btn.bind(on_release=pop.dismiss)
        pop.open()

class CharSelectScreen(BackgroundScreen):
    """3번, 6번: 캐릭터 선택창"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="[toopen] 캐릭터 선택", font_name=KOREAN_FONT, size_hint_y=0.1))
        
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", font_name=KOREAN_FONT, background_color=(0.3, 0.3, 0.5, 0.7))
            btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        
        back_btn = Button(text="처음으로", font_name=KOREAN_FONT, size_hint_y=0.15, background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class InventoryScreen(Screen):
    """4번: 인벤토리 한줄씩 저장/삭제"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='horizontal')
        
        # 왼쪽 카테고리 (이미지 73197.jpg 참조)
        side_menu = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=1)
        categories = ["양손무기", "한손무기", "갑옷", "ローブ", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for cat in categories:
            side_menu.add_widget(Button(text=cat, font_name=KOREAN_FONT, background_color=(0, 0, 0, 1)))
        main_layout.add_widget(side_menu)
        
        # 오른쪽 인벤토리 리스트
        right_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        self.item_list = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.item_list.bind(minimum_height=self.item_list.setter('height'))
        
        # 초기 3줄 추가
        for _ in range(3): self.add_item_row()
        
        right_layout.add_widget(self.item_list)
        
        # 하단 제어 버튼
        bottom_btns = BoxLayout(size_hint_y=0.1)
        add_btn = Button(text="+ 추가", font_name=KOREAN_FONT, background_color=(0.1, 0.4, 0.6, 1))
        add_btn.bind(on_release=lambda x: self.add_item_row())
        save_all_btn = Button(text="전체 저장", font_name=KOREAN_FONT, background_color=(0.1, 0.5, 0.3, 1))
        
        bottom_btns.add_widget(add_btn)
        bottom_btns.add_widget(save_all_btn)
        right_layout.add_widget(bottom_btns)
        
        main_layout.add_widget(right_layout)
        self.add_widget(main_layout)

    def add_item_row(self, *args):
        row = BoxLayout(size_hint_y=None, height=50, spacing=2)
        txt = TextInput(font_name=KOREAN_FONT, multiline=False)
        s_btn = Button(text="저장", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.1, 0.4, 0.2, 1))
        d_btn = Button(text="삭제", font_name=KOREAN_FONT, size_hint_x=0.2, background_color=(0.4, 0.1, 0.1, 1))
        
        d_btn.bind(on_release=lambda x: self.item_list.remove_widget(row))
        
        row.add_widget(txt)
        row.add_widget(s_btn)
        row.add_widget(d_btn)
        self.item_list.add_widget(row)

class PT1ManagerApp(App):
    def build(self):
        self.icon = 'Images.jpeg' # 1번: 앱 아이콘 설정
        self.title = "PT1 Manager"
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(InventoryScreen(name='inventory'))
        return sm

if __name__ == '__main__':
    PT1ManagerApp().run()
