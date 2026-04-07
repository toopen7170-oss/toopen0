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

# [1번 해결] 폰트 등록 - font.ttf 파일이 반드시 프로젝트 폴더에 있어야 합니다.
FONT_PATH = 'font.ttf'
if os.path.exists(FONT_PATH):
    LabelBase.register(name="KFont", fn_regular=FONT_PATH)
    K_FONT = "KFont"
else:
    K_FONT = 'Roboto' # 폰트 없을 경우 기본 폰트 사용

# 데이터 저장 파일명 (v12로 업그레이드)
store = JsonStore('pt1_final_v12.json')

# --- 스타일 버튼 ---
class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

# --- 공용 삭제 확인 팝업 ---
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

# --- 1. 메인 화면 (전체 검색 기능) ---
class MainMenu(Screen):
    def on_enter(self):
        self.refresh_list()

    def refresh_list(self, query=""):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 검색바 (전체 검색)
        search_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        self.search_ti = TextInput(text=query, hint_text="계정, 캐릭터, 장비 통합 검색", font_name=K_FONT, multiline=False)
        s_btn = Button(text="검색", font_name=K_FONT, size_hint_x=None, width=dp(70))
        s_btn.bind(on_release=lambda x: self.refresh_list(self.search_ti.text.strip()))
        search_box.add_widget(self.search_ti); search_box.add_widget(s_btn)
        root.add_widget(search_box)

        # 계정 추가 버튼
        add_acc_btn = SBtn(text="+ 새 계정 만들기", bg=(0.1, 0.5, 0.3, 1))
        add_acc_btn.bind(on_release=self.add_account_popup)
        root.add_widget(add_acc_btn)

        # 리스트 영역 (스크롤)
        scroll = ScrollView(do_scroll_x=False)
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        all_keys = sorted(store.keys())
        for acc_name in all_keys:
            acc_data = store.get(acc_name)
            
            # [검색 해결] 전체 데이터 내 단어 검색 로직
            if query:
                json_str = json.dumps(acc_data, ensure_ascii=False).lower()
                if query.lower() not in json_str and query.lower() not in acc_name.lower():
                    continue

            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            acc_btn = SBtn(text=f"계정: {acc_name}", bg=(0.3, 0.3, 0.3, 1))
            acc_btn.bind(on_release=lambda x, n=acc_name: self.go_slots(n))
            del_btn = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda x, n=acc_name: show_confirm("삭제 확인", f"'{n}' 계정을 삭제하시겠습니까?", lambda: self.del_acc(n)))
            row.add_widget(acc_btn); row.add_widget(del_btn)
            self.list_box.add_widget(row)

        scroll.add_widget(self.list_box); root.add_widget(scroll)
        self.add_widget(root)

    def add_account_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        # [1번 해결] 입력칸에 폰트 적용
        ti = TextInput(hint_text="계정 이름 입력", font_name=K_FONT, multiline=False)
        content.add_widget(ti)
        btn = SBtn(text="생성하기", bg=(0.1, 0.5, 0.3, 1))
        content.add_widget(btn)
        popup = Popup(title="새 계정", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda x: self.save_acc(ti.text, popup))
        popup.open()

    def save_acc(self, name, popup):
        if name and not store.exists(name):
            store.put(name, slots=[{"이름": f"캐릭터 {i+1}", "inven": []} for i in range(6)])
            popup.dismiss(); self.refresh_list()

    def del_acc(self, name):
        store.delete(name); self.refresh_list()

    def go_slots(self, name):
        self.manager.cur_acc = name; self.manager.current = 'slots'

# --- 2. 캐릭터 슬롯 화면 ---
class Slots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        slots = store.get(acc)['slots']
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"계정: {acc} - 캐릭터 선택", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            char_name = slots[i].get('이름', f'캐릭터 {i+1}')
            btn = Button(text=f"{i+1}번 슬롯\n{char_name}", font_name=K_FONT, halign='center', background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(b)
        layout.add_widget(grid)
        layout.add_widget(SBtn(text="메인 화면으로", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

    def go_detail(self, idx):
        self.manager.cur_idx = idx; self.manager.current = 'detail'

# --- 3. 캐릭터 상세 정보 (자동 스크롤 및 다중 사진 등록) ---
class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        self.photo_list = self.data.get('photos', []) # 다중 사진 데이터

        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # [2번 해결 핵심] 자동 스크롤을 위한 구조
        self.scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[0, 0, 0, dp(100)]) # 하단 여백 추가
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # [5번 해결] 사진 그리드 (v5, v6 형태)
        self.img_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
        self.img_grid.bind(minimum_height=self.img_grid.setter('height'))
        self.refresh_photos()
        self.content.add_widget(self.img_grid)
        
        # 사진 제어 버튼
        btn_box = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        add_photo_btn = SBtn(text="📷 사진 추가하기", bg=(0.2, 0.5, 0.8, 1))
        add_photo_btn.bind(on_release=self.pick_photo)
        go_inven_btn = SBtn(text="📦 인벤토리 관리", bg=(0.8, 0.5, 0.2, 1))
        go_inven_btn.bind(on_release=self.go_inven)
        btn_box.add_widget(add_photo_btn); btn_box.add_widget(go_inven_btn)
        self.content.add_widget(btn_box)

        # 상세 입력 필드 ( FocusTextInput 적용 )
        self.fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in self.fields:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            
            # 터치 시 자동 스크롤 입력창
            ti = TextInput(text=str(self.data.get(f, '')), font_name=K_FONT, multiline=False)
            ti.bind(on_focus=self.on_input_focus) # 포커스 시 스크롤 이동 바인딩
            row.add_widget(ti); self.inputs[f] = ti
            self.content.add_widget(row)
            
        self.scroll.add_widget(self.content); root.add_widget(self.scroll)
        
        # 하단 제어 버튼
        nav_box = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(5))
        save_btn = SBtn(text="정보 저장하기", bg=(0.1, 0.5, 0.3, 1))
        save_btn.bind(on_release=self.save_char)
        back_btn = SBtn(text="뒤로가기")
        back_btn.bind(on_release=self.go_back)
        nav_box.add_widget(save_btn); nav_box.add_widget(back_btn)
        root.add_widget(nav_box)

        self.add_widget(root)

    def refresh_photos(self):
        self.img_grid.clear_widgets()
        for i, path in enumerate(self.photo_list):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180))
            box.add_widget(AsyncImage(source=path, allow_stretch=True))
            del_p_btn = Button(text="삭제", size_hint_y=None, height=dp(30), font_name=K_FONT, background_color=(0.7, 0.2, 0.2, 1))
            del_p_btn.bind(on_release=lambda x, idx=i: show_confirm("삭제 확인", "사진을 지울까요?", lambda: self.del_photo(idx)))
            box.add_widget(del_p_btn)
            self.img_grid.add_widget(box)

    def pick_photo(self, *args):
        Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_photo), 0.1)

    def set_photo(self, selection):
        if selection:
            self.photo_list.append(selection[0]); self.refresh_photos()

    def del_photo(self, idx):
        self.photo_list.pop(idx); self.refresh_photos()

    # 입력창 포커스 시 자동 스크롤 함수
    def on_input_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance), 0.1)

    def save_char(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        for f in self.fields: slots[idx][f] = self.inputs[f].text
        slots[idx]['photos'] = self.photo_list # 다중 사진 저장
        store.put(acc, slots=slots)
        show_confirm("성공", "정보가 저장되었습니다.")

    def go_inven(self, *args): self.manager.current = 'inventory'
    def go_back(self, *args): self.manager.current = 'slots'

# --- 4. 인벤토리 관리 화면 ---
class Inventory(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        self.items = store.get(acc)['slots'][idx].get('inven', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        root.add_widget(Label(text="[인벤토리 편집]", font_name=K_FONT, size_hint_y=None, height=dp(40)))
        
        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        self.draw_items()
        
        self.scroll.add_widget(self.list_box); root.add_widget(self.scroll)
        
        nav_box = GridLayout(cols=2, size_hint_y=None, height=dp(110), spacing=dp(5))
        add_btn = SBtn(text="+ 아이템 추가", bg=(0.1, 0.4, 0.6, 1))
        add_btn.bind(on_release=self.add_i)
        save_btn = SBtn(text="인벤토리 저장", bg=(0.1, 0.5, 0.3, 1))
        save_btn.bind(on_release=self.save_i)
        back_btn = SBtn(text="돌아가기")
        back_btn.bind(on_release=self.go_back)
        nav_box.add_widget(add_btn); nav_box.add_widget(save_btn)
        nav_box.add_widget(back_btn); root.add_widget(nav_box)
        self.add_widget(root)

    def draw_items(self):
        self.list_box.clear_widgets()
        for i, item_val in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
            # [디자인 해결] 입력 시 화면 고정 TextInput 적용
            ti = TextInput(text=item_val, font_name=K_FONT, multiline=False)
            ti.bind(text=lambda instance, v, idx=i: self.update_val(idx, v))
            ti.bind(on_focus=self.on_inven_focus) # 스크롤 이동 바인딩
            del_b = Button(text="삭제", size_hint_x=None, width=dp(60), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, idx=i: show_confirm("아이템 삭제", "삭제하시겠습니까?", lambda: self.rem_i(idx)))
            row.add_widget(ti); row.add_widget(del_b)
            self.list_box.add_widget(row)

    def on_inven_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance), 0.1)

    def update_val(self, idx, v): self.items[idx] = v
    def add_i(self, *args): self.items.append(""); self.draw_items()
    def rem_i(self, idx): self.items.pop(idx); self.draw_items()
    
    def save_i(self, *args):
        acc = self.manager.cur_acc
        idx = self.manager.cur_idx
        slots = store.get(acc)['slots']
        slots[idx]['inven'] = self.items
        store.put(acc, slots=slots)
        show_confirm("완료", "인벤토리가 저장되었습니다.")

    def go_back(self, *args): self.manager.current = 'detail'

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
