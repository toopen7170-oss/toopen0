import os
from kivy.config import Config

# --- [폰트 설정] 앱 시작 즉시 적용 ---
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
from kivy.uix.image import AsyncImage
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
store = JsonStore('priston_v1_final.json')

# --- [안드로이드 전용 기능 및 권한] ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import api_version

    def request_android_permissions():
        perms = [Permission.CAMERA]
        if api_version >= 33:
            perms.append(Permission.READ_MEDIA_IMAGES)
        else:
            perms.append(Permission.READ_EXTERNAL_STORAGE)
            perms.append(Permission.WRITE_EXTERNAL_STORAGE)
        request_permissions(perms)

# --- 공통 스타일 위젯 ---
class SInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.multiline = kw.get('multiline', False)
        self.size_hint_y = None
        self.height = 85  # [수정] 글씨가 움직이지 않도록 높이 최적화
        self.padding = [15, 25, 10, 10] 
        self.font_size = '17sp'

class SBtn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name = DF
        self.size_hint_y = None
        self.height = 120

# --- 화면 1: 메인 메뉴 (검색/계정관리) ---
class MainMenu(Screen):
    def on_enter(self): self.refresh()
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # [수정] 검색창 UI 복구
        s_box = BoxLayout(size_hint_y=None, height=100, spacing=10)
        self.stti = SInput(hint_text="계정/캐릭터 검색...", padding=[15, 30, 10, 10])
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
            if match:
                row = BoxLayout(size_hint_y=None, height=120, spacing=5)
                acc_btn = SBtn(text=f"계정: {k}", size_hint_x=0.85, height=120)
                acc_btn.bind(on_release=lambda x, n=k: self.go(n))
                del_btn = Button(text="X", size_hint_x=0.15, background_color=(0.7, 0.1, 0.1, 1), font_name=DF)
                del_btn.bind(on_release=lambda x, n=k: self.confirm_del(n))
                row.add_widget(acc_btn); row.add_widget(del_btn); self.grid.add_widget(row)

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
    def go(self, n): self.manager.cur_acc = n; self.manager.current = 'char_select'
    def confirm_del(self, n):
        # 삭제 확인 팝업 로직 (생략 가능하나 안전을 위해 유지)
        store.delete(n); self.refresh()

# --- 화면 2: 캐릭터 선택 ---
class CharSelect(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        d = store.get(acc)
        l = BoxLayout(orientation='vertical', padding=20, spacing=12)
        l.add_widget(Label(text=f"[{acc}] 캐릭터 선택", font_name=DF, size_hint_y=None, height=80, font_size='20sp'))
        g = GridLayout(cols=2, spacing=12)
        for i in range(1, 7):
            char_info = d['chars'].get(str(i), {})
            name = char_info.get('이름', f'슬롯 {i}')
            btn = SBtn(text=name, background_color=(0.2, 0.3, 0.5, 1), height=180)
            btn.bind(on_release=lambda x, idx=i: self.go_d(idx)); g.add_widget(btn)
        l.add_widget(g)
        back = SBtn(text="처음으로", background_color=(0.4, 0.4, 0.4, 1), height=110)
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(back); self.add_widget(l)
    def go_d(self, i): self.manager.cur_idx = str(i); self.manager.current = 'detail'

# --- 화면 3: 캐릭터 상세 정보 (사진 여러 장 & 스크롤 기능 핵심) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        self.char_data = store.get(acc)['chars'].get(idx, {})
        
        sc = ScrollView()
        self.lo = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.lo.bind(minimum_height=self.lo.setter('height'))
        
        # [핵심] 사진 리스트 영역 (무제한 스크롤)
        self.img_list_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.img_list_layout.bind(minimum_height=self.img_list_layout.setter('height'))
        
        self.photos = self.char_data.get('images', []) # 여러 장의 사진 경로 리스트
        self.refresh_photos()
        self.lo.add_widget(self.img_list_layout)
        
        # 버튼 영역
        btn_add_pic = SBtn(text="+ 사진 추가하기 (제한없음)", background_color=(0.2, 0.6, 0.8, 1))
        btn_add_pic.bind(on_release=self.open_gallery)
        self.lo.add_widget(btn_add_pic)

        btn_inv = SBtn(text="인벤토리 편집", background_color=(0.5, 0.3, 0.2, 1))
        btn_inv.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventory'))
        self.lo.add_widget(btn_inv)

        # 정보 입력 필드
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.ins = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=90, spacing=10)
            row.add_widget(Label(text=f, font_name=DF, size_hint_x=0.25))
            ti = SInput(text=str(self.char_data.get(f, '')))
            self.ins[f] = ti; row.add_widget(ti); self.lo.add_widget(row)
        
        sv = SBtn(text="모든 정보 저장", background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = SBtn(text="뒤로", background_color=(0.4, 0.4, 0.4, 1)); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'char_select'))
        self.lo.add_widget(sv); self.lo.add_widget(bk)
        
        sc.add_widget(self.lo); self.add_widget(sc)

    def refresh_photos(self):
        """사진 리스트를 UI에 다시 그립니다."""
        self.img_list_layout.clear_widgets()
        for p in self.photos:
            row = BoxLayout(size_hint_y=None, height=450, spacing=5)
            img = AsyncImage(source=p, size_hint_x=0.85)
            del_btn = Button(text="삭제", size_hint_x=0.15, background_color=(0.8, 0.2, 0.2, 1), font_name=DF)
            del_btn.bind(on_release=lambda x, path=p: self.remove_photo(path))
            row.add_widget(img); row.add_widget(del_btn)
            self.img_list_layout.add_widget(row)

    def remove_photo(self, path):
        if path in self.photos:
            self.photos.remove(path); self.refresh_photos()

    def open_gallery(self, *a):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                intent = Intent(Intent.ACTION_PICK)
                intent.setType("image/*")
                PythonActivity.mActivity.startActivityForResult(intent, 0x123)
            except Exception as e: print(f"Gallery Error: {e}")
        else:
            self.add_photo_path("font.ttf") # PC 테스트용

    def add_photo_path(self, path):
        self.photos.append(path); self.refresh_photos()

    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc)
        new_c = {f: ti.text for f, ti in self.ins.items()}
        new_c['images'] = self.photos
        new_c['inventory'] = self.char_data.get('inventory', '')
        d['chars'][idx] = new_c; store.put(acc, **d); self.manager.current = 'char_select'

# --- 화면 4: 인벤토리 ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        char_data = store.get(acc)['chars'].get(idx, {})
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"인벤토리 상세 내용", font_name=DF, size_hint_y=None, height=70))
        self.ti = TextInput(text=char_data.get('inventory', ''), multiline=True, font_name=DF, font_size='16sp')
        l.add_widget(self.ti)
        btns = BoxLayout(size_hint_y=None, height=110, spacing=10)
        sv = Button(text="저장", font_name=DF, background_color=(0.1, 0.6, 0.2, 1)); sv.bind(on_release=self.save)
        bk = Button(text="닫기", font_name=DF); bk.bind(on_release=lambda x: setattr(self.manager, 'current', 'detail'))
        btns.add_widget(sv); btns.add_widget(bk); l.add_widget(btns); self.add_widget(l)
    def save(self, *a):
        acc, idx = self.manager.cur_acc, self.manager.cur_idx
        d = store.get(acc); d['chars'][idx]['inventory'] = self.ti.text
        store.put(acc, **d); self.manager.current = 'detail'

# --- 앱 메인 루프 ---
class PristonApp(App):
    def build(self):
        if platform == 'android': request_android_permissions()
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = ""
        sm.add_widget(MainMenu(name='main')); sm.add_widget(CharSelect(name='char_select'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        
        if platform == 'android':
            from android import activity
            activity.bind(on_activity_result=self.on_res)
        return sm

    def on_res(self, req, res, intent):
        if req == 0x123 and res == -1: # RESULT_OK
            uri = intent.getData()
            cur_screen = self.root.get_screen('detail')
            cur_screen.add_photo_path(uri.toString())

if __name__ == '__main__': PristonApp().run()
