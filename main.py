# ... (기본 설정 및 DataManager 클래스는 이전과 동일) ...

class CharacterSelectScreen(BackgroundScreen):
    """[toopen] 캐릭터 선택 화면 구현 (4단계로 가기 전 필수 관문)"""
    def on_pre_enter(self):
        self.data = DataManager.load()
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        f = safe_font()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # 상단 타이틀: [계정명] 캐릭터 선택
        account_name = self.data.get("account_id", "toopen")
        title = Label(
            text=f"[{account_name}] 캐릭터 선택", 
            font_name=f, 
            size_hint_y=None, 
            height=150, 
            font_size='24sp'
        )
        layout.add_widget(title)

        # 캐릭터 6개 그리드 배치 (사진과 동일한 2열 구성)
        grid = GridLayout(cols=2, spacing=15, padding=10)
        
        # 1번부터 6번 캐릭터 버튼 생성
        for i in range(1, 7):
            char_key = f"char_{i}_name"
            # 저장된 이름이 있으면 표시, 없으면 'n번 캐릭터'로 표시
            display_name = self.data.get(char_key, f"{i}번 캐릭터")
            
            btn = Button(
                text=display_name,
                font_name=f,
                background_normal='', # 배경색 적용을 위해 초기화
                background_color=(0.1, 0.15, 0.2, 0.9), # 어두운 네이비 톤 (사진 느낌)
                font_size='18sp'
            )
            # 버튼 클릭 시 해당 캐릭터의 세부 정보 화면으로 이동 (캐릭터 번호 전달)
            btn.bind(on_release=lambda x, idx=i: self.select_character(idx))
            grid.add_widget(btn)
            
        layout.add_widget(grid)

        # 하단 취소/뒤로가기 버튼
        bottom_btn = Button(
            text="취소", 
            font_name=f, 
            size_hint_y=None, 
            height=120,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        bottom_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'account_manager'))
        layout.add_widget(bottom_btn)

        self.add_widget(layout)

    def select_character(self, index):
        # 현재 선택된 캐릭터 번호를 임시 저장하고 세부 화면으로 이동
        self.app = App.get_running_app()
        self.app.selected_char_index = index 
        self.manager.current = 'detail'

# App 클래스의 build 부분에 화면 등록 추가
class PT1App(App):
    selected_char_index = 1 # 기본값

    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        # ... 다른 화면들 ...
        sm.add_widget(CharacterSelectScreen(name='char_select'))
        sm.add_widget(CharDetailScreen(name='detail'))
        return sm
