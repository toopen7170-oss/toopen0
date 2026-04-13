import os
import json
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
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

# 설정 파일
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"
DATA_FILE = "pt1_manager_data.json"

def load_korean_font():
    font_path = os.path.join(os.getcwd(), FONT_NAME)
    if os.path.exists(font_path):
        LabelBase.register(name="KoreanFont", fn_regular=font_path)
        return "KoreanFont"
    return None

class DataManager:
    """[과제 6] 데이터 저장 및 로드 로직"""
    @staticmethod
    def load():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class BackgroundScreen(Screen):
    """배경 공통 적용 클래스"""
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

# --- 2단계: 계정 관리 화면 ---
class AccountManagerScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="[2단계] 계정 관리", font_name=self.f, font_size='20sp', size_hint_y=None, height=100))

        create_btn = Button(text="+ 새 계정 만들기", font_name=self.f, size_hint_y=None, height=120, background_color=(0.1, 0.5, 0.1, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)

        scroll = ScrollView(do_scroll_x=False)
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # [수정] 임시 데이터 삭제, 실제 저장된 계정만 표시
        for acc_id in self.data.keys():
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            # 계정 버튼 (클릭 시 캐릭터 선택으로 이동)
            acc_btn = Button(text=f" 계정: {acc_id}", font_name=self.f, halign='left', background_color=(0.2, 0.2, 0.3, 1))
            acc_btn.bind(on_release=lambda x, a=acc_id: self.go_to_chars(a))
            row.add_widget(acc_btn)
            
            del_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.25, background_color=(0.7, 0.1, 0.1, 1))
            del_btn.bind(on_release=lambda x, a=acc_id: self.show_delete_popup(a))
            row.add_widget(del_btn)
            self.grid.add_widget(row)
            
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def go_to_chars(self, acc_id):
        App.get_running_app().current_account = acc_id
        self.manager.current = 'char_select'

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        # [수정] 입력창 글씨 크기 키움 (18sp -> 22sp)
        self.id_input = TextInput(hint_text="ID 입력", font_name=self.f, multiline=False, font_size='22sp', size_hint_y=None, height=120)
        content.add_widget(self.id_input)
        
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        create_b = Button(text="확인", font_name=self.f); cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b); btns.add_widget(create_b)
        content.add_widget(btns)
        
        popup = Popup(title="계정 생성", title_font=self.f, content=content, size_hint=(0.8, 0.4))
        create_b.bind(on_release=lambda x: self.create_acc(self.id_input.text, popup))
        cancel_b.bind(on_release=popup.dismiss); popup.open()

    def create_acc(self, acc_id, popup):
        if acc_id and acc_id not in self.data:
            self.data[acc_id] = {"chars": {f"char_{i}": {"name": f"캐릭터 {i}"} for i in range(1, 7)}}
            DataManager.save(self.data)
            self.on_pre_enter()
        popup.dismiss()

    def show_delete_popup(self, acc_id):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=f"'{acc_id}' 를 삭제할까요?", font_name=self.f, halign='center'))
        btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
        confirm_b = Button(text="삭제", font_name=self.f, background_color=(0.7, 0.1, 0.1, 1))
        cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b); btns.add_widget(confirm_b)
        content.add_widget(btns)
        popup = Popup(title="삭제 확인", title_font=self.f, content=content, size_hint=(0.7, 0.35))
        confirm_b.bind(on_release=lambda x: self.del_acc(acc_id, popup))
        cancel_b.bind(on_release=popup.dismiss); popup.open()

    def del_acc(self, acc_id, popup):
        if acc_id in self.data:
            del self.data[acc_id]
            DataManager.save(self.data)
            self.on_pre_enter()
        popup.dismiss()

# --- 3단계: 캐릭터 선택 화면 (사진 구성 반영) ---
class CharacterSelectScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        acc_id = self.app.current_account
        layout.add_widget(Label(text=f"[{acc_id}] 캐릭터 선택", font_name=self.f, font_size='22sp', size_hint_y=None, height=100))

        # 캐릭터 6개 그리드 (사진과 동일한 구성)
        grid = GridLayout(cols=2, spacing=15)
        chars = self.data[acc_id]["chars"]
        for i in range(1, 7):
            char_data = chars.get(f"char_{i}", {"name": "빈 슬롯"})
            btn = Button(text=char_data["name"], font_name=self.f, background_color=(0.1, 0.15, 0.25, 1))
            btn.bind(on_release=lambda x, idx=i: self.select_char(idx))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        back_btn = Button(text="뒤로가기", font_name=self.f, size_hint_y=None, height=120)
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_manager'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def select_char(self, idx):
        # 캐릭터 선택 로직 (다음 단계 세부화면 연결)
        print(f"{idx}번 캐릭터 선택됨")

class PT1App(App):
    current_account = ""
    def build(self):
        Window.softinput_mode = "below_target"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(AccountManagerScreen(name='account_manager'))
        sm.add_widget(CharacterSelectScreen(name='char_select'))
        return sm

if __name__ == '__main__':
    PT1App().run()
