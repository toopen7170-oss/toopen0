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

# [과제 1, 2 안정화 완료] 1단계 리소스 설정 유지
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"

def load_korean_font():
    font_path = os.path.join(os.getcwd(), FONT_NAME)
    if os.path.exists(font_path):
        LabelBase.register(name="KoreanFont", fn_regular=font_path)
        return "KoreanFont"
    return None

class BackgroundManager(BoxLayout):
    """배경 이미지를 공통으로 적용하는 베이스 레이아웃"""
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

# --- [2단계 핵심] 계정 관리 메인 화면 ---
class AccountManagerLayout(BackgroundManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15
        self.padding = 30
        self.f = load_korean_font()
        
        # [2단계 피드백 반영] 글씨 크기 줄임
        title_text = f"[2단계] 계정 관리 및 팝업 화면"
        self.add_widget(Label(text=title_text, font_name=self.f, font_size='20sp', size_hint_y=None, height=100))

        # 데이터베이스 틀 (임시)
        # 나중에 3단계에서 JSON 파일로 관리할 것입니다.
        self.accounts = {} 

        self.build_ui()

    def build_ui(self):
        # 1. 새 계정 만들기 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=self.f, size_hint_y=None, height=130)
        create_btn.bind(on_release=self.show_create_popup)
        self.add_widget(create_btn)

        # 2. 계정 리스트 영역 (스크롤 적용)
        self.scroll = ScrollView()
        self.account_grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.account_grid.bind(minimum_height=self.account_grid.setter('height'))
        
        self.refresh_account_list()
        
        self.scroll.add_widget(self.account_grid)
        self.add_widget(self.scroll)

    def refresh_account_list(self):
        """데이터베이스에 따라 목록을 새로고침"""
        self.account_grid.clear_widgets()
        for account_id in self.accounts.keys():
            row = BoxLayout(size_hint_y=None, height=120, spacing=10)
            
            # 계정 ID 라벨
            label = Label(text=account_id, font_name=self.f, halign='left')
            label.bind(size=label.setter('text_size'))
            row.add_widget(label)
            
            # 계정 삭제 버튼
            delete_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.25)
            delete_btn.bind(on_release=lambda x, a_id=account_id: self.show_delete_popup(a_id))
            row.add_widget(delete_btn)
            
            self.account_grid.add_widget(row)

    # --- [2단계 팝업 기능] ---

    def show_create_popup(self, *args):
        """계정 생성 팝업창"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 입력창
        self.id_input = TextInput(hint_text="계정 ID 입력", font_name=self.f, multiline=False, font_size='18sp')
        content.add_widget(self.id_input)
        
        # 버튼 영역
        btns = BoxLayout(size_hint_y=0.4, spacing=10)
        create_b = Button(text="생성 완료", font_name=self.f)
        cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b)
        btns.add_widget(create_b)
        content.add_widget(btns)
        
        popup = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        
        create_b.bind(on_release=lambda x: self.create_account(self.id_input.text, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def create_account(self, account_id, popup):
        """실제 계정 생성 로직 (3단계에서 JSON 저장 연동 예정)"""
        if account_id and account_id not in self.accounts:
            # 3단계 데이터 저장(과제 6)을 위한 기본 구조 틀 배치
            self.accounts[account_id] = {"chars": {}} 
            self.refresh_account_list()
        popup.dismiss()

    def show_delete_popup(self, account_id):
        """[과제] 삭제 확인 팝업창 구현"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 삭제 확인 멘트
        content.add_widget(Label(text=f"'{account_id}' 계정을\n삭제하시겠습니까?", font_name=self.f, halign='center'))
        
        # 버튼 영역
        btns = BoxLayout(size_hint_y=0.4, spacing=10)
        confirm_b = Button(text="삭제확인", font_name=self.f)
        cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b)
        btns.add_widget(confirm_b)
        content.add_widget(btns)
        
        popup = Popup(title="계정 삭제 안내", content=content, size_hint=(0.8, 0.35), auto_dismiss=False)
        
        confirm_b.bind(on_release=lambda x: self.delete_account(account_id, popup))
        cancel_b.bind(on_release=popup.dismiss)
        popup.open()

    def delete_account(self, account_id, popup):
        """실제 계정 삭제 로직 (3단계에서 JSON 동기화 연동 예정)"""
        if account_id in self.accounts:
            del self.accounts[account_id]
            self.refresh_account_list()
        popup.dismiss()

class PT1ProjectApp(App):
    def build(self):
        try:
            return AccountManagerLayout()
        except Exception:
            # [과제 7 안정화]
            error_msg = traceback.format_exc()
            print(error_msg)
            return Label(text=f"에러 발생!\n\n{error_msg}", color=(1, 0, 0, 1))

if __name__ == '__main__':
    PT1ProjectApp().run()
