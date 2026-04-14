import os
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.text import LabelBase

# [전수검사 1] S26 울트라 터치 프리징 및 키보드 간섭 방지 설정
Window.softinput_mode = 'pan'

# [전수검사 2] 리소스 경로 및 폰트 등록 무결성 확보
FONT_PATH = os.path.join(os.path.dirname(__file__), 'font.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name="CustomFont", fn_regular=FONT_PATH)

def get_data_path():
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'Pristontale.json')
    return 'Pristontale.json'

class DataManager:
    @staticmethod
    def load():
        path = get_data_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"accounts": []}

    @staticmethod
    def save(data):
        with open(get_data_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# [전수검사 3] 사진 디자인(초록색 테마) 및 검색바 레이아웃 반영
KV = '''
<StyledButton@Button>:
    font_name: "CustomFont" if app.font_exists else "Roboto"
    background_normal: ''
    background_color: (0, 0.3, 0.1, 1)  # 사진 속 진한 초록색
    size_hint_y: None
    height: '50dp'

<MainScreen>:
    canvas.before:
        Rectangle:
            source: 'bg.png'
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        # 상단 타이틀 및 검색바 (사진 반영)
        Label:
            text: "PristonTale"
            font_name: "CustomFont" if app.font_exists else "Roboto"
            font_size: '28sp'
            size_hint_y: None
            height: '60dp'
            color: (1, 1, 1, 1)

        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: 5
            TextInput:
                id: search_input
                hint_text: "전체 검색(계정, 아이템 등)"
                multiline: False
                background_color: (0.1, 0.1, 0.1, 0.8)
                foreground_color: (1, 1, 1, 1)
                on_text: root.filter_accounts(self.text)
            Button:
                text: "검색"
                size_hint_x: 0.2
                background_color: (0, 0.1, 0.2, 1)

        StyledButton:
            text: "+ 새 계정 만들기"
            on_release: root.show_add_popup()
            
        ScrollView:
            id: scroll_view
            BoxLayout:
                id: account_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 8

        StyledButton:
            text: "데이터 저장"
            on_release: app.save_all()

<AccountItem@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '65dp'
    padding: 10
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.6)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    Label:
        id: name_label
        text: ""
        font_name: "CustomFont" if app.font_exists else "Roboto"
        halign: 'left'
        text_size: self.size
    Button:
        text: "상세"
        size_hint_x: 0.2
        on_release: app.go_detail(root.account_data)
    Button:
        text: "삭제"
        size_hint_x: 0.2
        background_color: (0.8, 0.1, 0.1, 1)
        on_release: app.delete_account(root.account_data)
'''

class MainScreen(Screen):
    def show_add_popup(self):
        # [전수검사 4] 팝업 디자인 및 프리징 방지 로직 (사진 반영)
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.txt_input = TextInput(
            hint_text="생성할 계정 ID", 
            multiline=False, 
            font_size='18sp',
            size_hint_y=None,
            height='60dp'
        )
        
        add_btn = Button(
            text="생성 완료", 
            background_normal='', 
            background_color=(0, 0.3, 0.1, 1),
            size_hint_y=None,
            height='50dp'
        )
        
        content.add_widget(self.txt_input)
        content.add_widget(add_btn)
        
        self.popup = Popup(title="계정 생성", content=content, size_hint=(0.8, 0.5))
        add_btn.bind(on_release=self.add_account_logic)
        self.popup.open()

    def add_account_logic(self, instance):
        name = self.txt_input.text.strip()
        if name:
            app = App.get_running_app()
            new_acc = {"name": name, "inventory": []}
            app.data["accounts"].append(new_acc)
            app.refresh_main_list()
            app.save_all()
            # [전수검사 5] 추가 후 하단 자동 스크롤
            Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
            self.popup.dismiss()

    def scroll_to_bottom(self):
        self.ids.scroll_view.scroll_y = 0

    def filter_accounts(self, query):
        app = App.get_running_app()
        self.refresh_filtered_list(query.lower())

    def refresh_filtered_list(self, query):
        layout = self.ids.account_list
        layout.clear_widgets()
        app = App.get_running_app()
        for acc in app.data["accounts"]:
            if query in acc["name"].lower():
                from kivy.factory import Factory
                item = Factory.AccountItem()
                item.ids.name_label.text = acc["name"]
                item.account_data = acc
                layout.add_widget(item)

class DetailScreen(Screen):
    current_acc = None

class PT1Manager(App):
    def build(self):
        self.font_exists = os.path.exists(FONT_PATH)
        self.data = DataManager.load()
        Builder.load_string(KV)
        
        self.sm = ScreenManager()
        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)
        
        self.refresh_main_list()
        return self.sm

    def refresh_main_list(self):
        layout = self.main_screen.ids.account_list
        layout.clear_widgets()
        for acc in self.data["accounts"]:
            from kivy.factory import Factory
            item = Factory.AccountItem()
            item.ids.name_label.text = acc["name"]
            item.account_data = acc
            layout.add_widget(item)

    def delete_account(self, acc_data):
        self.data["accounts"].remove(acc_data)
        self.refresh_main_list()
        self.save_all()

    def save_all(self):
        DataManager.save(self.data)

if __name__ == '__main__':
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    PT1Manager().run()
