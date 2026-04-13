import os
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.text import LabelBase

# [과제 1] 파일명 대소문자 통일 (사용자 요청: bg.png)
BG_IMAGE = "bg.png" 
FONT_NAME = "font.ttf"

def load_korean_font():
    """[과제 2] 한글 깨짐 방지를 위한 폰트 강제 등록"""
    # 현재 작업 디렉토리에서 폰트 파일 확인
    font_path = os.path.join(os.getcwd(), FONT_NAME)
    if os.path.exists(font_path):
        LabelBase.register(name="KoreanFont", fn_regular=font_path)
        return "KoreanFont"
    return None

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # 배경 이미지 설정
        with self.canvas.before:
            if os.path.exists(BG_IMAGE):
                # 이미지가 있을 경우 출력
                self.rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                # [과제 7 대비] 이미지 파일이 없을 때 앱이 튕기지 않도록 검은색 배경 처리
                Color(0.1, 0.1, 0.1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 1단계 성공 여부 확인용 텍스트
        f = load_korean_font()
        self.add_widget(Label(
            text="[1단계 성공]\n배경(bg.png)과 한글이 보이나요?", 
            font_name=f if f else None,
            font_size='28sp',
            halign='center'
        ))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class PT1Manager(App):
    def build(self):
        try:
            # 정상 실행 시 레이아웃 반환
            return MainLayout()
        except Exception:
            # [과제 7] 실행 중 에러 발생 시 화면에 에러 로그 출력 (Traceback)
            error_msg = traceback.format_exc()
            print(error_msg)
            return Label(text=f"에러 발생!\n\n{error_msg}", color=(1, 0, 0, 1))

if __name__ == '__main__':
    PT1Manager().run()
