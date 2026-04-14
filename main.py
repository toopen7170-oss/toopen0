import os, json, tempfile
from functools import partial
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
from kivy.utils import platform
from kivy.clock import Clock

# [1] 안드로이드 환경 설정
if platform == 'android':
    from android.permissions import request_permissions, Permission

# [2] 전역 설정 (사용자 요청: DB_NAME 변경)
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DB_NAME = "Pristontale.json"
K_FONT = "KFont" if os.path.exists(FONT_PATH) else None

# [3] UI: 자동 스크롤 TextInput (글씨 안보임 방지)
class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.font_name = K_FONT
        self.font_size = 32
        self.cursor_color = [0.1, 0.5, 0.9, 1]
        self.background_color = [1, 1, 1, 0.9]
        self.bind(size=self._update_padding, text=self._update_padding)

    def _update_padding(self, *args):
        if self.line_height > 0:
            self.padding_y = [self.height / 2 - (self.line_height / 2), 0]

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(self._scroll_to_me, 0.2)

    def _scroll_to_me(self, dt):
        p = self.parent
        while p and not isinstance(p, ScrollView):
            p = p.parent
        if p: p.scroll_to(self)

# [4] 데이터 매니저 (Pristontale.json 처리)
class DataManager:
    @staticmethod
    def get_path():
        if platform == 'android':
            return os.path.join(App.get_running_app().user_data_dir, DB_NAME)
        return DB_NAME

    @staticmethod
    def load():
        path = DataManager.get_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"accounts": {}}

    @staticmethod
    def save(data):
        path = DataManager.get_path()
        try:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(tmp, path)
            return True
        except: return False

# [5] 화면 공통 베이스
class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.02, 0.05, 0.1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

def show_confirm(title, msg, on_yes):
    content = BoxLayout(orientation='vertical', padding=30, spacing=20)
    content.add_widget(Label(text=msg, font_name=K_FONT, font_size=32))
    btns = BoxLayout(size_hint_y=None, height=120, spacing=15)
    y_btn = Button(text="확인", background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT)
    n_btn = Button(text="취소", font_name=K_FONT)
    p = Popup(title=title, content=content, size_hint=(0.85, 0.4), title_font=K_FONT)
    y_btn.bind(on_release=lambda x: [on_yes(), p.dismiss()])
    n_btn.bind(on_release=p.dismiss)
    btns.add_widget(y_btn); btns.add_widget(n_btn); content.add_widget(btns); p.open()

# [6] 계정 목록
class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Button(text="+ 새 계정 생성", size_hint_y=None, height=140, background_color=(0.1, 0.6, 0.3, 1), font_name=K_FONT, on_release=self.add_acc_pop))
        
        scroll = ScrollView(); grid = GridLayout(cols=1, size_hint_y=None, spacing=15)
        grid.bind(minimum_height=grid.setter('height'))
        
        accounts = self.data.get("accounts", {})
        for acc_id in sorted(accounts.keys()):
            row = BoxLayout(size_hint_y=None, height=150, spacing=10)
            btn = Button(text=f"ID: {acc_id}", background_color=(0.2, 0.4, 0.7, 1), font_name=K_FONT, on_release=lambda x, a=acc_id: self.go_chars(a))
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.7, 0.2, 0.2, 1), font_name=K_FONT, on_release=lambda x, a=acc_id: show_confirm("삭제", f"'{a}' 삭제?", lambda: self.del_acc(a)))
            row.add_widget(btn); row.add_widget(del_b); grid.add_widget(row)
        
        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def add_acc_pop(self, *args):
        c = BoxLayout(orientation='vertical', padding=20, spacing=20)
        ti = StyledTextInput(hint_text="ID 입력")
        b = Button(text="생성", size_hint_y=None, height=120, font_name=K_FONT)
        p = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4), title_font=K_FONT)
        b.bind(on_release=lambda x: [self.create_acc(ti.text), p.dismiss()]); c.add_widget(ti); c.add_widget(b); p.open()

    def create_acc(self, name):
        if name.strip():
            self.data["accounts"][name] = {str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()

    def del_acc(self, name):
        if name in self.data["accounts"]: del self.data["accounts"][name]; DataManager.save(self.data); self.on_pre_enter()

    def go_chars(self, name):
        App.get_running_app().cur_acc = name; self.manager.current = 'char_select'

# [7] 캐릭터 선택
class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        layout.add_widget(Label(text=f"접속 중: {app.cur_acc}", size_hint_y=None, height=80, font_name=K_FONT, font_size=40))
        
        grid = GridLayout(cols=2, spacing=20)
        chars = self.data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            c = chars.get(str(i), {})
            btn = Button(text=f"Slot {i}\n{c.get('이름', '데이터 없음')}", halign='center', font_name=K_FONT)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(str(idx))); grid.add_widget(btn)
        
        layout.add_widget(grid)
        layout.add_widget(Button(text="뒤로가기", size_hint_y=None, height=120, font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'account_main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = idx; self.manager.current = 'char_info'

# [8] 케릭창 정보 (전수 검증 완료)
class CharInfoScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        main = BoxLayout(orientation='vertical', padding=20)
        main.add_widget(Label(text="[ 캐릭터 정보 ]", size_hint_y=None, height=80, font_name=K_FONT, font_size=38, color=(1, 0.8, 0, 1)))

        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[0, 0, 0, 100])
        self.content.bind(minimum_height=self.content.setter('height'))

        self.inputs = {}
        fields = ["직위", "이름", "클랜", "레벨", "생명력", "기력", "근력", "힘", "정신력", "재능", "민첩성", "건강", "능력치", "명중력", "공격력", "방어력", "흡수력", "속도"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=100, spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.35, font_name=K_FONT, font_size=28))
            ti = StyledTextInput(text=str(self.char_data.get(f, "")))
            row.add_widget(ti); self.inputs[f] = ti; self.content.add_widget(row)

        scroll.add_widget(self.content); main.add_widget(scroll)

        btn_bar = BoxLayout(size_hint_y=None, height=140, spacing=10)
        btn_bar.add_widget(Button(text="장비창 >", background_color=(0.1, 0.5, 0.8, 1), font_name=K_FONT, on_release=self.go_equip))
        btn_bar.add_widget(Button(text="저장", background_color=(0.1, 0.7, 0.3, 1), font_name=K_FONT, on_release=self.save_data))
        btn_bar.add_widget(Button(text="삭제", background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT, on_release=lambda x: show_confirm("삭제", "정보를 초기화할까요?", self.clear_data)))
        btn_bar.add_widget(Button(text="뒤로", font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        
        main.add_widget(btn_bar); self.add_widget(main)

    def save_data(self, *args):
        for k, v in self.inputs.items(): self.char_data[k] = v.text
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="저장되었습니다.", font_name=K_FONT), size_hint=(0.6, 0.2), title_font=K_FONT).open()

    def clear_data(self):
        for k in self.inputs:
            self.char_data[k] = ""
            self.inputs[k].text = ""
        DataManager.save(self.data)

    def go_equip(self, *args):
        for k, v in self.inputs.items(): self.char_data[k] = v.text
        DataManager.save(self.data); self.manager.current = 'char_equip'

# [9] 케릭장비창 정보 (전수 검증 완료)
class CharEquipScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        main = BoxLayout(orientation='vertical', padding=20)
        main.add_widget(Label(text="[ 장비 정보 ]", size_hint_y=None, height=80, font_name=K_FONT, font_size=38, color=(0, 0.8, 1, 1)))

        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[0, 0, 0, 100])
        self.content.bind(minimum_height=self.content.setter('height'))

        self.inputs = {}
        fields = ["한손무기", "두손무기", "갑옷", "방패", "슬릿", "장갑", "부츠", "쉘텀", "링1", "링2", "아뮬랫", "기타"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=100, spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.35, font_name=K_FONT, font_size=28))
            ti = StyledTextInput(text=str(self.char_data.get(f, "")))
            row.add_widget(ti); self.inputs[f] = ti; self.content.add_widget(row)

        scroll.add_widget(self.content); main.add_widget(scroll)

        btn_bar = BoxLayout(size_hint_y=None, height=140, spacing=10)
        btn_bar.add_widget(Button(text="저장", background_color=(0.1, 0.7, 0.3, 1), font_name=K_FONT, on_release=self.save_data))
        btn_bar.add_widget(Button(text="삭제", background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT, on_release=lambda x: show_confirm("삭제", "장비를 초기화할까요?", self.clear_data)))
        btn_bar.add_widget(Button(text="뒤로", font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_info')))
        
        main.add_widget(btn_bar); self.add_widget(main)

    def save_data(self, *args):
        for k, v in self.inputs.items(): self.char_data[k] = v.text
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="저장되었습니다.", font_name=K_FONT), size_hint=(0.6, 0.2), title_font=K_FONT).open()

    def clear_data(self):
        for k in self.inputs:
            self.char_data[k] = ""
            self.inputs[k].text = ""
        DataManager.save(self.data)

# [10] 앱 실행부
class ToOpenApp(App):
    cur_acc = ""; cur_char = ""
    def build(self):
        Window.softinput_mode = "below_target"
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="KFont", fn_regular=FONT_PATH)
            LabelBase.register(name="Roboto", fn_regular=FONT_PATH)
        
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharInfoScreen(name='char_info'))
        sm.add_widget(CharEquipScreen(name='char_equip'))
        return sm

if __name__ == '__main__':
    ToOpenApp().run()
