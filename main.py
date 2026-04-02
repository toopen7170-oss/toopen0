import json
import os
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
from kivy.core.text import LabelBase # 추가된 부분

# --- 한글 폰트 설정 시작 ---
font_file = "font.ttf"
if os.path.exists(font_file):
    LabelBase.register(name="KoreanFont", fn_regular=font_file)
    DEFAULT_FONT = "KoreanFont"
else:
    DEFAULT_FONT = None
# --- 한글 폰트 설정 끝 ---

# 데이터 저장소
store = JsonStore('priston_data.json')

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # font_name 추가
        layout.add_widget(Label(text="[PT1 캐릭터 관리]", font_size='24sp', size_hint_y=0.1, font_name=DEFAULT_FONT))
        
        search_box = BoxLayout(size_hint_y=0.1, spacing=5)
        self.search_input = TextInput(hint_text="이름/직업/아이템 검색", multiline=False, font_name=DEFAULT_FONT)
        btn_search = Button(text="검색", size_hint_x=0.2, font_name=DEFAULT_FONT)
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        btn_add = Button(text="+ 새 계정 추가", size_hint_y=0.1, background_color=(0.2, 0.6, 1, 1), font_name=DEFAULT_FONT)
        btn_add.bind(on_release=self.add_account)
        layout.add_widget(btn_add)

        self.acc_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.acc_list.bind(minimum_height=self.acc_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh()

    def refresh(self):
        self.acc_list.clear_widgets()
        for k in store.keys():
            btn = Button(text=f"계정: {k}", size_hint_y=None, height=120, font_name=DEFAULT_FONT)
            btn.bind(on_release=lambda x, key=k: self.select_acc(key))
            self.acc_list.add_widget(btn)

    def add_account(self, *args):
        content = BoxLayout(orientation='vertical')
        inp = TextInput(hint_text="계정 이름", multiline=False, font_name=DEFAULT_FONT)
        btn = Button(text="저장", font_name=DEFAULT_FONT)
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save_acc(x):
            if inp.text:
                store.put(inp.text, chars={str(i): {"name": f"캐릭터 {i}"} for i in range(1, 7)})
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
        layout = BoxLayout(orientation='vertical', padding=10)
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {"name": "비었음"})
            btn = Button(text=f"{i}. {c_data.get('name')}", font_name=DEFAULT_FONT)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        btn_back = Button(text="뒤로가기", size_hint_y=0.1, font_name=DEFAULT_FONT)
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
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        self.img = Image(source=self.data.get('img', ''), size_hint_y=None, height=400)
        layout.add_widget(self.img)
        btn_img = Button(text="사진 등록/수정", size_hint_y=None, height=80, font_name=DEFAULT_FONT)
        btn_img.bind(on_release=self.pick_img); layout.add_widget(btn_img)

        self.fields = {}
        items = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "장갑", "부츠", "링", "아뮬렛", "쉘텀", "인벤토리"]
        for f in items:
            row = BoxLayout(size_hint_y=None, height=60)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT))
            ti = TextInput(text=str(self.data.get(f, '')), multiline=(f=="인벤토리"), font_name=DEFAULT_FONT)
            if f=="인벤토리": row.height = 200
            self.fields[f] = ti; row.add_widget(ti); layout.add_widget(row)

        b_row = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_save = Button(text="저장", background_color=(0, 1, 0, 1), font_name=DEFAULT_FONT)
        btn_save.bind(on_release=self.save)
        btn_del = Button(text="삭제", background_color=(1, 0, 0, 1), font_name=DEFAULT_FONT)
        btn_del.bind(on_release=self.delete)
        b_row.add_widget(btn_save); b_row.add_widget(btn_del); layout.add_widget(b_row)
        
        btn_back = Button(text="뒤로", size_hint_y=None, height=80, font_name=DEFAULT_FONT)
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_back)
        scroll.add_widget(layout); self.add_widget(scroll)

    def pick_img(self, *args):
        fc = FileChooserIconView()
        btn = Button(text="선택완료", size_hint_y=0.1, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
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
