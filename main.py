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

# [폰트 설정] 4번 사진 폰트 오류 해결
K_FONT = "Roboto" # 기본값
FONT_PATH = 'font.ttf'
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name="KFont", fn_regular=FONT_PATH)
        K_FONT = "KFont"
    except Exception as e:
        print(f"Font Load Error: {e}")

# 데이터 파일 버전 (충돌 방지용)
store = JsonStore('pt1_final_v17.json')

# [입력창 커스텀] 글씨를 더 아래로 내림
class KTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.multiline = False
        self.font_size = '18sp'
        # [수정] padding [왼쪽, 위, 오른쪽, 아래] -> 위쪽(22)을 늘려 글자를 아래로 더 밀어냄
        self.padding = [dp(10), dp(22), dp(10), dp(5)] 
        self.background_color = (0.98, 0.98, 0.98, 1)

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

# --- 공용 확인 팝업 ---
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

# --- 1. 메인 화면 ---
class MainMenu(Screen):
    def on_enter(self): self.refresh_list()
    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        search_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_ti = KTextInput(hint_text="ID/아이템 검색")
        self.search_ti.text = query
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.search_ti.text.strip()))
        search_box.add_widget(self.search_ti); search_box.add_widget(s_btn)
        root.add_widget(search_box)
        root.add_widget(SBtn(text="+ 새 계정 생성", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_acc_pop))
        scroll = ScrollView(); self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        for acc in sorted(store.keys()):
            if query and query.lower() not in acc.lower(): continue
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            btn = SBtn(text=f"ID: {acc}", on_release=lambda x, n=acc: self.go_slots(n))
            del_b = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, n=acc: show_confirm("삭제", f"'{n}' 삭제?", lambda: [store.delete(n), self.refresh_list()]))
            row.add_widget(btn); row.add_widget(del_b); self.list_box.add_widget(row)
        scroll.add_widget(self.list_box); root.add_widget(scroll); self.add_widget(root)
    def add_acc_pop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        ti = KTextInput(hint_text="새 ID 입력")
        content.add_widget(ti); btn = SBtn(text="생성", bg=(0.1, 0.5, 0.3, 1))
        content.add_widget(btn); popup = Popup(title="계정 추가", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: [store.put(ti.text, slots=[{"이름":f"슬롯{i+1}","inven":[],"photos":[]} for i in range(6)]), popup.dismiss(), self.refresh_list()] if ti.text else None)
        popup.open()
    def go_slots(self, name): self.manager.cur_acc = name; self.manager.current = 'slots'

class Slots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; slots = store.get(acc)['slots']
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"ID: {acc}", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            btn = Button(text=f"{i+1}번 슬롯\n{slots[i].get('이름','')}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid); layout.add_widget(SBtn(text="메인으로", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)
    def go_detail(self, idx): self.manager.cur_idx = idx; self.manager.current = 'detail'

# --- 3. 캐릭터 상세 (자동 스크롤 대폭 강화) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        self.photo_list = self.data.get('photos', [])
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.scroll = ScrollView(do_scroll_x=False)
        # padding 아래쪽을 600까지 늘려 키보드가 올라와도 모든 칸이 맨 위로 올라갈 수 있게 함
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[0, 0, 0, dp(600)])
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.img_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
        self.img_grid.bind(minimum_height=self.img_grid.setter('height'))
        self.refresh_photos()
        self.content.add_widget(self.img_grid)
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        btn_box.add_widget(SBtn(text="📷 사진추가", on_release=self.pick_p))
        btn_box.add_widget(SBtn(text="📦 인벤토리", on_release=lambda x: setattr(self.manager, 'current', 'inventory')))
        self.content.add_widget(btn_box)

        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(65))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.25))
            ti = KTextInput(text=str(self.data.get(f, '')))
            ti.bind(on_focus=self.auto_scroll_up) # 자동 스크롤 함수 연결
            row.add_widget(ti); self.inputs[f] = ti
            self.content.add_widget(row)

        self.scroll.add_widget(self.content); root.add_widget(self.scroll)
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="정보 저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav); self.add_widget(root)

    # [수정] 터치한 칸이 키보드 위로 올라오도록 화면 최상단으로 강제 스크롤
    def auto_scroll_up(self, instance, value):
        if value:
            # 0.3초 지연을 주어 키보드가 올라온 뒤 스크롤이 작동하게 함
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance), 0.3)

    def refresh_photos(self):
        self.img_grid.clear_widgets()
        for i, p in enumerate(self.photo_list):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180))
            box.add_widget(AsyncImage(source=p, allow_stretch=True))
            btn = Button(text="삭제", size_hint_y=None, height=dp(35), font_name=K_FONT)
            btn.bind(on_release=lambda x, idx=i: show_confirm("사진 삭제", "이 사진을 삭제할까요?", lambda: [self.photo_list.pop(idx), self.refresh_photos()]))
            box.add_widget(btn); self.img_grid.add_widget(box)

    def pick_p(self, *args): Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_p), 0.1)
    def set_p(self, sel):
        if sel: self.photo_list.append(sel[0]); self.refresh_photos()
    def save(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        for f, ti in self.inputs.items(): slots[idx][f] = ti.text
        slots[idx]['photos'] = self.photo_list
        store.put(acc, slots=slots); show_confirm("알림", "정보가 저장되었습니다.")

class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('inven', [])
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=[0,0,0,dp(600)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.draw(); self.scroll.add_widget(self.list_box); root.add_widget(self.scroll)
        nav = GridLayout(cols=3, size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="+추가", on_release=lambda x: [self.items.append(""), self.draw()]))
        nav.add_widget(SBtn(text="저장", on_release=self.save))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'detail')))
        root.add_widget(nav); self.add_widget(root)
    def draw(self):
        self.list_box.clear_widgets()
        for i, v in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
            ti = KTextInput(text=v)
            ti.bind(text=lambda ins, txt, idx=i: self.items.__setitem__(idx, txt))
            ti.bind(on_focus=lambda ins, val: Clock.schedule_once(lambda dt: self.scroll.scroll_to(ins), 0.3) if val else None)
            btn = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7,0.2,0.2,1))
            btn.bind(on_release=lambda x, idx=i: [self.items.pop(idx), self.draw()])
            row.add_widget(ti); row.add_widget(btn); self.list_box.add_widget(row)
    def save(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items; store.put(acc, slots=slots); show_confirm("알림", "인벤토리 저장완료")

class PTApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main')); sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail')); sm.add_widget(Inventory(name='inventory'))
        return sm

if __name__ == '__main__':
    PTApp().run()
