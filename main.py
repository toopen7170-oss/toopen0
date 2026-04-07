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

# [시스템 설정] 한글 폰트 등록
FONT_PATH = 'font.ttf'
if os.path.exists(FONT_PATH):
    LabelBase.register(name="KFont", fn_regular=FONT_PATH)
    K_FONT = "KFont"
else:
    K_FONT = 'Roboto'

# 데이터 저장소 명칭 (버전 관리용)
store = JsonStore('priston_tale_v9.json')

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

def show_confirm(title, text, callback=None):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(text=text, font_name=K_FONT, halign='center', valign='middle'))
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

# --- 1. 메인 메뉴 (검색 기능) ---
class MainMenu(Screen):
    def on_enter(self):
        self.refresh_list()

    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 검색 영역
        search_row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_ti = TextInput(text=query, hint_text="계정 이름으로 검색...", font_name=K_FONT, multiline=False, padding=[dp(10), dp(15)])
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70), background_color=(0.2, 0.6, 0.8, 1))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.search_ti.text.strip()))
        search_row.add_widget(self.search_ti); search_row.add_widget(s_btn)
        root.add_widget(search_row)

        root.add_widget(SBtn(text="+ 새 계정 추가", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_acc_pop))

        # 계정 리스트 스크롤
        scroll = ScrollView(do_scroll_x=False)
        self.list_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        for acc_name in store.keys():
            if query and query.lower() not in acc_name.lower(): continue
            row = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(5))
            btn = SBtn(text=f"ID: {acc_name}", bg=(0.3, 0.3, 0.3, 1))
            btn.bind(on_release=lambda x, n=acc_name: self.go_slots(n))
            del_b = Button(text="삭제", font_name=K_FONT, size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, n=acc_name: show_confirm("계정 삭제", f"'{n}' 계정을 삭제하시겠습니까?", lambda: self.del_acc(n)))
            row.add_widget(btn); row.add_widget(del_b)
            self.list_box.add_widget(row)

        scroll.add_widget(self.list_box); root.add_widget(scroll)
        self.add_widget(root)

    def add_acc_pop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        ti = TextInput(font_name=K_FONT, multiline=False, padding=[dp(10), dp(15)]); content.add_widget(ti)
        b = SBtn(text="생성하기", bg=(0.1, 0.5, 0.3, 1))
        content.add_widget(b)
        pop = Popup(title="새 계정명 입력", content=content, size_hint=(0.8, 0.4))
        b.bind(on_release=lambda x: self.create_acc(ti.text, pop))
        pop.open()

    def create_acc(self, name, pop):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"캐릭터 {i+1}", "inven": [], "photos": []} for i in range(6)])
            pop.dismiss(); self.refresh_list()

    def del_acc(self, name):
        store.delete(name); self.refresh_list()

    def go_slots(self, name):
        self.manager.cur_acc = name; self.manager.current = 'slots'

# --- 2. 슬롯 선택 ---
class Slots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        slots = store.get(acc)['slots']
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        layout.add_widget(Label(text=f"접속 계정: {acc}", font_name=K_FONT, size_hint_y=None, height=dp(30), color=(1, 0.8, 0, 1)))
        
        grid = GridLayout(cols=2, spacing=dp(15))
        for i in range(6):
            c_name = slots[i].get('이름', f'캐릭터 {i+1}')
            b = Button(text=f"Slot {i+1}\n{c_name}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            b.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(b)
        layout.add_widget(grid)
        layout.add_widget(SBtn(text="로그아웃 (메인으로)", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.cur_idx = idx; self.manager.current = 'detail'

# --- 3. 캐릭터 상세 정보 (스크롤 및 사진 정밀 수정) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        self.photo_list = self.data.get('photos', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # [스크롤 해결] do_scroll_x는 끄고 do_scroll_y만 활성화
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        content = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # 사진 그리드 (2열 구성)
        self.img_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        self.img_grid.bind(minimum_height=self.img_grid.setter('height'))
        self.refresh_photos()
        content.add_widget(self.img_grid)
        
        # 제어 버튼 레이아웃
        btn_row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        btn_row.add_widget(SBtn(text="📷 사진 추가", bg=(0.2, 0.5, 0.9, 1), on_release=self.pick_photo))
        btn_row.add_widget(SBtn(text="📦 인벤토리", bg=(0.9, 0.6, 0.2, 1), on_release=lambda x: setattr(self.manager, 'current', 'inventory')))
        content.add_widget(btn_row)
        
        # 상세 필드 입력창
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            f_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(75), spacing=dp(5))
            f_box.add_widget(Label(text=f"■ {f}", font_name=K_FONT, size_hint_y=None, height=dp(25), halign='left', text_size=(dp(300), None)))
            ti = TextInput(text=str(self.data.get(f, '')), font_name=K_FONT, multiline=False, size_hint_y=None, height=dp(45), padding=[dp(10), dp(12)])
            f_box.add_widget(ti); self.inputs[f] = ti
            content.add_widget(f_box)
            
        scroll.add_widget(content); root.add_widget(scroll)
        
        # 하단 고정 바
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="💾 데이터 저장", bg=(0.1, 0.6, 0.3, 1), on_release=self.save))
        nav.add_widget(SBtn(text="⬅ 뒤로가기", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav)
        self.add_widget(root)

    def refresh_photos(self):
        self.img_grid.clear_widgets()
        for i, path in enumerate(self.photo_list):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200), padding=dp(2))
            box.add_widget(AsyncImage(source=path, allow_stretch=True))
            del_p = Button(text="사진 삭제", size_hint_y=None, height=dp(35), font_name=K_FONT, background_color=(0.8, 0.2, 0.2, 1))
            del_p.bind(on_release=lambda x, idx=i: show_confirm("사진 삭제", "이 사진을 목록에서 지울까요?", lambda: self.del_photo(idx)))
            box.add_widget(del_p)
            self.img_grid.add_widget(box)

    def pick_photo(self, *args):
        Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_photo), 0.1)

    def set_photo(self, selection):
        if selection:
            self.photo_list.append(selection[0]); self.refresh_photos()

    def del_photo(self, idx):
        self.photo_list.pop(idx); self.refresh_photos()

    def save(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        for f in self.fields: slots[idx][f] = self.inputs[f].text
        slots[idx]['photos'] = self.photo_list
        store.put(acc, slots=slots)
        show_confirm("완료", "캐릭터 정보가 성공적으로 저장되었습니다.")

# --- 4. 인벤토리 관리 (깨짐 방지 완벽 대응) ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('inven', [])
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"아이템 목록 ({len(self.items)}개)", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        scroll = ScrollView(do_scroll_x=False)
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.draw_items()
        
        scroll.add_widget(self.list_box); layout.add_widget(scroll)
        
        nav = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        nav.add_widget(SBtn(text="+ 아이템 추가", bg=(0.1, 0.4, 0.7, 1), on_release=self.add_i))
        nav.add_widget(SBtn(text="💾 인벤 저장", bg=(0.1, 0.6, 0.3, 1), on_release=self.save_i))
        nav.add_widget(SBtn(text="돌아가기", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        layout.add_widget(nav)
        self.add_widget(layout)

    def draw_items(self):
        self.list_box.clear_widgets()
        for i, val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(5))
            # [깨짐 방지] TextInput에 폰트 필수 적용
            ti = TextInput(text=val, font_name=K_FONT, multiline=False, padding=[dp(10), dp(13)], background_color=(0.95, 0.95, 0.95, 1))
            ti.bind(text=lambda instance, v, idx=i: self.update_val(idx, v))
            del_b = Button(text="삭제", font_name=K_FONT, size_hint_x=None, width=dp(60), background_color=(0.8, 0.3, 0.3, 1))
            del_b.bind(on_release=lambda x, idx=i: show_confirm("아이템 삭제", "이 아이템을 삭제할까요?", lambda: self.rem_i(idx)))
            row.add_widget(ti); row.add_widget(del_b)
            self.list_box.add_widget(row)

    def update_val(self, idx, v): self.items[idx] = v
    def add_i(self, *args): self.items.append(""); self.draw_items()
    def rem_i(self, idx): self.items.pop(idx); self.draw_items()
    def save_i(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items
        store.put(acc, slots=slots)
        show_confirm("완료", "인벤토리 데이터가 저장되었습니다.")

class PTApp(App):
    def build(self):
        self.title = "Priston Tale Chart"
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail'))
        sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
