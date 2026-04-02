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
from kivy.utils import platform

# 앱 배경색 설정 (다크 모드)
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# --- 1. 한글 폰트 설정 (폰트 깨짐 절대 방지 보완) ---
def get_font_path():
    font_name = "font.ttf"
    # 안드로이드 내부 경로와 깃허브 워크스페이스 경로 모두 확인
    paths = [
        font_name,
        os.path.join(os.path.dirname(sys.argv[0]), font_name),
        os.path.join(os.getcwd(), font_name),
        '/data/data/org.test.toopenapp/files/app/font.ttf' # 안드로이드 강제 경로
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

# --- 안드로이드 권한 요청 (사진 기능 필수) ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 제목
        layout.add_widget(Label(text="[PT1 캐릭터 관리]", font_size='28sp', bold=True, size_hint_y=0.1, font_name=DEFAULT_FONT, color=(1, 1, 1, 1)))
        
        # 검색 기능
        search_box = BoxLayout(size_hint_y=0.1, spacing=5)
        self.search_input = TextInput(hint_text="계정 이름 검색", multiline=False, font_name=DEFAULT_FONT)
        btn_search = Button(text="검색", size_hint_x=0.2, font_name=DEFAULT_FONT)
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        layout.add_widget(search_box)

        # 계정 추가 버튼 (손가락 터치 편하게 크게 설정)
        btn_add = Button(text="+ 새 계정 추가", size_hint_y=None, height=140, font_name=DEFAULT_FONT, background_color=(0.1, 0.6, 0.3, 1))
        btn_add.bind(on_release=self.add_account)
        layout.add_widget(btn_add)

        # 계정 리스트 (스크롤)
        self.acc_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.acc_list.bind(minimum_height=self.acc_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.acc_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh()

    def refresh(self):
        self.acc_list.clear_widgets()
        for k in store.keys():
            btn = Button(text=f"계정: {k}", size_hint_y=None, height=130, font_name=DEFAULT_FONT)
            btn.bind(on_release=lambda x, key=k: self.select_acc(key))
            self.acc_list.add_widget(btn)

    def add_account(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = TextInput(hint_text="계정 이름", multiline=False, font_name=DEFAULT_FONT)
        btn = Button(text="저장", size_hint_y=None, height=100, font_name=DEFAULT_FONT)
        content.add_widget(inp); content.add_widget(btn)
        pop = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        def save_acc(x):
            if inp.text:
                # 6개 슬롯 초기화
                store.put(inp.text, chars={str(i): {"name": f"슬롯 {i}"} for i in range(1, 7)})
                self.refresh(); pop.dismiss()
        btn.bind(on_release=save_acc); pop.open()

    def select_acc(self, key):
        self.manager.current_acc = key
        self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
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
            btn = Button(text=f"{i}. {c_data.get('name')}", size_hint_y=None, height=150, font_name=DEFAULT_FONT)
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        # 하단 버튼
        btn_back = Button(text="뒤로가기", size_hint_y=None, height=120, background_color=(0.5, 0.5, 0.5, 1), font_name=DEFAULT_FONT)
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.current_idx = str(idx)
        self.manager.current = 'detail'

    def delete_account(self, *args):
        # 계정 삭제 확인 팝업 (무료 사용 원칙 준수)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f" 정말 '{self.manager.current_acc}' 계정을\n 삭제하시겠습니까?", font_name=DEFAULT_FONT, halign='center'))
        b_box = BoxLayout(spacing=10); btn_y = Button(text="예", font_name=DEFAULT_FONT); btn_n = Button(text="아니오", font_name=DEFAULT_FONT)
        b_box.add_widget(btn_y); b_box.add_widget(btn_n); content.add_widget(b_box)
        pop = Popup(title="계정 삭제 확인", content=content, size_hint=(0.8, 0.5))
        def confirm_del(x):
            store.delete(self.manager.current_acc)
            pop.dismiss(); self.manager.current = 'main'
        btn_y.bind(on_release=confirm_del); btn_n.bind(on_release=pop.dismiss); pop.open()

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.current_idx
        # 데이터가 없을 경우 초기화 (튕김 방지)
        if not store.exists(acc): self.manager.current = 'main'; return
        acc_data = store.get(acc)
        self.data = acc_data['chars'].get(idx, {})
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 캐릭터 사진 (크기 확대)
        self.img = Image(source=self.data.get('img', ''), size_hint_y=None, height=500, allow_stretch=True)
        layout.add_widget(self.img)
        
        # 1번 사진 수정 / 2번 인벤토리 버튼 (크기 확대 및 디자인 개선)
        b_img_box = BoxLayout(size_hint_y=None, height=130, spacing=10)
        btn_img = Button(text="📷 사진 등록/수정", font_name=DEFAULT_FONT, background_color=(0.2, 0.2, 0.2, 1))
        btn_img.bind(on_release=self.pick_img) # 반응하도록 연동 완료
        btn_inven = Button(text="👜 인벤토리", font_name=DEFAULT_FONT, background_color=(0.6, 0.4, 0.2, 1))
        btn_inven.bind(on_release=self.go_inven) # 튕기지 않도록 연동 완료
        b_img_box.add_widget(btn_img); b_img_box.add_widget(btn_inven)
        layout.add_widget(b_img_box)

        # 세부 항목 입력 (암릿 포함)
        self.fields = {}
        items = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀"]
        for f in items:
            row = BoxLayout(size_hint_y=None, height=80, spacing=5)
            row.add_widget(Label(text=f, size_hint_x=0.3, font_name=DEFAULT_FONT, color=(0.8, 0.8, 0.8, 1)))
            ti = TextInput(text=str(self.data.get(f, '')), multiline=False, font_name=DEFAULT_FONT)
            self.fields[f] = ti; row.add_widget(ti); layout.add_widget(row)

        # 저장/삭제 버튼
        b_row = BoxLayout(size_hint_y=None, height=120, spacing=15)
        btn_save = Button(text="저장", background_color=(0.1, 0.6, 0.3, 1), font_name=DEFAULT_FONT)
        btn_save.bind(on_release=self.save)
        btn_del = Button(text="캐릭터 초기화", background_color=(0.8, 0.2, 0.2, 1), font_name=DEFAULT_FONT)
        btn_del.bind(on_release=self.delete)
        b_row.add_widget(btn_save); b_row.add_widget(btn_del); layout.add_widget(b_row)
        
        # 뒤로가기
        btn_back = Button(text="뒤로가기", size_hint_y=None, height=120, background_color=(0.5, 0.5, 0.5, 1), font_name=DEFAULT_FONT)
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        layout.add_widget(btn_back)
        
        scroll.add_widget(layout); self.add_widget(scroll)

    def pick_img(self, *args):
        # 1번 버튼 무반응 해결: 핸드폰 갤러리로 연결
        fc = FileChooserIconView(path='/sdcard') # 안드로이드 기본 경로
        btn = Button(text="선택완료", size_hint_y=0.15, font_name=DEFAULT_FONT, background_color=(0.1, 0.4, 0.8, 1))
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택 (허용 필요)", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def go_inven(self, *args):
        # 2번 버튼 튕김 해결: 안전하게 인벤토리 화면으로 이동
        self.manager.current = 'inventory'

    def save(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        new_d = {f: ti.text for f, ti in self.fields.items()}
        new_d['img'] = self.img.source
        # 기존 인벤토리 데이터 유지
        if 'inventory' in self.data: new_d['inventory'] = self.data['inventory']
        acc_data['chars'][idx] = new_d
        store.put(acc, **acc_data)
        self.manager.current = 'char_select'

    def delete(self, *args):
        def confirm_reset(x):
            acc, idx = self.manager.current_acc, self.manager.current_idx
            acc_data = store.get(acc)
            acc_data['chars'][idx] = {"name": "비었음"}
            store.put(acc, **acc_data); pop.dismiss(); self.manager.current = 'char_select'

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
        # 인벤토리 데이터 안전하게 불러오기 (튕김 방지)
        self.inven_text = char_data.get('inventory', '')
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        c_name = char_data.get('이름', '알수없음')
        layout.add_widget(Label(text=f"[{c_name}] 인벤토리", font_size='22sp', size_hint_y=0.1, font_name=DEFAULT_FONT, color=(1, 1, 1, 1)))
        
        self.ti_inven = TextInput(text=self.inven_text, multiline=True, font_name=DEFAULT_FONT, hint_text="인벤토리 내용을 입력하세요")
        layout.add_widget(self.ti_inven)
        
        b_row = BoxLayout(size_hint_y=None, height=130, spacing=15)
        btn_save = Button(text="저장", background_color=(0.1, 0.6, 0.3, 1), font_name=DEFAULT_FONT)
        btn_save.bind(on_release=self.save_inven)
        btn_back = Button(text="뒤로", background_color=(0.5, 0.5, 0.5, 1), font_name=DEFAULT_FONT)
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        b_row.add_widget(btn_save); b_row.add_widget(btn_back)
        layout.add_widget(b_row)
        self.add_widget(layout)

    def save_inven(self, *args):
        acc, idx = self.manager.current_acc, self.manager.current_idx
        acc_data = store.get(acc)
        # 인벤토리 데이터 저장 완료
        acc_data['chars'][idx]['inventory'] = self.ti_inven.text
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
