import os
import sys
import traceback
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
from kivy.core.window import Window
from kivy.metrics import dp
from plyer import filechooser, share

# [원칙] 키보드 가림 방지 및 무료 로그 시스템
Window.softinput_mode = 'below_target'

def logger(type, value, tb):
    log_content = "".join(traceback.format_exception(type, value, tb))
    log_path = os.path.join(os.path.dirname(__file__), "error_log.txt")
    with open(log_path, "w", encoding='utf-8') as f:
        f.write("--- PT1 Manager Error Log ---\n")
        f.write(log_content)
    try: share.share(log_path)
    except: pass
sys.excepthook = logger

# 폰트 및 데이터 저장소
FONT_NAME = "KFont" if os.path.exists("font.ttf") else None
if FONT_NAME: LabelBase.register(name=FONT_NAME, fn_regular="font.ttf")
store = JsonStore('pt1_manager_v4.json')

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kw):
        super().__init__(**kw)
        self.font_name = FONT_NAME
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = FONT_NAME
        self.size_hint_y = None
        self.height = dp(50)
        self.multiline = False

# --- 화면 구성 (검색, 계정, 캐릭터, 상세) ---
class MainScreen(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        l.add_widget(Label(text="[PT1 통합 매니저]", font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
        
        self.si = SInput(hint_text="전체 검색 (아이템, 직업, 레벨 등)")
        self.si.bind(text=self.refresh); l.add_widget(self.si)
        
        btn = SBtn(text="+ 새 계정 만들기", bg=(0.1, 0.5, 0.2, 1))
        btn.bind(on_release=self.add_acc_pop); l.add_widget(btn)
        
        self.sc = ScrollView()
        self.gl = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.gl.bind(minimum_height=self.gl.setter('height'))
        self.sc.add_widget(self.gl); l.add_widget(self.sc)
        self.add_widget(l)

    def refresh(self, *a):
        self.gl.clear_widgets()
        q = self.si.text.lower()
        for acc in sorted(store.keys()):
            data = store.get(acc)
            if not q or q in acc.lower() or q in json.dumps(data, ensure_ascii=False).lower():
                row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
                b = SBtn(text=f"계정: {acc}", bg=(0.2, 0.3, 0.5, 1))
                b.bind(on_release=lambda x, n=acc: self.go_acc(n))
                d = Button(text="삭제", size_hint_x=0.2, background_color=(0.7, 0.2, 0.2, 1))
                d.bind(on_release=lambda x, n=acc: self.confirm_del(n))
                row.add_widget(b); row.add_widget(d); self.gl.add_widget(row)

    def confirm_del(self, n):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text=f"'{n}'을 삭제하시겠습니까?", font_name=FONT_NAME))
        btns = BoxLayout(spacing=dp(10))
        y = SBtn(text="삭제", bg=(0.7, 0.1, 0.1, 1)); n_b = SBtn(text="취소")
        btns.add_widget(y); btns.add_widget(n_b); content.add_widget(btns)
        pop = Popup(title="경고", content=content, size_hint=(0.8, 0.3))
        y.bind(on_release=lambda x: [store.delete(n), self.refresh(), pop.dismiss()])
        n_b.bind(on_release=pop.dismiss); pop.open()

    def add_acc_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        i = SInput(hint_text="계정 ID"); b = SBtn(text="추가", bg=(0.1, 0.5, 0.2, 1))
        c.add_widget(i); c.add_widget(b)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4))
        def save(x):
            if i.text.strip():
                store.put(i.text.strip(), chars={str(k): {"이름": f"캐릭터 {k}"} for k in range(1, 7)})
                pop.dismiss(); self.refresh()
        b.bind(on_release=save); pop.open()

    def go_acc(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

class CharSelect(Screen):
    def on_enter(self):
        self.layout.clear_widgets()
        acc = self.manager.cur_acc
        self.layout.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
        grid = GridLayout(cols=2, spacing=dp(10))
        chars = store.get(acc)['chars']
        for i in range(1, 7):
            name = chars.get(str(i), {}).get("이름", f"슬롯 {i}")
            btn = SBtn(text=name, bg=(0.3, 0.3, 0.4, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_det(idx)); grid.add_widget(btn)
        self.layout.add_widget(grid)
        back = SBtn(text="뒤로", bg=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main')); self.layout.add_widget(back)

    def __init__(self, **kw):
        super().__init__(**kw); self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10)); self.add_widget(self.layout)
    def go_det(self, i): self.manager.cur_idx = str(i); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.root.clear_widgets()
        self.data = store.get(self.manager.cur_acc)['chars'][self.manager.cur_idx]
        sc = ScrollView()
        box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # 사진 및 편집 버튼
        p_path = self.data.get('photo', '')
        self.img = Image(source=p_path if os.path.exists(p_path) else '', size_hint_y=None, height=dp(250))
        box.add_widget(self.img)
        
        pb = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        b1 = SBtn(text="사진 추가", bg=(0.2, 0.4, 0.7, 1)); b1.bind(on_release=lambda x: filechooser.open_file(on_selection=self.on_p))
        b2 = SBtn(text="사진 삭제", bg=(0.7, 0.2, 0.2, 1)); b2.bind(on_release=self.del_p)
        pb.add_widget(b1); pb.add_widget(b2); box.add_widget(pb)

        inv = SBtn(text="📦 인벤토리 관리", bg=(0.6, 0.4, 0.2, 1))
        inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory')); box.add_widget(inv)

        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for f in fields:
            r = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            r.add_widget(Label(text=f, font_name=FONT_NAME, size_hint_x=0.3))
            ti = SInput(text=str(self.data.get(f, ''))); self.ins[f] = ti
            r.add_widget(ti); box.add_widget(r)

        btns = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        s = SBtn(text="저장", bg=(0.1, 0.6, 0.3, 1)); s.bind(on_release=self.save)
        b = SBtn(text="뒤로", bg=(0.4, 0.4, 0.4, 1)); b.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        btns.add_widget(s); btns.add_widget(b); box.add_widget(btns)
        sc.add_widget(box); self.root.add_widget(sc)

    def __init__(self, **kw): super().__init__(**kw); self.root = BoxLayout(orientation='vertical'); self.add_widget(self.root)
    def on_p(self, sel): 
        if sel: self.img.source = sel[0]
    def del_p(self, *a): self.img.source = ''

    def save(self, *a):
        acc = store.get(self.manager.cur_acc)
        for f, ti in self.ins.items(): self.data[f] = ti.text
        self.data['photo'] = self.img.source
        acc['chars'][self.manager.cur_idx] = self.data
        store.put(self.manager.cur_acc, **acc)
        self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.data = store.get(self.manager.cur_acc)['chars'][self.manager.cur_idx]
        self.ti.text = self.data.get('inventory', '')
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        l.add_widget(Label(text="인벤토리 편집", font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
        self.ti = TextInput(font_name=FONT_NAME, multiline=True, font_size='17sp')
        l.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        s = SBtn(text="저장", bg=(0.1, 0.6, 0.3, 1)); s.bind(on_release=self.save)
        b = SBtn(text="뒤로", bg=(0.4, 0.4, 0.4, 1)); b.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(s); btns.add_widget(b); l.add_widget(btns); self.add_widget(l)
    def save(self, *a):
        acc = store.get(self.manager.cur_acc)
        acc['chars'][self.manager.cur_idx]['inventory'] = self.ti.text
        store.put(self.manager.cur_acc, **acc)
        self.manager.current = 'detail'

class PT1App(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainScreen(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PT1App().run()
