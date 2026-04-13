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
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window

# --- 리소스 및 데이터 설정 ---
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
                try:
                    data = json.load(f)
                    if "accounts" not in data: data = {"accounts": {}}
                    return data
                except: return {"accounts": {}}
        return {"accounts": {}}

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

class AccountManagerScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Button(text="+ 새 계정 등록", font_name=self.f, size_hint_y=None, height=110, 
                                 background_color=(0.1, 0.5, 0.1, 1), on_release=self.show_create_popup))
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        for acc_id in self.data["accounts"].keys():
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            btn = Button(text=f" 계정: {acc_id}", font_name=self.f, halign='left', background_color=(0.2, 0.2, 0.3, 1))
            btn.bind(on_release=lambda x, a=acc_id: self.go_to_chars(a))
            row.add_widget(btn)
            self.grid.add_widget(row)
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with content.canvas.before:
            Color(0.05, 0.2, 0.1, 1)
            self.rect_p = Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda ins,v: setattr(self.rect_p, 'pos', ins.pos), size=lambda ins,v: setattr(self.rect_p, 'size', ins.size))
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
            self.data["accounts"][acc_id] = {str(i): {"name": f"캐릭 {i}", "job": "없음", "lv": "1", 
                                                    "stats": {"힘":"0","정":"0","민":"0","건":"0","재":"0"}} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()
        popup.dismiss()

    def go_to_chars(self, acc_id):
        App.get_running_app().current_account = acc_id
        self.manager.current = 'char_select'

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
        layout.add_widget(Label(text=f"[{acc_id}] 캐릭터 선택", font_name=self.f, font_size='20sp', size_hint_y=None, height=80))
        grid = GridLayout(cols=2, spacing=15)
        for i in range(1, 7):
            c = self.data["accounts"][acc_id][str(i)]
            btn = Button(text=f"{c['name']}\n(Lv.{c['lv']})", font_name=self.f, background_color=(0.1, 0.1, 0.2, 1), halign='center')
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        layout.add_widget(Button(text="뒤로가기", font_name=self.f, size_hint_y=None, height=110, on_release=lambda x: setattr(self.manager, 'current', 'account_manager')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.app.current_char_idx = str(idx)
        self.manager.current = 'char_detail'

class CharacterDetailScreen(BackgroundScreen):
    def on_pre_enter(self):
        self.f = load_korean_font()
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.current_account][self.app.current_char_idx]
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height=100, spacing=5)
        top_bar.add_widget(Button(text="뒤로", font_name=self.f, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        top_bar.add_widget(Button(text="저장", font_name=self.f, background_color=(0, 0.6, 0.2, 1), on_release=self.save_char))
        layout.add_widget(top_bar)
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[0,10])
        content.bind(minimum_height=content.setter('height'))
        row_basic = BoxLayout(size_hint_y=None, height=90, spacing=5)
        self.name_in = TextInput(text=self.char_data['name'], font_name=self.f, multiline=False)
        self.job_in = TextInput(text=self.char_data.get('job', '없음'), font_name=self.f, multiline=False)
        self.lv_in = TextInput(text=self.char_data.get('lv', '1'), font_name=self.f, multiline=False)
        row_basic.add_widget(self.name_in); row_basic.add_widget(self.job_in); row_basic.add_widget(self.lv_in)
        content.add_widget(row_basic)
        stats_grid = GridLayout(cols=2, size_hint_y=None, height=280, spacing=10)
        self.str_in = TextInput(text=self.char_data['stats'].get('힘','0'), hint_text="힘", font_name=self.f)
        self.spi_in = TextInput(text=self.char_data['stats'].get('정','0'), hint_text="정신", font_name=self.f)
        self.agi_in = TextInput(text=self.char_data['stats'].get('민','0'), hint_text="민첩", font_name=self.f)
        self.con_in = TextInput(text=self.char_data['stats'].get('건','0'), hint_text="건강", font_name=self.f)
        self.tal_in = TextInput(text=self.char_data['stats'].get('재','0'), hint_text="재능", font_name=self.f)
        stats_grid.add_widget(self.str_in); stats_grid.add_widget(self.spi_in)
        stats_grid.add_widget(self.agi_in); stats_grid.add_widget(self.con_in); stats_grid.add_widget(self.tal_in)
        content.add_widget(stats_grid)
        content.add_widget(Button(text="인벤토리 관리 이동", font_name=self.f, size_hint_y=None, height=110, background_color=(0.2, 0.4, 0.6, 1)))
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def save_char(self, *args):
        self.char_data['name'] = self.name_in.text
        self.char_data['job'] = self.job_in.text
        self.char_data['lv'] = self.lv_in.text
        self.char_data['stats'] = {"힘": self.str_in.text, "정": self.spi_in.text, "민": self.agi_in.text, "건": self.con_in.text, "재": self.tal_in.text}
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="저장 완료", font_name=self.f), size_hint=(0.4, 0.2)).open()

class PT1App(App):
    current_account = ""; current_char_idx = ""
    def build(self):
        Window.softinput_mode = "pan"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(AccountManagerScreen(name='account_manager'))
        sm.add_widget(CharacterSelectScreen(name='char_select'))
        sm.add_widget(CharacterDetailScreen(name='char_detail'))
        return sm

if __name__ == '__main__':
    PT1App().run()
