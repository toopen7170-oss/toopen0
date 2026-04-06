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
from kivy.core.window import Window

# --- [초강력 폰트 로드 로직] ---
# 1. 폰트 파일명 설정 (사용자가 바꾼 font.ttf)
FONT_NAME = "font.ttf"

# 2. 실행 환경에 따른 실제 경로 추출 (이게 핵심입니다)
if getattr(sys, 'frozen', False):
    # 빌드된 환경 (PyInstaller / Android 등)
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # 일반 파이썬 실행 환경
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

FONT_PATH = os.path.join(BASE_PATH, FONT_NAME)

# 3. 폰트 등록 시도
DF = None
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_PATH)
        # 4. Kivy 기본 폰트 강제 고정
        Config.set('kivy', 'default_font', ['KFont', FONT_PATH, FONT_PATH, FONT_PATH, FONT_PATH])
        Config.write() # 설정을 파일에 즉시 기록
        DF = "KFont"
        print(f"Success: Font loaded from {FONT_PATH}")
    except Exception as e:
        print(f"Error registering font: {e}")
else:
    # 만약 위 경로에 없다면 현재 폴더에서 한 번 더 찾기
    if os.path.exists(FONT_NAME):
        LabelBase.register(name="KFont", fn_regular=FONT_NAME)
        DF = "KFont"
        print("Success: Font loaded from current directory")

# 키보드 대응 모드 설정
Window.softinput_mode = "below_target"

# 데이터 저장소
store = JsonStore('priston_v1_1.json')

# --- 안드로이드 사진 권한 ---
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.MANAGE_EXTERNAL_STORAGE])
    except Exception as e: print(f"Permission: {e}")

# --- 공통 위젯 (폰트 기본값 DF 적용) ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = kw.get('multiline', False)
        self.size_hint_y = None
        self.height = 110 

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 150

# --- 화면 클래스들 (코드 동일하므로 생략하지 않고 전체 통합) ---
# [MainMenu, CharSelect, Detail, Inventory 클래스는 이전과 동일하므로 DF 변수를 그대로 사용합니다]
# (지면상 생략하지만, 위젯 생성 시 font_name=DF가 들어간 부분들이 잘 작동할 것입니다.)

# --- 기존 화면 클래스들 유지 ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.layout.add_widget(Label(text="[PT1 통합 검색]", font_size='22sp', size_hint_y=0.1, font_name=DF))
        
        s_box = BoxLayout(size_hint_y=None, height=120, spacing=5)
        self.stti = SInput(hint_text="계정/캐릭터 검색...")
        s_btn = Button(text="검색", font_name=DF, size_hint_x=0.25, background_color=(0.2, 0.6, 1, 1))
        s_btn.bind(on_release=self.refresh)
        s_box.add_widget(self.stti); s_box.add_widget(s_btn); self.layout.add_widget(s_box)

        add_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.7, 0.3, 1))
        add_btn.bind(on_release=self.add_pop); self.layout.add_widget(add_btn)

        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.grid); self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def refresh(self, *a):
        self.grid.clear_widgets()
        q = self.stti.text.strip().lower()
        for k in list(store.keys()):
            d = store.get(k)
            match = not q or q in k.lower()
            if not match:
                for idx in d.get('chars', {}):
                    if any(q in str(v).lower() for v in d['chars'][idx].values()):
                        match = True; break
            if match:
                row = BoxLayout(size_hint_y=None, height=140, spacing=5)
                acc_btn = SBtn(text=f"계정: {k}", size_hint_x=0.8, background_color=(0.1, 0.2, 0.4, 1))
                acc_btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: self.confirm_del(n))
                row.add_widget(acc_btn); row.add_widget(del_btn); self.grid.add_widget(row)

    def confirm_del(self, n):
        c = BoxLayout(orientation='vertical', padding=15, spacing=15)
        c.add_widget(Label(text=f"'{n}'\n삭제하시겠습니까?", font_name=DF, halign='center'))
        btns = BoxLayout(spacing=10, size_hint_y=0.4)
        ok = Button(text="삭제", background_color=(0.8, 0, 0, 1), font_name=DF)
        no = Button(text="취소", font_name=DF)
        btns.add_widget(ok); btns.add_widget(no); c.add_widget(btns)
        pop = Popup(title="경고", content=c, size_hint=(0.8, 0.4))
        ok.bind(on_release=lambda x: [store.delete(n), self.refresh(), pop.dismiss()])
        no.bind(on_release=pop.dismiss); pop.open()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=10, spacing=10)
        inp = SInput(hint_text="계정 이름 입력")
        btn = SBtn(text="생성", background_color=(0.1, 0.7, 0.3, 1))
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.8, 0.4))
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
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=DF, size_hint_y=0.1))
        g = GridLayout(cols=2, spacing=10)
        for i in range(1, 7):
            name = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            btn = SBtn(text=name, background_color=(0.3, 0.3, 0.5, 1))
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
        sc = ScrollView(do_scroll_x=False, do_scroll_y=True); self.l = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.l.bind(minimum_height=self.l.setter('height'))
        
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if img_src else '', size_hint_y=None, height=450); self.l.add_widget(self.img)
        br = BoxLayout(size_hint_y=None, height=130, spacing=10)
        btn_pic = SBtn(text="사진 변경", background_color=(0.2, 0.5, 0.8, 1)); btn_pic.bind(on_release=self.get_pic)
        btn_inv = SBtn(text="인벤토리", background_color=(0.6, 0.4, 0.2, 1)); btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        br.add_widget(btn_pic); br.add_widget(btn_inv); self.l.add_widget(br)

        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.ins = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=90, spacing=10); row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.3))
            ti = SInput(text=str(self.char_data.get(f, ''))); ti.bind(focus=lambda inst, val: Clock.schedule_once(lambda dt: sc.scroll_to(inst, padding=100), 0.1) if val else None)
            self.ins[f] = ti; row.add_widget(ti); self.l.add_widget(row)
        
        sv = SBtn(text="캐릭터 저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        self.l.add_widget(sv); self.l.add_widget(bk); sc.add_widget(self.l); self.add_widget(sc)

    def get_pic(self, *a):
        from kivy.uix.filechooser import FileChooserIconView
        p_path = '/sdcard' if platform == 'android' else '.'
        fc = FileChooserIconView(path=p_path, filters=['*.jpg', '*.png', '*.jpeg']); btn = Button(text="결정", size_hint_y=0.2, font_name=DF)
        content = BoxLayout(orientation='vertical'); content.add_widget(fc); content.add_widget(btn); pop = Popup(title="사진 선택", content=content, size_hint=(0.9, 0.9))
        def sel(x):
            if fc.selection: self.img.source = fc.selection[0]; pop.dismiss()
        btn.bind(on_release=sel); pop.open()

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}; new_c['img'] = self.img.source; new_c['inventory'] = self.char_data.get('inventory', '')
        d['chars'][idx] = new_c; store.put(acc, **d); self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        l.add_widget(Label(text=f"[{char_data.get('이름', '캐릭')}] 인벤토리", font_name=DF, size_hint_y=0.1))
        
        sc_inv = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.ti = SInput(text=char_data.get('inventory', ''), multiline=True)
        self.ti.size_hint_y = None
        self.ti.height = 1600 
        self.ti.bind(focus=lambda inst, val: Clock.schedule_once(lambda dt: sc_inv.scroll_to(inst, padding=120), 0.1) if val else None)
        sc_inv.add_widget(self.ti); l.add_widget(sc_inv)
        
        btns = BoxLayout(size_hint_y=None, height=130, spacing=10)
        sv = Button(text="저장", font_name=DF, background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = Button(text="닫기", font_name=DF, background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); l.add_widget(btns); self.add_widget(l)

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc); d['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **d); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory')); return sm

if __name__ == '__main__': PristonApp().run()
