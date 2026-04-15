import os
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# [전수검사] S26 울트라 최적화 및 경로 설정
Window.softinput_mode = 'below_target'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
resource_add_path(BASE_PATH)

# [폰트 무결성] Kivy 엔진 자체의 기본 폰트를 강제 변경 (깨짐 원천 차단)
FONT_NAME = 'font.ttf'
if os.path.exists(os.path.join(BASE_PATH, FONT_NAME)):
    LabelBase.register(name="CustomFont", fn_regular=FONT_NAME)
    from kivy.core.text import Label as CoreLabel
    CoreLabel.default_font = FONT_NAME

def get_data_path():
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'Pristontale.json')
    return os.path.join(BASE_PATH, 'Pristontale.json')

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
        try:
            with open(get_data_path(), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

KV = '''
<StyledButton@Button>:
    background_normal: ''
    background_color: (0, 0.3, 0.1, 1)
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
                background_color: (0.1, 0.1, 0.1, 0.8)
                foreground_color: (1, 1, 1, 1)
                on_text: root.filter_accounts(self.text)
            Button:
                text: "검색"
                size_hint_x: 0.2

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
        # [튕김 방지] 타이틀 바 기능을 끄고 내부 커스텀 라벨로 대체
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title_label = Label(text="새 계정 생성", font_size='20sp', size_hint_y=None, height='40dp')
        self.txt_input = TextInput(hint_text="계정 ID 입력", multiline=False, height='60dp', size_hint_y=None)
        add_btn = Button(text="생성 완료", background_color=(0, 0.3, 0.1, 1), background_normal='', size_hint_y=None, height='55dp')
        
        content.add_widget(title_label)
        content.add_widget(self.txt_input)
        content.add_widget(add_btn)
        
        # separator_height=0, title_size=0 으로 튕김 원인 제거
        self.popup = Popup(title="", separator_height=0, title_size=0, content=content, size_hint=(0.85, 0.45))
        add_btn.bind(on_release=self.add_account_logic)
        self.popup.open()

    def add_account_logic(self, instance):
        name = self.txt_input.text.strip()
        if name:
            app = App.get_running_app()
            app.data["accounts"].append({"name": name, "inventory": []})
            app.refresh_main_list()
            app.save_all()
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
        DataManager.save(self.data)

if __name__ == '__main__':
    PT1Manager().run()
