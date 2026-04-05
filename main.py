import os, sys
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

# --- 1. 폰트 엔진 및 환경 설정 ---
FONT_FILE = "font.ttf"
if os.path.exists(FONT_FILE):
    LabelBase.register(name="KFont", fn_regular=FONT_FILE)
    Config.set('kivy', 'default_font', ['KFont', FONT_FILE, FONT_FILE, FONT_FILE])
    DF = "KFont"
else:
    DF = None

# 데이터 저장 (기존 v3와 분리하여 새롭게 v1_1 생성)
store = JsonStore('priston_v1_1.json')

# --- 안드로이드 사진 권한 허용 ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# --- 공통 디자인 위젯 ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = kw.get('multiline', False)
        self.background_color = (0.95, 0.95, 0.95, 1)

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 140
        self.background_normal = ''

# --- 메인 화면: 전체 검색 및 계정 관리 ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 상단 타이틀
        self.layout.add_widget(Label(text="[PT1 차트표 v1.1]", font_size='22sp', size_hint_y=0.1, font_name=DF))

        # 전체 검색창 (4번 문제 해결)
        s_box = BoxLayout(size_hint_y=0.12, spacing=5)
        self.stti = SInput(hint_text="전체 검색 (아이템, 레벨, 직업 등...)")
        s_btn = Button(text="검색", font_name=DF, size_hint_x=0.25, background_color=(0.2, 0.6, 1, 1))
        s_btn.bind(on_release=self.refresh)
        s_box.add_widget(self.stti); s_box.add_widget(s_btn)
        self.layout.add_widget(s_box)

        # 계정 추가 버튼
        add_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.7, 0.3, 1))
        add_btn.bind(on_release=self.add_pop)
        self.layout.add_widget(add_btn)

        # 리스트 (스크롤)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.grid)
        self.layout.add_widget(scroll); self.add_widget(self.layout)

    def refresh(self, *a):
        self.grid.clear_widgets()
        q = self.stti.text.strip().lower()
        for k in list(store.keys()):
            d = store.get(k)
            match = False
            # 모든 항목 뒤지는 전체 검색 로직
            if not q or q in k.lower(): match = True
            else:
                for idx in d.get('chars', {}):
                    char = d['chars'][idx]
                    if any(q in str(val).lower() for val in char.values()):
                        match = True; break
            
            if match:
                row = BoxLayout(size_hint_y=None, height=140, spacing=5)
                acc_btn = SBtn(text=f"계정: {k}", size_hint_x=0.8, background_color=(0.1, 0.2, 0.4, 1))
                acc_btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: self.confirm_del(n)) # 3번: 경고 팝업 연결
                row.add_widget(acc_btn); row.add_widget(del_btn)
                self.grid.add_widget(row)

    def confirm_del(self, n): # 3번: 삭제 경고 팝업
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        c.add_widget(Label(text=f"'{n}'\n정말 삭제하시겠습니까?", font_name=DF, halign='center'))
        btns = BoxLayout(spacing=10, size_hint_y=0.4)
        ok = Button(text="삭제", background_color=(0.8, 0, 0, 1), font_name=DF)
        no = Button(text="취소", font_name=DF)
        btns.add_widget(ok); btns.add_widget(no)
        c.add_widget(btns)
        pop = Popup(title="주의", content=c, size_hint=(0.8, 0.4))
        ok.bind(on_release=lambda x: [store.delete(n), self.refresh(), pop.dismiss()])
        no.bind(on_release=pop.dismiss); pop.open()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름 입력")
        btn = SBtn(text="계정 생성", background_color=(0.1, 0.7, 0.3, 1))
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4))
        def save(x):
            if inp.text.strip():
                store.put(inp.text.strip(), chars={str(i): {"이름": f"슬롯 {i}"} for i in range(1, 7)})
                pop.dismiss(); self.refresh()
        btn.bind(on_release=save); pop.open()

    def go(self, n):
        self.manager.cur_acc = n; self.manager.current = 'char_select'

# --- 캐릭터 선택 화면 (6개 슬롯) ---
class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        d = store.get(acc)
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text=f"계정: {acc}", font_name=DF, size_hint_y=0.1))
        
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            c_data = d['chars'].get(str(i), {})
            name = c_data.get('이름', f'슬롯 {i}')
            btn = SBtn(text=name, background_color=(0.3, 0.3, 0.5, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_d(idx))
            g.add_widget(btn)
        l.add_widget(g)
        back = SBtn(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(back); self.add_widget(l)
    def go_d(self, i):
        self.manager.cur_idx = str(i); self.manager.current = 'detail'

# --- 상세 정보 화면 (2번: 아이템 복구 / 3번: 스크롤) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        
        self.sc = ScrollView()
        self.l = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.l.bind(minimum_height=self.l.setter('height'))
        
        # 사진 표시
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if img_src else '', size_hint_y=None, height=450)
        self.l.add_widget(self.img)
        
        # 사진/인벤 버튼
        br = BoxLayout(size_hint_y=None, height=130, spacing=10)
        btn_pic = SBtn(text="사진 변경", background_color=(0.2, 0.5, 0.8, 1))
        btn_pic.bind(on_release=self.get_pic)
        btn_inv = SBtn(text="인벤토리", background_color=(0.6, 0.4, 0.2, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        br.add_widget(btn_pic); br.add_widget(btn_inv); self.l.add_widget(br)

        # 2번: 모든 아이템 필드 복구
        self.ins = {}
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=90, spacing=10)
            row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, '')))
            ti.bind(focus=self.on_f) # 자동 스크롤
            self.ins[f] = ti; row.add_widget(ti); self.l.add_widget(row)
        
        # 하단 버튼
        sv = SBtn(text="캐릭터 저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로가기", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        self.l.add_widget(sv); self.l.add_widget(bk)
        self.sc.add_widget(self.l); self.add_widget(self.sc)

    def on_f(self, instance, value):
        if value: Clock.schedule_once(lambda dt: self.sc.scroll_to(instance), 0.2)

    def get_pic(self, *a): # 4번: 안드로이드 사진첩
        from kivy.uix.filechooser import FileChooserIconView
        p_path = '/sdcard' if platform == 'android' else '.'
        fc = FileChooserIconView(path=p_path, filters=['*.jpg', '*.png'])
        btn = Button(text="이 사진으로 선택", size_hint_y=0.15, font_name=DF)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn)
        pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
        def select(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=select); pop.open()

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['img'] = self.img.source
        new_c['inventory'] = self.char_data.get('inventory', '')
        d['chars'][idx] = new_char = new_c
        store.put(acc, **d); self.manager.current = 'char_select'

# --- 인벤토리 화면 ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리", font_name=DF, size_hint_y=0.1))
        self.ti = SInput(text=char_data.get('inventory', ''), multiline=True)
        l.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=0.15, spacing=10)
        sv = Button(text="저장", font_name=DF, background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = Button(text="뒤로", font_name=DF, background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); l.add_widget(btns); self.add_widget(l)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        d['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **d); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PristonApp().run()
