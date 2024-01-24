#zh-tw
# testEndFrame.py

#此程式碼為子畫面最終刷新測試碼
#--第一子畫面最終測試碼執行結果 Sentrak_RaspberryPie_GUI.py -> menuSubFrame.py
#--最新最子畫面最終測試碼執行結果 menuSubFrame.py -> testEndFrame.py
try:
    import traceback
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
    from PyQt5.QtGui import QFont
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")

font = QFont()
class testEndFrame(QWidget):
    def __init__(self, title, _style, user, stacked_widget, sub_pages):
        super().__init__()
        print(title)

        self.sub_pages=sub_pages
        
        end_label = QLabel(title, self)
        end_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(72)
        end_label.setFont(font)
        end_label.setStyleSheet(_style)

        user_label = QLabel(user.userInfo())
        user_label.setFont(font)
        user_label.setStyleSheet(_style)

        end_sub_frame_layout = QVBoxLayout(self)
        end_sub_frame_layout.setContentsMargins(0, 0, 0, 0)
        end_sub_frame_layout.setSpacing(0) 
        end_sub_frame_layout.addWidget(end_label)
        end_sub_frame_layout.addWidget(user_label)

        print('終節點測試畫面：', title)

        self.stacked_widget = stacked_widget
        end_frame_index = self.stacked_widget.addWidget(self)
        self.current_page_index = end_frame_index # 將當前的畫面索引設為 plot_page_index
        # 設定當前顯示的子畫面索引
        print('Current Page Index:', self.current_page_index)