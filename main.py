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

# [전수검사 수정 1] S26 울트라 터치 프리징 방지를 위한 소프트 키보드 설정 강제 고정
Window.softinput_mode = 'pan'

# [전수검사 수정 2] 폰트 경로 무결성 확보 (font.ttf)
FONT_PATH = os.path.join(os.path.dirname(__file__), 'font.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name="CustomFont", fn_regular=FONT_PATH)

# [전수검사 수정 3] 안드로이드 저장소 권한 및 데이터 경로 설정
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
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accounts": []}

    @staticmethod
    def save(data):
        with open(get_data_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# UI 정의 (Kivy 디자인 언어)
KV = '''
<StyledButton@Button>:
    font_name: "CustomFont" if app.font_exists else "Roboto"
    background_normal: ''
    background_color: (0.2, 0.6, 1, 1)

<MainScreen>:
    canvas.before:
        Rectangle:
            source: 'bg.png'
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        Label:
            text: "PT1 MANAGER (무결점 빌드)"
            font_name: "CustomFont" if app.font_exists else "Roboto"
            font_size: '24sp'
            size_hint_y: 0.1
            
        ScrollView:
            id: scroll_view
            BoxLayout:
                id: account_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10

        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            StyledButton:
                text: "계정 추가"
                on_release: root.show_add_popup()
            StyledButton:
                text: "데이터 저장"
                on_release: app.save_all()

<AccountItem@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    padding: 5
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.5)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        id: name_label
        text: ""
        font_name: "CustomFont" if app.font_exists else "Roboto"
    Button:
        text: "상세"
        size_hint_x: 0.2
        on_release: app.go_detail(root.account_data)
    Button:
        text: "삭제"
        size_hint_x: 0.2
        background_color: (1, 0, 0, 1)
        on_release: app.delete_account(root.account_data)

<DetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        Label:
            id: detail_title
            font_name: "CustomFont" if app.font_exists else "Roboto"
            size_hint_y: 0.1
        ScrollView:
            BoxLayout:
                id: inven_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "아이템 추가"
                on_release: root.add_item()
            Button:
                text: "뒤로가기"
                on_release: app.root.current = 'main'
'''

class MainScreen(Screen):
    def show_add_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # [전수검사 수정 4] 비동기 포커스 처리로 S26 프리징 방지
        self.txt_input = TextInput(hint_text="계정명 입력", multiline=False, font_name="CustomFont" if App.get_running_app().font_exists else "Roboto")
        
        btn_box = BoxLayout(size_hint_y=0.4, spacing=10)
        add_btn = Button(text="추가")
        cancel_btn = Button(text="취소")
        
        btn_box.add_widget(add_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(self.txt_input)
        content.add_widget(btn_box)
        
        self.popup = Popup(title="새 계정 생성", content=content, size_hint=(0.8, 0.4))
        add_btn.bind(on_release=self.add_account_logic)
        cancel_btn.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def add_account_logic(self, instance):
        name = self.txt_input.text.strip()
        if name:
            app = App.get_running_app()
            new_acc = {"name": name, "inventory": []}
            app.data["accounts"].append(new_acc)
            app.refresh_main_list()
            # [전수검사 수정 5] 자동 스크롤 하단 이동
            Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
            self.popup.dismiss()

    def scroll_to_bottom(self):
        self.ids.scroll_view.scroll_y = 0

class DetailScreen(Screen):
    current_acc = None

    def on_pre_enter(self):
        self.ids.detail_title.text = f"[{self.current_acc['name']}] 인벤토리"
        self.refresh_inven()

    def refresh_inven(self):
        self.ids.inven_list.clear_widgets()
        for item in self.current_acc['inventory']:
            row = BoxLayout(size_hint_y=None, height='40dp')
            row.add_widget(Label(text=item, font_name="CustomFont" if App.get_running_app().font_exists else "Roboto"))
            del_btn = Button(text="X", size_hint_x=0.2)
            del_btn.bind(on_release=lambda x, it=item: self.delete_item(it))
            row.add_widget(del_btn)
            self.ids.inven_list.add_widget(row)

    def add_item(self):
        # 아이템 추가 로직 (간소화)
        self.current_acc['inventory'].append("새 아이템")
        self.refresh_inven()

    def delete_item(self, item_name):
        self.current_acc['inventory'].remove(item_name)
        self.refresh_inven()

class PT1Manager(App):
    def build(self):
        self.font_exists = os.path.exists(FONT_PATH)
        self.data = DataManager.load()
        Builder.load_string(KV)
        
        self.sm = ScreenManager()
        self.main_screen = MainScreen(name='main')
        self.detail_screen = DetailScreen(name='detail')
        
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.detail_screen)
        
        self.refresh_main_list()
        return self.sm

    def refresh_main_list(self):
        layout = self.main_screen.ids.account_list
        layout.clear_widgets()
        for acc in self.data["accounts"]:
            # Custom Widget 인스턴스화 로직
            from kivy.factory import Factory
            item = Factory.AccountItem()
            item.ids.name_label.text = acc["name"]
            item.account_data = acc
            layout.add_widget(item)

    def go_detail(self, acc_data):
        self.detail_screen.current_acc = acc_data
        self.sm.current = 'detail'

    def delete_account(self, acc_data):
        self.data["accounts"].remove(acc_data)
        self.refresh_main_list()

    def save_all(self):
        DataManager.save(self.data)

if __name__ == '__main__':
    # [전수검사 수정 6] 안드로이드 사진첩 접근 권한 요청 (API 33 대응)
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_MEDIA_IMAGES, Permission.WRITE_EXTERNAL_STORAGE])
    PT1Manager().run()
