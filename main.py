import os, json, tempfile, time
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
from kivy.clock import Clock
from kivy.cache import Cache

# 안드로이드 네이티브 기능 (무료 오픈소스 라이브러리 활용)
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from android import activity
    from jnius import autoclass

# --- 설정 (bg.png, font.ttf 필수) ---
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DB_NAME = "toopen0_data_v4.json"

class DataManager:
    @staticmethod
    def get_path():
        if platform == 'android':
            base_dir = App.get_running_app().user_data_dir
            return os.path.join(base_dir, DB_NAME)
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

# --- 팝업 유틸리티 ---
def show_confirm(title, msg, on_yes):
    content = BoxLayout(orientation='vertical', padding=20, spacing=20)
    content.add_widget(Label(text=msg, font_name="KFont" if os.path.exists(FONT_PATH) else None))
    btns = BoxLayout(size_hint_y=None, height=100, spacing=10)
    y_btn = Button(text="예", background_color=(0.8, 0.2, 0.2, 1))
    n_btn = Button(text="아니오")
    p = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    y_btn.bind(on_release=lambda x: [on_yes(), p.dismiss()])
    n_btn.bind(on_release=p.dismiss)
    btns.add_widget(y_btn); btns.add_widget(n_btn); content.add_widget(btns); p.open()

# --- 1. 메인 계정 화면 (전체 검색 포함) ---
class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self, search_text=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=[20, 50, 20, 20], spacing=15)
        
        # 검색바
        search_layout = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.search_in = TextInput(text=search_text, hint_text="모든 항목 검색 (아이템, 레벨 등)", multiline=False)
        s_btn = Button(text="검색", size_hint_x=0.2, background_color=(0.2, 0.6, 1, 1))
        s_btn.bind(on_release=lambda x: self.render_ui(self.search_in.text))
        search_layout.add_widget(self.search_in); search_layout.add_widget(s_btn); layout.add_widget(search_layout)

        # 계정 추가 버튼
        add_btn = Button(text="+ 새 계정 만들기", size_hint_y=None, height=130, background_color=(0.1, 0.8, 0.4, 1))
        add_btn.bind(on_release=self.add_account_popup); layout.add_widget(add_btn)

        # 목록
        scroll = ScrollView(); grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        grid.bind(minimum_height=grid.setter('height'))
        
        accounts = self.data.get("accounts", {})
        for acc_id in sorted(accounts.keys()):
            # 검색 필터링 로직 (모든 텍스트 포함 검사)
            if search_text:
                found = False
                acc_str = json.dumps(accounts[acc_id], ensure_ascii=False).lower()
                if search_text.lower() in acc_str or search_text.lower() in acc_id.lower(): found = True
                if not found: continue

            row = BoxLayout(size_hint_y=None, height=140, spacing=10)
            btn = Button(text=f"계정: {acc_id}", background_color=(0.3, 0.4, 0.7, 1))
            btn.bind(on_release=lambda x, a=acc_id: self.go_chars(a))
            del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.9, 0.3, 0.3, 1))
            del_btn.bind(on_release=lambda x, a=acc_id: show_confirm("삭제", f"'{a}' 계정을 삭제하시겠습니까?", lambda: self.delete_account(a)))
            row.add_widget(btn); row.add_widget(del_btn); grid.add_widget(row)

        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def add_account_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        inp = TextInput(hint_text="계정 이름 입력", multiline=False, height=120, size_hint_y=None)
        btn = Button(text="생성", height=120, size_hint_y=None, background_color=(0.1, 0.8, 0.4, 1))
        p = Popup(title="계정 만들기", content=content, size_hint=(0.9, 0.4))
        btn.bind(on_release=lambda x: self.create_account(inp.text, p))
        content.add_widget(inp); content.add_widget(btn); p.open()

    def create_account(self, name, p):
        if name.strip():
            self.data["accounts"][name] = {str(i): {"name": f"캐릭터 {i}", "stats": {}, "items": {}, "photos": [], "inven": []} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter(); p.dismiss()

    def delete_account(self, name):
        if name in self.data["accounts"]:
            del self.data["accounts"][name]; DataManager.save(self.data); self.on_pre_enter()

    def go_chars(self, name):
        App.get_running_app().cur_acc = name; self.manager.current = 'char_select'

# --- 2. 캐릭터 선택 화면 (6개 슬롯) ---
class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        layout.add_widget(Label(text=f"계정: {app.cur_acc}", size_hint_y=None, height=100, font_size=40))
        
        grid = GridLayout(cols=2, spacing=20)
        chars = self.data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            c_info = chars.get(str(i), {"name": f"캐릭터 {i}"})
            btn = Button(text=f"Slot {i}\n{c_info.get('name')}", halign='center', background_color=(0.2, 0.5, 0.8, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(str(idx))); grid.add_widget(btn)
        
        layout.add_widget(grid)
        back_btn = Button(text="뒤로가기", size_hint_y=None, height=130, background_color=(0.5, 0.5, 0.5, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_main'))
        layout.add_widget(back_btn); self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = idx; self.manager.current = 'char_detail'

# --- 3. 캐릭터 세부 내용 & 인벤토리 연결 ---
class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=15)
        
        # 상단 바
        nav = BoxLayout(size_hint_y=None, height=130, spacing=10)
        b_btn = Button(text="뒤로", background_color=(0.5, 0.5, 0.5, 1))
        b_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        s_btn = Button(text="저장", background_color=(0.1, 0.7, 0.3, 1))
        s_btn.bind(on_release=self.save_all)
        d_btn = Button(text="초기화", background_color=(0.9, 0.3, 0.3, 1))
        d_btn.bind(on_release=lambda x: show_confirm("주의", "데이터를 초기화하시겠습니까?", self.reset_char))
        nav.add_widget(b_btn); nav.add_widget(s_btn); nav.add_widget(d_btn); layout.add_widget(nav)

        scroll = ScrollView(); self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.content.bind(minimum_height=self.content.setter('height'))

        # 인벤토리 이동 버튼
        inv_btn = Button(text="🎒 인벤토리 열기", size_hint_y=None, height=140, background_color=(0.9, 0.6, 0.1, 1))
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory_screen'))
        self.content.add_widget(inv_btn)

        # 기본 정보
        self.inputs = {}
        fields = [
            ("이름", "name"), ("직업", "job"), ("레벨", "level"), 
            ("힘", "str"), ("민첩", "dex"), ("정신", "int"), ("건강", "con"), ("재능", "tal"),
            ("양손무기", "w2"), ("한손무기", "w1"), ("갑옷", "armor"), ("로브", "robe"),
            ("방패", "shield"), ("암릿", "armlet"), ("장갑", "glove"), ("부츠", "boots"),
            ("아뮬렛", "amu"), ("링", "ring"), ("쉘텀", "shel"), ("기타", "etc")
        ]
        for label, key in fields:
            row = BoxLayout(size_hint_y=None, height=110, spacing=10)
            row.add_widget(Label(text=label, size_hint_x=0.3))
            ti = TextInput(text=str(self.char_data.get(key, "")), multiline=False)
            row.add_widget(ti); self.inputs[key] = ti; self.content.add_widget(row)

        # 사진 영역
        self.content.add_widget(Label(text="[ 사진 목록 ]", size_hint_y=None, height=80))
        self.photo_grid = GridLayout(cols=3, size_hint_y=None, spacing=5, height=350)
        self.draw_photos(); self.content.add_widget(self.photo_grid)
        
        p_btn = Button(text="+ 사진 추가", size_hint_y=None, height=120, background_color=(0.4, 0.4, 0.6, 1))
        p_btn.bind(on_release=self.open_gallery); self.content.add_widget(p_btn)

        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)

    def draw_photos(self):
        self.photo_grid.clear_widgets()
        for p in self.char_data.get("photos", []):
            img = AsyncImage(source=p, allow_stretch=True)
            btn = Button(size_hint_y=None, height=340); btn.add_widget(img)
            btn.bind(on_release=lambda x, path=p: show_confirm("삭제", "사진을 삭제하시겠습니까?", lambda: self.del_photo(path)))
            self.photo_grid.add_widget(btn)

    def del_photo(self, path):
        self.char_data["photos"].remove(path); self.draw_photos()

    def open_gallery(self, *args):
        if platform == 'android':
            request_permissions([Permission.READ_MEDIA_IMAGES], self.launch_gallery)
        else: self.launch_gallery(None, [True])

    def launch_gallery(self, p, results):
        if any(results):
            Intent = autoclass('android.content.Intent'); act = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT); intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("image/*")
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION)
            act.startActivityForResult(intent, 101)

    def save_all(self, *args):
        for key, ti in self.inputs.items(): self.char_data[key] = ti.text
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="저장되었습니다."), size_hint=(0.6, 0.3)).open()

    def reset_char(self):
        self.char_data.update({"name": "Empty", "photos": [], "inven": []})
        DataManager.save(self.data); self.on_pre_enter()

# --- 4. 인벤토리 화면 (한 줄씩 추가/삭제) ---
class InventoryScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        if "inven" not in self.char_data: self.char_data["inven"] = []
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        nav = BoxLayout(size_hint_y=None, height=130, spacing=10)
        b_btn = Button(text="뒤로", background_color=(0.5, 0.5, 0.5, 1))
        b_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_detail'))
        a_btn = Button(text="+ 아이템 추가", background_color=(0.1, 0.7, 0.3, 1))
        a_btn.bind(on_release=self.add_item)
        nav.add_widget(b_btn); nav.add_widget(a_btn); layout.add_widget(nav)

        scroll = ScrollView(); self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        self.item_inputs = []
        for i, item in enumerate(self.char_data["inven"]):
            row = BoxLayout(size_hint_y=None, height=120, spacing=10)
            ti = TextInput(text=item, multiline=False)
            ti.bind(on_text_validate=self.save_inven)
            del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.9, 0.3, 0.3, 1))
            del_btn.bind(on_release=lambda x, idx=i: show_confirm("삭제", "아이템을 삭제하시겠습니까?", lambda: self.del_item(idx)))
            row.add_widget(ti); row.add_widget(del_btn); self.grid.add_widget(row); self.item_inputs.append(ti)

        scroll.add_widget(self.grid); layout.add_widget(scroll)
        save_btn = Button(text="인벤토리 전체 저장", size_hint_y=None, height=130, background_color=(0.2, 0.5, 0.9, 1))
        save_btn.bind(on_release=self.save_inven); layout.add_widget(save_btn); self.add_widget(layout)

    def add_item(self, *args):
        self.char_data["inven"].append(""); self.render_ui()

    def del_item(self, idx):
        self.char_data["inven"].pop(idx); self.render_ui()

    def save_inven(self, *args):
        self.char_data["inven"] = [ti.text for ti in self.item_inputs]
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="인벤토리 저장 완료"), size_hint=(0.6, 0.3)).open()

# --- 앱 구동 ---
class ToOpenApp(App):
    cur_acc = ""; cur_char = ""

    def build(self):
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="KFont", fn_regular=FONT_PATH)
            LabelBase.register(name="Roboto", fn_regular=FONT_PATH)
        
        if platform == 'android': activity.bind(on_activity_result=self.on_gallery_result)
        
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='char_detail'))
        sm.add_widget(InventoryScreen(name='inventory_screen'))
        return sm

    def on_gallery_result(self, req_code, res_code, intent):
        if req_code == 101 and res_code == -1 and intent:
            uri = intent.getData()
            if uri:
                path = uri.toString()
                if platform == 'android':
                    try:
                        act = autoclass('org.kivy.android.PythonActivity').mActivity
                        takeFlags = intent.getFlags() & 1
                        act.getContentResolver().takePersistableUriPermission(uri, takeFlags)
                    except: pass
                if self.root.current == 'char_detail':
                    screen = self.root.current_screen
                    if path not in screen.char_data["photos"]:
                        screen.char_data["photos"].append(path); screen.draw_photos()
                        DataManager.save(screen.data)

if __name__ == '__main__':
    ToOpenApp().run()
