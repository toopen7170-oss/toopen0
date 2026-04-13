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
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window

# --- 환경 설정 (Galaxy S26 Ultra / GitHub) ---
BG_IMAGE = "bg.png"
FONT_NAME = "font.ttf"
DATA_FILE = "pt1_chart_data.json"

if os.path.exists(FONT_NAME):
    LabelBase.register(name="KFont", fn_regular=FONT_NAME)

class DataManager:
    @staticmethod
    def load():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    d = json.load(f)
                    return d if "accounts" in d else {"accounts": {}}
                except: return {"accounts": {}}
        return {"accounts": {}}

    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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

# --- 1. 메인 계정 차트 목록 ---
class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self, search_text=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 검색 기능
        search_box = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.search_in = TextInput(text=search_text, hint_text="계정/캐릭/아이템 통합 검색", font_name="KFont" if os.path.exists(FONT_NAME) else None, 
                                   multiline=False, background_color=(1, 1, 1, 0.85))
        s_btn = Button(text="검색", font_name="KFont" if os.path.exists(FONT_NAME) else None, size_hint_x=0.25, 
                       background_color=(0.1, 0.4, 0.7, 1))
        s_btn.bind(on_release=lambda x: self.render_ui(self.search_in.text.strip()))
        search_box.add_widget(self.search_in); search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        layout.add_widget(Button(text="+ 관리 계정 추가", font_name="KFont" if os.path.exists(FONT_NAME) else None, size_hint_y=None, height=130, 
                                 background_color=(0.1, 0.6, 0.3, 1), on_release=self.show_popup))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=12)
        grid.bind(minimum_height=grid.setter('height'))

        st = search_text.lower()
        for acc_id, chars in self.data.get("accounts", {}).items():
            match = False
            if not st or st in acc_id.lower(): match = True
            else:
                for c_id, c_data in chars.items():
                    all_text = (c_data.get('name', '') + "".join(c_data.get('items', {}).values()) + "".join(c_data.get('inventory', []))).lower()
                    if st in all_text: match = True; break
            
            if match:
                row = BoxLayout(size_hint_y=None, height=130, spacing=10)
                btn = Button(text=f" 관리 ID: {acc_id}", font_name="KFont" if os.path.exists(FONT_NAME) else None, background_color=(0.2, 0.2, 0.35, 1))
                btn.bind(on_release=lambda x, a=acc_id: self.go_chars(a))
                del_btn = Button(text="삭제", font_name="KFont" if os.path.exists(FONT_NAME) else None, size_hint_x=0.2, background_color=(0.7, 0.1, 0.1, 1))
                del_btn.bind(on_release=lambda x, a=acc_id: self.confirm_delete(a))
                row.add_widget(btn); row.add_widget(del_btn); grid.add_widget(row)

        scroll.add_widget(grid); layout.add_widget(scroll); self.add_widget(layout)

    def show_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.acc_in = TextInput(hint_text="계정 이름", font_name="KFont" if os.path.exists(FONT_NAME) else None, multiline=False, size_hint_y=None, height=100)
        content.add_widget(self.acc_in)
        btn = Button(text="등록 완료", font_name="KFont" if os.path.exists(FONT_NAME) else None, size_hint_y=None, height=110, background_color=(0.1, 0.5, 0.3, 1))
        btn.bind(on_release=lambda x: self.add_acc(self.acc_in.text, popup))
        content.add_widget(btn)
        popup = Popup(title="새 계정 등록", content=content, size_hint=(0.85, 0.38)); popup.open()

    def add_acc(self, acc_id, popup):
        if acc_id:
            self.data.setdefault("accounts", {})[acc_id] = {str(i): self.get_empty_char(i) for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()
        popup.dismiss()

    def get_empty_char(self, i):
        return {"name": f"캐릭터 슬롯 {i}", "lv": "1", "items": {k: "" for k in ["무기", "갑옷", "방패", "장신구", "기타"]}, "inventory": [], "photos": []}

    def confirm_delete(self, acc_id):
        c = BoxLayout(orientation='vertical', padding=20)
        c.add_widget(Label(text=f"'{acc_id}'의 모든 데이터를\n삭제하시겠습니까?", font_name="KFont" if os.path.exists(FONT_NAME) else None, halign='center'))
        b = BoxLayout(size_hint_y=None, height=100, spacing=10)
        y = Button(text="삭제", background_color=(0.8, 0.2, 0.2, 1)); n = Button(text="취소")
        y.bind(on_release=lambda x: self.delete_acc(acc_id, p)); n.bind(on_release=lambda x: p.dismiss())
        b.add_widget(y); b.add_widget(n); c.add_widget(b)
        p = Popup(title="주의", content=c, size_hint=(0.8, 0.4)); p.open()

    def delete_acc(self, acc_id, p):
        del self.data["accounts"][acc_id]; DataManager.save(self.data); self.on_pre_enter(); p.dismiss()

    def go_chars(self, acc_id):
        App.get_running_app().cur_acc = acc_id; self.manager.current = 'char_select'

# --- 2. 캐릭터 슬롯 선택 ---
class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=25, spacing=25)
        layout.add_widget(Label(text=f"관리 ID: {app.cur_acc}", size_hint_y=None, height=60, font_size=22, color=(1, 0.9, 0.5, 1)))
        
        grid = GridLayout(cols=2, spacing=20)
        chars = self.data["accounts"][app.cur_acc]
        for i in range(1, 7):
            c = chars[str(i)]
            btn = Button(text=f"{c['name']}\nLv.{c['lv']}", font_name="KFont" if os.path.exists(FONT_NAME) else None, halign='center', background_color=(0.1, 0.1, 0.25, 0.9))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        layout.add_widget(Button(text="메인 화면으로", size_hint_y=None, height=110, on_release=lambda x: setattr(self.manager, 'current', 'account_main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = str(idx); self.manager.current = 'char_detail'

# --- 3. 상세 차트표 및 사진 관리 ---
class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.char_data.setdefault("photos", [])
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        nav = BoxLayout(size_hint_y=None, height=110, spacing=10)
        nav.add_widget(Button(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="차트 저장", background_color=(0, 0.6, 0.3, 1), on_release=self.save_all))
        layout.add_widget(nav)

        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        self.content.bind(minimum_height=self.content.setter('height'))

        # 기본 차트 정보
        self.content.add_widget(Label(text="[ 기본 정보 ]", size_hint_y=None, height=40, color=(1, 0.8, 0, 1)))
        self.name_in = TextInput(text=self.char_data['name'], size_hint_y=None, height=100, multiline=False)
        self.lv_in = TextInput(text=self.char_data.get('lv','1'), size_hint_y=None, height=100, multiline=False)
        self.content.add_widget(self.name_in); self.content.add_widget(self.lv_in)

        # 사진 차트
        self.content.add_widget(Label(text="[ 참고 이미지 ]", size_hint_y=None, height=40, color=(0.2, 0.8, 1, 1)))
        self.photo_layout = GridLayout(cols=3, size_hint_y=None, spacing=10)
        self.photo_layout.bind(minimum_height=self.photo_layout.setter('height'))
        self.refresh_photos()
        self.content.add_widget(self.photo_layout)
        add_p = Button(text="+ 스샷 추가", size_hint_y=None, height=100, background_color=(0.4, 0.4, 0.4, 1))
        add_p.bind(on_release=self.open_fc); self.content.add_widget(add_p)

        # 장비 현황 차트
        self.content.add_widget(Label(text="[ 장비 현황 ]", size_hint_y=None, height=40, color=(1, 0.8, 0, 1)))
        self.item_inps = {}
        for k in ["양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]:
            row = BoxLayout(size_hint_y=None, height=90, spacing=8)
            row.add_widget(Label(text=k, size_hint_x=0.35))
            inp = TextInput(text=self.char_data['items'].get(k, ""), multiline=False)
            self.item_inps[k] = inp
            row.add_widget(inp); self.content.add_widget(row)

        # 인벤토리 데이터
        self.content.add_widget(Label(text="[ 상세 인벤토리 ]", size_hint_y=None, height=40, color=(1, 0.8, 0, 1)))
        add_i = Button(text="+ 차트 행 추가", size_hint_y=None, height=110, background_color=(0.2, 0.4, 0.7, 1))
        add_i.bind(on_release=self.add_inv_row); self.content.add_widget(add_i)

        self.inv_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.inv_layout.bind(minimum_height=self.inv_layout.setter('height'))
        self.refresh_inv(); self.content.add_widget(self.inv_layout)

        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)

    def refresh_photos(self):
        self.photo_layout.clear_widgets()
        valid = []
        for path in self.char_data["photos"]:
            if os.path.exists(path):
                valid.append(path)
                btn = Button(size_hint_y=None, height=200, background_normal=path)
                btn.bind(on_release=lambda x, p=path, idx=len(valid)-1: self.photo_pop(p, idx))
                self.photo_layout.add_widget(btn)
        self.char_data["photos"] = valid

    def open_fc(self, *args):
        content = BoxLayout(orientation='vertical')
        fc = FileChooserIconView(path='/sdcard/Download' if os.path.exists('/sdcard/Download') else os.path.expanduser("~"))
        content.add_widget(fc)
        btns = BoxLayout(size_hint_y=None, height=100)
        s = Button(text="선택 완료"); c = Button(text="취소", on_release=lambda x: p.dismiss())
        btns.add_widget(s); btns.add_widget(c); content.add_widget(btns)
        p = Popup(title="이미지 선택", content=content, size_hint=(0.95, 0.95))
        s.bind(on_release=lambda x: self.add_photo(fc.selection, p)); p.open()

    def add_photo(self, sel, p):
        if sel and sel[0] not in self.char_data["photos"]:
            self.char_data["photos"].append(sel[0]); DataManager.save(self.data); self.refresh_photos()
        p.dismiss()

    def photo_pop(self, path, idx):
        c = BoxLayout(orientation='vertical', padding=10)
        c.add_widget(Image(source=path))
        d = Button(text="이 이미지 삭제", size_hint_y=None, height=100, background_color=(0.8, 0.2, 0.2, 1))
        p = Popup(title="미리보기", content=c, size_hint=(0.9, 0.7))
        d.bind(on_release=lambda x: self.del_photo(idx, p)); c.add_widget(d); p.open()

    def del_photo(self, idx, p):
        self.char_data["photos"].pop(idx); DataManager.save(self.data); self.refresh_photos(); p.dismiss()

    def refresh_inv(self):
        self.inv_layout.clear_widgets(); self.inv_inps = []
        for i, txt in enumerate(self.char_data.get("inventory", [])):
            row = BoxLayout(size_hint_y=None, height=90, spacing=8)
            inp = TextInput(text=txt, multiline=False)
            self.inv_inps.append(inp)
            del_b = Button(text="삭제", size_hint_x=0.2, background_color=(0.6, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, cur_idx=i: self.del_inv_row(cur_idx))
            row.add_widget(inp); row.add_widget(del_b); self.inv_layout.add_widget(row)

    def add_inv_row(self, *args):
        self.sync_inv(); self.char_data["inventory"].append(""); self.refresh_inv()

    def sync_inv(self):
        self.char_data["inventory"] = [inp.text for inp in self.inv_inps]

    def del_inv_row(self, idx):
        # 삭제 시 데이터 무결성을 위해 동기화 먼저 수행
        self.sync_inv()
        if idx < len(self.char_data["inventory"]):
            self.char_data["inventory"].pop(idx)
            DataManager.save(self.data)
            self.refresh_inv()

    def save_all(self, *args):
        self.char_data['name'] = self.name_in.text
        self.char_data['lv'] = self.lv_in.text
        for k, inp in self.item_inps.items(): self.char_data['items'][k] = inp.text
        self.sync_inv()
        DataManager.save(self.data)
        Popup(title="저장", content=Label(text="차트표가 저장되었습니다."), size_hint=(0.5, 0.25)).open()

class PT1ChartApp(App):
    cur_acc = ""; cur_char = ""
    def build(self):
        Window.softinput_mode = "pan" # 모바일 키보드 최적화
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='char_detail'))
        return sm

if __name__ == '__main__':
    PT1ChartApp().run()
