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
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from plyer import filechooser

# [1. 폰트 설정] 이름을 font.ttf로 맞췄습니다.
FONT_NAME = 'font.ttf'
K_FONT = 'Roboto'
if os.path.exists(FONT_NAME):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_NAME)
        K_FONT = "KFont"
    except: pass

store = JsonStore('pt1_data_v21.json')

# [2. 배경 설정] 이름을 bg.png로 맞췄습니다.
class BgLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            bg_file = 'bg.png'
            if os.path.exists(bg_file):
                self.bg_rect = Rectangle(source=bg_file, pos=self.pos, size=self.size)
            else:
                # 파일이 없으면 어두운 회색 배경
                Color(0.1, 0.1, 0.1, 1)
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

# [3. 자동 스크롤 입력창]
class KTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.multiline = False
        self.font_size = '16sp'
        self.padding = [dp(10), dp(18), dp(10), dp(8)]
        self.background_color = (1, 1, 1, 0.9)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            target = self.parent
            while target and not isinstance(target, ScrollView):
                target = target.parent
            if target:
                Clock.schedule_once(lambda dt: target.scroll_to(self, padding=dp(350)), 0.2)
        return super().on_touch_down(touch)

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 0.8), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

# --- 화면 클래스들 (생략 없이 통합) ---
class MainMenu(Screen):
    def on_enter(self): self.refresh_list()
    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BgLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        s_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.s_ti = KTextInput(text=query, hint_text="ID 검색")
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.s_ti.text.strip()))
        s_box.add_widget(self.s_ti); s_box.add_widget(s_btn); root.add_widget(s_box)
        root.add_widget(SBtn(text="+ 새 계정 만들기", bg=(0.1, 0.5, 0.3, 0.9), on_release=self.add_pop))
        scroll = ScrollView(); box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        for name in sorted(store.keys()):
            if query and query.lower() not in name.lower(): continue
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            btn = SBtn(text=f"ID: {name}", bg=(0.2, 0.2, 0.2, 0.7))
            btn.bind(on_release=lambda x, n=name: self.go_s(n))
            del_b = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7,0.2,0.2,1))
            del_b.bind(on_release=lambda x, n=name: [store.delete(n), self.refresh_list()])
            row.add_widget(btn); row.add_widget(del_b); box.add_widget(row)
        scroll.add_widget(box); root.add_widget(scroll); self.add_widget(root)
    def add_pop(self, *args):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10); ti = KTextInput(hint_text="새 ID 입력")
        b = SBtn(text="생성", bg=(0.1, 0.5, 0.3, 1)); c.add_widget(ti); c.add_widget(b)
        p = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4))
        b.bind(on_release=lambda x: [store.put(ti.text, slots=[{"이름":f"슬롯{i+1}","inven":[],"photos":[]} for i in range(6)]), p.dismiss(), self.refresh_list()] if ti.text else None); p.open()
    def go_s(self, name): self.manager.cur_acc = name; self.manager.current = 'slots'

class Slots(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; slots = store.get(acc)['slots']
        root = BgLayout(orientation='vertical', padding=10, spacing=10)
        root.add_widget(Label(text=f"ID: {acc}", font_name=K_FONT, size_hint_y=None, height=40))
        g = GridLayout(cols=2, spacing=10)
        for i in range(6):
            btn = Button(text=f"{i+1}번\n{slots[i].get('이름','')}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 0.8))
            btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        root.add_widget(g); root.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(root)
    def go_d(self, idx): self.manager.cur_idx = idx; self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]; self.p_list = self.data.get('photos', [])
        root = BgLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView(); content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[0,0,0,1000])
        content.bind(minimum_height=content.setter('height'))
        btn_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=5)
        btn_box.add_widget(SBtn(text="📷 사진 추가", on_release=self.pick_p))
        btn_box.add_widget(SBtn(text="📦 인벤토리", on_release=lambda x: setattr(self.manager, 'current', 'inventory')))
        content.add_widget(btn_box)
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.ins = {}
        for f in self.fields:
            r = BoxLayout(size_hint_y=None, height=dp(55))
            r.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            ti = KTextInput(text=str(self.data.get(f, ''))); r.add_widget(ti); self.ins[f] = ti
            content.add_widget(r)
        scroll.add_widget(content); root.add_widget(scroll)
        nav = BoxLayout(size_hint_y=None, height=60, spacing=5)
        nav.add_widget(SBtn(text="정보 저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav); self.add_widget(root)
    def pick_p(self, *args): Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_p), 0.1)
    def set_p(self, sel):
        if sel: self.p_list.append(sel[0]); self.save()
    def save(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        for f, ti in self.ins.items(): slots[idx][f] = ti.text
        slots[idx]['photos'] = self.p_list; store.put(acc, slots=slots)

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('inven', [])
        root = BgLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView(); box = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=[0,0,0,1000])
        box.bind(minimum_height=box.setter('height'))
        for i, v in enumerate(self.items):
            r = BoxLayout(size_hint_y=None, height=55, spacing=5)
            ti = KTextInput(text=v); ti.bind(text=lambda ins, val, idx=i: self.up(idx, val))
            db = Button(text="X", size_hint_x=None, width=50, background_color=(0.7,0.2,0.2,1))
            db.bind(on_release=lambda x, idx=i: [self.items.pop(idx), self.on_enter()])
            r.add_widget(ti); r.add_widget(db); box.add_widget(r)
        scroll.add_widget(box); root.add_widget(scroll)
        nav = GridLayout(cols=3, size_hint_y=None, height=60, spacing=5)
        nav.add_widget(SBtn(text="+추가", on_release=lambda x: [self.items.append(""), self.on_enter()]))
        nav.add_widget(SBtn(text="저장", on_release=self.save_i)); nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        root.add_widget(nav); self.add_widget(root)
    def up(self, idx, v): self.items[idx] = v
    def save_i(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items; store.put(acc, slots=slots)

class PTApp(App):
    def build(self):
        self.title = "Priston Tale"
        sm = ScreenManager(transition=FadeTransition()); sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main')); sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
