import os
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

# [필독] 파일 설정 - 파일이 없어도 앱이 절대 튕기지 않게 안전장치 강화
BG_IMAGE = 'Images.jpeg'
FONT_FILE = "NanumGothic.ttf"

def safe_font():
    """폰트 파일이 실제 폴더 내에 존재할 때만 경로 반환 (튕김 방지)"""
    if os.path.exists(FONT_FILE):
        return FONT_FILE
    return None

class BackgroundScreen(Screen):
    """배경 이미지를 공통으로 사용하는 베이스 클래스"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                # 파일이 없으면 그냥 어두운 배경 처리
                Color(0.1, 0.1, 0.1, 1) 
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BackgroundScreen):
    """[1번, 5번] 메인 화면: 검색, 계정 생성, 계정 리스트"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 상단 타이틀
        layout.add_widget(Label(text="[PT1 통합 매니저]", font_size='28sp', font_name=f, size_hint_y=0.1))
        
        # 검색창
        search_box = BoxLayout(size_hint_y=0.08, spacing=5)
        search_box.add_widget(TextInput(hint_text="계정/캐릭터 검색...", font_name=f, multiline=False))
        search_box.add_widget(Button(text="검색", font_name=f, size_hint_x=0.2, background_color=(0.1, 0.2, 0.4, 1)))
        layout.add_widget(search_box)
        
        # 계정 생성 버튼
        create_btn = Button(text="+ 새 계정 만들기", font_name=f, size_hint_y=0.1, background_color=(0.1, 0.6, 0.3, 1))
        create_btn.bind(on_release=self.show_create_popup)
        layout.add_widget(create_btn)
        
        # 계정 리스트 (7번 삭제 기능 포함)
        self.acc_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        # 예시 데이터 추가 (뒤로가기 시 이 데이터가 유지되도록 하려면 데이터베이스가 필요합니다)
        self.add_account_row("계정: to", f)
        layout.add_widget(self.acc_list)
        
        layout.add_widget(Widget()) # 스페이서
        self.add_widget(layout)

    def add_account_row(self, name, f):
        row = BoxLayout(size_hint_y=None, height=60, spacing=5)
        btn = Button(text=name, font_name=f, background_color=(0.2, 0.2, 0.2, 0.8))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.5, 0.1, 0.1, 1))
        del_btn.bind(on_release=lambda x: self.confirm_delete(name, row, f))
        
        row.add_widget(btn)
        row.add_widget(del_btn)
        self.acc_list.add_widget(row)

    def show_create_popup(self, *args):
        """[2번] 큰 입력창 팝업"""
        f = safe_font()
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        # ID 입력창을 더 크게 배치
        content.add_widget(TextInput(hint_text="ID 입력", font_name=f, font_size='22sp', size_hint_y=0.6))
        gen_btn = Button(text="생성", font_name=f, size_hint_y=0.4, background_color=(0.1, 0.5, 0.2, 1))
        content.add_widget(gen_btn)
        pop = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.4))
        gen_btn.bind(on_release=pop.dismiss)
        pop.open()

    def confirm_delete(self, name, row_widget, f):
        """[7번] 삭제 확인 멘트"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=20)
        content.add_widget(Label(text=f"'{name}'을 삭제할까요?", font_name=f))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.4)
        no_b = Button(text="취소", font_name=f)
        yes_b = Button(text="확인", font_name=f, background_color=(0.6, 0.1, 0.1, 1))
        
        btn_layout.add_widget(no_b)
        btn_layout.add_widget(yes_b)
        content.add_widget(btn_layout)
        
        pop = Popup(title="삭제 확인", content=content, size_hint=(0.7, 0.3))
        # 확인 버튼 클릭 시에만 해당 리스트 삭제
        yes_b.bind(on_release=lambda x: (self.acc_list.remove_widget(row_widget), pop.dismiss()))
        no_b.bind(on_release=pop.dismiss)
        pop.open()

class CharSelectScreen(BackgroundScreen):
    """[3번, 6번] 캐릭터 선택창 (6개 슬롯 그리드)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="[to] 캐릭터 선택", font_name=f, size_hint_y=0.1))
        
        # 2열 3행 그리드
        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.7)
        for i in range(1, 7):
            btn = Button(text=f"슬롯 {i}", font_name=f, background_color=(0.3, 0.3, 0.6, 0.6))
            # 클릭 시 인벤토리 화면으로 이동
            btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
            grid.add_widget(btn)
        layout.add_widget(grid)
        
        # 처음으로 버튼
        back_btn = Button(text="처음으로", font_name=f, size_hint_y=0.1, background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

# [오류 해결] 드디어 인벤토리 화면 클래스 정의를 추가했습니다.
class InventoryScreen(Screen):
    """[4번] 인벤토리 화면: 왼쪽 카테고리, 오른쪽 무한 줄 추가 시스템"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = safe_font()
        # 전체 레이아웃 (수평 BoxLayout)
        main_layout = BoxLayout(orientation='horizontal')
        
        # 1. 왼쪽 카테고리 사이드 메뉴 (25% 비율)
        side_menu = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=1)
        categories = ["양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for cat in categories:
            # 카테고리 버튼
            side_menu.add_widget(Button(text=cat, font_name=f, background_color=(0, 0, 0, 1), font_size='12sp'))
        main_layout.add_widget(side_menu)
        
        # 2. 오른쪽 인벤토리 리스트 영역 (75% 비율)
        right_layout = BoxLayout(orientation='vertical', size_hint_x=0.75, padding=5)
        
        # 스크롤 뷰 내부에 그리드 레이아웃 배치
        scroll = ScrollView()
        self.item_grid = GridLayout(cols=1, size_hint_y=None, spacing=3)
        self.item_grid.bind(minimum_height=self.item_grid.setter('height'))
        
        # 초기 5줄 생성
        for _ in range(5): self.add_item_row(f)
        
        scroll.add_widget(self.item_grid)
        right_layout.add_widget(scroll)
        
        # 3. 하단 제어 버튼 영역
        bottom_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        # 줄 추가 버튼
        add_item_btn = Button(text="+ 추가", font_name=f, background_color=(0.1, 0.4, 0.7, 1))
        add_item_btn.bind(on_release=lambda x: self.add_item_row(f))
        
        # 뒤로가기 버튼
        back_btn = Button(text="뒤로", font_name=f, background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        
        bottom_layout.add_widget(add_item_btn)
        bottom_layout.add_widget(back_btn)
        right_layout.add_widget(bottom_layout)
        
        main_layout.add_widget(right_layout)
        self.add_widget(main_layout)

    def add_item_row(self, f):
        """[4번 핵심] 인벤토리에 무한 줄 추가: 입력창, 저장, 삭제 버튼 배치"""
        # 한 줄 BoxLayout (저장/삭제 버튼 포함)
        row = BoxLayout(size_hint_y=None, height=55, spacing=2)
        
        # 1. 입력창 (넓게)
        item_text = TextInput(font_name=f, multiline=False, size_hint_x=0.6)
        # 2. 저장 버튼
        save_btn = Button(text="저장", font_name=f, size_hint_x=0.2, background_color=(0.1, 0.5, 0.2, 1))
        # 3. 삭제 버튼
        del_btn = Button(text="삭제", font_name=f, size_hint_x=0.2, background_color=(0.6, 0.1, 0.1, 1))
        
        # 개별 삭제 기능 구현
        del_btn.bind(on_release=lambda x: self.item_grid.remove_widget(row))
        
        row.add_widget(item_text)
        row.add_widget(save_btn)
        row.add_widget(del_btn)
        
        self.item_grid.add_widget(row)

class PT1ManagerApp(App):
    """[1번] 앱 실행 클래스: 아이콘 및 화면 매니저 설정"""
    def build(self):
        try:
            # 아이콘 파일 존재 확인
            if os.path.exists(BG_IMAGE):
                self.icon = BG_IMAGE
            
            # 스크린 매니저 생성 (페이드 효과 추가)
            sm = ScreenManager(transition=FadeTransition())
            
            # [오류 해결 포인트] 172라인 근처의 에러는 InventoryScreen 클래스 정의가 없어서 발생했습니다.
            # 모든 화면 클래스 정의를 하나로 통합했습니다.
            sm.add_widget(MainScreen(name='main'))
            sm.add_widget(CharSelectScreen(name='char_select'))
            sm.add_widget(InventoryScreen(name='inventory')) # 드디어 추가되었습니다!
            
            return sm
            
        except Exception:
            # 혹시라도 또 에러가 나면 튕기지 않고 화면에 표시 (중요)
            # 이 화면이 보인다면 텍스트 내용을 캡처해서 알려주세요.
            err_log = traceback.format_exc()
            return Label(text=f"[Critical Error]\n\n{err_log}", color=(1,0,0,1))

if __name__ == '__main__':
    # 앱 실행
    PT1ManagerApp().run()
