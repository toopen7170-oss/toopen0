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
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

# --- [에러 로그 공유 시스템] ---
def logger(type, value, tb):
    log_content = "".join(traceback.format_exception(type, value, tb))
    log_path = "error_log.txt"
    if platform == 'android':
        from android.storage import app_storage_path
        log_path = os.path.join(app_storage_path(), "error_log.txt")
    with open(log_path, "w", encoding='utf-8') as f:
        f.write(log_content)
    if platform == 'android':
        try:
            from plyer import share
            share.share(log_path)
        except: pass
sys.excepthook = logger

# --- [시스템 설정] ---
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    DF = "KFont"
else: DF = None

store = JsonStore('priston_v3_0.json')

# --- [공통 위젯 스타일] ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.background_color = (1, 1, 1, 0.9)
        self.padding = [dp(10), dp(15)]
        self.size_hint_y = None
        self.height = dp(60)

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.background_normal = ''
        self.size_hint_y = None
        self.height = dp(60)

# --- [배경 레이아웃] ---
class BgLayout(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                self.bg_rect = Rectangle(source='bg.png', pos=self.pos, size=self.size)
            else:
                Color(0.1, 0.1, 0.1, 1)
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *a):
        self.bg_rect.pos, self.bg_rect.size = self.pos, self.size

# --- [메인 화면: 검색 기능 강화 & 삭제 확인] ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.root = BgLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.root.add_widget(Label(text="[PT1 통합 매니저]", font_size='22sp', size_hint_y=None, height=dp(50), font_name=DF))
        
        s_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        self.stti = SInput(hint_text="검색어를 입력하세요...")
        self.stti.bind(text=self.refresh) # 실시간 검색 (6번 해결)
        s_box.add_widget(self.stti)
        self.root.add_widget(s_box)

        add_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.7, 0.3, 1))
        add_btn.bind(on_release=self.add_pop); self.root.add_widget(add_btn)

        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView(do_scroll_x=False)
        self.scroll.add_widget(self.grid)
        self.root.add_widget(self.scroll)
        self.add_widget(self.root)

    def refresh(self, *a):
        self.grid.clear_widgets()
        q = self.stti.text.strip().lower()
        for k in sorted(list(store.keys())):
            if not q or q in k.lower():
                row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(5))
                btn = SBtn(text=f"계정: {k}", size_hint_x=0.8, background_color=(0.1, 0.2, 0.4, 0.8))
                btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: self.confirm_del(n)) # (1번 해결)
                row.add_widget(btn); row.add_widget(del_btn); self.grid.add_widget(row)

    def confirm_del(self, n):
        c = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        c.add_widget(Label(text=f"'{n}'을 삭제할까요?", font_name=DF))
        b_box = BoxLayout(spacing=dp(10))
        y = SBtn(text="삭제", background_color=(0.8, 0.2, 0.2, 1))
        n_btn = SBtn(text="취소", background_color=(0.4, 0.4, 0.4, 1))
        b_box.add_widget(y); b_box.add_widget(n_btn); c.add_widget(b_box)
        pop = Popup(title="삭제 확인", content=c, size_hint=(0.8, 0.3), title_font=DF)
        y.bind(on_release=lambda x: [store.delete(n), self.refresh(), pop.dismiss()])
        n_btn.bind(on_release=pop.dismiss); pop.open()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        inp = SInput(hint_text="ID 입력")
        btn = SBtn(text="생성", background_color=(0.1, 0.7, 0.3, 1))
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4), title_font=DF)
        def save(x):
            if inp.text.strip():
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()

    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

# --- [캐릭터 선택 & 상세 화면: 여백 및 사진 기능 추가] ---
class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        d = store.get(acc)
        l = BgLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
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
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # (7번 사진 기능 해결)
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if (img_src and os.path.exists(img_src)) else '', size_hint_y=None, height=dp(250))
        content.add_widget(self.img)
        
        img_btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        add_img = SBtn(text="사진 변경", background_color=(0.2, 0.5, 0.8, 1), height=dp(45))
        del_img = SBtn(text="사진 삭제", background_color=(0.7, 0.3, 0.3, 1), height=dp(45))
        img_btns.add_widget(add_img); img_btns.add_widget(del_img); content.add_widget(img_btns)

        # 인벤토리 버튼
        btn_inv = SBtn(text="📦 인벤토리 관리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        content.add_widget(btn_inv)

        fields = ["이름", "직업", "레벨", "무기", "갑옷", "방패", "장갑", "부츠", "기타"]
        self.ins = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, '')))
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

# --- [인벤토리 화면: 폰트 컬러 및 스크롤 개선] ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        root = BgLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        root.add_widget(Label(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리", font_name=DF, size_hint_y=None, height=dp(50)))
        
        # (3, 4, 5번 해결: 글씨가 잘 보이도록 배경색과 폰트색 조정)
        sc_inv = ScrollView(do_scroll_x=False)
        self.ti = TextInput(text=char_data.get('inventory', ''), font_name=DF, multiline=True, 
                            size_hint_y=None, height=dp(800), font_size='16sp',
                            foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1),
                            padding=[dp(15), dp(15)])
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
