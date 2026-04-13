import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window

# 설정 리소스 (사용자 지정)
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"
CHAR_ICON = "images.jpeg" 
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
        return {"accounts": {}} # 기본 구조

    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# 공통 배경 설정
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

# --- 1. 계정 관리 화면 ---
class AccountManagerScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 전체 검색창 (7단계 예정이나 미리 디자인 배치)
        search_box = BoxLayout(size_hint_y=None, height=100, spacing=5)
        self.search_input = TextInput(hint_text="계정, 캐릭터, 아이템 검색...", font_name=self.f, multiline=False)
        search_btn = Button(text="검색", font_name=self.f, size_hint_x=0.2, background_color=(0.2, 0.4, 0.8, 1))
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        layout.add_widget(search_box)

        layout.add_widget(Button(text="+ 새 계정 등록", font_name=self.f, size_hint_y=None, height=100, 
                                 background_color=(0.1, 0.5, 0.1, 1), on_release=self.show_create_popup))

        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        for acc_id in self.data.get("accounts", {}).keys():
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            btn = Button(text=f" 계정: {acc_id}", font_name=self.f, halign='left', background_color=(0.2, 0.2, 0.3, 1))
            btn.bind(on_release=lambda x, a=acc_id: self.go_to_chars(a))
            del_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.2, background_color=(0.7, 0.1, 0.1, 1))
            del_btn.bind(on_release=lambda x, a=acc_id: self.confirm_delete(a))
            row.add_widget(btn); row.add_widget(del_btn)
            self.grid.add_widget(row)
            
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def go_to_chars(self, acc_id):
        App.get_running_app().current_account = acc_id
        self.manager.current = 'char_select'

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with content.canvas.before:
            Color(0.05, 0.2, 0.1, 1) # 짙은 녹색
            self.rect_p = Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda ins,v: setattr(self.rect_p,'pos',ins.pos), size=lambda ins,v: setattr(self.rect_p,'size',ins.size))
        
        content.add_widget(Label(text="[toopen] 계정 생성", font_name=self.f))
        self.id_in = TextInput(hint_text="ID 입력", font_name=self.f, multiline=False, size_hint_y=None, height=90)
        content.add_widget(self.id_in)
        btn = Button(text="생성 완료", font_name=self.f, size_hint_y=None, height=90, background_color=(0.1, 0.6, 0.2, 1))
        content.add_widget(btn)
        
        popup = Popup(title="신규 등록", title_font=self.f, content=content, size_hint=(0.8, 0.35))
        btn.bind(on_release=lambda x: self.create_acc(self.id_in.text, popup))
        popup.open()

    def create_acc(self, acc_id, popup):
        if acc_id:
            if "accounts" not in self.data: self.data["accounts"] = {}
            self.data["accounts"][acc_id] = {str(i): {"name": f"캐릭터 {i}", "job": "없음", "lv": "1", "stats": {"힘": "0", "민": "0", "정": "0", "건": "0"}, "inv": []} for i in range(1, 7)}
            DataManager.save(self.data)
            self.on_pre_enter()
        popup.dismiss()

    def confirm_delete(self, acc_id):
        # 삭제 확인 멘트 추가
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"'{acc_id}'를 삭제하겠습니까?", font_name=self.f))
        btns = BoxLayout(size_hint_y=None, height=80, spacing=10)
        y_b = Button(text="삭제", font_name=self.f); n_b = Button(text="취소", font_name=self.f)
        btns.add_widget(n_b); btns.add_widget(y_b)
        content.add_widget(btns)
        popup = Popup(title="경고", title_font=self.f, content=content, size_hint=(0.7, 0.3))
        y_b.bind(on_release=lambda x: self.delete_acc(acc_id, popup))
        n_b.bind(on_release=popup.dismiss); popup.open()

    def delete_acc(self, acc_id, popup):
        del self.data["accounts"][acc_id]
        DataManager.save(self.data); self.on_pre_enter(); popup.dismiss()

# --- 2. 캐릭터 선택 화면 (6슬롯) ---
class CharacterSelectScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        acc_id = self.app.current_account
        layout.add_widget(Label(text=f"<{acc_id}> 캐릭터 선택", font_name=self.f, font_size='20sp', size_hint_y=None, height=80))

        grid = GridLayout(cols=2, spacing=15)
        chars = self.data["accounts"][acc_id]
        for i in range(1, 7):
            char_info = chars.get(str(i))
            btn = Button(background_color=(0.1, 0.1, 0.2, 1))
            box = BoxLayout(orientation='vertical', padding=5)
            box.add_widget(Image(source=CHAR_ICON, size_hint_y=0.7))
            box.add_widget(Label(text=f"{char_info['name']}\n(Lv.{char_info['lv']})", font_name=self.f, font_size='14sp', halign='center'))
            btn.add_widget(box)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        layout.add_widget(Button(text="뒤로가기", font_name=self.f, size_hint_y=None, height=100, on_release=lambda x: setattr(self.manager, 'current', 'account_manager')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.app.current_char_idx = str(idx)
        self.manager.current = 'char_detail'

# --- 3. 캐릭터 상세 세부내용 화면 (스탯 수정 및 사진) ---
class CharacterDetailScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.current_account][self.app.current_char_idx]
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        # 전체 스크롤 가능하게 구성
        main_scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 상단 이름 수정 (여기에 적으면 캐릭터창 이름도 바뀜)
        layout.add_widget(Label(text="캐릭터 이름 수정", font_name=self.f, size_hint_y=None, height=40))
        self.name_in = TextInput(text=self.char_data['name'], font_name=self.f, multiline=False, size_hint_y=None, height=90)
        layout.add_widget(self.name_in)

        # 직업 및 레벨
        row1 = BoxLayout(size_hint_y=None, height=90, spacing=10)
        self.job_in = TextInput(text=self.char_data['job'], hint_text="직업", font_name=self.f)
        self.lv_in = TextInput(text=self.char_data['lv'], hint_text="레벨", font_name=self.f)
        row1.add_widget(self.job_in); row1.add_widget(self.lv_in)
        layout.add_widget(row1)

        # 스탯 (힘, 민, 정, 건)
        stats_grid = GridLayout(cols=2, size_hint_y=None, height=200, spacing=10)
        self.str_in = TextInput(text=self.char_data['stats']['힘'], hint_text="힘(Str)", font_name=self.f)
        self.agi_in = TextInput(text=self.char_data['stats']['민'], hint_text="민첩(Agi)", font_name=self.f)
        stats_grid.add_widget(self.str_in); stats_grid.add_widget(self.agi_in)
        layout.add_widget(stats_grid)

        # 사진 표시 공간
        layout.add_widget(Label(text="캐릭터 사진", font_name=self.f, size_hint_y=None, height=40))
        layout.add_widget(Image(source=CHAR_ICON, size_hint_y=None, height=300))
        layout.add_widget(Button(text="사진 추가/변경 (갤러리)", font_name=self.f, size_hint_y=None, height=100, background_color=(0.4, 0.4, 0.4, 1)))

        # 하단 버튼바
        btn_bar = BoxLayout(size_hint_y=None, height=120, spacing=10)
        save_b = Button(text="정보 저장", font_name=self.f, background_color=(0.1, 0.5, 0.1, 1))
        save_b.bind(on_release=self.save_data)
        inv_b = Button(text="인벤토리 보기", font_name=self.f, background_color=(0.2, 0.4, 0.6, 1))
        back_b = Button(text="뒤로가기", font_name=self.f)
        back_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        btn_bar.add_widget(back_b); btn_bar.add_widget(inv_b); btn_bar.add_widget(save_b)
        layout.add_widget(btn_bar)

        main_scroll.add_widget(layout)
        self.add_widget(main_scroll)

    def save_data(self, *args):
        # 데이터 업데이트
        self.char_data['name'] = self.name_in.text
        self.char_data['job'] = self.job_in.text
        self.char_data['lv'] = self.lv_in.text
        self.char_data['stats'] = {"힘": self.str_in.text, "민": self.agi_in.text, "정": "0", "건": "0"}
        DataManager.save(self.data)
        # 저장 후 알림 (슬림 팝업 활용)
        c = Label(text="저장되었습니다!", font_name=self.f)
        p = Popup(title="알림", content=c, size_hint=(0.6, 0.2)); p.open()

class PT1App(App):
    current_account = ""
    current_char_idx = ""
    def build(self):
        Window.softinput_mode = "pan"
        # 시작 시 권한 허용 팝업 (가상)
        print("사진 및 저장소 권한을 요청합니다...")
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(AccountManagerScreen(name='account_manager'))
        sm.add_widget(CharacterSelectScreen(name='char_select'))
        sm.add_widget(CharacterDetailScreen(name='char_detail'))
        return sm

if __name__ == '__main__':
    PT1App().run()
