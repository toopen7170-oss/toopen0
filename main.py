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
from kivy.uix.image import AsyncImage
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.utils import platform

# 안드로이드 네이티브 최적화 (S26 울트라 대응)
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass

# --- 설정 (bg.png, font.ttf 필수) ---
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DB_NAME = "toopen0_final_v49.json"
K_FONT = "KFont" if os.path.exists(FONT_PATH) else None

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

def show_confirm(title, msg, on_yes):
    content = BoxLayout(orientation='vertical', padding=35, spacing=25)
    content.add_widget(Label(text=msg, font_name=K_FONT, halign='center', font_size=32))
    btns = BoxLayout(size_hint_y=None, height=130, spacing=20)
    y_btn = Button(text="확인(삭제)", background_color=(0.9, 0.2, 0.2, 1), font_name=K_FONT)
    n_btn = Button(text="취소", font_name=K_FONT)
    p = Popup(title=title, content=content, size_hint=(0.9, 0.45), title_font=K_FONT)
    y_btn.bind(on_release=lambda x: [on_yes(), p.dismiss()])
    n_btn.bind(on_release=p.dismiss)
    btns.add_widget(y_btn); btns.add_widget(n_btn); content.add_widget(btns); p.open()

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.02, 0.06, 0.12, 1)
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
        layout = BoxLayout(orientation='vertical', padding=[30, 90, 30, 60], spacing=25)
        
        # 통합 검색 영역
        sh = BoxLayout(size_hint_y=None, height=140, spacing=15)
        self.s_in = TextInput(text=search_text, hint_text="계정/아이템/직업 검색...", multiline=False, font_name=K_FONT, font_size=36)
        s_btn = Button(text="검색", size_hint_x=0.25, background_color=(0.1, 0.5, 0.9, 1), font_name=K_FONT)
        s_btn.bind(on_release=lambda x: self.render_ui(self.s_in.text))
        sh.add_widget(self.s_in); sh.add_widget(s_btn); layout.add_widget(sh)

        add = Button(text="+ 새 계정 만들기", size_hint_y=None, height=150, background_color=(0.1, 0.7, 0.4, 1), font_name=K_FONT, font_size=38)
        add.bind(on_release=self.add_acc_pop); layout.add_widget(add)

        scroll = ScrollView(); grid = GridLayout(cols=1, size_hint_y=None, spacing=18)
        grid.bind(minimum_height=grid.setter('height'))
        
        accounts = self.data.get("accounts", {})
        found = False
        for acc_id in sorted(accounts.keys()):
            if search_text:
                if search_text.lower() not in json.dumps(accounts[acc_id], ensure_ascii=False).lower() and \
                   search_text.lower() not in acc_id.lower(): continue
            found = True
            row = BoxLayout(size_hint_y=None, height=160, spacing=12)
            btn = Button(text=f"ID: {acc_id}", background_color=(0.2, 0.4, 0.7, 1), font_name=K_FONT, font_size=34)
            btn.bind(on_release=lambda x, a=acc_id: self.go_chars(a))
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT)
            del_b.bind(on_release=lambda x, a=acc_id: show_confirm("삭제 알림", f"'{a}'의 정보를 지울까요?", lambda: self.del_acc(a)))
            row.add_widget(btn); row.add_widget(del_b); grid.add_widget(row)

        if not found: grid.add_widget(Label(text="목록이 없거나 검색 결과가 없습니다.", font_name=K_FONT, font_size=30, size_hint_y=None, height=200))

        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def add_acc_pop(self, *args):
        c = BoxLayout(orientation='vertical', padding=30, spacing=20)
        ti = TextInput(hint_text="ID 입력", multiline=False, size_hint_y=None, height=130, font_name=K_FONT, font_size=36)
        b = Button(text="저장", size_hint_y=None, height=130, background_color=(0.1, 0.7, 0.4, 1), font_name=K_FONT)
        p = Popup(title="계정 추가", content=c, size_hint=(0.9, 0.45), title_font=K_FONT)
        b.bind(on_release=lambda x: self.create_acc(ti.text, p)); c.add_widget(ti); c.add_widget(b); p.open()

    def create_acc(self, name, p):
        if name.strip():
            self.data["accounts"][name] = {str(i): {"name": f"슬롯 {i}", "level": "1", "inven": [], "photos": []} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter(); p.dismiss()

    def del_acc(self, name):
        if name in self.data["accounts"]: del self.data["accounts"][name]; DataManager.save(self.data); self.on_pre_enter()

    def go_chars(self, name):
        App.get_running_app().cur_acc = name; self.manager.current = 'char_select'

class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=45, spacing=30)
        layout.add_widget(Label(text=f"접속 중: {app.cur_acc}", size_hint_y=None, height=110, font_name=K_FONT, font_size=42, color=(1, 0.9, 0.3, 1)))
        
        grid = GridLayout(cols=2, spacing=25)
        chars = self.data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            c = chars.get(str(i), {})
            btn = Button(text=f"[{i}번 슬롯]\n{c.get('name')}\nLv.{c.get('level')}", halign='center', background_color=(0.15, 0.45, 0.75, 1), font_name=K_FONT, font_size=32)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(str(idx))); grid.add_widget(btn)
        
        layout.add_widget(grid)
        back = Button(text="계정 선택으로 돌아가기", size_hint_y=None, height=140, background_color=(0.4, 0.4, 0.4, 1), font_name=K_FONT)
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_main')); layout.add_widget(back); self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = idx; self.manager.current = 'char_detail'

class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=15)
        nav = BoxLayout(size_hint_y=None, height=135, spacing=12)
        nav.add_widget(Button(text="취소", font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="모두 저장", background_color=(0.1, 0.7, 0.3, 1), font_name=K_FONT, on_release=self.save_all))
        layout.add_widget(nav)

        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[0, 10, 0, 150])
        self.content.bind(minimum_height=self.content.setter('height'))

        inv_btn = Button(text="🎒 인벤토리 관리", size_hint_y=None, height=170, background_color=(1, 0.5, 0, 1), font_name=K_FONT, font_size=40)
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory_screen'))
        self.content.add_widget(inv_btn)

        self.inputs = {}
        fields = [
            ("이름", "name"), ("직업", "job"), ("레벨", "level"), 
            ("힘", "str"), ("민첩", "dex"), ("정신", "int"), ("건강", "con"), ("재능", "tal"),
            ("양손무기", "w2"), ("한손무기", "w1"), ("갑옷", "armor"), ("로브", "robe"),
            ("방패", "shield"), ("암릿", "armlet"), ("장갑", "glove"), ("부츠", "boots"),
            ("아뮬렛", "amu"), ("링", "ring"), ("쉘텀", "shel"), ("기타", "etc")
        ]
        for lbl, key in fields:
            row = BoxLayout(size_hint_y=None, height=120, spacing=12)
            row.add_widget(Label(text=lbl, size_hint_x=0.32, font_name=K_FONT, font_size=32))
            ti = TextInput(text=str(self.char_data.get(key, "")), multiline=False, font_name=K_FONT, font_size=36)
            row.add_widget(ti); self.inputs[key] = ti; self.content.add_widget(row)

        self.p_grid = GridLayout(cols=3, size_hint_y=None, spacing=10, height=450)
        self.draw_photos(); self.content.add_widget(self.p_grid)
        
        p_btn = Button(text="+ 스크린샷 추가", size_hint_y=None, height=140, background_color=(0.4, 0.5, 0.9, 1), font_name=K_FONT)
        p_btn.bind(on_release=self.open_gal); self.content.add_widget(p_btn)

        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)

    def draw_photos(self):
        self.p_grid.clear_widgets()
        for p in self.char_data.get("photos", []):
            img = AsyncImage(source=p, allow_stretch=True)
            btn = Button(size_hint_y=None, height=400, background_color=(1,1,1,0.1))
            btn.add_widget(img)
            btn.bind(on_release=partial(self.ask_del_photo, p))
            self.p_grid.add_widget(btn)

    def ask_del_photo(self, path, *args):
        show_confirm("사진 삭제", "이 스크린샷을 삭제할까요?", lambda: self.del_photo(path))

    def del_photo(self, path):
        if path in self.char_data["photos"]:
            self.char_data["photos"].remove(path); self.draw_photos(); DataManager.save(self.data)

    def open_gal(self, *args):
        if platform == 'android': request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], self.launch_gal)
        else: self.launch_gal(None, [True])

    def launch_gal(self, p, res):
        if any(res):
            Intent = autoclass('android.content.Intent'); act = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT); intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("image/*")
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION)
            act.startActivityForResult(intent, 101)

    def save_all(self, *args):
        for key, ti in self.inputs.items(): self.char_data[key] = ti.text
        DataManager.save(self.data)
        Popup(title="저장", content=Label(text="데이터가 안전하게 저장되었습니다.", font_name=K_FONT), size_hint=(0.7, 0.3), title_font=K_FONT).open()

class InventoryScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        if "inven" not in self.char_data: self.char_data["inven"] = []
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=30, spacing=25)
        nav = BoxLayout(size_hint_y=None, height=140, spacing=12)
        nav.add_widget(Button(text="뒤로", font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_detail')))
        nav.add_widget(Button(text="+ 줄 추가", background_color=(0.1, 0.7, 0.4, 1), font_name=K_FONT, on_release=self.add_item))
        layout.add_widget(nav)

        scroll = ScrollView(); self.grid = GridLayout(cols=1, size_hint_y=None, spacing=15, padding=[0,0,0,250])
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        self.ti_list = []
        for i, item_text in enumerate(self.char_data["inven"]):
            row = BoxLayout(size_hint_y=None, height=140, spacing=12)
            ti = TextInput(text=item_text, multiline=False, font_size=36, font_name=K_FONT)
            del_btn = Button(text="X", size_hint_x=0.18, background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT)
            del_btn.bind(on_release=partial(self.ask_del_item, i))
            row.add_widget(ti); row.add_widget(del_btn); self.grid.add_widget(row); self.ti_list.append(ti)

        scroll.add_widget(self.grid); layout.add_widget(scroll)
        s_btn = Button(text="인벤토리 전체 저장", size_hint_y=None, height=150, background_color=(0.1, 0.5, 0.9, 1), font_name=K_FONT)
        s_btn.bind(on_release=self.save_inv); layout.add_widget(s_btn); self.add_widget(layout)

    def add_item(self, *args):
        self.char_data["inven"].append(""); self.render_ui()

    def ask_del_item(self, idx, *args):
        show_confirm("아이템 삭제", "이 줄을 삭제할까요?", lambda: self.del_item(idx))

    def del_item(self, idx):
        if 0 <= idx < len(self.char_data["inven"]):
            self.char_data["inven"].pop(idx); self.render_ui(); DataManager.save(self.data)

    def save_inv(self, *args):
        self.char_data["inven"] = [ti.text for ti in self.ti_list]
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="인벤토리가 저장되었습니다.", font_name=K_FONT), size_hint=(0.7, 0.3), title_font=K_FONT).open()

class ToOpenApp(App):
    cur_acc = ""; cur_char = ""
    def build(self):
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="KFont", fn_regular=FONT_PATH)
            LabelBase.register(name="Roboto", fn_regular=FONT_PATH)
        if platform == 'android': activity.bind(on_activity_result=self.on_gal_res)
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='char_detail'))
        sm.add_widget(InventoryScreen(name='inventory_screen'))
        return sm

    def on_gal_res(self, req, res, intent):
        if req == 101 and res == -1 and intent:
            uri = intent.getData()
            if uri:
                p = uri.toString()
                if platform == 'android':
                    try:
                        act = autoclass('org.kivy.android.PythonActivity').mActivity
                        act.getContentResolver().takePersistableUriPermission(uri, 1)
                    except: pass
                if self.root.current == 'char_detail':
                    scr = self.root.current_screen
                    if p not in scr.char_data["photos"]:
                        scr.char_data["photos"].append(p)
                        scr.char_data["photos"] = list(dict.fromkeys(scr.char_data["photos"]))
                        scr.draw_photos(); DataManager.save(scr.data)

if __name__ == '__main__':
    ToOpenApp().run()
