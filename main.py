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
from kivy.uix.image import AsyncImage
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.metrics import dp
from plyer import filechooser # 사진 선택을 위한 라이브러리

# 폰트 설정
FONT_NAME = 'font.ttf' 
if os.path.exists(FONT_NAME):
    LabelBase.register(name="KFont", fn_regular=FONT_NAME)
    DEFAULT_FONT = "KFont"
else:
    DEFAULT_FONT = 'Roboto'

store = JsonStore('pt1_full_data_v2.json')

class StyledBtn(Button):
    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '15sp'
        self.background_normal = ''
        self.background_color = bg_color
        self.size_hint_y = None
        self.height = dp(50)

# --- 공용 알림/확인 팝업 ---
def show_popup(title, text, on_confirm=None):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(text=text, font_name=DEFAULT_FONT))
    btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
    
    close_btn = Button(text="취소", font_name=DEFAULT_FONT)
    btn_layout.add_widget(close_btn)
    
    if on_confirm:
        confirm_btn = Button(text="확인", font_name=DEFAULT_FONT, background_color=(0.8, 0.2, 0.2, 1))
        confirm_btn.bind(on_release=lambda x: [on_confirm(), popup.dismiss()])
        btn_layout.add_widget(confirm_btn)
    
    content.add_widget(btn_layout)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    close_btn.bind(on_release=popup.dismiss)
    popup.open()

# --- 1. 메인 화면 (전체 검색 및 계정 관리) ---
class MainMenu(Screen):
    def on_enter(self):
        self.refresh_ui()

    def refresh_ui(self, query=""):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 검색바 영역
        search_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_input = TextInput(text=query, hint_text="계정, 캐릭터, 아이템 등 검색...", font_name=DEFAULT_FONT, multiline=False)
        s_btn = Button(text="검색", font_name=DEFAULT_FONT, size_hint_x=None, width=dp(70), background_color=(0.1, 0.3, 0.5, 1))
        s_btn.bind(on_release=lambda x: self.refresh_ui(self.search_input.text.strip()))
        search_box.add_widget(self.search_input)
        search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        layout.add_widget(StyledBtn(text="+ 새 계정 만들기", bg_color=(0.1, 0.5, 0.3, 1), on_release=self.add_account_popup))

        scroll = ScrollView()
        list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for acc_name in store.keys():
            acc_data = store.get(acc_name)
            # 모든 텍스트 내용 통합 검색
            if query:
                full_text = json.dumps(acc_data, ensure_ascii=False).lower()
                if query.lower() not in full_text and query.lower() not in acc_name.lower():
                    continue

            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            acc_btn = StyledBtn(text=f"계정: {acc_name}", bg_color=(0.3, 0.3, 0.3, 1))
            acc_btn.bind(on_release=lambda x, n=acc_name: self.go_slots(n))
            del_btn = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda x, n=acc_name: show_popup("삭제 확인", f"'{n}' 계정을 삭제하시겠습니까?", lambda: self.del_acc(n)))
            row.add_widget(acc_btn); row.add_widget(del_btn)
            list_layout.add_widget(row)

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def add_account_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        ti = TextInput(hint_text="계정 이름 입력", font_name=DEFAULT_FONT, multiline=False)
        content.add_widget(ti)
        btn = StyledBtn(text="생성", bg_color=(0.1, 0.5, 0.3, 1))
        content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(ti.text, pop))
        pop.open()

    def save_acc(self, name, pop):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"캐릭터 {i+1}", "inven_items": []} for i in range(6)])
            pop.dismiss(); self.refresh_ui()

    def del_acc(self, name):
        store.delete(name); self.refresh_ui()

    def go_slots(self, name):
        self.manager.current_acc = name
        self.manager.current = 'slots'

# --- 2. 캐릭터 슬롯 화면 (6개 창) ---
class CharacterSlots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc_name = self.manager.current_acc
        slots = store.get(acc_name)['slots']

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"계정: {acc_name}", font_name=DEFAULT_FONT, size_hint_y=None, height=dp(40)))

        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            char_name = slots[i].get("이름", f"캐릭터 {i+1}")
            btn = Button(text=f"{i+1}번\n{char_name}", font_name=DEFAULT_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)

        layout.add_widget(StyledBtn(text="메인 화면으로", bg_color=(0.4, 0.4, 0.4, 1), on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_slot_idx = idx
        self.manager.current = 'detail'

# --- 3. 캐릭터 세부 정보 화면 (사진/인벤토리 이동) ---
class CharDetail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc_name = self.manager.current_acc
        idx = self.manager.current_slot_idx
        self.char_data = store.get(acc_name)['slots'][idx]

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 스크롤 영역
        scroll = ScrollView()
        scroll_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # 사진 영역
        img_path = self.char_data.get('photo', '')
        self.img_widget = AsyncImage(source=img_path if img_path else 'placeholder.png', size_hint_y=None, height=dp(200))
        scroll_layout.add_widget(self.img_widget)
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        photo_btn = StyledBtn(text="📷 사진 올리기 (갤러리)", bg_color=(0.2, 0.5, 0.8, 1), on_release=self.open_gallery)
        inven_btn = StyledBtn(text="📦 인벤토리 관리", bg_color=(0.8, 0.5, 0.2, 1), on_release=self.go_inven)
        btn_box.add_widget(photo_btn); btn_box.add_widget(inven_btn)
        scroll_layout.add_widget(btn_box)

        # 입력 필드 리스트
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=DEFAULT_FONT, size_hint_x=0.3))
            ti = TextInput(text=str(self.char_data.get(f, '')), font_name=DEFAULT_FONT, multiline=False)
            row.add_widget(ti); self.inputs[f] = ti
            scroll_layout.add_widget(row)

        scroll.add_widget(scroll_layout)
        layout.add_widget(scroll)

        # 하단 버튼
        nav_box = GridLayout(cols=3, size_hint_y=None, height=dp(60), spacing=dp(5))
        nav_box.add_widget(StyledBtn(text="저장", bg_color=(0.1, 0.5, 0.3, 1), on_release=self.save_data))
        nav_box.add_widget(StyledBtn(text="뒤로", bg_color=(0.4, 0.4, 0.4, 1), on_release=self.go_back))
        nav_box.add_widget(StyledBtn(text="삭제", bg_color=(0.7, 0.2, 0.2, 1), on_release=lambda x: show_popup("삭제 확인", "캐릭터 정보를 초기화하시겠습니까?", self.reset_char)))
        layout.add_widget(nav_box)

        self.add_widget(layout)

    def open_gallery(self, *args):
        try:
            filechooser.open_file(on_selection=self.handle_selection, filters=[("Images", "*.jpg", "*.png", "*.jpeg")])
        except:
            show_popup("오류", "파일 선택기를 열 수 없습니다.")

    def handle_selection(self, selection):
        if selection:
            self.img_widget.source = selection[0]

    def save_data(self, *args):
        acc_name = self.manager.current_acc
        idx = self.manager.current_slot_idx
        slots = store.get(acc_name)['slots']
        for f in self.fields:
            slots[idx][f] = self.inputs[f].text
        slots[idx]['photo'] = self.img_widget.source
        store.put(acc_name, slots=slots)
        show_popup("성공", "저장되었습니다.")

    def reset_char(self):
        acc_name = self.manager.current_acc
        idx = self.manager.current_slot_idx
        slots = store.get(acc_name)['slots']
        slots[idx] = {"이름": f"캐릭터 {idx+1}", "inven_items": []}
        store.put(acc_name, slots=slots)
        self.go_back()

    def go_inven(self, *args): self.manager.current = 'inventory'
    def go_back(self, *args): self.manager.current = 'slots'

# --- 4. 인벤토리 관리 화면 ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc_name = self.manager.current_acc
        idx = self.manager.current_slot_idx
        char_data = store.get(acc_name)['slots'][idx]
        self.items = char_data.get('inven_items', [])

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text="[인벤토리 편집]", font_name=DEFAULT_FONT, size_hint_y=None, height=dp(40)))

        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)

        self.refresh_items()

        btn_box = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        btn_box.add_widget(StyledBtn(text="+ 아이템 추가", bg_color=(0.1, 0.4, 0.6, 1), on_release=self.add_item))
        btn_box.add_widget(StyledBtn(text="저장하기", bg_color=(0.1, 0.5, 0.3, 1), on_release=self.save_inven))
        btn_box.add_widget(StyledBtn(text="뒤로가기", bg_color=(0.4, 0.4, 0.4, 1), on_release=self.go_back))
        layout.add_widget(btn_box)
        self.add_widget(layout)

    def refresh_items(self):
        self.list_layout.clear_widgets()
        for i, item_val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            ti = TextInput(text=item_val, font_name=DEFAULT_FONT, multiline=False)
            ti.bind(text=lambda instance, value, idx=i: self.update_val(idx, value))
            del_btn = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda x, idx=i: self.remove_item(idx))
            row.add_widget(ti); row.add_widget(del_btn)
            self.list_layout.add_widget(row)

    def update_val(self, idx, val): self.items[idx] = val
    def add_item(self, *args): self.items.append(""); self.refresh_items()
    def remove_item(self, idx): self.items.pop(idx); self.refresh_items()

    def save_inven(self, *args):
        acc_name = self.manager.current_acc
        idx = self.manager.current_slot_idx
        slots = store.get(acc_name)['slots']
        slots[idx]['inven_items'] = self.items
        store.put(acc_name, slots=slots)
        show_popup("알림", "인벤토리가 저장되었습니다.")

    def go_back(self, *args): self.manager.current = 'detail'

class PT1App(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.current_acc = ""; sm.current_slot_idx = 0
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharacterSlots(name='slots'))
        sm.add_widget(CharDetail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PT1App().run()
