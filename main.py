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

# [과제 1] 리소스 설정 (파일명 대소문자 주의)
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"

def load_korean_font():
    """[과제 2] 모든 UI 요소에 적용할 폰트 등록"""
    font_path = os.path.join(os.getcwd(), FONT_NAME)
    if os.path.exists(font_path):
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
        
        # 텍스트 크기 최적화 (사진 피드백 반영)
        self.add_widget(Label(text="[2단계] 계정 관리 (수정본)", font_name=self.f, font_size='20sp', size_hint_y=None, height=100))

        # 계정 데이터 (테스트용)
        self.accounts = {f"test_acc_{i}": {"chars": {}} for i in range(15)} # 스크롤 테스트용 데이터

        self.build_ui()

    def build_ui(self):
        # 1. 새 계정 만들기 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=self.f, size_hint_y=None, height=130, background_color=(0, 0.5, 0, 1))
        create_btn.bind(on_release=self.show_create_popup)
        self.add_widget(create_btn)

        # 2. 계정 리스트 영역 (스크롤 최적화)
        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        # 중요: GridLayout의 height를 minimum_height에 바인딩해야 스크롤이 작동함
        self.account_grid = GridLayout(cols=1, size_hint_y=None, spacing=15, padding=[0, 20])
        self.account_grid.bind(minimum_height=self.account_grid.setter('height'))
        
        self.refresh_account_list()
        
        self.scroll.add_widget(self.account_grid)
        self.add_widget(self.scroll)

    def refresh_account_list(self):
        self.account_grid.clear_widgets()
        for account_id in self.accounts.keys():
            row = BoxLayout(size_hint_y=None, height=120, spacing=10)
            
            # 계정 표시 라벨
            label = Label(text=f" 계정: {account_id}", font_name=self.f, halign='left', font_size='18sp')
            label.bind(size=label.setter('text_size'))
            row.add_widget(label)
            
            # 삭제 버튼 (빨간색 계열)
            delete_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.3, background_color=(0.7, 0.1, 0.1, 1))
            delete_btn.bind(on_release=lambda x, a_id=account_id: self.show_delete_popup(a_id))
            row.add_widget(delete_btn)
            
            self.account_grid.add_widget(row)

    # --- [수정] 폰트 깨짐 방지를 위한 전용 팝업 생성 함수 ---
    def create_styled_popup(self, title, content, size_hint):
        # [과제 2] 팝업 제목(title)의 폰트 오류 해결을 위해 Label 객체 사용
        title_label = Label(text=title, font_name=self.f, font_size='20sp')
        return Popup(title=title, title_font=self.f, content=content, size_hint=size_hint, auto_dismiss=False)

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.id_input = TextInput(hint_text="생성할 계정 ID", font_name=self.f, multiline=False, font_size='18sp', size_hint_y=None, height=120)
        content.add_widget(self.id_input)
        
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        cancel_b = Button(text="취소", font_name=self.f)
        create_b = Button(text="생성 완료", font_name=self.f, background_color=(0, 0.5, 0, 1))
        btns.add_widget(cancel_b)
        btns.add_widget(create_b)
        content.add_widget(btns)
        
        popup = self.create_styled_popup("새 계정 만들기", content, (0.8, 0.4))
        create_b.bind(on_release=lambda x: self.create_account(self.id_input.text, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def create_account(self, account_id, popup):
        if account_id and account_id not in self.accounts:
            self.accounts[account_id] = {"chars": {}} 
            self.refresh_account_list()
        popup.dismiss()

    def show_delete_popup(self, account_id):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=f"'{account_id}' 계정을\n삭제하시겠습니까?", font_name=self.f, halign='center', font_size='18sp'))
        
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        cancel_b = Button(text="취소", font_name=self.f)
        confirm_b = Button(text="삭제확인", font_name=self.f, background_color=(0.7, 0.1, 0.1, 1))
        btns.add_widget(cancel_b)
        btns.add_widget(confirm_b)
        content.add_widget(btns)
        
        popup = self.create_styled_popup("계정 삭제", content, (0.8, 0.35))
        confirm_b.bind(on_release=lambda x: self.delete_account(account_id, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def delete_account(self, account_id, popup):
        if account_id in self.accounts:
            del self.accounts[account_id]
            self.refresh_account_list()
        popup.dismiss()

class PT1ProjectApp(App):
    def build(self):
        try:
            return AccountManagerLayout()
        except Exception:
            error_msg = traceback.format_exc()
            print(error_msg)
            return Label(text=f"Error Log:\n{error_msg}", color=(1, 0, 0, 1))

if __name__ == '__main__':
    PT1ProjectApp().run()
