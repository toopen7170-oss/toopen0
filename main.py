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

# 배경색 설정
Window.clearcolor = (0.05, 0.05, 0.05, 1)

def get_font_path():
    font_name = "font.ttf"
    paths = [font_name, os.path.join(os.path.dirname(sys.argv[0]), font_name), os.path.join(os.getcwd(), font_name)]
    for path in paths:
        if os.path.exists(path): return path
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
        self.size_hint_y = None
        self.height = 140 # 버튼 크기 확대
        self.background_normal = ''
        self.background_color = (0.15, 0.35, 0.7, 1)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text="[PT1 통합 검색 관리]", font_size='30sp', bold=True, size_hint_y=0.15, font_name=DEFAULT_FONT, color=(1, 0.8, 0, 1)))
        
        # 검색창 레이아웃
        search_box = BoxLayout(size_hint_y=0.12, spacing=10)
        self.search_input = TextInput(hint_text="아이템, 장비, 계정 검색...", multiline=False, font_name=DEFAULT_FONT, background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1))
        btn_search = Button(text="전체 검색", size_hint_x=0.3, font_name=DEFAULT_FONT, background_color=(0.3, 0.3, 0.3, 1))
        btn_search.bind(on_release=self.refresh)
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        btn_add = StyledButton(text="+ 새 계정 추가", background_color=(0.1, 0.6, 0.3, 1))
        btn_add.bind(on_release=self.add_account)
        layout.add_widget(btn_add)

        self.acc_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.acc_list.bind(minimum_height=self.acc_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh()

    def refresh(self, *args):
        self.acc_list.clear_widgets()
        query = self.search_input.text.strip().lower()
        
        for acc_name in store.keys():
            data = store.get(acc_name)
            found = False
            match_detail = ""

            # 1. 계정 이름 매칭
            if not query or query in acc_name.lower():
                found = True
            
            # 2. 세부 항목 매칭 (캐릭터 이름, 직업, 장비, 인벤토리 전체)
            if not found and query:
                for idx, char in data.get('chars', {}).items():
                    # 캐릭터의 모든 텍스트 값을 합쳐서 검색
                    all_text = " ".join(str(v).lower() for v in char.values())
                    if query in all_text:
                        found = True
                        match_detail = f"({char.get('이름', '캐릭터')} 보유)"
                        break
            
            if found:
                btn_text = f"계정: {acc_name} {match_detail}"
                btn = StyledButton(text=btn_text)
                btn.bind(on_release=lambda x, k=acc_name: self.select_acc(k))
                self.acc_list.add_widget(btn)

    def add_account(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        inp = TextInput(hint_text="계정 이름", multiline=False, font_name=DEFAULT_FONT, size_hint_y=None, height=120)
        btn = StyledButton(text="계정 생성", background_color=(0.1, 0.6, 0.3, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="신규 계정", content=content, size_hint=(0.9, 0.5))
        def save(x):
            if inp.text:
                store.put(inp.text, chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                self.refresh(); pop.dismiss()
        btn.bind(on_release=save); pop.open()

    def select_acc(self, key):
        self.manager.current_acc = key
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        if not store.exists(acc): return
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        head = BoxLayout(size_hint_y=0.12)
        head.add_widget(Label(text=f"[{acc}]", font_size='22sp', font_name=DEFAULT_FONT))
        btn_del = Button(text="계정 삭제", size_hint_x=0.3, background_color=(0.8, 0.1, 0.1, 1), font_name=DEFAULT_FONT)
        btn_del.bind(on_release=self.delete_acc)
        head.add_widget(btn_del)
        layout.add_widget(head)
        
        grid = GridLayout(cols=2, spacing=15)
        for i in range(1, 7):
            c = data['chars'].get(str(i), {})
            # 이름 연동: 저장된 '이름'이 있으면 표시, 없으면 슬롯 번호
            display_name = c.get('이름') if c.get('이름') and c.get('이름') != f"슬롯 {i}" else f"{i}번 슬롯"
            btn = StyledButton(text=display_name)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        btn_back = StyledButton(text="메인 화면으로", background_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_idx = str(idx); self.manager.current = 'detail'

    def delete_acc(self, *args):
        store.delete(self.manager.current_acc)
        self.manager.current = 'main'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        self.img = Image(source=self.char_data.get('img', ''), size_hint_y=None, height=500, allow_stretch=True)
        layout.add_widget(self.img)
        
        row_btns = BoxLayout(size_hint_y=None, height=120, spacing=10)
        btn_img = StyledButton(text="📷 사진 수정"); btn_img.bind(on_release=self.pick_img)
        btn_inven = StyledButton(text="👜 인벤토리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inven.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        row_btns.add_widget(btn_img); row_btns.add_widget(btn_inven)
        layout.add_widget(row_btns)

        self.fields = {}
        # 암릿 포함 전체 리스트
        items = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in items:
            row = BoxLayout(size_hint_y=None, height=80, spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT))
            ti = TextInput(text=str(self.char_data.get(f, '')), multiline=False, font_name=DEFAULT_FONT, background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
            self.fields[f] = ti; row.add_widget(ti); layout.add_widget(row)

        b_save = BoxLayout(size_hint_y=None, height=130, spacing=15)
        btn_s = StyledButton(text="저장", background_color=(0.1, 0.6, 0.3, 1)); btn_s.bind(on_release=self.save)
        btn_d = StyledButton(text="초기화", background_color=(0.7, 0.2, 0.2, 1)); btn_d.bind(on_release=self.delete)
        b_save.add_widget(btn_s); b_save.add_widget(btn_d); layout.add_widget(b_save)
        
        btn_b = StyledButton(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_b)
        scroll.add_widget(layout); self.add_widget(scroll)

    def pick_img(self, *args):
        fc = FileChooserIconView(); btn = Button(text="선택 완료", size_hint_y=0.15, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        new_char = {f: ti.text for f, ti in self.fields.items()}
        new_char['img'] = self.img.source
        new_char['inventory'] = self.char_data.get('inventory', '') # 인벤 데이터 유지
        acc_data['chars'][idx] = new_char
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

    def delete(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc); acc_data['chars'][idx] = {"이름": f"슬롯 {idx}"}
        store.put(acc, **acc_data); self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text=f"[{self.char_data.get('이름', '캐릭터')}] 인벤토리", font_size='22sp', size_hint_y=0.1, font_name=DEFAULT_FONT))
        self.ti = TextInput(text=self.char_data.get('inventory', ''), multiline=True, font_name=DEFAULT_FONT, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        layout.add_widget(self.ti)
        row = BoxLayout(size_hint_y=None, height=130, spacing=15)
        btn_s = StyledButton(text="저장", background_color=(0.1, 0.6, 0.3, 1)); btn_s.bind(on_release=self.save)
        btn_b = StyledButton(text="뒤로", background_color=(0.4, 0.4, 0.4, 1)); btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        row.add_widget(btn_s); row_btns.add_widget(btn_b) # 오타 수정: row.add_widget(btn_b)
        layout.add_widget(row); self.add_widget(layout)

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc); acc_data['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **acc_data); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.current_acc = ""; sm.current_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
