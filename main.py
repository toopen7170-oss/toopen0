import os
import sys
import traceback
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
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

# --- [0. 에러 로그 저장 시스템] ---
# 앱이 튕기면 핸드폰 내부에 error_log.txt를 생성합니다.
def logger(type, value, tb):
    log_path = "error_log.txt"
    if platform == 'android':
        from android.storage import app_storage_path
        log_path = os.path.join(app_storage_path(), "error_log.txt")
    
    with open(log_path, "w", encoding='utf-8') as f:
        f.write("--- PT1 Manager Error Log ---\n")
        f.write("".join(traceback.format_exception(type, value, tb)))

sys.excepthook = logger

# --- [1. 폰트 및 시스템 설정] ---
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_FILE)
        DF = "KFont"
    except: DF = None
else:
    DF = None

Window.softinput_mode = "below_target"
store = JsonStore('priston_v2_7.json') # 새 버전으로 시작

# --- [2. 배경 레이아웃 클래스] ---
class BgLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                self.bg_rect = Rectangle(source='bg.png', pos=self.pos, size=self.size)
            else:
                Color(0.1, 0.1, 0.1, 1)
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

# --- [3. 공통 위젯 스타일] ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = kw.get('multiline', False)
        self.size_hint_y = None
        self.height = dp(60) if not self.multiline else dp(200)

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.background_normal = '' 
        self.size_hint_y = None
        self.height = dp(60)

# --- [4. 화면 클래스들] ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main_root = BgLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.main_root.add_widget(Label(text="[PT1 통합 매니저]", font_size='22sp', size_hint_y=None, height=dp(50), font_name=DF))
        
        s_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        self.stti = SInput(hint_text="계정/캐릭터 검색...")
        s_btn = Button(text="검색", font_name=DF, size_hint_x=0.25, background_color=(0.2, 0.6, 1, 1))
        s_btn.bind(on_release=self.refresh)
        s_box.add_widget(self.stti); s_box.add_widget(s_btn); self.main_root.add_widget(s_box)

        add_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.7, 0.3, 1))
        add_btn.bind(on_release=self.add_pop); self.main_root.add_widget(add_btn)

        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView(do_scroll_x=False)
        self.scroll.add_widget(self.grid)
        self.main_root.add_widget(self.scroll)
        self.add_widget(self.main_root)

    def refresh(self, *a):
        self.grid.clear_widgets()
        q = self.stti.text.strip().lower()
        for k in sorted(list(store.keys())):
            d = store.get(k)
            if not q or q in k.lower():
                row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(5))
                acc_btn = SBtn(text=f"계정: {k}", size_hint_x=0.8, background_color=(0.1, 0.2, 0.4, 0.8))
                acc_btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: [store.delete(n), self.refresh()])
                row.add_widget(acc_btn); row.add_widget(del_btn); self.grid.add_widget(row)

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        inp = SInput(hint_text="ID 입력")
        btn = SBtn(text="생성", background_color=(0.1, 0.7, 0.3, 1))
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4), title_font=DF if DF else None)
        def save(x):
            if inp.text.strip():
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()

    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        d = store.get(acc)
        l = BgLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        l.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=DF, size_hint_y=None, height=dp(50)))
        g = GridLayout(cols=2, spacing=dp(10))
        for i in range(1, 7):
            char_name = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            btn = SBtn(text=char_name, background_color=(0.3, 0.3, 0.5, 0.8))
            btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        l.add_widget(g)
        back = SBtn(text="처음으로", background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(back); self.add_widget(l)
    def go_d(self, i):
        self.manager.cur_idx = str(i); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        root = BgLayout(orientation='vertical')
        sc = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if (img_src and os.path.exists(img_src)) else '', size_hint_y=None, height=dp(250))
        content.add_widget(self.img)
        br = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        btn_inv = SBtn(text="📦 인벤토리 관리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        br.add_widget(btn_inv); content.add_widget(br)
        fields = ["이름", "직업", "레벨", "무기", "갑옷", "방패", "장갑", "부츠", "기타"]
        self.ins = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
            row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, '')))
            ti.bind(focus=lambda inst, val: Clock.schedule_once(lambda dt: sc.scroll_to(inst, padding=dp(100)), 0.1) if val else None)
            self.ins[f] = ti; row.add_widget(ti); content.add_widget(row)
        sv = SBtn(text="변경사항 저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        content.add_widget(sv); content.add_widget(bk)
        sc.add_widget(content); root.add_widget(sc); self.add_widget(root)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['img'] = self.img.source
        new_c['inventory'] = self.char_data.get('inventory', '')
        d['chars'][idx] = new_c
        store.put(acc, **d)
        self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        root = BgLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        root.add_widget(Label(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리", font_name=DF, size_hint_y=None, height=dp(50)))
        sc_inv = ScrollView(do_scroll_x=False)
        self.ti = TextInput(text=char_data.get('inventory', ''), font_name=DF, multiline=True, size_hint_y=None, height=dp(1000))
        self.ti.bind(focus=lambda inst, val: Clock.schedule_once(lambda dt: sc_inv.scroll_to(inst, padding=dp(120)), 0.1) if val else None)
        sc_inv.add_widget(self.ti); root.add_widget(sc_inv)
        btns = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        sv = SBtn(text="저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="취소", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); root.add_widget(btns); self.add_widget(root)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        d['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **d)
        self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
