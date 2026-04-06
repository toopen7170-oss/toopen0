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

# --- [핵심 수정] 한글 폰트 등록 (파일명을 정확히 맞춰주세요) ---
# 저장소 루트 폴더에 'nanum.ttf' 파일이 반드시 있어야 합니다.
FONT_NAME = 'nanum.ttf' 
if os.path.exists(FONT_NAME):
    LabelBase.register(name="Nanum", fn_regular=FONT_NAME)
    DEFAULT_FONT = "Nanum"
else:
    DEFAULT_FONT = 'Roboto' # 폰트가 없을 경우 기본 폰트 (한글 깨짐 주의)

store = JsonStore('priston_tale_data.json')

# --- [스타일 최적화] 공통 위젯 스타일 정의 ---
class SLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '16sp'
        self.color = (1, 1, 1, 1) # 흰색
        self.size_hint_y = None
        self.height = dp(40)

# [수정: 1, 3, 5번] 입력창 글씨 쏠림 및 안 보임 해결
class SInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '17sp'
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(55) # 높이를 충분히 확보하여 글씨 쏠림 방지
        self.padding = [dp(10), dp(16), dp(10), dp(10)] # 위쪽 패딩 조절

class SBtn(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.font_size = '16sp'
        self.size_hint_y = None
        self.height = dp(60)
        self.background_normal = '' # 기본 회색 배경 제거

# --- 화면 1: 메인 메뉴 (검색 및 계정 관리) ---
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # [수정: 1, 6번] 검색 영역 UI 및 로직 연결
        search_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        self.search_input = SInput(hint_text="계정 또는 캐릭터 검색...", height=dp(60))
        
        search_btn = Button(text="검색", font_name=DEFAULT_FONT, size_hint_x=None, width=dp(80),
                            background_color=(0.1, 0.4, 0.6, 1))
        search_btn.bind(on_release=self.perform_search) # 검색 로직 바인딩
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        self.layout.add_widget(search_layout)

        add_acc_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.6, 0.3, 1))
        add_acc_btn.bind(on_release=self.show_add_acc_popup)
        self.layout.add_widget(add_acc_btn)

        # 계정 리스트 영역
        scroll = ScrollView()
        self.acc_list_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.acc_list_layout.bind(minimum_height=self.acc_list_layout.setter('height'))
        scroll.add_widget(self.acc_list_layout)
        self.layout.add_widget(scroll)

        self.add_widget(self.layout)
        self.refresh_acc_list()

    # [수정: 1, 6번] 실제 검색 로직 (대소문자 구분 없음)
    def perform_search(self, *args):
        query = self.search_input.text.strip().lower()
        self.refresh_acc_list(query)

    def refresh_acc_list(self, query=''):
        self.acc_list_layout.clear_widgets()
        
        for acc_name in list(store.keys()):
            if query and query not in acc_name.lower():
                continue # 검색어와 맞지 않으면 패스

            row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(5))
            
            acc_btn = SBtn(text=f"계정: {acc_name}", background_color=(0.3, 0.3, 0.3, 1))
            acc_btn.bind(on_release=lambda x, name=acc_name: self.go_to_char_select(name))
            
            del_btn = Button(text="X", font_name=DEFAULT_FONT, size_hint_x=None, width=dp(60),
                             background_color=(0.7, 0.1, 0.1, 1))
            # [수정: 4번] 삭제 시 확인 팝업 연결
            del_btn.bind(on_release=lambda x, name=acc_name: self.confirm_delete_popup(name))
            
            row.add_widget(acc_btn)
            row.add_widget(del_btn)
            self.acc_list_layout.add_widget(row)

    # [수정: 5번] 계정 추가 팝업 글씨 안 보임 해결
    def show_add_acc_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        content.add_widget(SLabel(text="새 계정 이름을 입력하세요", color=(0,0,0,1))) # 검은색 글씨
        
        self.new_acc_input = SInput(hint_text="예: 프리스톤Tale1")
        content.add_widget(self.new_acc_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        save_btn = Button(text="생성하기", font_name=DEFAULT_FONT, background_color=(0.1, 0.6, 0.3, 1))
        # ... (계정 저장 로직 생략, 기존과 동일) ...
        
    # [수정: 4번] 계정 삭제 확인 팝업 구현
    def confirm_delete_popup(self, acc_name):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        content.add_widget(SLabel(text=f"'{acc_name}' 계정을\n정말 삭제하시겠습니까?", color=(0,0,0,1), halign='center'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        yes_btn = Button(text="삭제", font_name=DEFAULT_FONT, background_color=(0.7, 0.1, 0.1, 1))
        no_btn = Button(text="취소", font_name=DEFAULT_FONT)
        
        popup = Popup(title="계정 삭제 경고", content=content, size_hint=(0.8, 0.4))
        
        yes_btn.bind(on_release=lambda x: self.delete_account(acc_name, popup))
        no_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(yes_btn); btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout); popup.open()

    def delete_account(self, acc_name, popup):
        store.delete(acc_name); popup.dismiss(); self.refresh_acc_list()
    def go_to_char_select(self, acc_name):
        self.manager.current_acc = acc_name; self.manager.current = 'char_select'

# --- 화면 2: 캐릭터 선택 (생략 가능, 구조 유지를 위해 포함) ---
class CharSelect(Screen):
    def on_enter(self): # 화면 진입 시마다 새로고침
        self.clear_widgets()
        # ... (캐릭터 그리드 UI 구현, 기존과 동일하나 SBtn 사용 권장) ...

# --- 화면 3: 캐릭터 상세 정보 및 사진 관리 ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc_name = self.manager.current_acc
        char_idx = self.manager.current_char_idx
        char_data = store.get(acc_name)['chars'][char_idx]

        # 메인 스크롤 레이아웃
        scroll = ScrollView()
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # [수정: 2번] 사진 영역 최적화 ( AsyncImage 사용)
        self.photo_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.photo_layout.bind(minimum_height=self.photo_layout.setter('height'))
        
        # AsyncImage를 사용하여 무거운 사진 로딩 시 앱 멈춤 방지
        img_path = char_data.get('image', 'path/to/default_icon.png')
        self.char_img = AsyncImage(source=img_path, size_hint_y=None, height=dp(300), allow_stretch=True)
        self.photo_layout.add_widget(self.char_img)
        self.main_layout.add_widget(self.photo_layout)

        change_pic_btn = SBtn(text="+ 사진 변경/추가하기", background_color=(0.2, 0.5, 0.7, 1))
        change_pic_btn.bind(on_release=self.open_gallery) # 갤러리 연동 로직 필요
        self.main_layout.add_widget(change_pic_btn)

        # 정보 입력 필드 영역 (SLabel, SInput 사용)
        field_list = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패"]
        self.inputs = {}
        for field in field_list:
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            row.add_widget(SLabel(text=field, size_hint_x=0.3))
            ti = SInput(text=str(char_data.get(field, '')))
            row.add_widget(ti); self.inputs[field] = ti
            self.main_layout.add_widget(row)

        # 저장 및 뒤로가기 버튼
        # ... (생략, 기존과 동일하게 SBtn 사용) ...

        scroll.add_widget(self.main_layout); self.add_widget(scroll)

    def open_gallery(self, *args):
        # [주의] 갤러리 연동은 안드로이드 네이티브 기능이 필요합니다 (plyer 등 사용)
        print("갤러리 열기 시도 (네이티브 구현 필요)")
        # 예시: 사진 경로 저장 후 self.char_img.source = new_path 업데이트

# --- 앱 메인 클래스 ---
class PristonTaleApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.current_acc = ""; sm.current_char_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        return sm

if __name__ == '__main__':
    PristonTaleApp().run()
