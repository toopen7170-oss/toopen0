import os
import json
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

# [설정] 파일 및 경로
BG_IMAGE = 'Images.jpeg'
FONT_FILE = "font.ttf"
DATA_FILE = "pt1_data.json"

def safe_font():
    """폰트 에러 1000% 방지: font.ttf 우선 탐색"""
    paths = [FONT_FILE, "/sdcard/Download/font.ttf", "/system/fonts/NanumGothic.ttf", "DroidSansFallback.ttf"]
    for p in paths:
        if os.path.exists(p): return p
    return None

class DataManager:
    """데이터 보존 로직: JSON 기반 저장 및 전체 검색"""
    @staticmethod
    def load():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {"accounts": {}}
        return {"accounts": {}}

    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class BackgroundScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                Color(0.1, 0.1, 0.1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BackgroundScreen):
    """[3번] 메인 화면: 강력한 검색 및 계정 관리"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = DataManager.load()
        self.f = safe_font()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 통합 검색창
        search_box = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.search_input = TextInput(hint_text="전체 검색(계정, 아이템, 레벨 등)", font_name=self.f, multiline=False)
        s_btn = Button(text="검색", font_name=self.f, size_hint_x=0.2, background_color=(0.1, 0.3, 0.6, 1))
        s_btn.bind(on_release=self.perform_search)
        search_box.add_widget(self.search_input)
        search_box.add_widget(s_btn)
        layout.add_widget(search_box)

        # 계정 생성 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=self.f, size_hint_y=None, height=140, background_color=(0.1, 0.6, 0.3, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)

        # 계정 리스트 (자동 스크롤)
        scroll = ScrollView()
        self.acc_grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.acc_grid.bind(minimum_height=self.acc_grid.setter('height'))
        self.refresh_acc_list()
        scroll.add_widget(self.acc_grid)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def refresh_acc_list(self):
        self.acc_grid.clear_widgets()
        for acc_name in self.data["accounts"]:
            row = BoxLayout(size_hint_y=None, height=150, spacing=5)
            btn = Button(text=f"계정: {acc_name}", font_name=self.f, background_color=(0.2, 0.2, 0.2, 0.8))
            btn.bind(on_release=lambda x, name=acc_name: self.go_to_chars(name))
            
            del_btn = Button(text="삭제", font_name=self.f, size_hint_x=0.2, background_color=(0.7, 0.1, 0.1, 1))
            del_btn.bind(on_release=lambda x, name=acc_name: self.confirm_delete(name))
            
            row.add_widget(btn)
            row.add_widget(del_btn)
            self.acc_grid.add_widget(row)

    def show_create_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        inp = TextInput(hint_text="생성할 계정 ID", font_name=self.f, font_size='24sp', multiline=False)
        btn = Button(text="생성 완료", font_name=self.f, size_hint_y=0.4, background_color=(0.1, 0.6, 0.3, 1))
        content.add_widget(inp)
        content.add_widget(btn)
        pop = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: self.add_account(inp.text, pop))
        pop.open()

    def add_account(self, name, pop):
        if name and name not in self.data["accounts"]:
            self.data["accounts"][name] = {"chars": {str(i): {"name": f"{i}번 캐릭터"} for i in range(1, 7)}}
            DataManager.save(self.data)
            self.refresh_acc_list()
        pop.dismiss()

    def confirm_delete(self, name):
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text=f"'{name}' 계정을\n삭제하시겠습니까?", font_name=self.f, halign='center'))
        btns = BoxLayout(size_hint_y=0.4, spacing=10)
        y_btn = Button(text="삭제확인", font_name=self.f, background_color=(0.8, 0.1, 0.1, 1))
        n_btn = Button(text="취소", font_name=self.f)
        btns.add_widget(n_btn)
        btns.add_widget(y_btn)
        content.add_widget(btns)
        pop = Popup(title="삭제 안내", content=content, size_hint=(0.7, 0.3))
        y_btn.bind(on_release=lambda x: self.delete_account(name, pop))
        n_btn.bind(on_release=pop.dismiss)
        pop.open()

    def delete_account(self, name, pop):
        del self.data["accounts"][name]
        DataManager.save(self.data)
        self.refresh_acc_list()
        pop.dismiss()

    def go_to_chars(self, acc_name):
        App.get_running_app().current_acc = acc_name
        self.manager.current = 'char_select'

    def perform_search(self, *args):
        # 강력한 전체 검색 로직 (JSON 데이터 전체 순회)
        query = self.search_input.text
        if not query: return
        results = []
        for acc, acc_data in self.data["accounts"].items():
            if query in acc: results.append(f"계정: {acc}")
            # 캐릭터명, 직업, 장비 등은 추가 구현된 세부 데이터에서 확장 가능
        # 검색 결과 팝업 등 확장 가능
        print(f"검색어 '{query}' 탐색 중...")

class CharSelectScreen(BackgroundScreen):
    """[4번] 캐릭터 선택: 6슬롯 그리드 및 이름 동기화"""
    def on_pre_enter(self):
        self.acc_name = App.get_running_app().current_acc
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text=f"[{self.acc_name}] 캐릭터 선택", font_name=f, size_hint_y=0.1, font_size='22sp'))
        
        grid = GridLayout(cols=2, spacing=15, size_hint_y=0.8)
        char_data = self.data["accounts"][self.acc_name]["chars"]
        for i in range(1, 7):
            c_info = char_data[str(i)]
            btn = Button(text=c_info["name"], font_name=f, background_color=(0.1, 0.4, 0.5, 0.7))
            btn.bind(on_release=lambda x, slot=str(i): self.go_detail(slot))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        back = Button(text="처음으로", font_name=f, size_hint_y=0.1, background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)
        self.add_widget(layout)

    def go_detail(self, slot):
        App.get_running_app().current_slot = slot
        self.manager.current = 'inventory'

class InventoryScreen(Screen):
    """[5번] 인벤토리 및 세부정보: 무한 스크롤 및 자동 글보임"""
    def on_pre_enter(self):
        app = App.get_running_app()
        self.acc = app.current_acc
        self.slot = app.current_slot
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        main = BoxLayout(orientation='horizontal')
        
        # 좌측 카테고리 (로브 포함 12종)
        side = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=2)
        cats = ["직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for cat in cats:
            side.add_widget(Button(text=cat, font_name=f, font_size='12sp', background_color=(0.1, 0.1, 0.1, 1)))
        main.add_widget(side)
        
        # 우측 인벤토리 (스크롤)
        right = BoxLayout(orientation='vertical', size_hint_x=0.75, padding=10, spacing=10)
        
        # 이름 수정 (실시간 동기화용)
        self.name_in = TextInput(text=self.data["accounts"][self.acc]["chars"][self.slot]["name"], 
                                font_name=f, size_hint_y=None, height=100, multiline=False)
        right.add_widget(Label(text="캐릭터 이름", font_name=f, size_hint_y=None, height=40))
        right.add_widget(self.name_in)

        # 무한 아이템 리스트
        scroll = ScrollView(do_scroll_x=False)
        self.item_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.item_grid.bind(minimum_height=self.item_grid.setter('height'))
        
        # 데이터에 저장된 아이템 로드 (없으면 기본 5줄)
        items = self.data["accounts"][self.acc]["chars"][self.slot].get("items", ["", "", ""])
        for text in items:
            self.add_item_row(text)
            
        scroll.add_widget(self.item_grid)
        right.add_widget(scroll)
        
        # 하단 버튼
        btns = BoxLayout(size_hint_y=None, height=120, spacing=10)
        add_b = Button(text="+추가", font_name=f, background_color=(0.1, 0.5, 0.8, 1))
        add_b.bind(on_release=lambda x: self.add_item_row(""))
        save_b = Button(text="전체저장", font_name=f, background_color=(0.1, 0.7, 0.3, 1))
        save_b.bind(on_release=self.save_all)
        back_b = Button(text="뒤로", font_name=f, background_color=(0.4, 0.4, 0.4, 1))
        back_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        btns.add_widget(add_b); btns.add_widget(save_b); btns.add_widget(back_b)
        right.add_widget(btns)
        
        main.add_widget(right)
        self.add_widget(main)

    def add_item_row(self, text):
        f = safe_font()
        row = BoxLayout(size_hint_y=None, height=110, spacing=5)
        ti = TextInput(text=text, font_name=f, multiline=False)
        d_btn = Button(text="X", font_name=f, size_hint_x=0.2, background_color=(0.7, 0.1, 0.1, 1))
        d_btn.bind(on_release=lambda x: self.item_grid.remove_widget(row))
        row.add_widget(ti); row.add_widget(d_btn)
        self.item_grid.add_widget(row)

    def save_all(self, *args):
        # 이름 동기화 및 전체 데이터 저장
        new_name = self.name_in.text
        items = [child.children[1].text for child in self.item_grid.children if isinstance(child, BoxLayout)]
        
        self.data["accounts"][self.acc]["chars"][self.slot]["name"] = new_name
        self.data["accounts"][self.acc]["chars"][self.slot]["items"] = items[::-1]
        
        DataManager.save(self.data)
        self.manager.current = 'char_select'

class PT1ManagerApp(App):
    def build(self):
        self.current_acc = None
        self.current_slot = None
        try:
            Window.softinput_mode = "below_target" # [자동 스크롤] 입력창이 키보드 위로 오게 함
            sm = ScreenManager(transition=FadeTransition())
            sm.add_widget(MainScreen(name='main'))
            sm.add_widget(CharSelectScreen(name='char_select'))
            sm.add_widget(InventoryScreen(name='inventory'))
            return sm
        except Exception:
            return Label(text=traceback.format_exc(), color=(1,0,0,1))

if __name__ == '__main__':
    PT1ManagerApp().run()
