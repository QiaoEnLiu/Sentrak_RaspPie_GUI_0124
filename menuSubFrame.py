#zh-tw 下列程式碼找出上述問題

# menuSubFrame.py
# 些程式碼為選單畫面：當Snetrak_Raspberry_GUI.py的功能選單的四個按鈕（設定、校正、記錄、識別）偵測到點擊事件時，所執行的程式碼並將子畫面刷新為清單畫面

try:
    import sys
    sys.path.append("venv-py3_9/Lib/site-packages")
    
    import os, traceback

    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget,\
        QListWidgetItem, QHBoxLayout
    from PyQt5.QtCore import Qt, QByteArray
    from PyQt5.QtGui import QFont, QPixmap, QImage

    from testEndFrame import testEndFrame
    from displayOption import displayOptionFrame # 設定 >> 顯示
    from communicationOption import comOptionFrame # 設定 >> 通訊
    from id_Frame import id_LogIn_Frame # 識別 >> 登入訊息
    from deviceInfo import deviceInfoFrame # 識別 >> 儀器資訊
    from img_to_base64 import image_to_base64

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")
font = QFont()
class menuSubFrame(QWidget):


    def __init__(self, title, _style, sub_pages, stacked_widget, main_window):
        super().__init__()
        self.sub_pages = sub_pages
        self.main_window = main_window
        self.stacked_widget = stacked_widget
        self.id_login_frame = id_LogIn_Frame

        self.title = title
        print(self.title)
        self.user=main_window.get_global_presentUser()
        print(title,self.user.userInfo())

        # 標題列
        title_layout = QVBoxLayout()        
        self.title_label = QLabel(self.title, self)
        # title_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(36)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(_style)
        title_layout.addWidget(self.title_label)

        content_layout = QVBoxLayout()
        # content_layout.setContentsMargins(0, 0, 0, 0)
        # content_layout.setSpacing(0)

        # 內容使用QListWidget
        self.list_widget = QListWidget(self)

        # 依功能添加列各自表項
        if self.title == '設定':
            for option in ['顯示', '警報輸出', '類比輸出', '感測器溫度保護', '診斷', '通訊', '時間', '語言']:
                self.create_list_item(option)
                self.itemDeescribe(option)

        elif self.title == '校正':
            for option in ['感測器校正', '大氣壓力校正', '類比輸出校正']:
                self.create_list_item(option)
                self.itemDeescribe(option)

        elif self.title == '記錄':
            for option in ['觀看記錄', '統計表', '下載記錄至隨身碟', '記錄方式設定']:
                self.create_list_item(option)
                self.itemDeescribe(option)

        elif self.title == '識別':
            for option in ['登入身份', '儀器資訊', '感測器資訊']:
                self.create_list_item(option)
                self.itemDeescribe(option)

        # 將垂直滾動條設置為不可見
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_layout.addWidget(self.list_widget)

        # 整體佈局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(content_layout)

    def create_list_item(self, option):

        # 創建 QListWidgetItem
        item = QListWidgetItem()
        
        # 設置圖示
        list_icon = QLabel('圖示')
        list_icon.setStyleSheet("border: 5px solid black;border-right: 0px;")
        
        pixmap = QPixmap('picture/test_icon.png')  # 請替換為您的實際圖示路徑
        list_icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "picture", "test_icon.png")
        icon_base64 = image_to_base64(list_icon_path)
        icon_bytes = QByteArray.fromBase64(icon_base64.encode())
        list_icon.setPixmap(QPixmap.fromImage(QImage.fromData(icon_bytes)).scaled(144, 144))
        # print('icon Hright1:', list_icon.pixmap().height())
        # print('icon Hright2:', pixmap.scaledToHeight(144).height())

        # label_font = list_icon.font()  # 獲取 QLabel 的字型
        # font_size = label_font.pointSize()  # 獲取字型大小
        # print('icon Hright Font:', font_size)
         
        # list_icon.setPixmap(pixmap.scaled(72, 72))  # 調整大小以符合您的需求
        item_label = QLabel(option)# 設置文字
        self.describe_label = QLabel()

        font.setPointSize(pixmap.scaledToHeight(144).height()*30//80)
        # font.setPointSize(42)
        item_label.setFont(font)
        item_label.setStyleSheet("border: 5px solid black;border-bottom: 0px;")
        item_label.setContentsMargins(0, 0, 0, 0)
        # print('item_label:', item_label.font().pointSize())

        self.describe_label.setText('描述')
        font.setPointSize(pixmap.scaledToHeight(144).height()*15//80)
        # font.setPointSize(12)
        self.describe_label.setFont(font)
        self.describe_label.setStyleSheet("border: 5px solid black;border-top: 0px; color: gray")
        self.describe_label.setContentsMargins(0, 0, 0, 0)
        # print('self.describe_label:', self.describe_label.font().pointSize())

        # 將圖示和文字排列在一行
        item_layout = QHBoxLayout()
        icon_layout = QHBoxLayout()
        label_layout = QVBoxLayout()
        item_label_layout = QHBoxLayout()
        describe_layout = QHBoxLayout()

        item_layout.setSizeConstraint(QHBoxLayout.SetMinAndMaxSize)
        icon_layout.setSizeConstraint(QHBoxLayout.SetMinAndMaxSize)
        label_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        item_label_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        describe_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # item_layout.addWidget(item_frame)
        # 將圖示和文字排列在一行，並確保沒有額外空間
        item_layout.setSpacing(0)
        icon_layout.addWidget(list_icon)

        label_layout.addLayout(item_label_layout)
        label_layout.addLayout(describe_layout)

        item_label_layout.addWidget(item_label)
        describe_layout.addWidget(self.describe_label)

        item_layout.addLayout(icon_layout)
        item_layout.addLayout(label_layout,1)

        # item_layout.setStretch(0,1)  # 添加伸縮因子

        # 設置項目的布局
        widget = QWidget()
        # 將 itemFrame 設置為 widget 的子 widget
        widget.setLayout(item_layout)

        item.setSizeHint(widget.sizeHint())

        # 將項目添加到 QListWidget
        item.setData(Qt.UserRole, option)  # 使用setData將選項存儲為UserRole
        self.list_widget.addItem(item)
        self.list_widget.setFont(font)
        self.list_widget.setItemWidget(item, widget)  # 將 widget 與 item 關聯起來


        # 設置點擊事件處理函數，連接點擊信號
        self.list_widget.itemClicked.connect(lambda item: self.handle_record_item_click(item))
        

    def itemDeescribe(self, option):
        item_title = option
        if item_title == '顯示':
            self.describe_label.setText('波形圖週期、單位')
        elif item_title == '警報輸出':
            self.describe_label.setText('Relay 1、Relay 2、Relay 3…')
        elif item_title == '類比輸出':
            self.describe_label.setText('濃度、溫度、類型')
        elif item_title == '感測器溫度保護':
            self.describe_label.setText('狀態、溫度設定')
        elif item_title == '診斷':
            self.describe_label.setText('觀看詳細數值')
        elif item_title == '通訊':
            self.describe_label.setText('RS-485、HTTP/TCPIP')
        elif item_title == '時間':
            self.describe_label.setText('調整時間、日期格式')
        elif item_title == '語言':
            self.describe_label.setText('多國語言')
        elif item_title =='感測器校正':
            self.describe_label.setText('空氣校正、直接校正')
        elif item_title =='大氣壓力校正':
            self.describe_label.setText('大氣壓力校正')
        elif item_title == '類比輸出校正':
            self.describe_label.setText('0 - 20 mA、4 - 20 mA')
        elif item_title == '觀看記錄':
            self.describe_label.setText('時間、數值')
        elif item_title == '統計表':
            self.describe_label.setText('最高值、值均值、最底值')
        elif item_title == '下載記錄至隨身碟':
            self.describe_label.setText('儲存格式：Excel、txt、json、csv')
        elif item_title == '記錄方式設定':
            self.describe_label.setText('自動、手動')
        elif item_title == '登入身份':
            self.describe_label.setText('輸入密碼')
        elif item_title == '儀器資訊':
            self.describe_label.setText('型號、序號、生產日期……')
        elif item_title == '感測器資訊':
            self.describe_label.setText('型號、序號、生產日期……')
        else :
            self.describe_label.setText('描述')


    # 在 MyWindow 類別中新增一個槽函數處理 '' 頁面 item 被點擊的信號
    def handle_record_item_click(self, item):
        # 在這裡處理四個功能頁面下 item 被點擊的事件
        # 例如，切換到 testEndFrame 並顯示被點擊的項目文字
        item_text = item.data(Qt.UserRole)

        # 判斷是否已經創建了 testEndFrame
        if item_text not in self.sub_pages: #"testEndFrame"
            print('進入選項：', item_text)
            if item_text == '顯示':
                # 由「設定」進入「顯示」介面
                next_frame = displayOptionFrame(item_text, self.title_label.styleSheet(), self.user, self.stacked_widget, self.sub_pages)

            elif item_text == '通訊':
                # 由「設定」進入「通訊」介面
                next_frame = comOptionFrame(item_text, self.title_label.styleSheet(), self.user, self.stacked_widget, self.sub_pages)

            elif item_text == '登入身份':
                # 由「識別」進入「登入身份」介面，此功能須再與解鎖功能區分
                # next_frame = id_LogIn_Frame(item_text, self.title_label.styleSheet(), self.user)
                next_frame = testEndFrame(item_text, self.title_label.styleSheet(), self.user, self.stacked_widget, self.sub_pages)

            elif item_text == '儀器資訊': 
                # 由「識別」進入「儀器資訊」介面，暫以本機開發硬體測試
                next_frame = deviceInfoFrame(item_text, self.title_label.styleSheet(), self.user, self.stacked_widget, self.sub_pages)

            else:
                # 如果還沒有，則創建一個新的 testEndFrame 為終節點畫面測試
                next_frame = testEndFrame(item_text, self.title_label.styleSheet(), self.user, self.stacked_widget, self.sub_pages)
                
            # 添加到堆疊中
            next_frame_index = self.stacked_widget.addWidget(next_frame)
            self.sub_pages[item_text] = next_frame_index
        else:
            # 如果已經存在，取得 下一頁（testEndFrame） 的索引
            next_frame_index = self.sub_pages[item_text]

        # 設定當前顯示的子畫面索引為 testEndFrame
        self.stacked_widget.setCurrentIndex(next_frame_index)
        self.current_page_index = next_frame_index

        # print('Current Page Index:', self.current_page_index)
