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

# --- 1. 한글 폰트 설정 (폰트 깨짐 보험 강화) ---
# font.ttf 파일이 저장소에 업로드되어 있어야 합니다.
def get_font_path():
    font_name = "font.ttf"
    # 안드로이드 내부 경로와 깃허브 워크스페이스 경로 모두 확인
    paths = [
        font_name,
        os.path.join(os.path.dirname(sys.argv[0]), font_name),
        os.path.join(os.getcwd(), font_name)
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

FONT_PATH = get_font_path()
if FONT_PATH:
    LabelBase.register(name="KoreanFont", fn_regular=FONT_PATH)
    DEFAULT_FONT = "KoreanFont"
else:
    DEFAULT_FONT = None # 폰트가 없으면 기본 폰트로 실행 (튕김 방지)

# 데이터 저장소 (휴대폰 내부에 자동 생성)
store = JsonStore('priston_data.json')

# --- 버튼 스타일 통일 ---
class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.size_hint_y = None
        self.height = 120 # 손가락 클릭 편하게 크게 설정
        self.background_color = (0.2, 0.4, 0.8, 1) # 블루 톤

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 제목
        layout.add_widget(Label(text="[PT1 캐릭터 관리]", font_size='28sp', bold=True, size_hint_y=0.1, font_name=DEFAULT_FONT))
        
        # 검색 기능 (계정 이름 검색)
        search_box = BoxLayout(size_hint_y=0.1, spacing=5)
        self.search_input = TextInput(hint_text="계정 이름 검색", multiline=False, font_name=DEFAULT_FONT)
        btn_search = Button(text="검색", size_hint_x=0.2, font_name=DEFAULT_FONT)
        btn_search.bind(on_release=self.refresh) # 검색 버튼 누르면 리스트 새로고침
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        # 계정 추가 버튼
        btn_add = StyledButton(text="+ 새 계정 추가", background_color=(0.1, 0.6, 0.3, 1))
        btn_add.bind(on_release=self.add_account)
        layout.add_widget(btn_add)

        # 계정 리스트 (스크롤)
        self.acc_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.acc_list.bind(minimum_height=self.acc_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh()

    def refresh(self, *args):
        self.acc_list.clear_widgets()
        search_text = self.search_input.text.strip().lower()
        
        for k in store.keys():
            # 검색어가 있으면 필터링
            if search_text and search_text not in k.lower():
                continue
                
            btn = StyledButton(text=f"계정: {k}")
            btn.bind(on_release=lambda x, key=k: self.select_acc(key))
            self.acc_list.add_widget(btn)

    def add_account(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(hint_text="계정 이름을 입력하세요", multiline=False, font_name=DEFAULT_FONT)
        btn = Button(text="저장", size_hint_y=None, height=100, font_name=DEFAULT_FONT)
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save_acc(x):
            if inp.text:
                # 6개 캐릭터 슬롯 초기화 (1번 이름 -> 2번 슬롯 연동 문제 해결)
                chars_data = {str(i): {"name": f"슬롯 {i}"} for i in range(1, 7)}
                store.put(inp.text, chars=chars_data)
                self.refresh(); pop.dismiss()
        btn.bind(on_release=save_acc); pop.open()

    def select_acc(self, key):
        self.manager.current_acc = key
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        
        if not store.exists(acc): # 계정이 삭제된 경우 방지
            self.manager.current = 'main'
            return

        data = store.get(acc)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 제목 및 삭제 버튼
        top_box = BoxLayout(size_hint_y=0.1, spacing=5)
        top_box.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_size='22sp', font_name=DEFAULT_FONT))
        btn_del_acc = Button(text="계정 삭제", size_hint_x=0.3, background_color=(1, 0, 0, 1), font_name=DEFAULT_FONT)
        btn_del_acc.bind(on_release=self.delete_account)
        top_box.add_widget(btn_del_acc)
        layout.add_widget(top_box)
        
        # 6개 캐릭터 그리드
        grid = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = data['chars'].get(str(i), {"name": "비었음"})
            # 실제 캐릭터 이름 표시 (이름 연동 오류 해결)
            btn = StyledButton(text=f"{i}. {c_data.get('이름', '비었음')}")
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        # 하단 버튼
        btn_back = StyledButton(text="뒤로가기", height=100, background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_idx = str(idx)
        self.manager.current = 'detail'

    def delete_account(self, *args):
        def confirm_del(x):
            acc = self.manager.current_acc
            store.delete(acc)
            pop.dismiss()
            self.manager.current = 'main'

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f" 정말 '{self.manager.current_acc}' 계정을\n 삭제하시겠습니까?", font_name=DEFAULT_FONT, halign='center'))
        b_box = BoxLayout(spacing=10); btn_y = Button(text="예", font_name=DEFAULT_FONT); btn_n = Button(text="아니오", font_name=DEFAULT_FONT)
        b_box.add_widget(btn_y); b_box.add_widget(btn_n); content.add_widget(b_box)
        pop = Popup(title="계정 삭제 확인", content=content, size_hint=(0.8, 0.5))
        btn_y.bind(on_release=confirm_del); btn_n.bind(on_release=pop.dismiss); pop.open()

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        # 데이터가 없을 경우 초기화
        acc_data = store.get(acc)
        self.data = acc_data['chars'].get(idx, {})
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 캐릭터 사진 (크기 최적화)
        self.img = Image(source=self.data.get('img', ''), size_hint_y=None, height=450, allow_stretch=True)
        layout.add_widget(self.img)
        
        b_img_box = BoxLayout(size_hint_y=None, height=100, spacing=10)
        btn_img = StyledButton(text="📷 사진 등록", background_color=(0.4, 0.4, 0.4, 1))
        btn_img.bind(on_release=self.pick_img)
        # 인벤토리 버튼 추가
        btn_inven = StyledButton(text="👜 인벤토리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inven.bind(on_release=self.go_inven)
        b_img_box.add_widget(btn_img); b_img_box.add_widget(btn_inven)
        layout.add_widget(b_img_box)

        # 세부 항목 입력 (암릿 추가)
        self.fields = {}
        items = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in items:
            row = BoxLayout(size_hint_y=None, height=70, spacing=5)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT))
            ti = TextInput(text=str(self.data.get(f, '')), multiline=False, font_name=DEFAULT_FONT)
            self.fields[f] = ti; row.add_widget(ti); layout.add_widget(row)

        # 저장/삭제 버튼
        b_row = BoxLayout(size_hint_y=None, height=100, spacing=15)
        btn_save = StyledButton(text="저장", background_color=(0.1, 0.6, 0.3, 1))
        btn_save.bind(on_release=self.save)
        btn_del = StyledButton(text="캐릭터 초기화", background_color=(0.8, 0.2, 0.2, 1))
        btn_del.bind(on_release=self.delete)
        b_row.add_widget(btn_save); b_row.add_widget(btn_del); layout.add_widget(b_row)
        
        # 뒤로가기
        btn_back = StyledButton(text="뒤로가기", height=100, background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_back)
        
        scroll.add_widget(layout); self.add_widget(scroll)

    def pick_img(self, *args):
        fc = FileChooserIconView(path='/sdcard') # 안드로이드 기본 경로 시도
        btn = Button(text="선택완료", size_hint_y=0.15, font_name=DEFAULT_FONT)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def go_inven(self, *args):
        self.manager.current = 'inventory'

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        # 데이터 무결성 확인
        if not store.exists(acc): return
        
        acc_data = store.get(acc)
        
        # 입력된 데이터 수집
        new_d = {f: ti.text for f, ti in self.fields.items()}
        new_d['img'] = self.img.source
        # 기존 인벤토리 데이터 유지
        if 'inventory' in self.data:
            new_d['inventory'] = self.data['inventory']
        
        # 데이터 업데이트 (이름 연동 해결)
        acc_data['chars'][idx] = new_d
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

    def delete(self, *args):
        def confirm_reset(x):
            acc, idx = self.manager.current_acc, self.manager.current_idx
            acc_data = store.get(acc)
            # 해당 슬롯 초기화
            acc_data['chars'][idx] = {"name": "비었음"}
            store.put(acc, **acc_data)
            pop.dismiss()
            self.manager.current = 'char_select'

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=" 이 캐릭터 정보를 정말\n 초기화하시겠습니까?", font_name=DEFAULT_FONT, halign='center'))
        b_box = BoxLayout(spacing=10); btn_y = Button(text="예", font_name=DEFAULT_FONT); btn_n = Button(text="아니오", font_name=DEFAULT_FONT)
        b_box.add_widget(btn_y); b_box.add_widget(btn_n); content.add_widget(b_box)
        pop = Popup(title="캐릭터 초기화 확인", content=content, size_hint=(0.8, 0.4))
        btn_y.bind(on_release=confirm_reset); btn_n.bind(on_release=pop.dismiss); pop.open()

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        # 인벤토리 데이터 불러오기 (없으면 빈 텍스트)
        self.inven_text = char_data.get('inventory', '')
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # 제목 (캐릭터 이름 표시)
        c_name = char_data.get('이름', '알수없음')
        layout.add_widget(Label(text=f"[{c_name}] 인벤토리", font_size='22sp', size_hint_y=0.1, font_name=DEFAULT_FONT))
        
        # 인벤토리 입력창 (전체화면 스크롤)
        self.ti_inven = TextInput(text=self.inven_text, multiline=True, font_name=DEFAULT_FONT, hint_text="인벤토리 내용을 입력하세요")
        layout.add_widget(self.ti_inven)
        
        # 하단 버튼
        b_row = BoxLayout(size_hint_y=None, height=120, spacing=15)
        btn_save = StyledButton(text="저장", background_color=(0.1, 0.6, 0.3, 1))
        btn_save.bind(on_release=self.save_inven)
        btn_back = StyledButton(text="뒤로", background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        b_row.add_widget(btn_save); b_row.add_widget(btn_back)
        layout.add_widget(b_row)
        self.add_widget(layout)

    def save_inven(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        # 인벤토리 텍스트 데이터 업데이트
        acc_data['chars'][idx]['inventory'] = self.ti_inven.text
        store.put(acc, **acc_data)
        self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        # 전역 변수 초기화
        sm.current_acc = ""; sm.current_idx = ""
        # 화면 추가
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory')) # 인벤토리 화면 추가
        return sm

if __name__ == '__main__':
    PristonApp().run()
