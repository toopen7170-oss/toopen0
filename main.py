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
from kivy.clock import Clock
from kivy.utils import platform

# 안드로이드 네이티브 갤러리 연동 (빌드 시 필수)
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass

# --- 환경 설정 ---
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DATA_FILE = "pt_manager_data.json"

if os.path.exists(FONT_PATH):
    LabelBase.register(name="KFont", fn_regular=FONT_PATH)
    DEFAULT_FONT = "KFont"
else:
    DEFAULT_FONT = None

class DataManager:
    @staticmethod
    def load():
        default_data = {"accounts": {}}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return default_data
        return default_data

    @staticmethod
    def save(data):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except: return False

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.05, 0.05, 0.1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size

class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self, search_text=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=[30, 80, 30, 30], spacing=20)
        search_box = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.search_in = TextInput(text=search_text, hint_text="계정/캐릭/아이템 검색", font_name=DEFAULT_FONT, multiline=False)
        s_btn = Button(text="검색", font_name=DEFAULT_FONT, size_hint_x=0.25, background_color=(0.1, 0.5, 0.9, 1))
        s_btn.bind(on_release=lambda x: self.render_ui(self.search_in.text))
        search_box.add_widget(self.search_in); search_box.add_widget(s_btn); layout.add_widget(search_box)
        layout.add_widget(Button(text="+ 새 계정 만들기", font_name=DEFAULT_FONT, size_hint_y=None, height=140, background_color=(0.2, 0.7, 0.4, 1), on_release=self.popup_add_acc))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=15)
        grid.bind(minimum_height=grid.setter('height'))
        st = search_text.lower()
        for acc_id, details in sorted(self.data["accounts"].items()):
            if not st or st in acc_id.lower() or st in str(details).lower():
                row = BoxLayout(size_hint_y=None, height=140, spacing=10)
                btn = Button(text=f"ID: {acc_id}", font_name=DEFAULT_FONT, background_color=(0.2, 0.3, 0.6, 1))
                btn.bind(on_release=lambda x, a=acc_id: self.go_chars(a))
                del_btn = Button(text="삭제", font_name=DEFAULT_FONT, size_hint_x=0.25, background_color=(0.8, 0.2, 0.2, 1))
                del_btn.bind(on_release=lambda x, a=acc_id: self.ask_delete(a))
                row.add_widget(btn); row.add_widget(del_btn); grid.add_widget(row)
        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def popup_add_acc(self, *args):
        c = BoxLayout(orientation='vertical', padding=25, spacing=20)
        inp = TextInput(hint_text="계정 ID 입력", font_name=DEFAULT_FONT, multiline=False, size_hint_y=None, height=120)
        b = Button(text="등록", font_name=DEFAULT_FONT, size_hint_y=None, height=120, background_color=(0.2, 0.6, 0.4, 1))
        p = Popup(title="계정 추가", content=c, size_hint=(0.9, 0.4), title_font=DEFAULT_FONT)
        b.bind(on_release=lambda x: self.add_acc(inp.text, p)); c.add_widget(inp); c.add_widget(b); p.open()

    def add_acc(self, acc_id, p):
        if acc_id.strip():
            self.data["accounts"][acc_id] = {str(i): self.get_empty_char(i) for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()
        p.dismiss()

    def get_empty_char(self, i):
        return {"name": f"캐릭터 {i}", "job": "", "lv": "1", "stats": {s: "0" for s in ["힘", "민첩", "정신", "건강", "재능"]}, "items": {k: "" for k in ["무기", "갑옷", "방패", "장갑", "부츠", "아뮬", "링1", "링2"]}, "inventory": [], "photos": []}

    def ask_delete(self, acc_id):
        c = BoxLayout(orientation='vertical', padding=25, spacing=20)
        c.add_widget(Label(text=f"'{acc_id}'를 삭제할까요?", font_name=DEFAULT_FONT))
        y = Button(text="삭제", font_name=DEFAULT_FONT, background_color=(0.8, 0.2, 0.2, 1))
        p = Popup(title="확인", content=c, size_hint=(0.8, 0.4), title_font=DEFAULT_FONT)
        y.bind(on_release=lambda x: self.do_delete(acc_id, p)); c.add_widget(y); p.open()

    def do_delete(self, acc_id, p):
        if acc_id in self.data["accounts"]: del self.data["accounts"][acc_id]; DataManager.save(self.data); self.on_pre_enter()
        p.dismiss()

    def go_chars(self, acc_id): App.get_running_app().cur_acc = acc_id; self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    def on_pre_enter(self): self.data = DataManager.load(); self.render_ui()
    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        layout.add_widget(Label(text=f"ID: {app.cur_acc}", font_name=DEFAULT_FONT, size_hint_y=None, height=80))
        grid = GridLayout(cols=2, spacing=25)
        chars = self.data["accounts"][app.cur_acc]
        for i in range(1, 7):
            c = chars[str(i)]
            btn = Button(text=f"SLOT {i}\n{c['name']}", font_name=DEFAULT_FONT, halign='center')
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx)); grid.add_widget(btn)
        layout.add_widget(grid)
        layout.add_widget(Button(text="뒤로", font_name=DEFAULT_FONT, size_hint_y=None, height=130, on_release=lambda x: setattr(self.manager, 'current', 'account_main')))
        self.add_widget(layout)
    def go_detail(self, idx): App.get_running_app().cur_char = str(idx); self.manager.current = 'char_detail'

class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        if platform == 'android': activity.bind(on_activity_result=self.on_gallery_result)
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=15)
        nav = BoxLayout(size_hint_y=None, height=130, spacing=10)
        nav.add_widget(Button(text="뒤로", font_name=DEFAULT_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="저장", font_name=DEFAULT_FONT, background_color=(0, 0.6, 0.3, 1), on_release=self.save_all))
        layout.add_widget(nav)
        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[0, 20, 0, 60])
        self.content.bind(minimum_height=self.content.setter('height'))
        self.name_in = self.add_row("캐릭터명", self.char_data['name'])
        self.add_tag("스텟")
        self.stat_inps = {s: self.add_row(s, self.char_data['stats'].get(s, "0")) for s in ["힘", "민첩", "정신", "건강", "재능"]}
        self.add_tag("스크린샷 (터치 시 삭제)")
        self.photo_grid = GridLayout(cols=3, size_hint_y=None, spacing=8, height=300)
        self.draw_photos(); self.content.add_widget(self.photo_grid)
        btn_pic = Button(text="+ 갤러리 열기", font_name=DEFAULT_FONT, size_hint_y=None, height=120, background_color=(0.4, 0.4, 0.6, 1))
        btn_pic.bind(on_release=self.open_gallery); self.content.add_widget(btn_pic)
        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)

    def add_tag(self, text): self.content.add_widget(Label(text=f"■ {text}", font_name=DEFAULT_FONT, size_hint_y=None, height=70, color=(1, 0.9, 0.2, 1)))
    def add_row(self, label, val):
        r = BoxLayout(size_hint_y=None, height=120, spacing=15)
        r.add_widget(Label(text=label, font_name=DEFAULT_FONT, size_hint_x=0.3))
        inp = TextInput(text=str(val), font_name=DEFAULT_FONT, multiline=False); r.add_widget(inp); self.content.add_widget(r); return inp

    def draw_photos(self):
        self.photo_grid.clear_widgets()
        for path in self.char_data.get("photos", []):
            if os.path.exists(path):
                img = Button(background_normal=path, size_hint_y=None, height=280)
                img.bind(on_release=lambda x, p=path: self.del_photo(p)); self.photo_grid.add_widget(img)

    def del_photo(self, path):
        if path in self.char_data["photos"]: self.char_data["photos"].remove(path); self.draw_photos()

    def open_gallery(self, *args):
        if platform == 'android': request_permissions([Permission.READ_MEDIA_IMAGES], self.launch_gallery)
        else: print("PC환경")

    def launch_gallery(self, *args):
        Intent = autoclass('android.content.Intent'); act = autoclass('org.kivy.android.PythonActivity').mActivity
        intent = Intent(Intent.ACTION_PICK); intent.setType("image/*"); act.startActivityForResult(intent, 101)

    def on_gallery_result(self, request_code, result_code, intent):
        if request_code == 101 and result_code == -1:
            uri = intent.getData(); path = self.get_real_path(uri)
            if path: self.char_data.setdefault("photos", []).append(path); self.draw_photos()

    def get_real_path(self, uri):
        try:
            act = autoclass('org.kivy.android.PythonActivity').mActivity
            CursorLoader = autoclass('android.content.CursorLoader')
            proj = ["_data"]; loader = CursorLoader(act, uri, proj, None, None, None)
            cursor = loader.loadInBackground()
            idx = cursor.getColumnIndexOrThrow("_data"); cursor.moveToFirst()
            path = cursor.getString(idx); cursor.close(); return path
        except: return None

    def save_all(self, *args):
        self.char_data['name'] = self.name_in.text
        for s, inp in self.stat_inps.items(): self.char_data['stats'][s] = inp.text
        DataManager.save(self.data); Popup(title="알림", content=Label(text="저장 완료"), size_hint=(0.6, 0.3)).open()

class PTManagerApp(App):
    def build(self):
        self.title = "PRISTON TAIL Manager"
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='char_detail'))
        return sm

if __name__ == '__main__':
    PTManagerApp().run()
