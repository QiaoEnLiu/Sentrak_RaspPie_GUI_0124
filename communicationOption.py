#zh-tw
# communicationOption.py

# 此程式碼為設定-通訊選項
#-- RS-486為進入RS-486的設定
#-- HTTP \ TCPIP為進入HTTP \ TCPIP的設定

try:
    import traceback
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy
    from PyQt5.QtGui import QFont
    from HTTP_TCPIP import internetFrame
    from testEndFrame import testEndFrame
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")


font = QFont()

class comOptionFrame(QWidget):
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
        rs485_layout = QVBoxLayout()
        HTTP_TCPIP_layout = QVBoxLayout()
        comOption_layout =QVBoxLayout()
                
        self.title_label = QLabel(title, self)
        self.title_label.setAlignment(Qt.AlignCenter)  
        self.title_label.setContentsMargins(0, 0, 0, 0)
        font.setPointSize(72)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(_style)

        # user_label = QLabel(user.userInfo())
        # user_label.setFont(font)
        # user_label.setStyleSheet(_style)

        font.setPointSize(54)
        rs485=QPushButton('RS485', self)
        rs485.setFont(font)
        # rs485.setStyleSheet(_style)
        rs485.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        HTTP_TCPIP=QPushButton('HTTP / TCPIP', self)
        HTTP_TCPIP.setFont(font)
        # HTTP_TCPIP.setStyleSheet(_style)
        HTTP_TCPIP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        title_layout.addWidget(self.title_label)
        rs485_layout.addWidget(rs485)
        HTTP_TCPIP_layout.addWidget(HTTP_TCPIP)
        comOption_layout.addLayout(rs485_layout)
        # comOption_layout.addStretch()
        comOption_layout.addLayout(HTTP_TCPIP_layout)
        # comOption_layout.addStretch()


        main_layout.addLayout(title_layout)
        # main_layout.addStretch()
        main_layout.addLayout(comOption_layout)

        # print('終節點測試畫面：', title)
        print(user.userInfo())

        comOption_frame_index = self.stacked_widget.addWidget(self)
        self.current_page_index = comOption_frame_index # 將當前的畫面索引設為 plot_page_index
        # 設定當前顯示的子畫面索引
        print('Current Page Index:', self.current_page_index)
        
        rs485.clicked.connect(lambda:self.comOptionClick(rs485.text(),self.title_label.styleSheet()))
        HTTP_TCPIP.clicked.connect(lambda:self.comOptionClick(HTTP_TCPIP.text(),self.title_label.styleSheet()))

    
    def comOptionClick(self, option, _style):
        if option not in self.sub_pages or not self.stacked_widget.widget(self.sub_pages[option]):

            if option == 'RS485':
                # 設定RS485
                print(option)
                next_frame = testEndFrame(option, _style, self.user, self.stacked_widget, self.sub_pages)
            elif option == 'HTTP / TCPIP':
                # 設定HTTP / TCPIP
                print(option)
                next_frame = internetFrame(option, _style, self.user, self.stacked_widget, self.sub_pages)
            else:
                print('Wrong Option:',option)

            next_frame_index = self.stacked_widget.addWidget(next_frame)
            self.sub_pages[option] = next_frame_index
        else:
            next_frame_index = self.sub_pages[option]

        self.stacked_widget.setCurrentIndex(next_frame_index)
        self.current_page_index = next_frame_index
