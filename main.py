import os
import json
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock

# --- [전수 검사 완료] 환경 설정 ---
FONT_PATH = "font.ttf"
BG_IMAGE = "bg.png"
DATA_FILE = "pt1_chart_data.json"

# 한글 폰트 적용 (파일이 없을 경우 대비 예외 처리)
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
                Color(0.08, 0.08, 0.15, 1) # 배경이미지 없을 시 대비
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size

# --- 1. 계정 목록 및 통합 검색 ---
class AccountScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.render_ui()

    def render_ui(self, search_text=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=[30, 80, 30, 30], spacing=20)
        
        # 통합 검색바
        search_box = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.search_in = TextInput(text=search_text, hint_text="계정/캐릭/아이템 검색", 
                                   font_name=DEFAULT_FONT, multiline=False, padding=[20, 30, 10, 10])
        s_btn = Button(text="검색", font_name=DEFAULT_FONT, size_hint_x=0.25, background_color=(0.1, 0.5, 0.9, 1))
        s_btn.bind(on_release=lambda x: self.render_ui(self.search_in.text))
        search_box.add_widget(self.search_in); search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        layout.add_widget(Button(text="+ 새 계정 만들기", font_name=DEFAULT_FONT, size_hint_y=None, height=140, 
                                 background_color=(0.2, 0.7, 0.4, 1), on_release=self.popup_add_acc))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=15)
        grid.bind(minimum_height=grid.setter('height'))

        st = search_text.lower()
        for acc_id, details in sorted(self.data["accounts"].items()):
            # 모든 텍스트 기반 통합 검색 로직
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
        inp = TextInput(hint_text="계정 아이디 입력", font_name=DEFAULT_FONT, multiline=False, size_hint_y=None, height=120)
        c.add_widget(inp)
        b = Button(text="등록하기", font_name=DEFAULT_FONT, size_hint_y=None, height=120, background_color=(0.2, 0.6, 0.4, 1))
        p = Popup(title="계정 추가", content=c, size_hint=(0.9, 0.4), title_font=DEFAULT_FONT)
        b.bind(on_release=lambda x: self.add_acc(inp.text, p)); c.add_widget(b); p.open()

    def add_acc(self, acc_id, p):
        if acc_id.strip():
            self.data["accounts"][acc_id] = {str(i): self.get_empty_char(i) for i in range(1, 7)}
            DataManager.save(self.data); self.on_pre_enter()
        p.dismiss()

    def get_empty_char(self, i):
        return {
            "name": f"캐릭터 {i}", "job": "", "lv": "1",
            "stats": {"힘": "0", "민첩": "0", "정신": "0", "건강": "0", "재능": "0"},
            "items": {k: "" for k in ["양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]},
            "inventory": [], "photos": []
        }

    def ask_delete(self, acc_id):
        c = BoxLayout(orientation='vertical', padding=25, spacing=25)
        c.add_widget(Label(text=f"계정 '{acc_id}'를\n삭제하시겠습니까?", font_name=DEFAULT_FONT, halign='center'))
        btns = BoxLayout(size_hint_y=None, height=110, spacing=15)
        y = Button(text="삭제", font_name=DEFAULT_FONT, background_color=(0.8, 0.2, 0.2, 1))
        n = Button(text="취소", font_name=DEFAULT_FONT, on_release=lambda x: p.dismiss())
        y.bind(on_release=lambda x: self.do_delete(acc_id, p))
        btns.add_widget(y); btns.add_widget(n); c.add_widget(btns)
        p = Popup(title="삭제 확인", content=c, size_hint=(0.85, 0.45), title_font=DEFAULT_FONT); p.open()

    def do_delete(self, acc_id, p):
        if acc_id in self.data["accounts"]:
            del self.data["accounts"][acc_id]; DataManager.save(self.data); self.on_pre_enter()
        p.dismiss()

    def go_chars(self, acc_id):
        App.get_running_app().cur_acc = acc_id; self.manager.current = 'char_select'

# --- 2. 캐릭터 선택 화면 (6개 슬롯) ---
class CharSelectScreen(BaseScreen):
    def on_pre_enter(self):
        self.data = DataManager.load(); self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        layout.add_widget(Label(text=f"ID: {app.cur_acc} 캐릭터 슬롯", font_name=DEFAULT_FONT, size_hint_y=None, height=80, font_size=24))
        
        grid = GridLayout(cols=2, spacing=25)
        chars = self.data["accounts"][app.cur_acc]
        for i in range(1, 7):
            c = chars[str(i)]
            btn = Button(text=f"SLOT {i}\n{c['name']}\nLv.{c['lv']}", font_name=DEFAULT_FONT, halign='center', background_color=(0.3, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        layout.add_widget(Button(text="뒤로가기", font_name=DEFAULT_FONT, size_hint_y=None, height=130, on_release=lambda x: setattr(self.manager, 'current', 'account_main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        App.get_running_app().cur_char = str(idx); self.manager.current = 'char_detail'

# --- 3. 상세 정보/수정/인벤토리/사진 ---
class CharDetailScreen(BaseScreen):
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.data = DataManager.load()
        self.char_data = self.data["accounts"][self.app.cur_acc][self.app.cur_char]
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15)
        
        # 상단 네비게이션
        nav = BoxLayout(size_hint_y=None, height=130, spacing=10)
        nav.add_widget(Button(text="뒤로", font_name=DEFAULT_FONT, on_release=lambda x: setattr(self.manager, 'current', 'char_select')))
        nav.add_widget(Button(text="저장하기", font_name=DEFAULT_FONT, background_color=(0, 0.6, 0.3, 1), on_release=self.save_all))
        nav.add_widget(Button(text="전체삭제", font_name=DEFAULT_FONT, background_color=(0.8, 0.1, 0.1, 1), on_release=self.ask_reset))
        layout.add_widget(nav)

        scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[0, 20, 0, 60])
        self.content.bind(minimum_height=self.content.setter('height'))

        # 1. 기본 인포
        self.add_tag("기본 정보 관리")
        self.name_in = self.add_row("캐릭터명", self.char_data['name'])
        self.job_in = self.add_row("직업", self.char_data.get('job', ""))
        self.lv_in = self.add_row("레벨", self.char_data.get('lv', "1"))

        # 2. 스텟 인포 (힘, 민첩, 정신, 건강, 재능)
        self.add_tag("스텟 정보 (STAT)")
        self.stat_inps = {}
        for s in ["힘", "민첩", "정신", "건강", "재능"]:
            self.stat_inps[s] = self.add_row(s, self.char_data['stats'].get(s, "0"))

        # 3. 장비 인포
        self.add_tag("착용 장비 관리")
        self.item_inps = {}
        for k in ["양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]:
            self.item_inps[k] = self.add_row(k, self.char_data['items'].get(k, ""))

        # 4. 이미지 인포
        self.add_tag("스크린샷 (터치 시 삭제)")
        self.photo_grid = GridLayout(cols=3, size_hint_y=None, spacing=8, height=280)
        self.draw_photos()
        self.content.add_widget(self.photo_grid)
        pic_btn = Button(text="+ 사진 파일 추가", font_name=DEFAULT_FONT, size_hint_y=None, height=120, background_color=(0.4, 0.4, 0.6, 1))
        pic_btn.bind(on_release=self.open_gallery); self.content.add_widget(pic_btn)

        # 5. 인벤토리 관리
        self.add_tag("캐릭터 인벤토리")
        self.inv_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.inv_layout.bind(minimum_height=self.inv_layout.setter('height'))
        for item in self.char_data.get('inventory', []):
            self.draw_inv_row(item)
        self.content.add_widget(self.inv_layout)
        
        add_i_btn = Button(text="+ 인벤토리 항목 추가", font_name=DEFAULT_FONT, size_hint_y=None, height=120, background_color=(0.2, 0.5, 0.8, 1))
        add_i_btn.bind(on_release=lambda x: self.draw_inv_row("")); self.content.add_widget(add_i_btn)

        scroll.add_widget(self.content); layout.add_widget(scroll); self.add_widget(layout)

    def add_tag(self, text):
        self.content.add_widget(Label(text=f"■ {text}", font_name=DEFAULT_FONT, size_hint_y=None, height=70, color=(1, 0.9, 0.2, 1), halign='left'))

    def add_row(self, label, val):
        r = BoxLayout(size_hint_y=None, height=120, spacing=15)
        r.add_widget(Label(text=label, font_name=DEFAULT_FONT, size_hint_x=0.35))
        inp = TextInput(text=str(val), font_name=DEFAULT_FONT, multiline=False, padding=[15, 30, 10, 10])
        r.add_widget(inp); self.content.add_widget(r)
        return inp

    def draw_inv_row(self, text=""):
        r = BoxLayout(size_hint_y=None, height=120, spacing=10)
        inp = TextInput(text=text, font_name=DEFAULT_FONT, multiline=False, padding=[15, 30, 10, 10])
        del_b = Button(text="삭제", font_name=DEFAULT_FONT, size_hint_x=0.22, background_color=(0.8, 0.3, 0.3, 1))
        del_b.bind(on_release=lambda x: self.ask_row_del(r))
        r.add_widget(inp); r.add_widget(del_b); self.inv_layout.add_widget(r)

    def ask_row_del(self, row):
        c = BoxLayout(orientation='vertical', padding=25, spacing=20)
        c.add_widget(Label(text="이 항목을 삭제하시겠습니까?", font_name=DEFAULT_FONT))
        y = Button(text="삭제", font_name=DEFAULT_FONT, height=110, size_hint_y=None, background_color=(0.8,0,0,1))
        p = Popup(title="삭제 확인", content=c, size_hint=(0.8, 0.35), title_font=DEFAULT_FONT)
        y.bind(on_release=lambda x: self.do_row_del(row, p)); c.add_widget(y); p.open()

    def do_row_del(self, row, p):
        self.inv_layout.remove_widget(row); p.dismiss()

    def draw_photos(self):
        self.photo_grid.clear_widgets()
        for path in self.char_data.get("photos", []):
            if os.path.exists(path):
                img = Button(background_normal=path, size_hint_y=None, height=260)
                img.bind(on_release=lambda x, p=path: self.ask_photo_del(p))
                self.photo_grid.add_widget(img)

    def ask_photo_del(self, path):
        c = BoxLayout(orientation='vertical', padding=25, spacing=20)
        c.add_widget(Label(text="이 사진을 삭제하시겠습니까?", font_name=DEFAULT_FONT))
        y = Button(text="사진 삭제", font_name=DEFAULT_FONT, height=110, size_hint_y=None, background_color=(0.8,0,0,1))
        p = Popup(title="확인", content=c, size_hint=(0.8, 0.35), title_font=DEFAULT_FONT)
        y.bind(on_release=lambda x: self.do_photo_del(path, p)); c.add_widget(y); p.open()

    def do_photo_del(self, path, p):
        if path in self.char_data["photos"]: self.char_data["photos"].remove(path)
        p.dismiss(); self.draw_photos()

    def open_gallery(self, *args):
        c = BoxLayout(orientation='vertical')
        fc = FileChooserIconView(path='/sdcard/Download' if os.path.exists('/sdcard') else '.')
        c.add_widget(fc)
        btns = BoxLayout(size_hint_y=None, height=120)
        s = Button(text="가져오기", font_name=DEFAULT_FONT)
        cl = Button(text="닫기", font_name=DEFAULT_FONT, on_release=lambda x: p.dismiss())
        btns.add_widget(s); btns.add_widget(cl); c.add_widget(btns)
        p = Popup(title="이미지 선택", content=c, size_hint=(0.95, 0.95), title_font=DEFAULT_FONT)
        s.bind(on_release=lambda x: self.add_pic(fc.selection, p)); p.open()

    def add_pic(self, sel, p):
        if sel:
            self.char_data.setdefault("photos", []).append(sel[0]); self.draw_photos()
        p.dismiss()

    def ask_reset(self, *args):
        c = BoxLayout(orientation='vertical', padding=25, spacing=25)
        c.add_widget(Label(text="이 캐릭터 슬롯의 모든 정보를\n삭제(초기화)하시겠습니까?", font_name=DEFAULT_FONT, halign='center'))
        y = Button(text="전체 초기화", font_name=DEFAULT_FONT, background_color=(0.8, 0.2, 0.2, 1), height=110, size_hint_y=None)
        p = Popup(title="경고", content=c, size_hint=(0.9, 0.45), title_font=DEFAULT_FONT)
        y.bind(on_release=lambda x: self.do_reset(p)); c.add_widget(y); p.open()

    def do_reset(self, p):
        self.data["accounts"][self.app.cur_acc][self.app.cur_char] = AccountScreen().get_empty_char(self.app.cur_char)
        DataManager.save(self.data); p.dismiss(); self.on_pre_enter()

    def save_all(self, *args):
        self.char_data['name'] = self.name_in.text
        self.char_data['job'] = self.job_in.text
        self.char_data['lv'] = self.lv_in.text
        for s, inp in self.stat_inps.items(): self.char_data['stats'][s] = inp.text
        for k, inp in self.item_inps.items(): self.char_data['items'][k] = inp.text
        
        new_inv = []
        for row in self.inv_layout.children:
            for child in row.children:
                if isinstance(child, TextInput): new_inv.append(child.text)
        self.char_data['inventory'] = new_inv[::-1]

        if DataManager.save(self.data):
            m = Popup(title="저장 완료", content=Label(text="정보가 안전하게 저장되었습니다.", font_name=DEFAULT_FONT), size_hint=(0.7, 0.25), title_font=DEFAULT_FONT)
            m.open(); Clock.schedule_once(lambda dt: m.dismiss(), 1.5)

class PT1ManagerApp(App):
    def build(self):
        Window.softinput_mode = "below_target"
        self.cur_acc = ""; self.cur_char = ""
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(AccountScreen(name='account_main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='char_detail'))
        return sm

if __name__ == '__main__':
    PT1ManagerApp().run()
