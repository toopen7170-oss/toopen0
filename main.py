import os, sys
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
from kivy.config import Config
from kivy.clock import Clock

# --- 1. 폰트 및 시스템 설정 (절대 안 깨지게 고정) ---
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KoreanFont", fn_regular=FONT_FILE)
    Config.set('kivy', 'default_font', ['KoreanFont', FONT_FILE, FONT_FILE, FONT_FILE])
    DF = "KoreanFont"
else:
    DF = None

store = JsonStore('priston_v3.json')

# --- 2. 커스텀 위젯 (디자인 유지) ---
class SLabel(Label):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = False

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 145
        self.background_color = (0.15, 0.3, 0.6, 1)

# --- 3. 화면 구성 (기존 기능 모두 복구) ---
class MainMenu(Screen):
    def on_enter(self): self.refresh_list()
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(SLabel(text="[PT1 계정 매니저]", font_size='24sp', size_hint_y=0.1))
        
        # 검색창 (가장 잘 되던 로직으로 보강)
        search_box = BoxLayout(size_hint_y=0.12, spacing=10)
        self.stti = SInput(hint_text="계정 또는 캐릭터명 검색...")
        s_btn = Button(text="검색", font_name=DF, size_hint_x=0.3)
        s_btn.bind(on_release=self.refresh_list)
        search_box.add_widget(self.stti); search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        btn_add = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.5, 0.2, 1))
        btn_add.bind(on_release=self.add_popup)
        layout.add_widget(btn_add)

        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.grid)
        layout.add_widget(scroll); self.add_widget(layout)

    def refresh_list(self, *a):
        self.grid.clear_widgets()
        q = self.stti.text.strip().lower()
        for acc in list(store.keys()):
            data = store.get(acc)
            match = False
            if not q or q in acc.lower(): match = True
            else:
                chars = data.get('chars', {})
                for i in range(1, 7):
                    if q in chars.get(str(i), {}).get('이름', '').lower():
                        match = True; break
            if match:
                btn = SBtn(text=f"계정: {acc}")
                btn.bind(on_release=lambda x, a=acc: self.go_acc(a))
                self.grid.add_widget(btn)

    def add_popup(self, *a):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름 입력")
        btn = SBtn(text="생성", background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save(x):
            if inp.text.strip():
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh_list()
        btn.bind(on_release=save); pop.open()

    def go_acc(self, acc):
        self.manager.cur_acc = acc; self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(SLabel(text=f"[{acc}] 캐릭터 선택", size_hint_y=0.1))
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {})
            btn = SBtn(text=c_data.get('이름', f"슬롯 {i}"))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        back = SBtn(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back); self.add_widget(layout)
    def go_detail(self, idx):
        self.manager.cur_idx = str(idx); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 사진 기능 복구
        img_path = self.char_data.get('img', '')
        self.img = Image(source=img_path if img_path else '', size_hint_y=None, height=450)
        layout.add_widget(self.img)
        
        btn_row = BoxLayout(size_hint_y=None, height=120, spacing=10)
        b_pic = SBtn(text="사진 변경"); b_pic.bind(on_release=self.get_pic)
        b_inv = SBtn(text="인벤토리", background_color=(0.5, 0.3, 0.1, 1))
        b_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        btn_row.add_widget(b_pic); btn_row.add_widget(b_inv)
        layout.add_widget(btn_row)

        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in fields:
            r = BoxLayout(size_hint_y=None, height=85, spacing=10)
            r.add_widget(SLabel(text=f, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, '')))
            self.ins[f] = ti; r.add_widget(ti); layout.add_widget(r)
        
        sv = SBtn(text="저장하기", background_color=(0.1, 0.5, 0.2, 1))
        sv.bind(on_release=self.save); layout.add_widget(sv)
        bk = SBtn(text="뒤로", background_color=(0.4, 0.4, 0.4, 1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(bk); scroll.add_widget(layout); self.add_widget(scroll)

    def get_pic(self, *a):
        content = FileChooserIconView(path='/sdcard' if os.path.exists('/sdcard') else '.', filters=['*.jpg', '*.png'])
        btn = Button(text="선택 완료", size_hint_y=0.15, font_name=DF)
        box = BoxLayout(orientation='vertical'); box.add_widget(content); box.add_widget(btn)
        pop = Popup(title="이미지 선택", content=box, size_hint=(0.9, 0.9))
        def sel(x):
            if content.selection: self.img.source = content.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        acc_data = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['img'] = self.img.source
        new_c['inventory'] = self.char_data.get('inventory', '')
        acc_data['chars'][idx] = new_c
        store.put(acc, **acc_data); self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(SLabel(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리", size_hint_y=0.1))
        self.ti = SInput(text=char_data.get('inventory', '')); self.ti.multiline = True
        layout.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=None, height=130, spacing=10)
        sv = SBtn(text="저장", background_color=(0.1, 0.5, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); layout.add_widget(btns); self.add_widget(layout)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        acc_data = store.get(acc)
        acc_data['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **acc_data); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
