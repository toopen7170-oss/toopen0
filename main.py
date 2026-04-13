import os
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window

# [과제 1] 리소스 설정
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"

def load_korean_font():
    """[과제 2] 폰트 경로 참조 및 강제 등록"""
    font_path = os.path.join(os.getcwd(), FONT_NAME)
    if os.path.exists(font_path):
        # 폰트를 'KoreanFont'라는 이름으로 등록
        LabelBase.register(name="KoreanFont", fn_regular=font_path)
        return "KoreanFont"
    return None

class BackgroundManager(BoxLayout):
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

class AccountManagerLayout(BackgroundManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15
        self.padding = 30
        self.f = load_korean_font()
        
        # 상단 타이틀 (글씨 크기 조정)
        self.add_widget(Label(text="[2단계] 계정 관리 시스템", font_name=self.f, font_size='18sp', size_hint_y=None, height=80))

        # 데이터베이스 (3단계에서 파일 저장으로 발전 예정)
        self.accounts = {f"계정_{i}": {"chars": {}} for i in range(12)} 

        self.build_ui()

    def build_ui(self):
        # 1. 새 계정 만들기 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=self.f, size_hint_y=None, height=120, background_color=(0.1, 0.5, 0.1, 1))
        create_btn.bind(on_release=self.show_create_popup)
        self.add_widget(create_btn)

        # 2. 계정 리스트 영역 (자동 스크롤 최적화)
        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.account_grid = GridLayout(cols=1, size_hint_y=None, spacing=12, padding=[0, 10])
        self.account_grid.bind(minimum_height=self.account_grid.setter('height'))
        
        self.refresh_account_list()
        
        self.scroll.add_widget(self.account_grid)
        self.add_widget(self.scroll)

    def refresh_account_list(self):
        self.account_grid.clear_widgets()
        for account_id in self.accounts.keys():
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            
            # 모든 텍스트 요소에 font_name=self.f 강제 적용
            label = Label(text=f" {account_id}", font_name=self.f, halign='left', font_size='16sp')
            label.bind(size=label.setter('text_size'))
            row.add_widget(label)
            
            delete_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.25, background_color=(0.7, 0.1, 0.1, 1))
            delete_btn.bind(on_release=lambda x, a_id=account_id: self.show_delete_popup(a_id))
            row.add_widget(delete_btn)
            
            self.account_grid.add_widget(row)

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        # 입력창에도 폰트 적용
        self.id_input = TextInput(hint_text="계정 아이디 입력...", font_name=self.f, multiline=False, size_hint_y=None, height=100)
        content.add_widget(self.id_input)
        
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        cancel_b = Button(text="취소", font_name=self.f)
        create_b = Button(text="확인", font_name=self.f, background_color=(0.1, 0.5, 0.1, 1))
        btns.add_widget(cancel_b); btns.add_widget(create_b)
        content.add_widget(btns)
        
        # [해결] 팝업 제목 폰트까지 적용
        popup = Popup(title="계정 생성", title_font=self.f, content=content, size_hint=(0.8, 0.4))
        create_b.bind(on_release=lambda x: self.create_account(self.id_input.text, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def create_account(self, account_id, popup):
        if account_id:
            self.accounts[account_id] = {"chars": {}}
            self.refresh_account_list()
        popup.dismiss()

    def show_delete_popup(self, account_id):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=f"'{account_id}'\n삭제할까요?", font_name=self.f, halign='center'))
        
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        cancel_b = Button(text="아니오", font_name=self.f)
        confirm_b = Button(text="삭제", font_name=self.f, background_color=(0.7, 0.1, 0.1, 1))
        btns.add_widget(cancel_b); btns.add_widget(confirm_b)
        content.add_widget(btns)
        
        popup = Popup(title="주의", title_font=self.f, content=content, size_hint=(0.7, 0.35))
        confirm_b.bind(on_release=lambda x: self.delete_account(account_id, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def delete_account(self, account_id, popup):
        if account_id in self.accounts:
            del self.accounts[account_id]
            self.refresh_account_list()
        popup.dismiss()

class PT1App(App):
    def build(self):
        # [과제 3/6] 자동 스크롤(소프트 키보드 대응) 설정
        Window.softinput_mode = "below_target"
        try:
            return AccountManagerLayout()
        except Exception:
            return Label(text=traceback.format_exc())

if __name__ == '__main__':
    PT1App().run()
