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

# [전수검사] S26 울트라 프리징 방지 및 키보드 모드 설정
Window.softinput_mode = 'pan'

# 절대 경로를 통한 폰트 등록 (깨짐 방지)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_PATH, 'font.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name="CustomFont", fn_regular=FONT_PATH)

def get_data_path():
    if platform == 'android':
        from android.storage import app_storage_path
        path = os.path.join(app_storage_path(), 'Pristontale.json')
    else:
        path = os.path.join(BASE_PATH, 'Pristontale.json')
    return path

class DataManager:
    @staticmethod
    def load():
        path = get_data_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Load Error: {e}")
        return {"accounts": []}

    @staticmethod
    def save(data):
        path = get_data_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Save Error: {e}")
            return False

KV = '''
<StyledButton@Button>:
    font_name: "CustomFont" if app.font_exists else "Roboto"
    background_normal: ''
    background_color: (0, 0.3, 0.1, 1)  # 사진 속 진한 초록색
    size_hint_y: None
    height: '55dp'

<MainScreen>:
    canvas.before:
        Rectangle:
            source: 'bg.png'
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 12
        
        Label:
            text: "PristonTale"
            font_name: "CustomFont" if app.font_exists else "Roboto"
            font_size: '32sp'
            size_hint_y: None
            height: '70dp'

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 5
            TextInput:
                id: search_input
                hint_text: "전체 검색(계정, 아이템 등)"
                multiline: False
                font_name: "CustomFont" if app.font_exists else "Roboto"
                background_color: (0.1, 0.1, 0.1, 0.8)
                foreground_color: (1, 1, 1, 1)
                on_text: root.filter_accounts(self.text)
            Button:
                text: "검색"
                size_hint_x: 0.2
                background_color: (0.05, 0.05, 0.15, 1)

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
                spacing: 10

        StyledButton:
            text: "데이터 저장"
            on_release: app.save_all()

<AccountItem@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '70dp'
    padding: [15, 5]
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.7)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
    Label:
        id: name_label
        text: ""
        font_name: "CustomFont" if app.font_exists else "Roboto"
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Button:
        text: "삭제"
        size_hint_x: 0.2
        background_color: (0.7, 0.1, 0.1, 1)
        on_release: app.delete_account(root.account_data)
'''

class MainScreen(Screen):
    def show_add_popup(self):
        # 튕김 방지: 키보드 강제 해제 후 팝업 생성
        Window.release_all_keyboards()
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.txt_input = TextInput(
            hint_text="생성할 계정 ID", 
            multiline=False, 
            height='65dp', 
            size_hint_y=None,
            font_name="CustomFont" if App.get_running_app().font_exists else "Roboto"
        )
        add_btn = Button(
            text="생성 완료", 
            background_color=(0, 0.3, 0.1, 1), 
            background_normal='', 
            size_hint_y=None, 
            height='55dp'
        )
        content.add_widget(self.txt_input)
        content.add_widget(add_btn)
        
        self.popup = Popup(title="계정 생성", content=content, size_hint=(0.85, 0.45))
        add_btn.bind(on_release=self.add_account_logic)
        self.popup.open()

    def add_account_logic(self, instance):
        name = self.txt_input.text.strip()
        if name:
            app = App.get_running_app()
            app.data["accounts"].append({"name": name, "inventory": []})
            app.refresh_main_list()
            app.save_all()
            # 자동 스크롤 하단 이동
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, 'scroll_y', 0), 0.1)
            self.popup.dismiss()

    def filter_accounts(self, query):
        layout = self.ids.account_list
        layout.clear_widgets()
        app = App.get_running_app()
        for acc in app.data["accounts"]:
            if query.lower() in acc["name"].lower():
                from kivy.factory import Factory
                item = Factory.AccountItem()
                item.ids.name_label.text = acc["name"]
                item.account_data = acc
                layout.add_widget(item)

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
        self.main_screen.filter_accounts("")

    def delete_account(self, acc_data):
        self.data["accounts"].remove(acc_data)
        self.refresh_main_list()
        self.save_all()

    def save_all(self):
        if DataManager.save(self.data):
            print("Save Success")

if __name__ == '__main__':
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    PT1Manager().run()
