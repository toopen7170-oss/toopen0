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
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# [전수검사] S26 울트라 및 안드로이드 경로 무결성 확보
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
resource_add_path(BASE_PATH)
Window.softinput_mode = 'below_target'

# [폰트 집중 수정] 엔진 레벨에서 기본 폰트를 강제 변경 (깨짐 원천 차단)
FONT_FILE = 'font.ttf'
if os.path.exists(os.path.join(BASE_PATH, FONT_FILE)):
    LabelBase.register(name="CustomFont", fn_regular=FONT_FILE)
    from kivy.core.text import Label as CoreLabel
    # 모든 위젯의 기본 폰트 자체를 사용자 폰트로 교체
    CoreLabel.default_font = FONT_FILE

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
            text: "PristonTale Manager"
            font_size: '28sp'
            size_hint_y: None
            height: '70dp'

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 5
            TextInput:
                id: search_input
                hint_text: "계정 또는 아이템 검색"
                multiline: False
                background_color: (0.1, 0.1, 0.1, 0.8)
                foreground_color: (1, 1, 1, 1)
                on_text: root.filter_accounts(self.text)
            Button:
                text: "검색"
                size_hint_x: 0.2

        StyledButton:
            text: "+ 새 계정 등록하기"
            on_release: root.show_add_popup()
            
        ScrollView:
            BoxLayout:
                id: account_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10

        StyledButton:
            text: "모든 데이터 저장"
            on_release: app.save_all()

<AccountItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '75dp'
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
        font_size: '18sp'
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Button:
        text: "삭제"
        size_hint_x: 0.25
        background_color: (0.7, 0.1, 0.1, 1)
        on_release: root.confirm_delete()

<DetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            id: detail_label
            text: ""
            font_size: '20sp'
        Button:
            text: "목록으로 돌아가기"
            size_hint_y: None
            height: '55dp'
            on_release: app.root.current = 'main'
'''

class AccountItem(ButtonBehavior, BoxLayout):
    def __init__(self, account_data, **kwargs):
        super().__init__(**kwargs)
        self.account_data = account_data
        self.ids.name_label.text = account_data['name']

    def on_release(self):
        # [클릭 반응 해결] 상세 화면으로 전환 및 데이터 전달
        app = App.get_running_app()
        app.root.get_screen('detail').ids.detail_label.text = f"계정명: {self.account_data['name']}\\n\\n상세 인벤토리 정보 준비 중..."
        app.root.current = 'detail'

    def confirm_delete(self):
        # [삭제 확인 멘트 해결] 팝업 내부 커스텀 라벨로 깨짐 방지
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text=f"[{self.account_data['name']}] 계정을\\n정말 삭제하시겠습니까?", halign='center'))
        
        btns = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        y_btn = Button(text="삭제", background_color=(0.8, 0.2, 0.2, 1))
        n_btn = Button(text="취소")
        
        btns.add_widget(y_btn)
        btns.add_widget(n_btn)
        content.add_widget(btns)
        
        self.popup = Popup(title="", separator_height=0, title_size=0, content=content, size_hint=(0.8, 0.35))
        y_btn.bind(on_release=self.perform_delete)
        n_btn.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def perform_delete(self, instance):
        app = App.get_running_app()
        app.delete_account(self.account_data)
        self.popup.dismiss()

class MainScreen(Screen):
    def show_add_popup(self):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text="새 계정 추가", font_size='20sp', size_hint_y=None, height='40dp'))
        self.txt_input = TextInput(hint_text="계정 ID 입력", multiline=False, size_hint_y=None, height='55dp')
        add_btn = Button(text="추가 완료", background_color=(0, 0.3, 0.1, 1), size_hint_y=None, height='55dp')
        
        content.add_widget(self.txt_input)
        content.add_widget(add_btn)
        
        self.pop = Popup(title="", separator_height=0, title_size=0, content=content, size_hint=(0.85, 0.45))
        add_btn.bind(on_release=self.add_logic)
        self.pop.open()

    def add_logic(self, instance):
        name = self.txt_input.text.strip()
        if name:
            app = App.get_running_app()
            app.data["accounts"].append({"name": name, "inventory": []})
            app.refresh_main_list()
            app.save_all()
            self.pop.dismiss()

    def filter_accounts(self, query):
        layout = self.ids.account_list
        layout.clear_widgets()
        app = App.get_running_app()
        for acc in app.data["accounts"]:
            if query.lower() in acc["name"].lower():
                layout.add_widget(AccountItem(account_data=acc))

class DetailScreen(Screen):
    pass

class PT1Manager(App):
    def build(self):
        self.data = DataManager.load()
        Builder.load_string(KV)
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(DetailScreen(name='detail'))
        self.refresh_main_list()
        return self.sm

    def refresh_main_list(self):
        self.sm.get_screen('main').filter_accounts("")

    def delete_account(self, acc_data):
        self.data["accounts"].remove(acc_data)
        self.refresh_main_list()
        self.save_all()

    def save_all(self):
        DataManager.save(self.data)

if __name__ == '__main__':
    PT1Manager().run()
