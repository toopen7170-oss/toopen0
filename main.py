import os
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

# [과제 1 해결] 저장소 파일명과 대소문자 일치 (소문자 images.jpeg)
BG_IMAGE = 'images.jpeg' 
FONT_FILE = 'font.ttf'

def safe_font():
    """[과제 2 해결] 한글 깨짐 방지를 위한 폰트 탐색 로직"""
    # 현재 폴더 및 안드로이드 다운로드 경로 모두 확인
    paths = [
        os.path.join(os.getcwd(), FONT_FILE),
        FONT_FILE,
        "/sdcard/Download/font.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None # 폰트가 없을 경우 시스템 기본 폰트 사용 (튕김 방지)

class BackgroundScreen(Screen):
    """배경 이미지를 그려주는 기본 클래스"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                # 이미지 파일이 존재하면 배경으로 설정
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                # 이미지 파일이 없으면 짙은 회색 배경 (에러 방지)
                Color(0.2, 0.2, 0.2, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class TestScreen(BackgroundScreen):
    """폰트와 배경이 잘 나오는지 확인하는 테스트 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        f = safe_font()
        
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 한글이 잘 나오는지 확인하는 라벨
        title = Label(
            text="[PT1 매니저 테스트]\n배경과 한글이 보이나요?", 
            font_name=f, 
            font_size='30sp',
            halign='center'
        )
        
        status_text = f"현재 폰트 경로: {f}\n배경 파일 존재: {os.path.exists(BG_IMAGE)}"
        status_label = Label(text=status_text, font_name=f, font_size='18sp')
        
        btn = Button(text="확인 완료", font_name=f, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5})
        
        layout.add_widget(title)
        layout.add_widget(status_label)
        layout.add_widget(btn)
        self.add_widget(layout)

class PT1TestApp(App):
    def build(self):
        try:
            sm = ScreenManager()
            sm.add_widget(TestScreen(name='test'))
            return sm
        except Exception:
            # 에러 발생 시 화면에 로그 출력
            return Label(text=traceback.format_exc(), color=(1,0,0,1))

if __name__ == '__main__':
    PT1TestApp().run()
