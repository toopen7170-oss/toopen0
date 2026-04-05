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

# --- 1. 폰트 강제 고정 시스템 ---
# font.ttf 파일이 있으면 시스템 전체 기본 폰트로 박아버립니다.
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KoreanFont", fn_regular=FONT_FILE)
    Config.set('kivy', 'default_font', ['KoreanFont', FONT_FILE, FONT_FILE, FONT_FILE])
    DF = "KoreanFont"
else:
    DF = None

# 데이터 저장소 (파일명은 기존과 동일하게 유지)
store = JsonStore('priston_v3.json')

# --- 2. 커스텀 위젯 (디자인 및 한글 방어) ---
class SLabel(Label):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = False
        self.write_tab = False # 탭키 오류 방지

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 145
        self.background_normal = '' # 색상 적용을 위해 배경 초기화
        self.background_color = (0.15, 0.3, 0.6, 1)

# --- 3. 메인 화면 (검색 기능 복구) ---
class MainMenu(Screen):
    def on_enter(self): self.refresh_list()
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(SLabel(text="[프리스톤테일 계정 관리]", font_size='26sp', size_hint_y=0.1))
        
        # 검색창 (가장 반응 좋았던 로직)
        search_box = BoxLayout(size_hint_y=0.12, spacing=10)
        self.search_ti = SInput(hint_text="계정명 또는 캐릭터명 입력...")
        btn_search = Button(text="검색", font_name=DF, size_hint_x=0.3, background_color=(0.2, 0.6, 0.8, 1))
        btn_search.bind(on_release=self.refresh_list)
        search_box.add_widget(self.search_ti)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        btn_add = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.5, 0.2, 1))
        btn_add.bind(on_release=self.add_popup)
        layout.add_widget(btn_add)

        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def refresh_list(self, *a):
        self.grid.clear_widgets()
        q = self.search_ti.text.strip().lower()
        # 모든 데이터를 돌며 계정명 혹은 캐릭터 이름 매칭 확인
        for acc in list(store.keys()):
            data = store.get(acc)
            match = False
            if not q or q in acc.lower():
                match = True
            else:
                chars = data.get('chars', {})
                for i in range(1, 7):
                    c_name = chars.get(str(i), {}).get('이름', '').lower()
                    if q in c_name:
                        match = True
                        break
            if match:
                btn = SBtn(text=f"계정: {acc}")
                btn.bind(on_release=lambda x, a=acc: self.go_acc(a))
                self.grid.add_widget(btn)

    def add_popup(self, *a):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="새 계정명")
        btn = SBtn(text="생성하기", background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save_new(x):
            if inp.text.strip():
                # 초기 캐릭터 6개 슬롯 자동 생성
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh_list()
        btn.bind(on_release=save_new); pop.open()

    def go_acc(self, acc):
        self.manager.cur_acc = acc
        self.manager.current = 'char_select'

# --- 4. 캐릭터 선택 (디자인 복구) ---
class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(SLabel(text=f"[{acc}] 캐릭터 목록", size_hint_y=0.1))
        
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {})
            btn = SBtn(text=c_data.get('이름', f"슬롯 {i}"))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        back = SBtn(text="메인으로 돌아가기", background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.cur_idx = str(idx)
        self.manager.current = 'detail'

# --- 5. 상세 정보 (사진 및 모든 항목 복구) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        
        sc = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 이미지 영역
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if img_src else '', size_hint_y=None, height=450)
        layout.add_widget(self.img)
        
        btn_row = BoxLayout(size_hint_y=None, height=120, spacing=10)
        btn_pic = SBtn(text="사진 변경"); btn_pic.bind(on_release=self.get_pic)
        btn_inv = SBtn(text="인벤토리", background_color=(0.5, 0.3, 0.1, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        btn_row.add_widget(btn_pic); btn_row.add_widget(btn_inv)
        layout.add_widget(btn_row)

        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in fields:
            r = BoxLayout(size_hint_y=None, height=85, spacing=10)
            r.add_widget(SLabel(text=f, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, '')))
            self.ins[f] = ti
            r.add_widget(ti)
            layout.add_widget(r)
            
        sv = SBtn(text="데이터 저장", background_color=(0.1, 0.5, 0.2, 1))
        sv.bind(on_release=self.save)
        layout.add_widget(sv)
        
        bk = SBtn(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(bk)
        
        sc.add_widget(layout)
        self.add_widget(sc)

    def get_pic(self, *a):
        # 안드로이드 경로 및 PC 경로 대응
        start_p = '/sdcard' if os.path.exists('/sdcard') else '.'
        fc = FileChooserIconView(path=start_p, filters=['*.jpg', '*.png', '*.jpeg'])
        btn = Button(text="이 파일로 선택", size_hint_y=0.15, font_name=DF)
        box = BoxLayout(orientation='vertical'); box.add_widget(fc); box.add_widget(btn)
        pop = Popup(title="사진 선택", content=box, size_hint=(0.9, 0.9))
        def select_file(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=select_file); pop.open()

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        acc_data = store.get(acc)
        new_char = {f: ti.text for f, ti in self.ins.items()}
        new_char['img'] = self.img.source
        new_char['inventory'] = self.char_data.get('inventory', '')
        acc_data['chars'][idx] = new_char
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

# --- 6. 인벤토리 (긴 텍스트 대응) ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(SLabel(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리 내역", size_hint_y=0.1))
        self.ti = SInput(text=char_data.get('inventory', ''))
        self.ti.multiline = True # 여러 줄 입력 가능하게
        layout.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=None, height=130, spacing=10)
        sv = SBtn(text="저장", background_color=(0.1, 0.5, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="닫기", background_color=(0.4, 0.4, 0.4, 1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk)
        layout.add_widget(btns); self.add_widget(layout)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        acc_data = store.get(acc)
        acc_data['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **acc_data); self.manager.current = 'detail'

# --- 7. 앱 구동 ---
class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
