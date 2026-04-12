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
from kivy.core.window import Window

# --- [163번 기준] 폰트 설정 ---
FONT_FILE = "font.ttf"
DF = None
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    DF = "KFont"

Window.softinput_mode = "below_target"
store = JsonStore('priston_v1_1.json')

# --- 안드로이드 미디어 접근 권한 ---
def ask_permission():
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

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
        self.height = 120

# --- 메인 메뉴 (검색/삭제 복구) ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 검색창 복구
        self.search_input = SInput(hint_text="계정 검색...", multiline=False)
        self.search_input.bind(text=self.refresh)
        self.layout.add_widget(self.search_input)

        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.grid); self.layout.add_widget(scroll)
        
        # 계정 추가 버튼
        add_btn = SBtn(text="새 계정 추가", background_color=(0.2, 0.6, 0.2, 1))
        add_btn.bind(on_release=self.add_pop); self.layout.add_widget(add_btn)
        self.add_widget(self.layout)

    def refresh(self, *a):
        self.grid.clear_widgets()
        query = self.search_input.text.lower()
        for k in list(store.keys()):
            if query in k.lower():
                row = BoxLayout(size_hint_y=None, height=130, spacing=10)
                btn = SBtn(text=f"계정: {k}"); btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="삭제", size_hint_x=0.25, background_color=(0.8, 0.2, 0.2, 1))
                if DF: del_btn.font_name = DF
                del_btn.bind(on_release=lambda x, n=k: self.del_acc(n))
                row.add_widget(btn); row.add_widget(del_btn); self.grid.add_widget(row)

    def del_acc(self, n):
        store.delete(n); self.refresh()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름 입력")
        btn = SBtn(text="생성하기"); c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4))
        def save(x):
            if inp.text:
                store.put(inp.text, chars={str(i): {"이름": f"슬롯 {i}", "inv_list": []} for i in range(1, 7)})
                pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()

    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

# --- 캐릭터 선택 및 상세 화면 ---
class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; d = store.get(acc)
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            name = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            btn = SBtn(text=name); btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        l.add_widget(g); bk = SBtn(text="뒤로가기"); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
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
        self.img = Image(source=img_p if img_p and os.path.exists(img_p) else '', size_hint_y=0.5)
        l.add_widget(self.img)
        b_p = SBtn(text="사진 등록/변경"); b_p.bind(on_release=self.get_pic); l.add_widget(b_p)
        b_i = SBtn(text="인벤토리 관리"); b_i.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        l.add_widget(b_i); bk = SBtn(text="뒤로가기"); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        l.add_widget(bk); self.add_widget(l)

    def get_pic(self, *a):
        from kivy.uix.filechooser import FileChooserIconView
        path = '/sdcard/DCIM/Camera' if platform == 'android' else '.'
        fc = FileChooserIconView(path=path, filters=['*.jpg', '*.png', '*.jpeg'])
        content = BoxLayout(orientation='vertical'); btn = SBtn(text="선택 완료")
        content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection:
                self.img.source = fc.selection[0]
                acc, idx = self.manager.cur_acc, self.manager.cur_idx
                d = store.get(acc); d['chars'][idx]['img'] = fc.selection[0]
                store.put(acc, **d); pop.dismiss()
        btn.bind(on_release=sel); pop.open()

# --- 인벤토리 관리 (줄별 무한 추가) ---
class Inventory(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.items = store.get(acc)['chars'].get(idx, {}).get('inv_list', [])
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        g = GridLayout(cols=1, spacing=10, size_hint_y=None)
        g.bind(minimum_height=g.setter('height'))
        s = ScrollView(); s.add_widget(g); l.add_widget(s)
        for i, t in enumerate(self.items):
            r = BoxLayout(size_hint_y=None, height=110, spacing=5)
            ti = TextInput(text=t, multiline=False, font_name=DF if DF else None)
            ti.bind(text=lambda instance, v, i=i: self.upd(i, v))
            db = Button(text="삭제", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
            if DF: db.font_name = DF
            db.bind(on_release=lambda x, i=i: self.rem(i))
            r.add_widget(ti); r.add_widget(db); g.add_widget(r)
        bb = BoxLayout(size_hint_y=None, height=130, spacing=10)
        ab = SBtn(text="+ 줄 추가"); ab.bind(on_release=self.add_l)
        bk = SBtn(text="뒤로가기"); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        bb.add_widget(ab); bb.add_widget(bk); l.add_widget(bb); self.add_widget(l)
    def upd(self, i, v): self.items[i] = v; self.save()
    def add_l(self, *a): self.items.append(""); self.save(); self.refresh()
    def rem(self, i): self.items.pop(i); self.save(); self.refresh()
    def save(self):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc); d['chars'][idx]['inv_list'] = self.items; store.put(acc, **d)

class PristonApp(App):
    def build(self):
        ask_permission()
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
