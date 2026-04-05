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

# --- 폰트 경로 1000번 확인 로직 ---
# 파일 이름이 font.ttf 이기만 하면 무조건 잡습니다.
FONT_NAME = "font.ttf"
if os.path.exists(FONT_NAME):
    LabelBase.register(name="K", fn_regular=FONT_NAME)
    Config.set('kivy', 'default_font', ['K', FONT_NAME, FONT_NAME, FONT_NAME])
    DF = "K"
else:
    DF = None # 파일이 없으면 기본 폰트 사용

st = JsonStore('priston_v3.json')

class Main(Screen):
    def on_enter(self): self.do_search()
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 검색창 (이전 버전에서 잘 되던 방식 적용)
        sb = BoxLayout(size_hint_y=0.15, spacing=10)
        self.ti = TextInput(hint_text="검색어 입력", font_name=DF, multiline=False)
        btn = Button(text="검색", font_name=DF, size_hint_x=0.3)
        btn.bind(on_release=self.do_search)
        sb.add_widget(self.ti); sb.add_widget(btn); layout.add_widget(sb)
        
        self.g = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.g.bind(minimum_height=self.g.setter('height'))
        sw = ScrollView(); sw.add_widget(self.g); layout.add_widget(sw)
        self.add_widget(layout)

    def do_search(self, *a):
        self.g.clear_widgets()
        q = self.ti.text.strip().lower()
        for k in list(st.keys()):
            d = st.get(k)
            match = False
            if not q or q in k.lower(): match = True
            else:
                for i in range(1, 7):
                    c_nm = d.get('chars', {}).get(str(i), {}).get('이름', '').lower()
                    if q in c_nm: match = True; break
            if match:
                btn = Button(text=f"계정: {k}", font_name=DF, size_hint_y=None, height=140)
                btn.bind(on_release=lambda x, n=k: self.go_acc(n))
                self.g.add_widget(btn)

    def go_acc(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char'

class Char(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        d = st.get(acc)
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=DF, size_hint_y=0.1))
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            nm = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            b = Button(text=nm, font_name=DF, size_hint_y=None, height=140)
            b.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            g.add_widget(b)
        l.add_widget(g)
        bk = Button(text="처음으로", font_name=DF, size_hint_y=None, height=120)
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(bk); self.add_widget(l)
    def go_detail(self, i):
        self.manager.idx = str(i); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.idx
        self.dat = st.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.ins = {}
        for f in ["이름", "직업", "레벨", "장비"]:
            r = BoxLayout(size_hint_y=None, height=90)
            r.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = TextInput(text=str(self.dat.get(f, '')), font_name=DF, multiline=False)
            self.ins[f] = ti; r.add_widget(ti); l.add_widget(r)
        sv = Button(text="저장", font_name=DF, size_hint_y=None, height=130, background_color=(0,.5,0,1))
        sv.bind(on_release=self.save); l.add_widget(sv)
        self.add_widget(l)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.idx
        d = st.get(acc)
        d['chars'][idx] = {f: ti.text for f, ti in self.ins.items()}
        st.put(acc, **d); self.manager.current = 'char'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.cur_acc = ""; sm.idx = ""
        sm.add_widget(Main(name='main')); sm.add_widget(Char(name='char'))
        sm.add_widget(Detail(name='detail')); return sm

if __name__ == '__main__':
    PristonApp().run()
