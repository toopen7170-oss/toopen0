import os
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
from kivy.clock import Clock
from plyer import filechooser

# 폰트 등록 (파일이 없을 경우 시스템 폰트 사용)
FONT_NAME = 'font.ttf'
if os.path.exists(FONT_NAME):
    LabelBase.register(name="KFont", fn_regular=FONT_NAME)
    K_FONT = "KFont"
else:
    K_FONT = 'Roboto'

store = JsonStore('pt1_data_v3.json')

# --- 공용 스타일 버튼 ---
class StyledBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(50)

# --- 삭제 확인 팝업 함수 ---
def ask_confirm(title, msg, callback):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(text=msg, font_name=K_FONT))
    
    btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
    yes_btn = Button(text="확인", font_name=K_FONT, background_color=(0.8, 0.2, 0.2, 1))
    no_btn = Button(text="취소", font_name=K_FONT)
    
    btns.add_widget(yes_btn)
    btns.add_widget(no_btn)
    content.add_widget(btns)
    
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    yes_btn.bind(on_release=lambda x: [callback(), popup.dismiss()])
    no_btn.bind(on_release=popup.dismiss)
    popup.open()

# --- 메인 화면 ---
class MainMenu(Screen):
    def on_enter(self):
        self.refresh_list()

    def refresh_list(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 검색바
        search_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.search_in = TextInput(hint_text="계정 검색...", font_name=K_FONT, multiline=False)
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list())
        search_box.add_widget(self.search_in)
        search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        layout.add_widget(StyledBtn(text="+ 새 계정 생성", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_acc_pop))

        scroll = ScrollView(do_scroll_x=False)
        self.list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        query = self.search_in.text if hasattr(self, 'search_in') else ""
        for name in store.keys():
            if query and query not in name: continue
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            btn = StyledBtn(text=name)
            btn.bind(on_release=lambda x, n=name: self.go_slots(n))
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, n=name: ask_confirm("계정 삭제", f"'{n}'을 삭제할까요?", lambda: self.del_acc(n)))
            row.add_widget(btn); row.add_widget(del_b)
            self.list_layout.add_widget(row)

        scroll.add_widget(self.list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def add_acc_pop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        ti = TextInput(multiline=False, font_name=K_FONT)
        content.add_widget(ti)
        b = Button(text="추가", font_name=K_FONT)
        content.add_widget(b)
        pop = Popup(title="계정명 입력", content=content, size_hint=(0.8, 0.4))
        b.bind(on_release=lambda x: self.create_acc(ti.text, pop))
        pop.open()

    def create_acc(self, name, pop):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"캐릭터 {i+1}", "items": []} for i in range(6)])
            pop.dismiss(); self.refresh_list()

    def del_acc(self, name):
        store.delete(name); self.refresh_list()

    def go_slots(self, name):
        self.manager.cur_acc = name
        self.manager.current = 'slots'

# --- 캐릭터 슬롯 (1~6번) ---
class CharSlots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        data = store.get(acc)['slots']
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"계정: {acc}", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            name = data[i].get('이름', f'캐릭터 {i+1}')
            b = Button(text=f"{i+1}번\n{name}", font_name=K_FONT, halign='center')
            b.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(b)
        layout.add_widget(grid)
        layout.add_widget(StyledBtn(text="뒤로가기", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.cur_idx = idx
        self.manager.current = 'detail'

# --- 세부 정보 (사진 및 입력) ---
class CharDetail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 스크롤 가능 영역 (2번 문제 해결)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # 이미지
        img_path = self.data.get('photo', '')
        self.img = AsyncImage(source=img_path if img_path else 'placeholder.png', size_hint_y=None, height=dp(250))
        content.add_widget(self.img)
        
        content.add_widget(StyledBtn(text="📷 사진 선택 (안드로이드 갤러터)", bg=(0.2, 0.4, 0.8, 1), on_release=self.pick_photo))
        content.add_widget(StyledBtn(text="📦 인벤토리 관리", bg=(0.7, 0.4, 0.1, 1), on_release=lambda x: setattr(self.manager, 'current', 'inven')))
        
        # 입력 필드
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            ti = TextInput(text=str(self.data.get(f, '')), font_name=K_FONT, multiline=False)
            row.add_widget(ti); self.inputs[f] = ti
            content.add_widget(row)
            
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        # 하단 버튼
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(StyledBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save))
        nav.add_widget(StyledBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        layout.add_widget(nav)
        self.add_widget(layout)

    def pick_photo(self, *args):
        # 정지 현상 방지를 위해 클럭 사용 (1번 문제 해결)
        Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_photo), 0.1)

    def set_photo(self, selection):
        if selection:
            self.img.source = selection[0]

    def save(self, *args):
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        for f in self.fields:
            slots[idx][f] = self.inputs[f].text
        slots[idx]['photo'] = self.img.source
        store.put(acc, slots=slots)
        ask_confirm("성공", "정보가 저장되었습니다.", lambda: None)

# --- 인벤토리 관리 ---
class InvenPage(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('items', [])
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text="[인벤토리 편집]", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.scroll.add_widget(self.list_box)
        layout.add_widget(self.scroll)
        
        self.draw_items()
        
        nav = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        nav.add_widget(StyledBtn(text="+ 아이템 추가", bg=(0.1, 0.4, 0.6, 1), on_release=self.add_i))
        nav.add_widget(StyledBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save_i))
        nav.add_widget(StyledBtn(text="뒤로가기", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        layout.add_widget(nav)
        self.add_widget(layout)

    def draw_items(self):
        self.list_box.clear_widgets()
        for i, val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            ti = TextInput(text=val, font_name=K_FONT, multiline=False)
            ti.bind(text=lambda instance, v, idx=i: self.update_item(idx, v))
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, idx=i: ask_confirm("아이템 삭제", "이 아이템을 삭제할까요?", lambda: self.rem_i(idx)))
            row.add_widget(ti); row.add_widget(del_b)
            self.list_box.add_widget(row)

    def update_item(self, idx, v): self.items[idx] = v
    def add_i(self, *args): self.items.append(""); self.draw_items()
    def rem_i(self, idx): self.items.pop(idx); self.draw_items()
    
    def save_i(self, *args):
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        slots[idx]['items'] = self.items
        store.put(acc, slots=slots)

class PTApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSlots(name='slots'))
        sm.add_widget(CharDetail(name='detail'))
        sm.add_widget(InvenPage(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
