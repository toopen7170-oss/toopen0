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

# 설정 리소스
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
    @staticmethod
    def load():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try: return json.load(f)
                except: return {}
        return {}

    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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

# --- [수정] 모든 팝업에 "사진 1번"의 슬림한 디자인 적용 ---
class SlimPopup(Popup):
    def __init__(self, p_title, p_content, p_size=(0.75, 0.35), **kwargs):
        super().__init__(**kwargs)
        self.title = p_title
        self.title_font = load_korean_font()
        self.content = p_content
        self.size_hint = p_size
        self.auto_dismiss = False

# --- 2/3단계: 계정 관리 화면 ---
class AccountManagerScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="[PT1 매니저] 계정 선택", font_name=self.f, font_size='20sp', size_hint_y=None, height=100))

        create_btn = Button(text="+ 새 계정 등록", font_name=self.f, size_hint_y=None, height=120, background_color=(0.1, 0.5, 0.1, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)

        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        for acc_id in self.data.keys():
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            acc_btn = Button(text=f" {acc_id}", font_name=self.f, halign='left', background_color=(0.2, 0.2, 0.3, 1))
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
        # [사진 1번 반영] 슬림한 입력창 디자인
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text="계정 ID를 입력하세요", font_name=self.f, size_hint_y=None, height=40))
        
        # [핵심] 입력칸 높이를 슬림하게(80) 조정
        self.id_input = TextInput(hint_text="ID 입력", font_name=self.f, multiline=False, font_size='18sp', size_hint_y=None, height=90)
        content.add_widget(self.id_input)
        
        btns = BoxLayout(size_hint_y=None, height=90, spacing=10)
        ok_b = Button(text="등록", font_name=self.f); cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b); btns.add_widget(ok_b)
        content.add_widget(btns)
        
        popup = SlimPopup("계정 생성", content)
        ok_b.bind(on_release=lambda x: self.create_acc(self.id_input.text, popup))
        cancel_b.bind(on_release=popup.dismiss); popup.open()

    def create_acc(self, acc_id, popup):
        if acc_id and acc_id not in self.data:
            # 4단계용 상세 데이터 구조 (레벨, 직업 추가)
            self.data[acc_id] = {"chars": {f"{i}": {"name": f"캐릭터 {i}", "lv": "1", "job": "없음"} for i in range(1, 7)}}
            DataManager.save(self.data)
            self.on_pre_enter()
        popup.dismiss()

    def show_delete_popup(self, acc_id):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=f"'{acc_id}'\n정말 삭제할까요?", font_name=self.f, halign='center'))
        btns = BoxLayout(size_hint_y=None, height=90, spacing=10)
        confirm_b = Button(text="삭제", font_name=self.f, background_color=(0.7, 0.1, 0.1, 1))
        cancel_b = Button(text="취소", font_name=self.f)
        btns.add_widget(cancel_b); btns.add_widget(confirm_b)
        content.add_widget(btns)
        popup = SlimPopup("삭제 확인", content, p_size=(0.7, 0.3))
        confirm_b.bind(on_release=lambda x: self.del_acc(acc_id, popup))
        cancel_b.bind(on_release=popup.dismiss); popup.open()

    def del_acc(self, acc_id, popup):
        if acc_id in self.data:
            del self.data[acc_id]
            DataManager.save(self.data)
            self.on_pre_enter()
        popup.dismiss()

# --- 4단계: 캐릭터 선택 및 상세 정보 확인 ---
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
        layout.add_widget(Label(text=f"<{acc_id}> 캐릭터 목록", font_name=self.f, font_size='22sp', size_hint_y=None, height=100))

        grid = GridLayout(cols=2, spacing=15)
        chars = self.data[acc_id]["chars"]
        for i in range(1, 7):
            char_info = chars.get(str(i), {"name": "빈 슬롯", "lv": "-"})
            # 버튼에 이름과 레벨 표시
            btn_text = f"{char_info['name']}\n(Lv.{char_info['lv']})"
            btn = Button(text=btn_text, font_name=self.f, background_color=(0.1, 0.15, 0.25, 1), halign='center')
            btn.bind(on_release=lambda x, idx=i: self.view_char_detail(idx))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        back_btn = Button(text="뒤로가기", font_name=self.f, size_hint_y=None, height=110, background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_manager'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def view_char_detail(self, idx):
        # 캐릭터 상세 보기 (나중에 인벤토리로 연결)
        print(f"{idx}번 캐릭터 상세 화면 진입 예정")

class PT1App(App):
    current_account = ""
    def build(self):
        Window.softinput_mode = "pan" # 2번 사진처럼 입력창 상단 고정
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(AccountManagerScreen(name='account_manager'))
        sm.add_widget(CharacterSelectScreen(name='char_select'))
        return sm

if __name__ == '__main__':
    PT1App().run()
