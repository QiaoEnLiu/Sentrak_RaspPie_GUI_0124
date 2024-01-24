#zh-tw
# displayOption.py

# 此程式碼為設定-顯示選項
#-- 「波形圖週期」為進入波形圖週期的設定
#-- 「單位」為進入溫度及氧氣濃度單位的設定

try:
    import traceback
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy
    from PyQt5.QtGui import QFont

    from setUnit import setUnitFrame
    from testEndFrame import testEndFrame
    
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")


font = QFont()

class displayOptionFrame(QWidget):
    def __init__(self, title, _style, user, stacked_widget, sub_pages):
        super().__init__()
        
        self.user=user
        self.stacked_widget=stacked_widget
        self.sub_pages=sub_pages

        print(title,self.user.userInfo())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0) 

        title_layout =QVBoxLayout()
        # title_layout.setContentsMargins(0, 0, 0, 0) 
        # title_layout.setSpacing(0)
        time_layout = QVBoxLayout()
        unit_layout = QVBoxLayout()
        displayOption_layout =QVBoxLayout()
                
        self.title_label = QLabel(title, self)
        self.title_label.setAlignment(Qt.AlignCenter)  
        self.title_label.setContentsMargins(0, 0, 0, 0)
        font.setPointSize(72)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(_style)


        font.setPointSize(54)
        time=QPushButton('波形圖週期', self)
        time.setFont(font)
        # time.setStyleSheet(_style)
        time.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        unit=QPushButton('單位', self)
        unit.setFont(font)
        # unit.setStyleSheet(_style)
        unit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        title_layout.addWidget(self.title_label)
        time_layout.addWidget(time)
        unit_layout.addWidget(unit)
        displayOption_layout.addLayout(time_layout)
        # displayOption_layout.addStretch()
        displayOption_layout.addLayout(unit_layout)
        # displayOption_layout.addStretch()


        main_layout.addLayout(title_layout)
        # main_layout.addStretch()
        main_layout.addLayout(displayOption_layout)

        # print('終節點測試畫面：', title)
        print(user.userInfo())

        displayOption_frame_index = self.stacked_widget.addWidget(self)
        self.current_page_index = displayOption_frame_index # 將當前的畫面索引設為 plot_page_index
        # 設定當前顯示的子畫面索引
        print('Current Page Index:', self.current_page_index)
        
        time.clicked.connect(lambda:self.displayOptionClick(time.text(),self.title_label.styleSheet()))
        unit.clicked.connect(lambda:self.displayOptionClick(unit.text(),self.title_label.styleSheet()))

    
    def displayOptionClick(self, option, _style):
        if option not in self.sub_pages or not self.stacked_widget.widget(self.sub_pages[option]):

            if option == '波形圖週期':
                print(option)
                next_frame = testEndFrame(option, _style, self.user, self.stacked_widget, self.sub_pages)
            elif option == '單位':
                print(option)
                next_frame = setUnitFrame(option, _style, self.user, self.stacked_widget, self.sub_pages)
            else:
                print('Wrong Option:',option)

            next_frame_index = self.stacked_widget.addWidget(next_frame)
            self.sub_pages[option] = next_frame_index
        else:
            next_frame_index = self.sub_pages[option]

        self.stacked_widget.setCurrentIndex(next_frame_index)
        self.current_page_index = next_frame_index
