import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window

# --- [1단계] 폰트 및 앱 설정 ---
FONT_FILE = "font.ttf"
DF = None

if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    DF = "KFont"
    Config.set('kivy', 'default_font', ['KFont', FONT_FILE, FONT_FILE, FONT_FILE, FONT_FILE])

# 🎯 아이콘 적용 설정
if os.path.exists("icon.png"):
    Config.set('kivy', 'icon', 'icon.png')

Window.softinput_mode = "below_target"
store = JsonStore('priston_v1_1.json')

# --- [2단계] 안드로이드 사진 권한 강제 요청 ---
def ask_permission():
    if platform == 'android':
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.MANAGE_EXTERNAL_STORAGE # 최신 폰 대응
            ])
        except Exception as e:
            print(f"Permission Error: {e}")

# --- [3단계] 커스텀 위젯 ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        if DF: self.font_name = DF
        self.size_hint_y = None
        self.height = 110 

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        if DF: self.font_name = DF
        self.size_hint_y = None
        self.height = 130

# --- [4단계] 화면 구성 ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        if os.path.exists("bg.png"): #
            layout.add_widget(Image(source="bg.png", size_hint_y=0.25))
        lbl = Label(text="[PT1 매니저]", font_size='22sp', size_hint_y=0.1)
        if DF: lbl.font_name = DF
        layout.add_widget(lbl)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.grid); layout.add_widget(scroll)
        add_btn = SBtn(text="+ 새 계정 추가", background_color=(0.1, 0.7, 0.3, 1))
        add_btn.bind(on_release=self.add_pop); layout.add_widget(add_btn)
        self.add_widget(layout)

    def refresh(self, *a):
        self.grid.clear_widgets()
        for k in list(store.keys()):
            btn = SBtn(text=f"계정: {k}"); btn.bind(on_release=lambda x, n=k: self.go(n))
            self.grid.add_widget(btn)
    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름")
        btn = SBtn(text="생성"); c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="추가", content=c, size_hint=(0.8, 0.4))
        def save(x):
            store.put(inp.text, chars={str(i): {"이름": f"슬롯 {i}", "inv_list": []} for i in range(1, 7)})
            pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()
    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; d = store.get(acc)
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        if os.path.exists("images.jpeg"): #
            l.add_widget(Image(source="images.jpeg", size_hint_y=0.25))
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            name = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            btn = SBtn(text=name); btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        l.add_widget(g); bk = SBtn(text="뒤로"); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(bk); self.add_widget(l)
    def go_d(self, i):
        self.manager.cur_idx = str(i); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        img_p = self.char_data.get('img', '')
        # 🎯 사진 로딩 문제 해결: 경로 존재 확인
        self.img = Image(source=img_p if img_p and os.path.exists(img_p) else '', size_hint_y=0.5)
        l.add_widget(self.img)
        btn_p = SBtn(text="사진 선택"); btn_p.bind(on_release=self.get_pic); l.add_widget(btn_p)
        btn_i = SBtn(text="인벤토리 관리", background_color=(0.6, 0.4, 0.2, 1))
        btn_i.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        l.add_widget(btn_i)
        bk = SBtn(text="뒤로"); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        l.add_widget(bk); self.add_widget(l)

    def get_pic(self, *a):
        from kivy.uix.filechooser import FileChooserIconView
        # 🎯 안드로이드 실제 경로 접근
        path = '/sdcard/DCIM/Camera' if platform == 'android' else '.'
        fc = FileChooserIconView(path=path, filters=['*.jpg', '*.png', '*.jpeg'])
        content = BoxLayout(orientation='vertical'); btn = SBtn(text="선택완료")
        content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 찾기", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection:
                self.img.source = fc.selection[0]
                acc, idx = self.manager.cur_acc, self.manager.cur_idx
                d = store.get(acc); d['chars'][idx]['img'] = fc.selection[0]
                store.put(acc, **d); pop.dismiss()
        btn.bind(on_release=sel); pop.open()

# --- 🎯 인벤토리 한 줄씩 무한 추가/삭제 기능 ---
class Inventory(Screen):
    def on_enter(self):
        self.refresh()
    def refresh(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        data = store.get(acc)['chars'].get(idx, {})
        self.items = data.get('inv_list', [])
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text="[인벤토리 줄별 관리]", size_hint_y=0.1, font_name=DF if DF else None))
        
        self.scroll_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scroll_grid.bind(minimum_height=self.scroll_grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.scroll_grid); layout.add_widget(scroll)

        for i, text in enumerate(self.items):
            self.add_item_row(i, text)

        btn_box = BoxLayout(size_hint_y=None, height=130, spacing=10)
        add_line = SBtn(text="+ 줄 추가"); add_line.bind(on_release=self.add_line)
        back = SBtn(text="뒤로"); back.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btn_box.add_widget(add_line); btn_box.add_widget(back); layout.add_widget(btn_box)
        self.add_widget(layout)

    def add_item_row(self, index, text):
        row = BoxLayout(size_hint_y=None, height=110, spacing=5)
        ti = TextInput(text=text, multiline=False, font_name=DF if DF else None)
        ti.bind(text=lambda instance, value, i=index: self.update_val(i, value))
        del_btn = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=DF if DF else None)
        del_btn.bind(on_release=lambda x, i=index: self.del_line(i))
        row.add_widget(ti); row.add_widget(del_btn); self.scroll_grid.add_widget(row)

    def update_val(self, i, val):
        self.items[i] = val
        self.sync_storage()

    def add_line(self, *a):
        self.items.append("")
        self.sync_storage(); self.refresh()

    def del_line(self, i):
        self.items.pop(i)
        self.sync_storage(); self.refresh()

    def sync_storage(self):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc); d['chars'][idx]['inv_list'] = self.items
        store.put(acc, **d)

class PristonApp(App):
    def build(self):
        ask_permission() #
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
