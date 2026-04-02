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
from kivy.clock import Clock

# 배경색 설정
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# --- 1. 폰트 로딩 오류 완벽 수정 ---
def get_font_path():
    font_name = "font.ttf"
    # 안드로이드 내부 경로 강제 탐색 포함
    paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), font_name),
        os.path.join(os.getcwd(), font_name),
        font_name,
        "./font.ttf"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

FONT_PATH = get_font_path()
if FONT_PATH:
    LabelBase.register(name="Korean", fn_regular=FONT_PATH)
    DEFAULT_FONT = "Korean"
else:
    DEFAULT_FONT = None

# 데이터 저장소
store = JsonStore('priston_data_v2.json')

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.size_hint_y = None
        self.height = 150 # 터치 영역 확대
        self.background_normal = ''
        self.background_color = (0.15, 0.35, 0.7, 1)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 제목
        self.main_layout.add_widget(Label(text="[PT1 통합 검색기]", font_size='32sp', bold=True, 
                                          size_hint_y=0.15, font_name=DEFAULT_FONT, color=(1, 0.8, 0, 1)))
        
        # 검색창 레이아웃
        search_box = BoxLayout(size_hint_y=0.12, spacing=10)
        self.search_input = TextInput(hint_text="계정, 아이템, 장비 검색...", multiline=False, 
                                      font_name=DEFAULT_FONT, background_color=(0.2, 0.2, 0.2, 1), 
                                      foreground_color=(1, 1, 1, 1), padding=[10, 10])
        
        # 검색 버튼 (1번 오류 수정: 실시간 리스트 갱신 함수 연결)
        btn_search = Button(text="검색", size_hint_x=0.25, font_name=DEFAULT_FONT, background_color=(0.4, 0.4, 0.4, 1))
        btn_search.bind(on_release=self.refresh_list)
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        self.main_layout.add_widget(search_box)

        # 계정 추가 버튼
        btn_add = StyledButton(text="+ 새 계정 만들기", background_color=(0.1, 0.6, 0.3, 1))
        btn_add.bind(on_release=self.show_add_popup)
        self.main_layout.add_widget(btn_add)

        # 계정 리스트 (2번 오류 수정: 스크롤뷰 내 그리드 레이아웃 초기화)
        self.scroll = ScrollView()
        self.acc_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.acc_grid.bind(minimum_height=self.acc_grid.setter('height'))
        self.scroll.add_widget(self.acc_grid)
        self.main_layout.add_widget(self.scroll)
        
        self.add_widget(self.main_layout)

    def on_enter(self):
        # 화면에 진입할 때마다 리스트 갱신
        self.refresh_list()

    def refresh_list(self, *args):
        self.acc_grid.clear_widgets()
        query = self.search_input.text.strip().lower()
        
        # 저장소의 모든 계정을 확인
        for acc_name in store.keys():
            acc_data = store.get(acc_name)
            should_show = False
            
            # 1. 계정 이름 매칭
            if not query or query in acc_name.lower():
                should_show = True
            
            # 2. 내부 상세 데이터 매칭 (장비, 인벤토리 등)
            if not should_show:
                for char_idx in range(1, 7):
                    char = acc_data.get('chars', {}).get(str(char_idx), {})
                    # 모든 텍스트 값을 합쳐서 검색
                    all_text = " ".join(str(v).lower() for v in char.values()).replace("none", "")
                    if query in all_text:
                        should_show = True
                        break
            
            if should_show:
                btn = StyledButton(text=f"계정: {acc_name}")
                btn.bind(on_release=lambda x, name=acc_name: self.go_to_acc(name))
                self.acc_grid.add_widget(btn)

    def show_add_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        inp = TextInput(hint_text="계정 이름을 입력하세요", multiline=False, font_name=DEFAULT_FONT, size_hint_y=None, height=120)
        btn = StyledButton(text="계정 저장", background_color=(0.1, 0.6, 0.3, 1))
        content.add_widget(inp)
        content.add_widget(btn)
        
        pop = Popup(title="새 계정 생성", content=content, size_hint=(0.9, 0.4))
        
        def save_new_acc(x):
            if inp.text.strip():
                # 3번 오류 수정: 계정 생성 시 6개 캐릭터 슬롯 즉시 생성 및 저장
                initial_chars = {str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)}
                store.put(inp.text.strip(), chars=initial_chars)
                pop.dismiss()
                self.refresh_list()
        
        btn.bind(on_release=save_new_acc)
        pop.open()

    def go_to_acc(self, name):
        self.manager.current_acc = name
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 헤더 (계정명 및 삭제)
        head = BoxLayout(size_hint_y=0.1)
        head.add_widget(Label(text=f"계정: {acc}", font_size='20sp', font_name=DEFAULT_FONT))
        btn_del = Button(text="계정삭제", size_hint_x=0.3, background_color=(0.8, 0.1, 0.1, 1), font_name=DEFAULT_FONT)
        btn_del.bind(on_release=self.confirm_delete)
        head.add_widget(btn_del)
        layout.add_widget(head)
        
        # 6개 캐릭터 그리드
        grid = GridLayout(cols=2, spacing=15)
        for i in range(1, 7):
            char_data = data['chars'].get(str(i), {})
            display_name = char_data.get('이름', f"{i}번 슬롯")
            btn = StyledButton(text=display_name)
            btn.bind(on_release=lambda x, idx=i: self.select_char(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        btn_back = StyledButton(text="메인 화면으로", background_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def select_char(self, idx):
        self.manager.current_idx = str(idx)
        self.manager.current = 'detail'

    def confirm_delete(self, *args):
        store.delete(self.manager.current_acc)
        self.manager.current = 'main'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        self.char_full_data = store.get(acc)
        self.char_data = self.char_full_data['chars'].get(idx, {})
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 캐릭터 이미지
        self.img = Image(source=self.char_data.get('img', ''), size_hint_y=None, height=500, allow_stretch=True)
        layout.add_widget(self.img)
        
        # 이미지/인벤토리 버튼
        btn_row = BoxLayout(size_hint_y=None, height=130, spacing=10)
        btn_img = StyledButton(text="📷 사진변경"); btn_img.bind(on_release=self.open_file_picker)
        btn_inv = StyledButton(text="👜 인벤토리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        btn_row.add_widget(btn_img); btn_row.add_widget(btn_inv)
        layout.add_widget(btn_row)

        # 상세 필드 (암릿 포함)
        self.inputs = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=85, spacing=10)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT))
            ti = TextInput(text=str(self.char_data.get(f, '')), multiline=False, font_name=DEFAULT_FONT,
                           background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
            self.inputs[f] = ti
            row.add_widget(ti)
            layout.add_widget(row)

        # 저장/초기화 버튼
        save_row = BoxLayout(size_hint_y=None, height=140, spacing=15)
        btn_save = StyledButton(text="저장하기", background_color=(0.1, 0.6, 0.3, 1)); btn_save.bind(on_release=self.save_data)
        btn_reset = StyledButton(text="초기화", background_color=(0.7, 0.2, 0.2, 1)); btn_reset.bind(on_release=self.reset_data)
        save_row.add_widget(btn_save); save_row.add_widget(btn_reset)
        layout.add_widget(save_row)
        
        btn_back = StyledButton(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_back)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_file_picker(self, *args):
        fc = FileChooserIconView(path='/sdcard' if platform == 'android' else '.')
        btn = Button(text="선택 완료", size_hint_y=0.15, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="이미지 선택", content=content, size_hint=(0.9, 0.9))
        def select(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=select); pop.open()

    def save_data(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        new_char_data = {f: ti.text for f, ti in self.inputs.items()}
        new_char_data['img'] = self.img.source
        new_char_data['inventory'] = self.char_data.get('inventory', '') # 인벤토리 유지
        acc_data['chars'][idx] = new_char_data
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

    def reset_data(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        acc_data['chars'][idx] = {"이름": f"슬롯 {idx}"}
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text=f"[{char_data.get('이름', '캐릭터')}] 인벤토리", 
                                font_size='24sp', size_hint_y=0.1, font_name=DEFAULT_FONT))
        
        self.inven_input = TextInput(text=char_data.get('inventory', ''), multiline=True, font_name=DEFAULT_FONT,
                                     background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        layout.add_widget(self.inven_input)
        
        row = BoxLayout(size_hint_y=None, height=140, spacing=15)
        btn_s = StyledButton(text="인벤 저장", background_color=(0.1, 0.6, 0.3, 1)); btn_s.bind(on_release=self.save_inven)
        btn_b = StyledButton(text="뒤로 가기", background_color=(0.4, 0.4, 0.4, 1))
        btn_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        row.add_widget(btn_s); row.add_widget(btn_b)
        layout.add_widget(row)
        self.add_widget(layout)

    def save_inven(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        acc_data['chars'][idx]['inventory'] = self.inven_input.text
        store.put(acc, **acc_data)
        self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        self.title = "Priston Character Manager"
        sm = ScreenManager()
        sm.current_acc = ""
        sm.current_idx = ""
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
