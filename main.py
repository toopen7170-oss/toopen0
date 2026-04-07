import os
import json
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
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from plyer import filechooser

# [폰트 설정] font.ttf 파일 연결
FONT_PATH = 'font.ttf'
if os.path.exists(FONT_PATH):
    LabelBase.register(name="KFont", fn_regular=FONT_PATH)
    K_FONT = "KFont"
else:
    K_FONT = 'Roboto'

store = JsonStore('pt1_final_v6.json')

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

# 공용 삭제 확인 팝업
def show_confirm(title, text, callback=None):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(text=text, font_name=K_FONT, halign='center'))
    btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
    
    close_btn = Button(text="취소", font_name=K_FONT)
    btn_layout.add_widget(close_btn)
    
    if callback:
        ok_btn = Button(text="확인", font_name=K_FONT, background_color=(0.8, 0.2, 0.2, 1))
        ok_btn.bind(on_release=lambda x: [callback(), popup.dismiss()])
        btn_layout.add_widget(ok_btn)
    
    content.add_widget(btn_layout)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    close_btn.bind(on_release=popup.dismiss)
    popup.open()

# --- 메인 화면 (계정 검색 및 관리) ---
class MainMenu(Screen):
    def on_enter(self):
        self.refresh_list()

    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        search_row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_ti = TextInput(text=query, hint_text="계정/캐릭터/아이템 통합 검색", font_name=K_FONT, multiline=False)
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.search_ti.text.strip()))
        search_row.add_widget(self.search_ti); search_row.add_widget(s_btn)
        root.add_widget(search_row)

        root.add_widget(SBtn(text="+ 새 계정 만들기", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_acc_pop))

        scroll = ScrollView(do_scroll_x=False)
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        for acc_name in store.keys():
            acc_data = store.get(acc_name)
            if query:
                full_content = json.dumps(acc_data, ensure_ascii=False).lower()
                if query.lower() not in full_content and query.lower() not in acc_name.lower(): continue

            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            btn = SBtn(text=f"계정: {acc_name}", bg=(0.3, 0.3, 0.3, 1))
            btn.bind(on_release=lambda x, n=acc_name: self.go_slots(n))
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, n=acc_name: show_confirm("삭제 확인", f"'{n}' 계정을 삭제할까요?", lambda: self.del_acc(n)))
            row.add_widget(btn); row.add_widget(del_b)
            self.list_box.add_widget(row)

        scroll.add_widget(self.list_box); root.add_widget(scroll)
        self.add_widget(root)

    def add_acc_pop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        ti = TextInput(font_name=K_FONT, multiline=False); content.add_widget(ti)
        b = SBtn(text="생성", bg=(0.1, 0.5, 0.3, 1))
        content.add_widget(b)
        pop = Popup(title="계정명", content=content, size_hint=(0.8, 0.4))
        b.bind(on_release=lambda x: self.create_acc(ti.text, pop))
        pop.open()

    def create_acc(self, name, pop):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"캐릭터 {i+1}", "inven": []} for i in range(6)])
            pop.dismiss(); self.refresh_list()

    def del_acc(self, name):
        store.delete(name); self.refresh_list()

    def go_slots(self, name):
        self.manager.cur_acc = name; self.manager.current = 'slots'

# --- 캐릭터 슬롯 화면 ---
class Slots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        slots = store.get(acc)['slots']
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"<{acc}> 캐릭터 선택", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            c_name = slots[i].get('이름', f'캐릭터 {i+1}')
            b = Button(text=f"{i+1}번 슬롯\n{c_name}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            b.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(b)
        layout.add_widget(grid)
        layout.add_widget(SBtn(text="메인으로 가기", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.cur_idx = idx; self.manager.current = 'detail'

# --- 3. 캐릭터 상세/수정 (사진 추가/삭제 버튼 구현) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 스크롤 가능 영역
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # [해결] 사진 영역 구조 수정 ( AsyncImage + 버튼 2개 )
        photo_root = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(310), spacing=dp(5))
        
        img_path = self.data.get('photo', 'placeholder.png')
        self.img = AsyncImage(source=img_path, size_hint_y=None, height=dp(250), allow_stretch=True)
        photo_root.add_widget(self.img)
        
        # 사진 제어 버튼 (추가/삭제)
        photo_btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        add_photo_btn = Button(text="📷 사진 추가 (갤러리)", font_name=K_FONT, background_color=(0.2, 0.5, 0.8, 1))
        add_photo_btn.bind(on_release=self.pick_photo)
        
        del_photo_btn = Button(text="❌ 사진 삭제", font_name=K_FONT, background_color=(0.8, 0.2, 0.2, 1))
        del_photo_btn.bind(on_release=lambda x: show_confirm("사진 삭제", "사진을 삭제하시겠습니까?", self.remove_photo))
        
        photo_btns.add_widget(add_photo_btn); photo_btns.add_widget(del_photo_btn)
        photo_root.add_widget(photo_btns)
        
        content.add_widget(photo_root)
        
        # 인벤토리 이동 버튼
        content.add_widget(SBtn(text="📦 인벤토리 관리", bg=(0.8, 0.5, 0.2, 1), on_release=self.go_inven))
        
        # 필드 입력
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            ti = TextInput(text=str(self.data.get(f, '')), font_name=K_FONT, multiline=False)
            row.add_widget(ti); self.inputs[f] = ti
            content.add_widget(row)
            
        scroll.add_widget(content)
        root.add_widget(scroll)
        
        # 제어 버튼
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav)
        self.add_widget(root)

    def pick_photo(self, *args):
        # Clock을 사용하여 안드로이드 갤러리 앱과 충돌 방지
        Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_photo), 0.1)

    def set_photo(self, selection):
        if selection:
            self.img.source = selection[0]

    # [해결] 사진 삭제 기능 구현 및 확인 팝업 연결
    def remove_photo(self):
        self.img.source = 'placeholder.png' # 기본 이미지로 변경
        self.manager.cur_idx = self.manager.cur_idx # 화면 새로고침 효과
        show_confirm("알림", "사진이 삭제되었습니다. (저장을 해야 반영됩니다)")

    def save(self, *args):
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        for f in self.fields:
            slots[idx][f] = self.inputs[f].text
        # AsyncImage의 소스(경로)를 저장
        slots[idx]['photo'] = self.img.source
        store.put(acc, slots=slots)
        show_confirm("알림", "정보가 저장되었습니다.")

    def go_inven(self, *args): self.manager.current = 'inventory'

# --- 4. 인벤토리 관리 화면 ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        acc_data = store.get(acc)
        self.items = acc_data['slots'][idx].get('inven', [])
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text="[인벤토리 편집]", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        self.draw_items()
        
        scroll.add_widget(self.list_box); layout.add_widget(scroll)
        
        nav = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        nav.add_widget(SBtn(text="+ 아이템 추가", bg=(0.1, 0.4, 0.6, 1), on_release=self.add_i))
        nav.add_widget(SBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save_i))
        nav.add_widget(SBtn(text="뒤로가기", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        layout.add_widget(nav)
        self.add_widget(layout)

    def draw_items(self):
        self.list_box.clear_widgets()
        for i, val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
            ti = TextInput(text=val, font_name=K_FONT, multiline=False)
            ti.bind(text=lambda instance, v, idx=i: self.update_val(idx, v))
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, idx=i: show_confirm("아이템 삭제", "삭제하시겠습니까?", lambda: self.rem_i(idx)))
            row.add_widget(ti); row.add_widget(del_b)
            self.list_box.add_widget(row)

    def update_val(self, idx, v): self.items[idx] = v
    def add_i(self, *args): self.items.append(""); self.draw_items()
    def rem_i(self, idx): self.items.pop(idx); self.draw_items()
    
    def save_i(self, *args):
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items
        store.put(acc, slots=slots)
        show_confirm("알림", "인벤토리가 저장되었습니다.")

class PTApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
