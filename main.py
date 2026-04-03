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
from kivy.utils import platform

# 배경색 설정
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# --- 1. 폰트 문제 해결 (절대 경로 및 시스템 폰트 백업) ---
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FONT_NAME = "font.ttf"
FONT_PATH = resource_path(FONT_NAME)

# 한글 폰트 등록 시도
try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name="Korean", fn_regular=FONT_PATH)
        DEFAULT_FONT = "Korean"
    else:
        # 파일이 없을 경우 안드로이드 시스템 한글 폰트 경로 시도
        system_fonts = ["/system/fonts/NanumGothic.ttf", "/system/fonts/DroidSansFallback.ttf"]
        found_system = False
        for f in system_fonts:
            if os.path.exists(f):
                LabelBase.register(name="Korean", fn_regular=f)
                DEFAULT_FONT = "Korean"
                found_system = True
                break
        if not found_system: DEFAULT_FONT = None
except:
    DEFAULT_FONT = None

# 데이터 저장소 (데이터가 안 나올 때를 대비해 새 파일명 사용)
store = JsonStore('priston_v3.json')

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.size_hint_y = None
        self.height = 145
        self.background_normal = ''
        self.background_color = (0.15, 0.3, 0.6, 1)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # 1. 폰트 깨짐 방지용 제목
        self.layout.add_widget(Label(text="[PT1 통합 검색]", font_size='28sp', 
                                     font_name=DEFAULT_FONT, size_hint_y=0.1, color=(1, 0.9, 0, 1)))
        
        # 3. 검색창 (작동 안 하던 문제 해결)
        search_box = BoxLayout(size_hint_y=0.1, spacing=10)
        self.search_ti = TextInput(hint_text="검색어 입력...", multiline=False, font_name=DEFAULT_FONT)
        btn_search = Button(text="검색", size_hint_x=0.25, font_name=DEFAULT_FONT)
        btn_search.bind(on_release=self.refresh) # 검색 실행
        search_box.add_widget(self.search_ti)
        search_box.add_widget(btn_search)
        self.layout.add_widget(search_box)

        # 2. 계정 추가 버튼
        btn_add = StyledButton(text="+ 새 계정 만들기", background_color=(0.1, 0.5, 0.2, 1))
        btn_add.bind(on_release=self.add_popup)
        self.layout.add_widget(btn_add)

        self.acc_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.acc_grid.bind(minimum_height=self.acc_grid.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_grid)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def on_enter(self): self.refresh()

    def refresh(self, *args):
        # 검색 및 목록 출력 로직
        self.acc_grid.clear_widgets()
        q = self.search_ti.text.strip().lower()
        
        for acc in store.keys():
            data = store.get(acc)
            # 계정명 또는 캐릭터 상세 정보에서 검색
            match = False
            if not q or q in acc.lower(): match = True
            else:
                for c_idx in range(1, 7):
                    char = data.get('chars', {}).get(str(c_idx), {})
                    if q in " ".join(str(v).lower() for v in char.values()):
                        match = True; break
            
            if match:
                btn = StyledButton(text=f"계정: {acc}")
                btn.bind(on_release=lambda x, a=acc: self.go_acc(a))
                self.acc_grid.add_widget(btn)

    def add_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(hint_text="계정 이름", multiline=False, font_name=DEFAULT_FONT, size_hint_y=None, height=120)
        btn = StyledButton(text="생성", background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        
        def save(x):
            if inp.text.strip():
                # 계정 생성 시 즉시 6개 슬롯 할당
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()

    def go_acc(self, acc):
        self.manager.current_acc = acc
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=f"[{acc}] 캐릭터", font_name=DEFAULT_FONT, size_hint_y=0.1))
        
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {})
            btn = StyledButton(text=c_data.get('이름', f"슬롯 {i}"))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        btn_b = StyledButton(text="뒤로", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_b)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_idx = str(idx); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        
        sc = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        self.img = Image(source=self.char_data.get('img', ''), size_hint_y=None, height=450)
        layout.add_widget(self.img)
        
        btn_row = BoxLayout(size_hint_y=None, height=120, spacing=10)
        btn_pic = StyledButton(text="사진 수정"); btn_pic.bind(on_release=self.get_pic)
        btn_inv = StyledButton(text="인벤토리", background_color=(0.5, 0.3, 0.1, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        btn_row.add_widget(btn_pic); btn_row.add_widget(btn_inv)
        layout.add_widget(btn_row)

        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in fields:
            r = BoxLayout(size_hint_y=None, height=80, spacing=10)
            r.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT))
            ti = TextInput(text=str(self.char_data.get(f, '')), multiline=False, font_name=DEFAULT_FONT)
            self.ins[f] = ti; r.add_widget(ti); layout.add_widget(r)

        btn_s = StyledButton(text="저장", background_color=(0.1, 0.5, 0.2, 1))
        btn_s.bind(on_release=self.save); layout.add_widget(btn_s)
        
        btn_b = StyledButton(text="뒤로", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_b)
        sc.add_widget(layout); self.add_widget(sc)

    def get_pic(self, *args):
        fc = FileChooserIconView(path='/sdcard' if platform == 'android' else '.')
        btn = Button(text="선택", size_hint_y=0.15, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="이미지", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['img'] = self.img.source
        new_c['inventory'] = self.char_data.get('inventory', '')
        acc_data['chars'][idx] = new_c
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=f"[{char_data.get('이름', '캐릭터')}] 인벤", font_name=DEFAULT_FONT, size_hint_y=0.1))
        self.ti = TextInput(text=char_data.get('inventory', ''), multiline=True, font_name=DEFAULT_FONT)
        layout.add_widget(self.ti)
        btn_s = StyledButton(text="저장", background_color=(0.1, 0.5, 0.2, 1))
        btn_s.bind(on_release=self.save); layout.add_widget(btn_s)
        self.add_widget(layout)

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        acc_data['chars'][idx]['inventory'] = self.ti.text
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
