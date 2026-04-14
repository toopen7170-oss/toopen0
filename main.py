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
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock

# [1] 안드로이드 네이티브 검증 (S26 울트라 호환성 최적화)
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass

# [2] 환경 설정
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DB_NAME = "toopen0_final_v49.json"
K_FONT = "KFont" if os.path.exists(FONT_PATH) else None

# [3] UI 컴포넌트: 수직 중앙 정렬 스타일 TextInput (전수 검사 수정 완료)
class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.font_name = K_FONT
        self.font_size = 36
        self.cursor_color = [0.1, 0.5, 0.9, 1]
        self.background_normal = "" 
        self.background_color = [1, 1, 1, 0.9]
        self.bind(size=self._update_padding, text=self._update_padding)

    def _update_padding(self, *args):
        # 텍스트가 위젯의 정중앙에 오도록 Y 패딩 계산
        self.padding_y = [self.height / 2 - (self.line_height / 2), 0]

    def on_focus(self, instance, value):
        if value:
            # 키보드 활성화 시 자동 스크롤
            parent = self.parent
            while parent and not isinstance(parent, ScrollView):
                parent = parent.parent
            if parent:
                Clock.schedule_once(lambda dt: parent.scroll_to(self), 0.2)

# [4] 데이터 관리 (DataManager)
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

# [5] 화면 공통 베이스 (전수 검사: rect 객체 참조 오류 방지)
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
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

# [6] 공통 알림 팝업
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

# [7] 계정 목록 화면
class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self, search_text=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=[30, 90, 30, 60], spacing=25)
        sh = BoxLayout(size_hint_y=None, height=140, spacing=15)
        self.s_in = StyledTextInput(text=search_text, hint_text="검색어 입력...")
        s_btn = Button(text="검색", size_hint_x=0.25, background_color=(0.1, 0.5, 0.9, 1), font_name=K_FONT)
        s_btn.bind(on_release=lambda x: self.render_ui(self.s_in.text))
        sh.add_widget(self.s_in); sh.add_widget(s_btn); layout.add_widget(sh)

        add = Button(text="+ 새 계정 생성", size_hint_y=None, height=150, background_color=(0.1, 0.7, 0.4, 1), font_name=K_FONT, font_size=38)
        add.bind(on_release=self.add_acc_pop); layout.add_widget(add)

        scroll = ScrollView(); grid = GridLayout(cols=1, size_hint_y=None, spacing=18)
        grid.bind(minimum_height=grid.setter('height'))
        
        accounts = self.data.get("accounts", {})
        for acc_id in sorted(accounts.keys()):
            if search_text and search_text.lower() not in acc_id.lower(): continue
            row = BoxLayout(size_hint_y=None, height=160, spacing=12)
            btn = Button(text=f"ID: {acc_id}", background_color=(0.2, 0.4, 0.7, 1), font_name=K_FONT, font_size=34)
            btn.bind(on_release=lambda x, a=acc_id: self.go_chars(a))
            del_b = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT)
            del_b.bind(on_release=lambda x, a=acc_id: show_confirm("삭제", f"'{a}'를 삭제할까요?", lambda: self.del_acc(a)))
            row.add_widget(btn); row.add_widget(del_b); grid.add_widget(row)

        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def add_acc_pop(self, *args):
        c = BoxLayout(orientation='vertical', padding=30, spacing=20)
        ti = StyledTextInput(hint_text="계정 ID", size_hint_y=None, height=130)
        b = Button(text="저장", size_hint_y=None, height=130, background_color=(0.1, 0.7, 0.4, 1), font_name=K_FONT)
        p = Popup(title="계정 추가", content=c, size_hint=(0.9, 0.45), title_font=K_FONT)
        b.bind(on_release=lambda x: self.create_acc(ti.text, p)); c.add_widget(ti); c.add_widget(b); p.open()

    def create_acc(self, name, p):
        if name.strip():
            self.data["accounts"][name] = {str(i): {"name": f"Slot {i}", "level": "1", "inven": [], "photos": []} for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter(); p.dismiss()

    def del_acc(self, name):
        if name in self.data["accounts"]: del self.data["accounts"][name]; DataManager.save(self.data); self.on_pre_enter()

    def go_chars(self, name):
        App.get_running_app().cur_acc = name; self.manager.current = 'char_select'

# [8] 캐릭터 선택 화면
class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=45, spacing=30)
        layout.add_widget(Label(text=f"접속 ID: {app.cur_acc}", size_hint_y=None, height=110, font_name=K_FONT, font_size=42, color=(1, 0.9, 0.3, 1)))
        
        grid = GridLayout(cols=2, spacing=25)
        chars = self.data["accounts"].get(app.cur_acc, {})
        for i in range(1, 7):
            c = chars.get(str(i), {})
            btn = Button(text=f"Slot {i}\n{c.get('name')}\nLv.{c.get('level')}", halign='center', background_color=(0.15, 0.45, 0.75, 1), font_name=K_FONT, font_size=32)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(str(idx))); grid.add_widget(btn)
        
        layout.add_widget(grid)
        back = Button(text="계정 목록", size_hint_y=None, height=140, background_color=(0.4, 0.4, 0.4, 1), font_name=K_FONT)
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_main')); layout.add_widget(back); self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = idx; self.manager.current = 'char_detail'

# [9] 캐릭터 상세 정보 화면
class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app(); self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets(); layout = BoxLayout(orientation='vertical', padding=15)
        nav = BoxLayout(size_hint_y=None, height=135, spacing=12)
        nav.add_widget(Button(text="취소", font_name=K_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="저장", background_color=(0.1, 0.7, 0.3, 1), font_name=K_FONT, on_release=self.save_all))
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
            ("무기1", "w1"), ("무기2", "w2"), ("갑옷", "armor"), ("방패", "shield"),
            ("장갑", "glove"), ("부츠", "boots"), ("아뮬렛", "amu"), ("링", "ring")
        ]
        for lbl, key in fields:
            row = BoxLayout(size_hint_y=None, height=120, spacing=12)
            row.add_widget(Label(text=lbl, size_hint_x=0.3, font_name=K_FONT, font_size=32))
            ti = StyledTextInput(text=str(self.char_data.get(key, "")))
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
        show_confirm("사진 삭제", "선택한 사진을 삭제할까요?", lambda: self.del_photo(path))

    def del_photo(self, path):
        if path in self.char_data["photos"]:
            self.char_data["photos"].remove(path); self.draw_photos(); DataManager.save(self.data)

    def open_gal(self, *args):
        if platform == 'android': 
            request_permissions([Permission.READ_MEDIA_IMAGES, Permission.WRITE_EXTERNAL_STORAGE], self.launch_gal)
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
        Popup(title="성공", content=Label(text="저장되었습니다.", font_name=K_FONT), size_hint=(0.6, 0.25), title_font=K_FONT).open()

# [10] 인벤토리 화면 (전수 검사: 삭제 동기화 수정 완료)
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
            ti = StyledTextInput(text=item_text)
            del_btn = Button(text="X", size_hint_x=0.18, background_color=(0.8, 0.2, 0.2, 1), font_name=K_FONT)
            del_btn.bind(on_release=partial(self.ask_del_item, i))
            row.add_widget(ti); row.add_widget(del_btn); self.grid.add_widget(row); self.ti_list.append(ti)

        scroll.add_widget(self.grid); layout.add_widget(scroll)
        s_btn = Button(text="인벤토리 저장", size_hint_y=None, height=150, background_color=(0.1, 0.5, 0.9, 1), font_name=K_FONT)
        s_btn.bind(on_release=self.save_inv); layout.add_widget(s_btn); self.add_widget(layout)

    def add_item(self, *args):
        self.char_data["inven"].append(""); self.render_ui()

    def ask_del_item(self, idx, *args):
        show_confirm("삭제", "해당 항목을 삭제할까요?", lambda: self.del_item(idx))

    def del_item(self, idx):
        # 전수 검사 수정: 인덱스 범위 확인 및 즉시 저장
        if 0 <= idx < len(self.char_data["inven"]):
            self.char_data["inven"].pop(idx)
            DataManager.save(self.data)
            self.render_ui()

    def save_inv(self, *args):
        self.char_data["inven"] = [ti.text for ti in self.ti_list]
        DataManager.save(self.data)
        Popup(title="알림", content=Label(text="저장되었습니다.", font_name=K_FONT), size_hint=(0.6, 0.25), title_font=K_FONT).open()

# [11] 앱 메인 클래스
class ToOpenApp(App):
    cur_acc = ""; cur_char = ""
    def build(self):
        Window.softinput_mode = "below_target"
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="KFont", fn_regular=FONT_PATH)
            LabelBase.register(name="Roboto", fn_regular=FONT_PATH)
        
        if platform == 'android': 
            activity.bind(on_activity_result=self.on_gal_res)
            request_permissions([Permission.READ_MEDIA_IMAGES, Permission.WRITE_EXTERNAL_STORAGE])
            
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
