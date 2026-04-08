import os
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
from kivy.metrics import dp
from kivy.clock import Clock
from plyer import filechooser

# [폰트 설정]
FONT_NAME = "KFont"
FONT_PATH = 'font.ttf'
if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
        K_FONT = FONT_NAME
    except:
        K_FONT = 'Roboto'
else:
    K_FONT = 'Roboto'

store = JsonStore('pt1_chart_v18.json')

# [입력창 커스텀] 글씨 위치를 밑으로 내림
class KTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.multiline = False
        self.font_size = '17sp'
        # [수정] 두 번째 값(위쪽 패딩)을 20으로 늘려 글씨를 아래로 내림
        self.padding = [dp(10), dp(20), dp(10), dp(5)] 

class SBtn(Button):
    def __init__(self, bg=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = K_FONT
        self.background_normal = ''
        self.background_color = bg
        self.size_hint_y = None
        self.height = dp(55)

# --- 화면 구성 ---
class MainMenu(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        root.add_widget(SBtn(text="+ 새 계정 생성", bg=(0.1, 0.5, 0.3, 1), on_release=self.add_acc))
        scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        for acc in sorted(store.keys()):
            row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
            btn = SBtn(text=f"ID: {acc}", on_release=lambda x, n=acc: self.go_slots(n))
            del_b = Button(text="X", size_hint_x=None, width=dp(50), background_color=(0.7, 0.2, 0.2, 1))
            del_b.bind(on_release=lambda x, n=acc: [store.delete(n), self.on_enter()])
            row.add_widget(btn); row.add_widget(del_b); self.list_box.add_widget(row)
        scroll.add_widget(self.list_box); root.add_widget(scroll)
        self.add_widget(root)
    def add_acc(self, *args):
        # 간단한 이름 생성 (날짜/순번 등)
        name = f"ID_{len(store.keys())+1}"
        store.put(name, slots=[{"이름":f"캐릭{i+1}","inven":[],"photos":[]} for i in range(6)])
        self.on_enter()
    def go_slots(self, name): self.manager.cur_acc = name; self.manager.current = 'slots'

class Slots(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; slots = store.get(acc)['slots']
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        grid = GridLayout(cols=2, spacing=dp(10))
        for i in range(6):
            btn = Button(text=f"{i+1}번\n{slots[i].get('이름','')}", font_name=K_FONT, halign='center')
            btn.bind(on_release=lambda x, idx=i: self.go_detail(idx))
            grid.add_widget(btn)
        layout.add_widget(grid); layout.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)
    def go_detail(self, idx): self.manager.cur_idx = idx; self.manager.current = 'detail'

class Detail(Screen):
    def on_enter(self):
        self.clear_widgets()
        acc = self.manager.cur_acc; idx = self.manager.cur_idx
        self.data = store.get(acc)['slots'][idx]
        self.photo_list = self.data.get('photos', [])
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.scroll = ScrollView()
        # 하단 여백을 많이 줘서 키보드 공간 확보
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[0, 0, 0, dp(500)])
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # 사진 영역
        self.img_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
        self.img_grid.bind(minimum_height=self.img_grid.setter('height'))
        self.refresh_photos()
        self.content.add_widget(self.img_grid)
        self.content.add_widget(SBtn(text="📷 사진 추가", on_release=self.pick_p))

        # 입력 필드
        fields = ["이름", "직업", "레벨", "양손무기", "한손무기", "갑옷", "로브", "방패", "암릿", "장갑", "부츠", "아뮬렛", "링", "쉘텀", "기타"]
        self.inputs = {}
        for f in fields:
            row = BoxLayout(size_hint_y=None, height=dp(60))
            row.add_widget(Label(text=f, font_name=K_FONT, size_hint_x=0.3))
            ti = KTextInput(text=str(self.data.get(f, '')))
            # [수정] 자동 스크롤 기능 추가
            ti.bind(on_focus=self.auto_scroll)
            row.add_widget(ti); self.inputs[f] = ti
            self.content.add_widget(row)

        self.scroll.add_widget(self.content); root.add_widget(self.scroll)
        nav = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
        nav.add_widget(SBtn(text="저장", bg=(0.1, 0.5, 0.3, 1), on_release=self.save))
        nav.add_widget(SBtn(text="뒤로", on_release=lambda x: setattr(self.manager, 'current', 'slots')))
        root.add_widget(nav); self.add_widget(root)

    # [수정] 터치 시 해당 입력창이 키보드 위(화면 상단)로 오게 함
    def auto_scroll(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(instance), 0.3)

    def refresh_photos(self):
        self.img_grid.clear_widgets()
        for i, p in enumerate(self.photo_list):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
            box.add_widget(AsyncImage(source=p))
            btn = Button(text="삭제", size_hint_y=None, height=dp(30), font_name=K_FONT)
            btn.bind(on_release=lambda x, idx=i: [self.photo_list.pop(idx), self.refresh_photos()])
            box.add_widget(btn); self.img_grid.add_widget(box)

    def pick_p(self, *args): Clock.schedule_once(lambda dt: filechooser.open_file(on_selection=self.set_p), 0.1)
    def set_p(self, sel):
        if sel: self.photo_list.append(sel[0]); self.refresh_photos()
    def save(self, *args):
        acc = self.manager.cur_acc; idx = self.manager.cur_idx; slots = store.get(acc)['slots']
        for f, ti in self.inputs.items(): slots[idx][f] = ti.text
        slots[idx]['photos'] = self.photo_list
        store.put(acc, slots=slots)

class PTApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.cur_acc = ""; sm.cur_idx = 0
        sm.add_widget(MainMenu(name='main')); sm.add_widget(Slots(name='slots'))
        sm.add_widget(Detail(name='detail'))
        return sm

if __name__ == '__main__':
    PTApp().run()
