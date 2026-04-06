import os
from kivy.config import Config

# --- [폰트 강제 설정] 앱 시작 즉시 적용 ---
FONT_NAME = "font.ttf"
if os.path.exists(FONT_NAME):
    Config.set('kivy', 'default_font', ['KFont', FONT_NAME, FONT_NAME, FONT_NAME, FONT_NAME])

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

# 폰트 등록
DF = None
if os.path.exists(FONT_NAME):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_NAME)
        DF = "KFont"
    except: pass

Window.softinput_mode = "below_target"
store = JsonStore('priston_v1_1.json')

# --- [안드로이드 전용 기능] ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import api_version
    from jnius import autoclass, cast

    def request_android_permissions():
        perms = [Permission.CAMERA]
        if api_version >= 33:
            perms.append(Permission.READ_MEDIA_IMAGES)
        else:
            perms.append(Permission.READ_EXTERNAL_STORAGE)
            perms.append(Permission.WRITE_EXTERNAL_STORAGE)
        request_permissions(perms)

# --- 공통 위젯 ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = kw.get('multiline', False)
        self.size_hint_y = None
        # [2번 문제 해결] 높이를 80으로 늘리고 글씨가 안 잘리게 여백(padding) 조정
        self.height = 80
        self.padding = [10, 20, 10, 10] 
        self.font_size = '18sp'

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 130

# --- 화면 클래스들 ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # [1번 문제 해결] 상단 검색 영역 UI 복구
        s_box = BoxLayout(size_hint_y=None, height=100, spacing=10)
        self.stti = SInput(hint_text="계정/캐릭터 검색...", padding=[10, 25, 10, 10])
        s_btn = Button(text="검색", font_name=DF, size_hint_x=0.25, background_color=(0.1, 0.4, 0.7, 1))
        s_btn.bind(on_release=self.refresh)
        s_box.add_widget(self.stti); s_box.add_widget(s_btn)
        self.layout.add_widget(s_box)

        add_btn = SBtn(text="+ 새 계정 만들기", background_color=(0.1, 0.6, 0.3, 1), height=110)
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
                row = BoxLayout(size_hint_y=None, height=120, spacing=5)
                acc_btn = SBtn(text=f"계정: {k}", size_hint_x=0.85, height=120)
                acc_btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.7, 0.1, 0.1, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: self.confirm_del(n))
                row.add_widget(acc_btn); row.add_widget(del_btn); self.grid.add_widget(row)

    def confirm_del(self, n):
        c = BoxLayout(orientation='vertical', padding=20, spacing=20)
        c.add_widget(Label(text=f"'{n}' 계정을\n삭제하시겠습니까?", font_name=DF, halign='center'))
        btns = BoxLayout(spacing=10, size_hint_y=None, height=100)
        ok = Button(text="삭제", background_color=(0.8, 0, 0, 1), font_name=DF)
        no = Button(text="취소", font_name=DF)
        btns.add_widget(ok); btns.add_widget(no); c.add_widget(btns)
        pop = Popup(title="경고", content=c, size_hint=(0.85, 0.4))
        ok.bind(on_release=lambda x: [store.delete(n), self.refresh(), pop.dismiss()])
        no.bind(on_release=pop.dismiss); pop.open()

    def add_pop(self, *a):
        c = BoxLayout(orientation='vertical', padding=20, spacing=15)
        inp = SInput(hint_text="새 계정 이름")
        btn = SBtn(text="생성하기", background_color=(0.1, 0.6, 0.3, 1), height=100)
        c.add_widget(inp); c.add_widget(btn)
        pop = Popup(title="계정 추가", content=c, size_hint=(0.85, 0.35))
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
        l = BoxLayout(orientation='vertical', padding=20, spacing=12)
        l.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=DF, size_hint_y=None, height=80, font_size='20sp'))
        g = GridLayout(cols=2, spacing=12)
        for i in range(1, 7):
            name = d['chars'].get(str(i), {}).get('이름', f'슬롯 {i}')
            btn = SBtn(text=name, background_color=(0.2, 0.3, 0.5, 1), height=180)
            btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        l.add_widget(g)
        back = SBtn(text="처음으로", background_color=(0.4, 0.4, 0.4, 1), height=110)
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(back); self.add_widget(l)
    def go_d(self, i):
        self.manager.cur_idx = str(i); self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        sc = ScrollView(); self.lo = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.lo.bind(minimum_height=self.lo.setter('height'))
        
        img_src = self.char_data.get('img', '')
        self.img = Image(source=img_src if img_src and os.path.exists(img_src) else 'font.ttf', size_hint_y=None, height=500)
        self.lo.add_widget(self.img)
        
        br = BoxLayout(size_hint_y=None, height=120, spacing=10)
        btn_pic = SBtn(text="사진 변경", background_color=(0.2, 0.5, 0.8, 1)); btn_pic.bind(on_release=self.open_gallery)
        btn_inv = SBtn(text="인벤토리", background_color=(0.5, 0.3, 0.2, 1)); btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        br.add_widget(btn_pic); br.add_widget(btn_inv); self.lo.add_widget(br)

        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.ins = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=90, spacing=10)
            row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.25))
            ti = SInput(text=str(self.char_data.get(f, '')))
            self.ins[f] = ti; row.add_widget(ti); self.lo.add_widget(row)
        
        sv = SBtn(text="캐릭터 저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        self.lo.add_widget(sv); self.lo.add_widget(bk); sc.add_widget(self.lo); self.add_widget(sc)

    # [3번 문제 해결] 팅김 방지를 위한 안드로이드 시스템 갤러리 호출
    def open_gallery(self, *a):
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                intent = Intent(Intent.ACTION_PICK)
                intent.setType("image/*")
                PythonActivity.mActivity.startActivityForResult(intent, 0x123)
                # 결과 처리는 앱 클래스에서 담당
            except Exception as e: print(f"Gallery Error: {e}")
        else:
            # PC 환경용 간이 선택기 (팅김 방지용)
            self.img.source = "font.ttf" 

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['img'] = self.img.source
        new_c['inventory'] = self.char_data.get('inventory', '')
        d['chars'][idx] = new_c; store.put(acc, **d); self.manager.current = 'char_select'

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"[{char_data.get('이름','캐릭')}] 인벤토리", font_name=DF, size_hint_y=None, height=70))
        self.ti = SInput(text=char_data.get('inventory', ''), multiline=True)
        self.ti.size_hint_y = 1 
        l.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=None, height=110, spacing=10)
        sv = Button(text="저장", font_name=DF, background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = Button(text="닫기", font_name=DF); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); l.add_widget(btns); self.add_widget(l)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc); d['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **d); self.manager.current = 'detail'

class PristonApp(App):
    def build(self):
        if platform == 'android': request_android_permissions()
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        
        # 안드로이드 갤러리 결과 처리 등록
        if platform == 'android':
            from android import activity
            activity.bind(on_activity_result=self.on_res)
        return sm

    def on_res(self, req, res, intent):
        if req == 0x123 and res == -1: # RESULT_OK
            uri = intent.getData()
            # URI를 이미지 경로로 설정
            self.root.get_screen('detail').img.source = uri.toString()

if __name__ == '__main__': PristonApp().run()
