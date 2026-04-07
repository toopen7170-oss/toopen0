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
from kivy.core.window import Window

# --- [핵심 수정] 사용자님의 파일명 'font.ttf'에 맞춤 ---
FONT_NAME = 'font.ttf' 
if os.path.exists(FONT_NAME):
    LabelBase.register(name="KFont", fn_regular=FONT_NAME)
    DEFAULT_FONT = "KFont"
else:
    DEFAULT_FONT = 'Roboto' # 폰트가 없을 경우 기본 폰트

# 데이터 저장소
store = JsonStore('priston_tale_data.json')

# --- [스타일 최적화] 안드로이드 터치 및 한글 최적화 ---
class SLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '16sp'
        self.size_hint_y = None
        self.height = dp(45)

class SInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '18sp'
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(60) # 높이를 키워 글씨 쏠림 방지
        self.padding = [dp(10), dp(15), dp(10), dp(10)] # 안드로이드 입력창 최적화
        self.hint_text_color = (0.5, 0.5, 0.5, 1)

class SBtn(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '18sp'
        self.size_hint_y = None
        self.height = dp(65) # 안드로이드에서 누르기 편한 크기
        self.background_normal = '' 

# --- 화면 1: 메인 메뉴 ---
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 검색 영역
        search_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        self.search_input = SInput(hint_text="계정 또는 캐릭터 검색...")
        
        search_btn = Button(text="검색", font_name=DEFAULT_FONT, size_hint_x=None, width=dp(90),
                            background_color=(0.1, 0.3, 0.5, 1))
        search_btn.bind(on_release=self.perform_search)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        self.layout.add_widget(search_layout)

        # 새 계정 버튼
        add_acc_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.5, 0.3, 1))
        add_acc_btn.bind(on_release=self.show_add_acc_popup)
        self.layout.add_widget(add_acc_btn)

        # 계정 리스트 영역
        scroll = ScrollView()
        self.acc_list_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.acc_list_layout.bind(minimum_height=self.acc_list_layout.setter('height'))
        scroll.add_widget(self.acc_list_layout)
        self.layout.add_widget(scroll)

        self.add_widget(self.layout)
        self.refresh_acc_list()

    def perform_search(self, *args):
        query = self.search_input.text.strip().lower()
        self.refresh_acc_list(query)

    def refresh_acc_list(self, query=''):
        self.acc_list_layout.clear_widgets()
        for acc_name in list(store.keys()):
            if query and query not in acc_name.lower():
                continue

            row = BoxLayout(size_hint_y=None, height=dp(75), spacing=dp(5))
            acc_btn = SBtn(text=f"계정: {acc_name}", background_color=(0.2, 0.2, 0.2, 1))
            acc_btn.bind(on_release=lambda x, name=acc_name: self.go_to_detail(name))
            
            del_btn = Button(text="삭제", font_name=DEFAULT_FONT, size_hint_x=None, width=dp(80),
                             background_color=(0.6, 0.1, 0.1, 1))
            del_btn.bind(on_release=lambda x, name=acc_name: self.delete_account(name))
            
            row.add_widget(acc_btn)
            row.add_widget(del_btn)
            self.acc_list_layout.add_widget(row)

    def show_add_acc_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(SLabel(text="새 계정 이름을 입력하세요"))
        self.new_acc_input = SInput(hint_text="계정명 입력")
        content.add_widget(self.new_acc_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        save_btn = SBtn(text="생성", background_color=(0.1, 0.5, 0.3, 1))
        cancel_btn = SBtn(text="취소")
        btn_layout.add_widget(save_btn); btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="계정 추가", content=content, size_hint=(0.9, 0.5))
        save_btn.bind(on_release=lambda x: self.save_account(popup))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def save_account(self, popup):
        name = self.new_acc_input.text.strip()
        if name:
            store.put(name, chars=[{}])
            self.refresh_acc_list()
            popup.dismiss()

    def delete_account(self, name):
        store.delete(name)
        self.refresh_acc_list()

    def go_to_detail(self, acc_name):
        self.manager.current_acc = acc_name
        self.manager.current = 'detail'

# --- 화면 2: 캐릭터 상세 정보 ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc_name = self.manager.current_acc
        char_data = store.get(acc_name)['chars'][0] if store.exists(acc_name) else {}

        scroll = ScrollView()
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # 제목
        self.main_layout.add_widget(SLabel(text=f"[{acc_name}] 인벤토리 편집", font_size='20sp'))

        # 입력 필드들
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패"]
        self.inputs = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            row.add_widget(SLabel(text=f, size_hint_x=0.3))
            ti = SInput(text=str(char_data.get(f, '')))
            row.add_widget(ti)
            self.inputs[f] = ti
            self.main_layout.add_widget(row)

        # 저장 및 돌아가기 버튼
        btn_row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10))
        save_btn = SBtn(text="저장하기", background_color=(0.1, 0.4, 0.6, 1))
        back_btn = SBtn(text="뒤로가기", background_color=(0.3, 0.3, 0.3, 1))
        
        save_btn.bind(on_release=self.save_data)
        back_btn.bind(on_release=self.go_back)
        
        btn_row.add_widget(save_btn); btn_row.add_widget(back_btn)
        self.main_layout.add_widget(btn_row)

        scroll.add_widget(self.main_layout)
        self.add_widget(scroll)

    def save_data(self, *args):
        acc_name = self.manager.current_acc
        new_data = {f: self.inputs[f].text for f in self.inputs}
        store.put(acc_name, chars=[new_data])
        self.go_back()

    def go_back(self, *args):
        self.manager.current = 'main'

class PT1App(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.current_acc = ""
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(Detail(name='detail'))
        return sm

if __name__ == '__main__':
    PT1App().run()
