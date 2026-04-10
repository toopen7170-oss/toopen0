import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import platform

# 폰트 설정 (font.ttf 파일이 같은 폴더에 있어야 합니다)
FONT_NAME = "KFont"
FONT_PATH = "font.ttf"
if os.path.exists(FONT_PATH):
    LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
else:
    FONT_NAME = None

store = JsonStore('priston_data_v4.json')

# --- 공통 스타일 위젯 ---
class StyledButton(Button):
    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ''
        self.background_color = bg_color
        self.size_hint_y = None
        self.height = dp(55)
        self.font_size = '16sp'

class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(10), dp(12)]

# --- 1. 메인 화면 (강력한 전체 검색 기능) ---
class MainScreen(Screen):
    def on_enter(self): self.refresh_list()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 제목 및 검색바
        layout.add_widget(Label(text="[PT1 통합 검색 매니저]", font_name=FONT_NAME, size_hint_y=None, height=dp(50), font_size='20sp'))
        
        self.search_input = StyledInput(hint_text="아이템, 직업, 레벨, 내용물 검색...")
        self.search_input.bind(text=self.refresh_list)
        layout.add_widget(self.search_input)

        # 계정 추가 버튼
        add_btn = StyledButton(text="+ 새 계정 만들기", bg_color=(0.1, 0.5, 0.2, 1))
        add_btn.bind(on_release=self.add_account_popup)
        layout.add_widget(add_btn)

        # 계정 리스트 (스크롤)
        self.scroll = ScrollView()
        self.account_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.account_list.bind(minimum_height=self.account_list.setter('height'))
        self.scroll.add_widget(self.account_list)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)

    def refresh_list(self, *args):
        self.account_list.clear_widgets()
        query = self.search_input.text.lower()
        
        for acc_id in sorted(store.keys()):
            acc_data = store.get(acc_id)
            match_found = not query or query in acc_id.lower()
            
            # 모든 데이터 필드 검색 (직업, 무기, 인벤토리 등)
            if not match_found:
                for char_idx in acc_data['chars']:
                    char = acc_data['chars'][char_idx]
                    combined_text = " ".join(str(v).lower() for v in char.values())
                    if query in combined_text:
                        match_found = True
                        break
            
            if match_found:
                row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
                btn = StyledButton(text=f"계정: {acc_id}", bg_color=(0.2, 0.3, 0.5, 1))
                btn.bind(on_release=lambda x, a=acc_id: self.go_to_account(a))
                
                del_btn = Button(text="삭제", size_hint_x=0.2, font_name=FONT_NAME, background_color=(0.7, 0.2, 0.2, 1))
                del_btn.bind(on_release=lambda x, a=acc_id: self.confirm_delete(a))
                
                row.add_widget(btn)
                row.add_widget(del_btn)
                self.account_list.add_widget(row)

    def confirm_delete(self, acc_id):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=f"'{acc_id}' 계정을 삭제하시겠습니까?", font_name=FONT_NAME))
        btns = BoxLayout(spacing=dp(10))
        y_btn = StyledButton(text="삭제", bg_color=(0.8, 0.1, 0.1, 1))
        n_btn = StyledButton(text="취소")
        btns.add_widget(y_btn); btns.add_widget(n_btn); content.add_widget(btns)
        
        pop = Popup(title="경고", content=content, size_hint=(0.8, 0.3), title_font=FONT_NAME)
        y_btn.bind(on_release=lambda x: [store.delete(acc_id), self.refresh_list(), pop.dismiss()])
        n_btn.bind(on_release=pop.dismiss); pop.open()

    def add_account_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        inp = StyledInput(hint_text="새 계정 ID")
        btn = StyledButton(text="생성", bg_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4), title_font=FONT_NAME)
        
        def save(x):
            if inp.text.strip():
                # 6개 캐릭터 슬롯 초기화
                chars = {str(i): {"이름": f"슬롯 {i}", "inventory": ""} for i in range(1, 7)}
                store.put(inp.text.strip(), chars=chars)
                pop.dismiss(); self.refresh_list()
        btn.bind(on_release=save); pop.open()

    def go_to_account(self, acc_id):
        self.manager.current_acc = acc_id
        self.manager.current = 'char_select'

# --- 2. 캐릭터 선택 화면 (6개 슬롯) ---
class CharSelectScreen(Screen):
    def on_enter(self):
        self.layout.clear_widgets()
        acc_id = self.manager.current_acc
        acc_data = store.get(acc_id)
        
        self.layout.add_widget(Label(text=f"[{acc_id}] 캐릭터 선택", font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
        
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(1, 7):
            char_info = acc_data['chars'].get(str(i), {})
            char_name = char_info.get("이름", f"슬롯 {i}")
            btn = StyledButton(text=char_name, bg_color=(0.3, 0.3, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        
        self.layout.add_widget(grid)
        back = StyledButton(text="뒤로가기", bg_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        self.layout.add_widget(back)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.add_widget(self.layout)
    def go_detail(self, idx):
        self.manager.current_char_idx = str(idx)
        self.manager.current = 'detail'

# --- 3. 캐릭터 세부 내역 (수정, 사진, 인벤토리 연동) ---
class DetailScreen(Screen):
    def on_enter(self):
        self.root.clear_widgets()
        acc_id = self.manager.current_acc
        char_idx = self.manager.current_char_idx
        self.char_data = store.get(acc_id)['chars'][char_idx]
        
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))

        # 사진 영역
        img_path = self.char_data.get('photo', '')
        self.img_widget = Image(source=img_path if os.path.exists(img_path) else '', size_hint_y=None, height=dp(200))
        container.add_widget(self.img_widget)
        
        photo_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        add_p = StyledButton(text="사진 변경", bg_color=(0.2, 0.4, 0.6, 1))
        del_p = StyledButton(text="사진 삭제", bg_color=(0.6, 0.2, 0.2, 1))
        photo_box.add_widget(add_p); photo_box.add_widget(del_p); container.add_widget(photo_box)

        # 인벤토리 이동 버튼
        inv_btn = StyledButton(text="📦 인벤토리 관리 (전체화면)", bg_color=(0.6, 0.4, 0.2, 1))
        inv_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        container.add_widget(inv_btn)

        # 입력 필드들
        self.inputs = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=FONT_NAME, size_hint_x=0.3))
            ti = StyledInput(text=str(self.char_data.get(f, '')))
            self.inputs[f] = ti
            row.add_widget(ti)
            container.add_widget(row)

        # 하단 버튼
        btn_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        save_b = StyledButton(text="캐릭터 저장", bg_color=(0.1, 0.6, 0.3, 1))
        save_b.bind(on_release=self.save_data)
        back_b = StyledButton(text="뒤로가기", bg_color=(0.4, 0.4, 0.4, 1))
        back_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        btn_row.add_widget(save_b); btn_row.add_widget(back_b)
        container.add_widget(btn_row)
        scroll.add_widget(container); self.root.add_widget(scroll)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root = BoxLayout(orientation='vertical')
        self.add_widget(self.root)

    def save_data(self, *args):
        acc_id = self.manager.current_acc
        char_idx = self.manager.current_char_idx
        acc_data = store.get(acc_id)
        
        for f, ti in self.inputs.items():
            self.char_data[f] = ti.text
        
        acc_data['chars'][char_idx] = self.char_data
        store.put(acc_id, **acc_data)
        self.manager.current = 'char_select'

# --- 4. 인벤토리 화면 (전체화면 편집) ---
class InventoryScreen(Screen):
    def on_enter(self):
        acc_id = self.manager.current_acc
        char_idx = self.manager.current_char_idx
        self.char_data = store.get(acc_id)['chars'][char_idx]
        self.ti.text = self.char_data.get('inventory', '')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text="인벤토리 상세 편집", font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
        
        self.ti = TextInput(font_name=FONT_NAME, multiline=True, font_size='18sp', padding=[dp(10), dp(10)])
        layout.add_widget(self.ti)
        
        btns = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        save = StyledButton(text="저장", bg_color=(0.1, 0.6, 0.3, 1))
        save.bind(on_release=self.save_inv)
        back = StyledButton(text="뒤로", bg_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(save); btns.add_widget(back); layout.add_widget(btns)
        self.add_widget(layout)

    def save_inv(self, *args):
        acc_id = self.manager.current_acc
        char_idx = self.manager.current_char_idx
        acc_data = store.get(acc_id)
        acc_data['chars'][char_idx]['inventory'] = self.ti.text
        store.put(acc_id, **acc_data)
        self.manager.current = 'detail'

# --- 앱 실행부 ---
class PristonManagerApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.current_acc = ""; sm.current_char_idx = ""
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CharSelectScreen(name='char_select'))
        sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(InventoryScreen(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonManagerApp().run()
