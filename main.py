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
from kivy.config import Config

# --- 1. 폰트 및 키보드 환경 설정 ---
Window.softinput_mode = "below_target"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FONT_PATH = resource_path("font.ttf")

# 앱 엔진의 기본 폰트를 아예 font.ttf로 고정 (이게 가장 강력합니다)
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)
    Config.set('kivy', 'default_font', ['Korean', FONT_PATH, FONT_PATH, FONT_PATH])
    DEFAULT_FONT = "Korean"
else:
    DEFAULT_FONT = None

Window.clearcolor = (0.05, 0.05, 0.05, 1)
store = JsonStore('priston_v3.json')

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# --- 2. 폰트 깨짐 방지용 커스텀 위젯 ---
class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.size_hint_y = None
        self.height = 145
        self.background_normal = ''
        self.background_color = (0.15, 0.3, 0.6, 1)

class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT # 입력창 한글 깨짐 방지
        self.multiline = False
        self.hint_text_color = (0.5, 0.5, 0.5, 1)

# --- 3. 화면 구성 ---
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.layout.add_widget(StyledLabel(text="[PT1 통합 검색]", font_size='28sp', size_hint_y=0.1))
        
        search_box = BoxLayout(size_hint_y=0.1, spacing=10)
        self.search_ti = StyledInput(hint_text="계정 또는 캐릭터명 검색...")
        btn_search = StyledButton(text="검색", size_hint_x=0.3, background_color=(0.2, 0.6, 0.8, 1))
        btn_search.height = 110 # 검색버튼 높이 조정
        btn_search.bind(on_release=self.refresh)
        search_box.add_widget(self.search_ti)
        search_box.add_widget(btn_search)
        self.layout.add_widget(search_box)

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
        self.acc_grid.clear_widgets()
        query = self.search_ti.text.strip().lower() # 공백 제거 및 소문자화
        
        for acc in store.keys():
            data = store.get(acc)
            is_match = False
            
            # 1. 계정명 검색
            if not query or query in acc.lower():
                is_match = True
            # 2. 계정 내 캐릭터 이름 검색 (캐릭터가 있을 경우)
            else:
                chars = data.get('chars', {})
                for i in range(1, 7):
                    char_info = chars.get(str(i), {})
                    if query in char_info.get('이름', '').lower():
                        is_match = True
                        break
            
            if is_match:
                btn = StyledButton(text=f"계정: {acc}")
                btn.bind(on_release=lambda x, a=acc: self.go_acc(a))
                self.acc_grid.add_widget(btn)

    def add_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = StyledInput(hint_text="계정 이름", size_hint_y=None, height=120)
        btn = StyledButton(text="생성", background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save(x):
            if inp.text.strip():
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
        head = BoxLayout(size_hint_y=0.12, spacing=10)
        head.add_widget(StyledLabel(text=f"[{acc}]", font_size='20sp'))
        btn_del_acc = Button(text="계정 삭제", size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), font_name=DEFAULT_FONT)
        btn_del_acc.bind(on_release=self.confirm_delete)
        head.add_widget(btn_del_acc)
        layout.add_widget(head)
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {})
            btn = StyledButton(text=c_data.get('이름', f"슬롯 {i}"))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        btn_b = StyledButton(text="메인으로 돌아가기", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_b)
        self.add_widget(layout)
    def confirm_delete(self, *args):
        store.delete(self.manager.current_acc); self.manager.current = 'main'
    def go_detail(self, idx):
        self.manager.current_idx = str(idx); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        self.sc = ScrollView()
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.img = Image(source=self.char_data.get('img', ''), size_hint_y=None, height=450)
        self.layout.add_widget(self.img)
        btn_row = BoxLayout(size_hint_y=None, height=120, spacing=10)
        btn_pic = StyledButton(text="사진 수정"); btn_pic.bind(on_release=self.get_pic)
        btn_inv = StyledButton(text="인벤토리", background_color=(0.5, 0.3, 0.1, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        btn_row.add_widget(btn_pic); btn_row.add_widget(btn_inv)
        self.layout.add_widget(btn_row)
        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in fields:
            r = BoxLayout(size_hint_y=None, height=85, spacing=10)
            r.add_widget(StyledLabel(text=f, size_hint_x=0.3))
            ti = StyledInput(text=str(self.char_data.get(f, '')))
            ti.bind(focus=self.on_focus)
            self.ins[f] = ti; r.add_widget(ti); self.layout.add_widget(r)
        btn_s = StyledButton(text="저장", background_color=(0.1, 0.5, 0.2, 1))
        btn_s.bind(on_release=self.save); self.layout.add_widget(btn_s)
        btn_b = StyledButton(text="뒤로", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        self.layout.add_widget(btn_b)
        self.sc.add_widget(self.layout); self.add_widget(self.sc)
    def on_focus(self, instance, value):
        if value: self.sc.scroll_to(instance)
    def get_pic(self, *args):
        start_path = '/sdcard' if platform == 'android' else '.'
        fc = FileChooserIconView(path=start_path, filters=['*.png', '*.jpg', '*.jpeg'])
        btn = Button(text="선택 완료", size_hint_y=0.15, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="이미지 선택", content=content, size_hint=(0.9, 0.9))
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
        store.put(acc, **acc_data); self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(StyledLabel(text=f"[{char_data.get('이름', '캐릭터')}] 인벤토리", size_hint_y=0.1))
        self.ti = StyledInput(text=char_data.get('inventory', ''))
        self.ti.multiline = True # 인벤토리는 여러 줄 가능하게 다시 설정
        layout.add_widget(self.ti)
        btn_row = BoxLayout(size_hint_y=None, height=130, spacing=10)
        btn_s = StyledButton(text="저장", background_color=(0.1, 0.5, 0.2, 1)); btn_s.bind(on_release=self.save)
        btn_b = StyledButton(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btn_row.add_widget(btn_s); btn_row.add_widget(btn_b)
        layout.add_widget(btn_row)
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
