import os, sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
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

# --- 5번: 폰트 깨짐 방지 (엔진 강제 주입) ---
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    Config.set('kivy', 'default_font', ['KFont', FONT_FILE, FONT_FILE, FONT_FILE])
    DF = "KFont"
else:
    DF = None

store = JsonStore('priston_v3.json')

# --- 4번: 사진 권한 허용 (안드로이드 전용 로직) ---
def request_android_permissions():
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# --- 공통 위젯 설정 ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = False

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 140

# --- 1번: 검색 작동 / 2번: 계정 삭제 ---
class MainMenu(Screen):
    def on_enter(self): 
        request_android_permissions()
        self.refresh()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.lay = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 검색 영역
        sh = BoxLayout(size_hint_y=0.12, spacing=10)
        self.ti = SInput(hint_text="계정/캐릭터 검색...")
        sb = Button(text="검색", font_name=DF, size_hint_x=0.3)
        sb.bind(on_release=self.refresh) # 1번: 검색 기능 연결
        sh.add_widget(self.ti); sh.add_widget(sb); self.lay.add_widget(sh)

        # 계정 생성
        add = SBtn(text="+ 새 계정 추가", background_color=(0, .5, 0, 1))
        add.bind(on_release=self.add_pop); self.lay.add_widget(add)

        # 리스트 영역 (스크롤 작동)
        self.g = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.g.bind(minimum_height=self.g.setter('height'))
        self.sw = ScrollView(); self.sw.add_widget(self.g); self.lay.add_widget(self.sw)
        self.add_widget(self.lay)

    def refresh(self, *a):
        self.g.clear_widgets()
        q = self.ti.text.strip().lower()
        for k in list(store.keys()):
            d = store.get(k)
            match = False
            if not q or q in k.lower(): match = True
            else:
                for i in range(1, 7):
                    if q in d.get('chars', {}).get(str(i), {}).get('이름', '').lower():
                        match = True; break
            if match:
                # 2번: 삭제 버튼이 포함된 계정 줄
                row = BoxLayout(size_hint_y=None, height=145, spacing=5)
                acc_b = SBtn(text=f"계정: {k}", size_hint_x=0.8)
                acc_b.bind(on_release=lambda x, n=k: self.go(n))
                del_b = Button(text="X", size_hint_x=0.2, background_color=(.8, 0, 0, 1), font_name=DF)
                del_b.bind(on_release=lambda x, n=k: self.del_acc(n))
                row.add_widget(acc_b); row.add_widget(del_b)
                self.g.add_widget(row)

    def del_acc(self, n): # 2번: 계정 삭제 기능
        store.delete(n); self.refresh()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름")
        b = SBtn(text="생성", background_color=(0, .5, 0, 1))
        c.add_widget(inp); c.add_widget(b)
        p = Popup(title="추가", content=c, size_hint=(0.8, 0.4))
        def sv(x):
            if inp.text.strip():
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                p.dismiss(); self.refresh()
        b.bind(on_release=sv); p.open()

    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        d = store.get(self.manager.cur_acc)
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text=f"[{self.manager.cur_acc}]", font_name=DF, size_hint_y=0.1))
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            nm = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            b = SBtn(text=nm); b.bind(on_release=lambda x, idx=i: self.go_d(idx))
            g.add_widget(b)
        l.add_widget(g)
        bk = SBtn(text="뒤로", background_color=(.4, .4, .4, 1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(bk); self.add_widget(l)
    def go_d(self, i):
        self.manager.idx = str(i); self.manager.current = 'detail'

# --- 3번: 키보드 올라와도 스크롤 유지 ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.dat = store.get(self.manager.cur_acc)['chars'].get(self.manager.idx, {})
        self.sc = ScrollView()
        self.l = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.l.bind(minimum_height=self.l.setter('height'))
        
        self.img = Image(source=self.dat.get('img', ''), size_hint_y=None, height=400)
        self.l.add_widget(self.img)
        
        # 사진/인벤 버튼
        br = BoxLayout(size_hint_y=None, height=120, spacing=10)
        pic = SBtn(text="사진변경"); pic.bind(on_release=self.get_pic)
        inv = SBtn(text="인벤토리", background_color=(.5, .3, .1, 1))
        inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inv'))
        br.add_widget(pic); br.add_widget(inv); self.l.add_widget(br)

        self.ins = {}
        for f in ["이름", "직업", "레벨", "무기", "방어구", "기타"]:
            r = BoxLayout(size_hint_y=None, height=90, spacing=10)
            r.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = SInput(text=str(self.dat.get(f, '')))
            ti.bind(focus=self.on_f) # 3번: 포커스 시 스크롤 이동
            self.ins[f] = ti; r.add_widget(ti); self.l.add_widget(r)
        
        sv = SBtn(text="저장", background_color=(0, .5, 0, 1)); sv.bind(on_release=self.save)
        self.l.add_widget(sv)
        bk = SBtn(text="뒤로", background_color=(.4, .4, .4, 1))
        bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char'))
        self.l.add_widget(bk); self.sc.add_widget(self.l); self.add_widget(self.sc)

    def on_f(self, instance, value): # 3번: 입력창 클릭 시 자동으로 해당 위치로 스크롤
        if value: Clock.schedule_once(lambda dt: self.sc.scroll_to(instance), 0.2)

    def get_pic(self, *a): # 4번: 사진첩 열기
        from kivy.uix.filechooser import FileChooserIconView
        fc = FileChooserIconView(path='/sdcard' if platform == 'android' else '.', filters=['*.jpg', '*.png'])
        btn = Button(text="선택", size_hint_y=0.15, font_name=DF)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="이미지", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *a):
        d = store.get(self.manager.cur_acc)
        new = {f: ti.text for f, ti in self.ins.items()}
        new['img'] = self.img.source; new['inventory'] = self.dat.get('inventory', '')
        d['chars'][self.manager.idx] = new
        store.put(self.manager.cur_acc, **d); self.manager.current = 'char'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        d = store.get(self.manager.cur_acc)['chars'].get(self.manager.idx, {})
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text="인벤토리", font_name=DF, size_hint_y=0.1))
        self.ti = SInput(text=d.get('inventory', '')); self.ti.multiline = True
        l.add_widget(self.ti)
        b = SBtn(text="저장 후 닫기"); b.bind(on_release=self.sv); l.add_widget(b)
        self.add_widget(l)
    def sv(self, *a):
        d = store.get(self.manager.cur_acc)
        d['chars'][self.manager.idx]['inventory'] = self.ti.text
        store.put(self.manager.cur_acc, **d); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.cur_acc = ""; sm.idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inv'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
