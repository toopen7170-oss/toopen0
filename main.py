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

# [폰트 설정]
FONT_PATH = 'font.ttf'
K_FONT = 'Roboto'
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_PATH)
        K_FONT = "KFont"
    except: pass

store = JsonStore('pt1_final_v15.json')

# [디자인] 커스텀 입력창
class KTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.multiline = False
        self.font_size = '16sp'
        # 글씨 위치 아래로 내림
        self.padding = [dp(10), dp(20), dp(10), dp(5)] 

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
    msg = Label(text=text, font_name=K_FONT, halign='center', valign='middle')
    msg.bind(size=msg.setter('text_size'))
    content.add_widget(msg)
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

class MainMenu(Screen):
    def on_enter(self): self.refresh_list()
    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        search_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_ti = KTextInput(text=query, hint_text="통합 검색")
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.search_ti.text.strip()))
        search_box.add_widget(self.search_ti); search_box.add_widget(s_btn)
        root.add_widget(search_box)
        root.add_widget(SBtn(text="+ 새 계정 만들기", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_account_popup))
        scroll = ScrollView(do_scroll_x=False)
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        for acc_name in sorted(store.keys()):
            acc_data = store.get(acc_name)
            if query:
                json_str = json.dumps(acc_data, ensure_ascii=False).lower()
                if query.lower() not in json_str and query.lower() not in acc_name.lower(): continue
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            acc_btn = SBtn(text=f"계정: {acc_name}", bg=(0.3, 0.3, 0.3, 1))
            acc_btn.bind(on_release=lambda x, n=acc_name: self.go_slots(n))
            del_btn = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda x, n=acc_name: show_confirm("삭제 확인", f"'{n}'을 삭제할까요?", lambda: self.del_acc(n)))
            row.add_widget(acc_btn); row.add_widget(del_btn); self.list_box.add_widget(row)
        scroll.add_widget(self.list_box); root.add_widget(scroll); self.add_widget(root)
    def add_account_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10)); ti = KTextInput(hint_text="ID 입력")
        content.add_widget(ti); btn = SBtn(text="생성", bg=(0.1, 0.5, 0.3, 1))
        content.add_widget(btn); popup = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(ti.text, popup)); popup.open()
    def save_acc(self, name, popup):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"슬롯 {i+1}", "inven": [], "photos": []} for i in range(6)])
            popup.dismiss(); self.refresh_list()
    def del_acc(self, name): store.delete(name); self.refresh_list()
    def go_slots(self, name): self.manager.cur_acc = name; self.manager.current = 'slots'

class Slots(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; slots = store.get(acc)['slots']
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"계정: {acc}", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            char_name = slots[i].get('이름', f'슬롯 {i+1}')
            btn = Button(text=f"{i+1}번\n{char_name}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx)); grid.add_widget(btn)
        layout.add_widget(grid); layout.add_widget(SBtn(text="뒤로가기", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)
    def go_detail(self, idx): self.manager.cur_idx = idx; self.manager.current = 'detail'

# --- 3. 캐릭터 상세 (자동 스크롤 로직 전면 수정) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]; self.photo_list = self.data.get('photos', []) 
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.scroll = ScrollView(do_scroll_x=False)
        # 하단 여백 대폭 증가 (dp(1000)으로 설정하여 무조건 위로 끝까지 올라가게 함)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[0, 0, 0, dp(1000)])
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.img_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
        self.img_grid.bind(minimum_height=self.img_grid.setter('height')); self.refresh_photos()
        self.content.add_widget(self.img_grid)
        btn_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        btn_box.add_widget(SBtn(text="📷 사진 추가", bg=(0.2, 0.5, 0.8, 1), on_release=self.pick_photo))
        btn_box.add_widget(SBtn(text="📦 인벤토리", bg=(0.8, 0.5, 0.2, 1), on_release=lambda x: setattr(self.manager, 'current', 'inventory')))
        self.content.add_widget(btn_box)

        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            ti = KTextInput(text=str(self.data.get(f, '')))
            # [수정] 터치하자마자(on_touch_down) 스크롤 로직 작동 시도
            ti.bind(focus=self.force_scroll)
            row.add_widget(ti); self.inputs[f] = ti
            self.content.add_widget(row)
            
        self.scroll.add_widget(self.content); root.add_widget(self.scroll)
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save_char))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav); self.add_widget(root)

    # [수정] 강제 스크롤 함수: 터치한 칸을 화면 꼭대기로 보내버림
    def force_scroll(self, instance, value):
        if value:
            # 키보드 올라오는 시간에 맞춰 두 번에 걸쳐 확실히 밀어올림
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance, padding=dp(500)), 0.1)
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance, padding=dp(500)), 0.4)

    def refresh_photos(self):
        self.img_grid.clear_widgets()
        for i, path in enumerate(self.photo_list):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180))
            box.add_widget(AsyncImage(source=path, allow_stretch=True))
            del_p = Button(text="삭제", size_hint_y=None, height=dp(35), font_name=K_FONT, background_color=(0.7, 0.2, 0.2, 1))
            del_p.bind(on_release=lambda x, idx=i: show_confirm("삭제", "삭제하시겠습니까?", lambda: self.del_photo(idx)))
            box.add_widget(del_p); self.img_grid.add_widget(box)
    def pick_photo(self, *args): Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_photo), 0.1)
    def set_photo(self, selection):
        if selection: self.photo_list.append(selection[0]); self.refresh_photos()
    def del_photo(self, idx): self.photo_list.pop(idx); self.refresh_photos()
    def save_char(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        for f in self.fields: slots[idx][f] = self.inputs[f].text
        slots[idx]['photos'] = self.photo_list
        store.put(acc, slots=slots); show_confirm("알림", "저장되었습니다.")

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets(); acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('inven', [])
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=[0, 0, 0, dp(1000)])
        self.list_box.bind(minimum_height=self.list_box.setter('height')); self.draw_items()
        self.scroll.add_widget(self.list_box); root.add_widget(self.scroll)
        nav = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        nav.add_widget(SBtn(text="+ 추가", bg=(0.1, 0.4, 0.6, 1), on_release=self.add_i))
        nav.add_widget(SBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save_i))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        root.add_widget(nav); self.add_widget(root)
    def draw_items(self):
        self.list_box.clear_widgets()
        for i, val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
            ti = KTextInput(text=val)
            ti.bind(text=lambda instance, v, idx=i: self.update_val(idx, v))
            ti.bind(focus=lambda instance, v: Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance, padding=dp(500)), 0.3) if v else None)
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, idx=i: show_confirm("삭제", "삭제할까요?", lambda: self.rem_i(idx)))
            row.add_widget(ti); row.add_widget(del_b); self.list_box.add_widget(row)
    def update_val(self, idx, v): self.items[idx] = v
    def add_i(self, *args): self.items.append(""); self.draw_items()
    def rem_i(self, idx): self.items.pop(idx); self.draw_items()
    def save_i(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items; store.put(acc, slots=slots); show_confirm("알림", "저장되었습니다.")

class PTApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition()); sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main')); sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
