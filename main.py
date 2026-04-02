import json
import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# 앱 배경색 설정 (진한 회색)
Window.clearcolor = (0.07, 0.07, 0.07, 1)

def get_font_path():
    font_name = "font.ttf"
    if os.path.exists(font_name): return font_name
    bundle_path = os.path.join(os.path.dirname(sys.argv[0]), font_name)
    if os.path.exists(bundle_path): return bundle_path
    return None

FONT_PATH = get_font_path()
if FONT_PATH:
    LabelBase.register(name="KoreanFont", fn_regular=FONT_PATH)
    DEFAULT_FONT = "KoreanFont"
else:
    DEFAULT_FONT = None

store = JsonStore('priston_data.json')

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.background_normal = ''
        self.background_color = (0.1, 0.4, 0.8, 1) # 블루 포인트
        self.height = 100

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text="[PT1 캐릭터 관리]", font_size='28sp', 
                                bold=True, size_hint_y=0.15, font_name=DEFAULT_FONT, color=(1, 0.8, 0, 1)))
        
        search_box = BoxLayout(size_hint_y=0.1, spacing=10)
        self.search_input = TextInput(hint_text="검색어를 입력하세요", multiline=False, 
                                      font_name=DEFAULT_FONT, background_color=(0.2, 0.2, 0.2, 1),
                                      foreground_color=(1, 1, 1, 1), cursor_color=(1, 1, 1, 1))
        btn_search = StyledButton(text="검색", size_hint_x=0.25, background_color=(0.3, 0.3, 0.3, 1))
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        btn_add = StyledButton(text="+ 새 계정 추가", size_hint_y=0.1, background_color=(0.1, 0.6, 0.4, 1))
        btn_add.bind(on_release=self.add_account)
        layout.add_widget(btn_add)

        self.acc_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.acc_list.bind(minimum_height=self.acc_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh()

    def refresh(self):
        self.acc_list.clear_widgets()
        for k in store.keys():
            btn = StyledButton(text=f"계정: {k}", size_hint_y=None, height=130)
            btn.bind(on_release=lambda x, key=k: self.select_acc(key))
            self.acc_list.add_widget(btn)

    def add_account(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(hint_text="계정 이름을 입력하세요", multiline=False, font_name=DEFAULT_FONT)
        btn = StyledButton(text="저장하기", background_color=(0.1, 0.6, 0.4, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="새 계정 생성", content=content, size_hint=(0.8, 0.4))
        def save_acc(x):
            if inp.text:
                store.put(inp.text, chars={str(i): {"name": f"슬롯 {i}"} for i in range(1, 7)})
                self.refresh(); pop.dismiss()
        btn.bind(on_release=save_acc); pop.open()

    def select_acc(self, key):
        self.manager.current_acc = key
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_size='22sp', size_hint_y=0.1, font_name=DEFAULT_FONT))
        
        grid = GridLayout(cols=2, spacing=15)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {"name": "비었음"})
            btn = StyledButton(text=f"{i}. {c_data.get('name')}")
            if c_data.get('name') == "비었음": btn.background_color = (0.2, 0.2, 0.2, 1)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        btn_back = StyledButton(text="메인으로 돌아가기", size_hint_y=0.12, background_color=(0.5, 0.2, 0.2, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_idx = str(idx)
        self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.data = store.get(acc)['chars'].get(idx, {})
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        self.img = Image(source=self.data.get('img', ''), size_hint_y=None, height=450)
        layout.add_widget(self.img)
        btn_img = StyledButton(text="📷 사진 등록", size_hint_y=None, height=90, background_color=(0.4, 0.4, 0.4, 1))
        btn_img.bind(on_release=self.pick_img); layout.add_widget(btn_img)

        items = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "장갑", "부츠", "링", "아뮬렛", "쉘텀", "인벤토리"]
        self.fields = {}
        for f in items:
            row = BoxLayout(size_hint_y=None, height=70, spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT, color=(0.8, 0.8, 0.8, 1)))
            ti = TextInput(text=str(self.data.get(f, '')), multiline=(f=="인벤토리"), 
                           font_name=DEFAULT_FONT, background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
            if f=="인벤토리": row.height = 250
            self.fields[f] = ti; row.add_widget(ti); layout.add_widget(row)

        b_row = BoxLayout(size_hint_y=None, height=100, spacing=15)
        btn_save = StyledButton(text="저장", background_color=(0.1, 0.6, 0.3, 1))
        btn_save.bind(on_release=self.save)
        btn_del = StyledButton(text="삭제", background_color=(0.8, 0.2, 0.2, 1))
        btn_del.bind(on_release=self.delete)
        b_row.add_widget(btn_save); b_row.add_widget(btn_del); layout.add_widget(b_row)
        
        btn_back = StyledButton(text="뒤로", size_hint_y=None, height=90, background_color=(0.3, 0.3, 0.3, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_back)
        scroll.add_widget(layout); self.add_widget(scroll)

    def pick_img(self, *args):
        fc = FileChooserIconView()
        btn = StyledButton(text="선택 완료", size_hint_y=0.15)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="갤러리에서 사진 선택", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        all_d = store.get(acc)
        new_d = {f: ti.text for f, ti in self.fields.items()}
        new_d['img'] = self.img.source
        all_d['chars'][idx] = new_d
        store.put(acc, **all_d)
        self.manager.current = 'char_select'

    def delete(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        all_d = store.get(acc)
        all_d['chars'][idx] = {"name": "비었음"}
        store.put(acc, **all_d)
        self.manager.current = 'char_select'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.current_acc = ""; sm.current_idx = ""
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
