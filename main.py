import os, sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import LabelBase
from kivy.config import Config

# 1. 폰트 강제 설정 (줄 길어짐 방지용 최적화)
def get_path(p):
    return os.path.join(sys._MEIPASS, p) if hasattr(sys, '_MEIPASS') else os.path.join(".", p)

F_PATH = get_path("font.ttf")
if os.path.exists(F_PATH):
    LabelBase.register(name="K", fn_regular=F_PATH)
    Config.set('kivy', 'default_font', ['K', F_PATH, F_PATH, F_PATH])
    DF = "K"
else: DF = None

store = JsonStore('priston_v3.json')

# 2. 공통 위젯
class KInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = False

class KBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 140

# 3. 메인 화면 (검색 기능 강화)
class Main(Screen):
    def on_enter(self): self.ref()
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=20, spacing=15)
        s_box = BoxLayout(size_hint_y=0.15, spacing=10)
        self.ti = KInput(hint_text="계정/캐릭 검색")
        b = Button(text="검색", font_name=DF, size_hint_x=0.3)
        b.bind(on_release=self.ref)
        s_box.add_widget(self.ti); s_box.add_widget(b); l.add_widget(s_box)
        
        self.g = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.g.bind(minimum_height=self.g.setter('height'))
        sw = ScrollView(); sw.add_widget(self.g); l.add_widget(sw)
        self.add_widget(l)

    def ref(self, *a):
        self.g.clear_widgets()
        q = self.ti.text.strip().lower()
        for k in store.keys():
            d = store.get(k)
            match = False
            if not q or q in k.lower(): match = True
            else:
                for i in range(1, 7):
                    if q in d.get('chars', {}).get(str(i), {}).get('이름', '').lower():
                        match = True; break
            if match:
                btn = KBtn(text=f"계정: {k}")
                btn.bind(on_release=lambda x, n=k: self.go(n))
                self.g.add_widget(btn)
    def go(self, n):
        self.manager.current_acc = n
        self.manager.current = 'char'

# 4. 캐릭터 선택 (간결화)
class Char(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.current_acc
        d = store.get(acc)
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"[{acc}] 캐릭터", font_name=DF, size_hint_y=0.1))
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            nm = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            b = KBtn(text=nm)
            b.bind(on_release=lambda x, idx=i: self.go_d(idx))
            g.add_widget(b)
        l.add_widget(g)
        back = KBtn(text="뒤로가기", background_color=(.3,.3,.3,1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(back); self.add_widget(l)
    def go_d(self, i):
        self.manager.idx = str(i); self.manager.current = 'detail'

# 5. 상세 정보 (핵심 기능만)
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.current_acc, self.manager.idx
        self.dat = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.ins = {}
        for f in ["이름", "직업", "레벨", "무기"]:
            r = BoxLayout(size_hint_y=None, height=90)
            r.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = KInput(text=str(self.dat.get(f, '')))
            self.ins[f] = ti; r.add_widget(ti); l.add_widget(r)
        sv = KBtn(text="저장", background_color=(0,.5,0,1))
        sv.bind(on_release=self.save); l.add_widget(sv)
        bk = KBtn(text="뒤로", background_color=(.3,.3,.3,1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'char', 'char'))
        l.add_widget(bk); self.add_widget(l)
    def save(self, *a):
        acc, idx = self.manager.current_acc, self.manager.idx
        d = store.get(acc)
        d['chars'][idx] = {f: ti.text for f, ti in self.ins.items()}
        store.put(acc, **d); self.manager.current = 'char'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.current_acc = ""; sm.idx = ""
        sm.add_widget(Main(name='main')); sm.add_widget(Char(name='char'))
        sm.add_widget(Detail(name='detail')); return sm

if __name__ == '__main__':
    PristonApp().run()
