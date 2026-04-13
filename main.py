import os
import json
import tempfile
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.cache import Cache

# 안드로이드 네이티브 브릿지 (Termux 절대 금지 원칙 준수)
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from android import activity
    from jnius import autoclass

# --- 설정 및 경로 ---
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DB_VERSION = "v31_master"

class DataManager:
    @staticmethod
    def get_path():
        if platform == 'android':
            base_dir = App.get_running_app().user_data_dir
            os.makedirs(base_dir, exist_ok=True)
            return os.path.join(base_dir, f"pt1_data_{DB_VERSION}.json")
        return f"pt1_data_{DB_VERSION}.json"

    @staticmethod
    def load():
        path = DataManager.get_path()
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) and "accounts" in data else {"accounts": {}}
            except: return {"accounts": {}}
        return {"accounts": {}}

    @staticmethod
    def save(data):
        path = DataManager.get_path()
        try:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            return True
        except: return False

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0, 0.01, 0.02, 1) # OLED 블랙 최적화
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
        self.search_in = TextInput(text=search_text, hint_text="계정 검색...", multiline=False, font_name="KFont" if os.path.exists(FONT_PATH) else None)
        s_btn = Button(text="찾기", size_hint_x=0.25, background_color=(0.1, 0.5, 0.9, 1))
        s_btn.bind(on_release=lambda x: self.render_ui(self.search_in.text))
        search_box.add_widget(self.search_in); search_box.add_widget(s_btn); layout.add_widget(search_box)
        layout.add_widget(Button(text="+ 계정 추가", size_hint_y=None, height=140, background_color=(0.1, 0.7, 0.3, 1), on_release=self.popup_add_acc))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=15)
        grid.bind(minimum_height=grid.setter('height'))
        accounts = self.data.get("accounts", {})
        for acc_id in sorted(accounts.keys()):
            if not search_text or search_text.lower() in str(acc_id).lower():
                row = BoxLayout(size_hint_y=None, height=140, spacing=10)
                btn = Button(text=f"ID: {acc_id}", background_color=(0.2, 0.3, 0.6, 1))
                btn.bind(on_release=lambda x, a=acc_id: self.go_chars(str(a)))
                del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
                del_btn.bind(on_release=lambda x, a=acc_id: self.do_delete(str(a)))
                row.add_widget(btn); row.add_widget(del_btn); grid.add_widget(row)
        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)
    def popup_add_acc(self, *args):
        c = BoxLayout(orientation='vertical', padding=25, spacing=20)
        inp = TextInput(hint_text="ID 입력", multiline=False, size_hint_y=None, height=120)
        b = Button(text="등록", size_hint_y=None, height=120, background_color=(0.2, 0.6, 0.4, 1))
        p = Popup(title="계정 추가", content=c, size_hint=(0.9, 0.4))
        b.bind(on_release=lambda x: self.add_acc(inp.text, p)); c.add_widget(inp); c.add_widget(b); p.open()
    def add_acc(self, acc_id, p):
        acc_id = acc_id.strip()
        if acc_id:
            if "accounts" not in self.data: self.data["accounts"] = {}
            self.data["accounts"][acc_id] = {str(i): {"name": f"슬롯 {i}", "photos": []} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()
        p.dismiss()
    def do_delete(self, acc_id):
        if acc_id in self.data["accounts"]: del self.data["accounts"][acc_id]; DataManager.save(self.data); self.on_pre_enter()
    def go_chars(self, acc_id): App.get_running_app().cur_acc = acc_id; self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    def on_pre_enter(self): self.data = DataManager.load(); self.render_ui()
    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        grid = GridLayout(cols=2, spacing=25)
        chars = self.data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            char_info = chars.get(str(i), {"name": f"슬롯 {i}"})
            btn = Button(text=f"SLOT {i}\n{char_info['name']}", halign='center')
            btn.bind(on_release=lambda x, idx=i: self.go_detail(str(idx))); grid.add_widget(btn)
        layout.add_widget(grid)
        layout.add_widget(Button(text="메인으로", size_hint_y=None, height=130, on_release=lambda x: setattr(self.manager, 'current', 'account_main')))
        self.add_widget(layout)
    def go_detail(self, idx): App.get_running_app().cur_char = idx; self.manager.current = 'char_detail'

class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        acc_data = self.data["accounts"].get(self.app.cur_acc, {})
        self.char_data = acc_data.get(self.app.cur_char, {"name": "Empty", "photos": []})
        self.render_ui()
    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=15)
        nav = BoxLayout(size_hint_y=None, height=130, spacing=10)
        nav.add_widget(Button(text="취소", on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="저장", background_color=(0, 0.6, 0.3, 1), on_release=self.save_all))
        layout.add_widget(nav)
        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[0, 20, 0, 60])
        self.content.bind(minimum_height=self.content.setter('height'))
        self.name_in = self.add_row("캐릭터명", self.char_data['name'])
        self.photo_grid = GridLayout(cols=3, size_hint_y=None, spacing=8, height=360)
        self.draw_photos(); self.content.add_widget(self.photo_grid)
        btn_pic = Button(text="+ 사진 추가", size_hint_y=None, height=120, background_color=(0.4, 0.4, 0.6, 1))
        btn_pic.bind(on_release=self.open_gallery); self.content.add_widget(btn_pic)
        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)
    def add_row(self, label, val):
        r = BoxLayout(size_hint_y=None, height=120, spacing=15)
        r.add_widget(Label(text=label, size_hint_x=0.35)); inp = TextInput(text=str(val), multiline=False)
        r.add_widget(inp); self.content.add_widget(r); return inp
    def draw_photos(self):
        self.photo_grid.clear_widgets()
        for path in self.char_data.get("photos", []):
            img = AsyncImage(source=f"{path}#t={time.time()}", allow_stretch=True, keep_ratio=True, nocache=True)
            btn = Button(size_hint_y=None, height=340, background_normal='', background_color=(1,1,1,0.05))
            btn.add_widget(img); btn.bind(on_release=lambda x, p=path: self.del_photo(p))
            self.photo_grid.add_widget(btn)
    def del_photo(self, path):
        if path in self.char_data["photos"]: self.char_data["photos"].remove(path)
        Clock.schedule_once(lambda dt: self.draw_photos())
    def open_gallery(self, *args):
        if platform == 'android':
            perm = Permission.READ_MEDIA_IMAGES
            if check_permission(perm): self.launch_gallery([], [True])
            else: request_permissions([perm], self.launch_gallery)
    def launch_gallery(self, permissions, results):
        if any(results):
            Intent = autoclass('android.content.Intent'); act = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("image/*")
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION)
            act.startActivityForResult(intent, 101)
    def save_all(self, *args):
        self.char_data['name'] = self.name_in.text; DataManager.save(self.data)
        Popup(title="성공", content=Label(text="저장 완료"), size_hint=(0.6, 0.3)).open()

class PTManagerApp(App):
    cur_acc = ""
    cur_char = ""

    def build(self):
        self.title = "PT1 Manager Master"
        # 폰트 오류 수정 (Line-by-line 강화)
        if os.path.exists(FONT_PATH):
            try: 
                LabelBase.register(name="KFont", fn_regular=FONT_PATH)
                # Kivy 기본 폰트를 사용자 폰트로 강제 대체
                LabelBase.register(name="Roboto", fn_regular=FONT_PATH)
            except Exception as e:
                print(f"Font Load Error: {e}")
        
        if platform == 'android': activity.bind(on_activity_result=self.on_gallery_result)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main')); sm.add_widget(CharSelectScreen(name='char_select')); sm.add_widget(CharDetailScreen(name='char_detail'))
        return sm
    def on_gallery_result(self, request_code, result_code, intent):
        if request_code == 101 and result_code == -1 and intent:
            uri = intent.getData()
            if uri:
                path = uri.toString()
                if platform == 'android':
                    try:
                        act = autoclass('org.kivy.android.PythonActivity').mActivity
                        takeFlags = intent.getFlags() & (autoclass('android.content.Intent').FLAG_GRANT_READ_URI_PERMISSION)
                        act.getContentResolver().takePersistableUriPermission(uri, takeFlags)
                    except: pass
                if self.root.current == 'char_detail':
                    Clock.schedule_once(lambda dt: self.update_char_photos(path))
    def update_char_photos(self, path):
        screen = self.root.current_screen
        if path not in screen.char_data.setdefault("photos", []):
            screen.char_data["photos"].append(path); screen.draw_photos()
            DataManager.save(screen.data)
    def on_pause(self): 
        Cache.remove('kv.image'); Cache.remove('kv.texture')
        return True

if __name__ == '__main__':
    PTManagerApp().run()
