import os
import traceback
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

# [설정] 파일명 및 폰트 (파일이 없어도 앱이 튕기지 않게 체크함)
BG_IMAGE = 'Images.jpeg'
FONT_FILE = "NanumGothic.ttf"

def get_font():
    if os.path.exists(FONT_FILE):
        return FONT_FILE
    # 안드로이드 시스템 기본 한글 폰트 경로들 확인
    paths = ["/system/fonts/NanumGothic.ttf", "/system/fonts/DroidSansFallback.ttf"]
    for p in paths:
        if os.path.exists(p): return p
    return None # 기본 폰트 사용

class BackgroundScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.1, 0.1, 0.1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = get_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="[PT1 통합 매니저]", font_size='28sp', font_name=f, size_hint_y=0.1))
        
        search_box = BoxLayout(size_hint_y=0.08, spacing=5)
        search_box.add_widget(TextInput(hint_text="계정/캐릭터 검색...", font_name=f, multiline=False))
        search_box.add_widget(Button(text="검색", font_name=f, size_hint_x=0.2))
        layout.add_widget(search_box)
        
        create_btn = Button(text="+ 새 계정 만들기", font_name=f, size_hint_y=0.1, background_color=(0.1, 0.6, 0.3, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)
        
        self.acc_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        self.add_account_row("계정: to", f)
        layout.add_widget(self.acc_list)
        layout.add_widget(Widget())
        self.add_widget(layout)

    def add_account_row(self, name, f):
        row = BoxLayout(size_hint_y=None, height=60, spacing=5)
        btn = Button(text=name, font_name=f, background_color=(0.2, 0.2, 0.2, 0.8))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.5, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.confirm_delete(name, row, f))
        row.add_widget(btn)
        row.add_widget(del_btn)
        self.acc_list.add_widget(row)

    def show_create_popup(self, *args):
        f = get_font()
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(TextInput(hint_text="ID 입력", font_name=f, font_size='22sp'))
        gen_btn = Button(text="생성", font_name=f, size_hint_y=0.4)
        content.add_widget(gen_btn)
        pop = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.4))
        gen_btn.bind(on_release=pop.dismiss)
        pop.open()

    def confirm_delete(self, name, row, f):
        content = BoxLayout(orientation='vertical', padding=15, spacing=20)
        content.add_widget(Label(text=f"'{name}'을 삭제할까요?", font_name=f))
        btns = BoxLayout(spacing=10, size_hint_y=0.4)
        no_b = Button(text="취소", font_name=f)
        yes_b = Button(text="확인", font_name=f, background_color=(0.6, 0.1, 0.1, 1))
        btns.add_widget(no_b)
        btns.add_widget(yes_b)
        content.add_widget(btns)
        pop = Popup(title="삭제 확인", content=content, size_hint=(0.7, 0.3))
        yes_b.bind(on_release=lambda x: (self.acc_list.remove_widget(row), pop.dismiss()))
        no_b.bind(on_release=pop.dismiss)
        pop.open()

class CharSelectScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = get_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="[to] 캐릭터 선택", font_name=f, size_hint_y=0.1))
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", font_name=f)
            btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
            grid.add_widget(btn)
        layout.add_widget(grid)
        back = Button(text="처음으로", font_name=f, size_hint_y=0.1)
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)
        self.add_widget(layout)

class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = get_font()
        main_layout = BoxLayout(orientation='horizontal')
        side = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=1)
        cats = ["양손무기", "한손무기", "갑옷", "ローブ", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for c in cats: side.add_widget(Button(text=c, font_name=f, font_size='10sp'))
        main_layout.add_widget(side)
        
        right = BoxLayout(orientation='vertical', size_hint_x=0.75, padding=5)
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=3)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        for _ in range(5): self.add_row(f)
        scroll.add_widget(self.grid)
        right.add_widget(scroll)
        
        bottom = BoxLayout(size_hint_y=0.1)
        add_b = Button(text="+ 추가", font_name=f)
        add_b.bind(on_release=lambda x: self.add_row(f))
        right.add_widget(bottom)
        main_layout.add_widget(right)
        self.add_widget(main_layout)

    def add_row(self, f):
        row = BoxLayout(size_hint_y=None, height=50, spacing=2)
        row.add_widget(TextInput(font_name=f, multiline=False))
        row.add_widget(Button(text="저장", font_name=f, size_hint_x=0.2))
        d_btn = Button(text="삭제", font_name=f, size_hint_x=0.2)
        d_btn.bind(on_release=lambda x: self.grid.remove_widget(row))
        row.add_widget(d_btn)
        self.grid.add_widget(row)

class PT1ManagerApp(App):
    def build(self):
        try:
            self.icon = BG_IMAGE if os.path.exists(BG_IMAGE) else None
            sm = ScreenManager(transition=FadeTransition())
            sm.add_widget(MainScreen(name='main'))
            sm.add_widget(CharSelectScreen(name='char_select'))
            sm.add_widget(InventoryScreen(name='inventory'))
            return sm
        except Exception:
            # 오류 발생 시 화면에 에러 표시
            err = traceback.format_exc()
            return Label(text=f"[오류 발생]\n\n{err}", font_size='14sp', color=(1,0,0,1))

if __name__ == '__main__':
    PT1ManagerApp().run()
