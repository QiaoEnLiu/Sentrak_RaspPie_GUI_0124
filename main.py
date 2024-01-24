#zh-tw

# main.py
# 此程式碼為主畫面，顯示折線圖為主

try:
    import sys
    # sys.path.append("venv-py3_9/Lib/site-packages")
    # print(sys.path)

    import os, traceback, minimalmodbus

    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QWidget, QStatusBar, QVBoxLayout,\
        QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QFrame, QGridLayout,\
        QPushButton, QStackedWidget, QMessageBox, QDesktopWidget
    from PyQt5.QtCore import Qt, QTimer, QDateTime, QByteArray, pyqtSlot, pyqtSignal
    from PyQt5.QtGui import QFont, QPixmap, QImage

    from modbus_RTU_Connect_GUI import ModbusRTUConfigurator

    from unit_transfer import unit_transfer
    from plotCanvas import plotCanvas
    from menuSubFrame import menuSubFrame
    from img_to_base64 import image_to_base64
    from testRTU import testRTU_Frame
    from login import LoginDialog


except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")

font = QFont()

global_presentUser = None

temperature_unit_text='Celsius' # Celsius, Fahrenheit
temperature_test = 16.8 # 攝氏
oxygen_concentration = 12.56

class MyWindow(QMainWindow):

    data_updated = pyqtSignal(float, float)
    def __init__(self):
        super().__init__()

        self.isLogin=False

        self.plot_canvas = plotCanvas(self, width=5, height=4)

        # 設置主視窗的尺寸
        # 取得螢幕解析度
        screen_resolution = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

        # 如果解析度為1920*1080，則全螢幕，否則使用固定解析度
        if screen_width == 1920 and screen_height == 1080:
            self.showFullScreen()
        else:
            self.setFixedSize(1920, 1080)
            print()

        window_size = self.size()
        winWidth = window_size.width()
        winHeight = window_size.height()

        print('視窗大小：', winWidth, '*', winHeight)
        print('螢幕解析：', screen_width, '*', screen_height)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 創建狀態列
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        status_bar.setGeometry(0, 0, 1920, 100)  # 設置狀態列的尺寸
        status_bar.setStyleSheet("background-color: lightgray;")  # 設置背景顏色
        status_bar.setSizeGripEnabled(False)  # 隱藏右下角的調整大小的三角形

        # 在狀態列中央加入日期時間
        self.datetime_label = QLabel(self)
        status_bar.addWidget(self.datetime_label, 1)  # 將 QLabel 加入狀態列，並指定伸縮因子為1
        self.datetime_label.setAlignment(Qt.AlignCenter)  # 文字置中
        font.setPointSize(36)
        self.datetime_label.setFont(font)

        # 更新日期時間的 QTimer
        self.update_datetime_timer = QTimer(self)
        self.update_datetime_timer.timeout.connect(self.update_datetime)
        self.update_datetime_timer.start(1000)  # 每秒更新一次

        # 更新一次日期時間，避免一開始顯示空白
        self.update_datetime()

        # 創建主畫面
        main_frame = QFrame(self)
        main_frame.setGeometry(0, 100, 960, 780)
        main_frame.setStyleSheet("background-color: lightblue;")
        # main_frame.setStyleSheet("background-color: white;")  # 主畫面背景顏色

        temperature_unit=unit_transfer.set_temperature_unit(unit=temperature_unit_text)
        temperature=unit_transfer.convert_temperature(temperature=temperature_test,unit=temperature_unit_text)
        self.main_label = QLabel(f"O<sub>2</sub>: {oxygen_concentration:.2f} ppb<br>T: {temperature_test:.2f} {temperature_unit}") # ° 為Alt 0176
        self.main_label.setAlignment(Qt.AlignCenter)  # 文字置中
        font.setPointSize(72)
        self.main_label.setFont(font)
        main_frame_layout = QVBoxLayout(main_frame)
        # main_frame_layout.setContentsMargins(0, 0, 0, 0)
        main_frame_layout.setSpacing(0)  # 添加這一行以消除元素之間的間距
        main_frame_layout.addWidget(self.main_label)

        # 創建子畫面
        self.sub_frame = QFrame(self)
        self.sub_frame.setGeometry(960, 100, 960, 780)
        # self.sub_frame.setStyleSheet("background-color: lightblue;")  # 子畫面背景顏色
        # sub_label = QLabel('子畫面')
        # sub_label.setAlignment(Qt.AlignCenter)  # 文字置中
        # font.setPointSize(72)
        # sub_label.setFont(font)
        self.sub_frame_layout = QVBoxLayout(self.sub_frame)
        self.sub_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_frame_layout.setSpacing(0)  # 添加這一行以消除元素之間的間距
        self.sub_frame_layout.addWidget(self.plot_canvas) # 在子畫面中加入 Matplotlib 的畫布
        # self.sub_frame_layout.addWidget(sub_label)

        # 創建功能列
        function_bar = QFrame(self)
        function_bar.setGeometry(0, 880, 1920, 200)  # 設置功能列的尺寸
        function_bar.setStyleSheet("background-color: lightgray;")  # 設置背景顏色

        # 在功能列中添加按鈕
        save_button = QPushButton('資料儲存', function_bar)
        # test_button = QPushButton('測試', function_bar)
        self.test_RTU_button = QPushButton('測試RTU', function_bar)
        self.quit_button=QPushButton('離開',function_bar)
        # self.lock_label = QLabel('螢幕鎖',function_bar)
        self.lock_button=QPushButton('解鎖',function_bar)
        self.logout_button = QPushButton('登出', function_bar)
        self.menu_button = QPushButton('選單', function_bar)
        self.return_button = QPushButton('返回', function_bar)

        # 在 MyWindow 類別的 __init__ 方法中初始化 QStackedWidget
        self.stacked_widget = QStackedWidget(self.sub_frame)
        self.plot_page_index = self.stacked_widget.addWidget(self.plot_canvas) # 此處僅添加 plot 畫面
        self.menu_page_index = self.stacked_widget.addWidget(self.create_menu_page()) #此處添加了 menu 畫面
        self.tsRTU_page_index = None
        self.stacked_widget.setCurrentIndex(self.plot_page_index) #設定初始顯示的畫面
        self.current_page_index = self.plot_page_index # 將當前的畫面索引設為 plot_page_index

        # 設定當前顯示的子畫面索引
        print('Current Page Index:', self.current_page_index)

        # 在 MyWindow 類別中添加 sub_pages 作為成員變數
        self.sub_pages = {}

        # 將QStackedWidget添加到sub_frame佈局
        self.sub_frame_layout.addWidget(self.stacked_widget)


        # 創建一個放置元件的底層佈局
        global_layout = QVBoxLayout(central_widget)
        global_layout.setContentsMargins(0, 0, 0, 0)  # 消除佈局的邊距
        global_layout.setSpacing(0)

        # 添加狀態列到佈局
        global_layout.addWidget(status_bar, 1)  # 狀態列佔用 1 的高度

        # 創建一個放置元件的子佈局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.addWidget(main_frame, 1)  # 添加主畫面到佈局，第二個參數是優先級，表示佔用100的寬度
        main_layout.addWidget(self.sub_frame, 1) # 添加子畫面到佈局
        global_layout.addLayout(main_layout,8) # 添加子佈局到佈局
        global_layout.addWidget(function_bar, 2)  # 添加功能列到佈局，功能列佔用 2 的高度


        # 設定按鈕大小
        button_width, button_height = 200, 200

        save_button.setFixedSize(button_width, button_height)
        # test_button.setFixedSize(button_width, button_height)
        self.test_RTU_button.setFixedSize(button_width, button_height)
        self.quit_button.setFixedSize(button_width,button_height)
        # self.lock_label.setFixedSize(button_width, button_height)
        self.lock_button.setFixedSize(button_width, button_height)
        self.logout_button.setFixedSize(button_width, button_height)
        self.menu_button.setFixedSize(button_width, button_height)
        self.return_button.setFixedSize(button_width, button_height)
        
        font.setPointSize(36)
        save_button.setFont(font)
        # test_button.setFont(font)
        self.test_RTU_button.setFont(font)
        self.quit_button.setFont(font)
        # self.lock_label.setFont(font)
        self.lock_button.setFont(font)
        self.logout_button.setFont(font)
        self.menu_button.setFont(font)
        self.return_button.setFont(font)

        # 設定圖片路徑，picture資料夾和程式碼同一個資料夾中

        # lock_icon_path = os.path.join('picture', 'lock_icon.png')
        # print("Absolute path of image:", os.path.abspath(lock_icon_path))

        # lock_icon_path = "picture/lock_icon.png"
        self.lock_icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "picture", "lock_icon.png")
        self.lock_icon_base64 = image_to_base64(self.lock_icon_path) # 使用 lock_icon_base64
        self.lock_icon_bytes = QByteArray.fromBase64(self.lock_icon_base64.encode())
        # self.lock_label.setPixmap(QPixmap.fromImage(QImage.fromData(self.lock_icon_bytes)))
        # lock_pixmap = QPixmap(lock_icon_path)
        # lock_label.setPixmap(lock_pixmap.scaled(button_width, button_height, Qt.KeepAspectRatio))

        # 將 SpacerItem 插入按鈕之間，靠左、置中、靠右
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_left = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        function_bar_layout = QHBoxLayout(function_bar)

        function_bar_layout1 = QHBoxLayout()
        function_bar_layout2 = QHBoxLayout()
        function_bar_layout3 = QHBoxLayout()

        function_bar_layout1.addWidget(save_button)
        # function_bar_layout1.addWidget(test_button)
        function_bar_layout1.addWidget(self.test_RTU_button)
        function_bar_layout1.addWidget(self.quit_button)
        function_bar_layout1.addItem(spacer)

        function_bar_layout2.addItem(spacer_right)
        # function_bar_layout2.addWidget(self.lock_label)
        function_bar_layout2.addWidget(self.lock_button)
        function_bar_layout2.addWidget(self.logout_button)
        function_bar_layout2.addItem(spacer_left)
        
        function_bar_layout3.addItem(spacer)
        function_bar_layout3.addWidget(self.menu_button)
        function_bar_layout3.addWidget(self.return_button)

        function_bar_layout.addLayout(function_bar_layout1, 1)
        function_bar_layout.addLayout(function_bar_layout2, 1)
        function_bar_layout.addLayout(function_bar_layout3, 1)

        self.quit_button.clicked.connect(self.show_confirmation_dialog)
        self.test_RTU_button.clicked.connect(self.conect_modbus_RTU)
        self.lock_button.clicked.connect(self.showLoginDialog)
        self.menu_button.clicked.connect(self.switch_to_menu)
        self.return_button.clicked.connect(self.switch_to_previous_page)
        self.logout_button.clicked.connect(self.logout_button_click)

        self.lock_button.setVisible(not self.isLogin)
        self.logout_button.setVisible(self.isLogin)
        self.menu_button.setVisible(True)
        self.return_button.setVisible(False)
        print('登入：',self.logout_button.isVisible())

        # 顯示視窗
        self.show()

    def testClicked(self):
        print('測試按鈕')

    def show_confirmation_dialog(self):
        # 顯示確認對話框
        reply = QMessageBox.question(self, '程式關閉', '確定要關閉程式嗎？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 如果用戶選擇 "Yes"，則關閉應用程式
            QApplication.quit()

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("yyyy-MM-dd hh:mm:ss")
        self.datetime_label.setText(formatted_datetime)
        # 清除之前的圖例
        self.plot_canvas.ax.clear()

        # 重新繪製折線圖
        self.plot_canvas.plot(temperature_unit=temperature_unit_text) # Celsius, Fahrenheit

        # 在這裡更新畫布
        self.plot_canvas.draw()

    def showLoginDialog(self):

        # 顯示帳號和密碼輸入對話框
        login_dialog = LoginDialog()
        result = login_dialog.exec_()

        if result == LoginDialog.Accepted: # 使用者按下確定按鈕，取得輸入的值
            global global_presentUser
            self.isLogin=True
            # username = login_dialog.username_input.text()
            # password = login_dialog.password_input.text()
            self.logout_button.setVisible(self.isLogin)
            self.lock_button.setVisible(not self.isLogin)
            # print('logout_button:',self.logout_button.isVisible())
            print('登入成功', login_dialog.get_global_loginUser())
            global_presentUser = login_dialog.get_global_loginUser()

            print('main.py:',global_presentUser.userInfo())

        else:
            print('登入取消')

    def get_global_presentUser(self):
        return global_presentUser


    def handle_login_success(self, checkLogin):
        # 登入成功時觸發，將 logout_button 由不可見改為可見
        print('收到 login_successful 信號:', checkLogin)
        self.logout_button.setVisible(True)
        # print('logout_button:',self.logout_button.isVisible())
        self.lock_icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "picture", "unlock_icon.png")
        self.lock_icon_base64 = image_to_base64(self.lock_icon_path) # 使用 lock_icon_base64
        self.lock_icon_bytes = QByteArray.fromBase64(self.lock_icon_base64.encode())
        # self.lock_label.setPixmap(QPixmap.fromImage(QImage.fromData(self.lock_icon_bytes)))

    def logout_button_click(self):
        # 顯示確認對話框
        reply = QMessageBox.question(self, '登出', '確定要登出嗎？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 如果用戶選擇 "Yes"，則登出應用程式
                    


            global global_presentUser
            self.isLogin=False

            QMessageBox.information(self, '登出成功', '返回主頁面')
            self.logout_button.setVisible(self.isLogin) 
            print('logout_button_click:',self.logout_button.isVisible())

            self.lock_icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "picture", "lock_icon.png")
            self.lock_icon_base64 = image_to_base64(self.lock_icon_path) # 使用 lock_icon_base64
            self.lock_icon_bytes = QByteArray.fromBase64(self.lock_icon_base64.encode())
            # self.lock_label.setPixmap(QPixmap.fromImage(QImage.fromData(self.lock_icon_bytes)))

            # 將畫面切換回主畫面（清空堆疊）
            # 判斷是否只剩下一頁，如果是，則不執行刪除
            print('Totle Pages:', self.stacked_widget.count())
            if self.stacked_widget.count() > 1:
                print('Remove Pages:', self.stacked_widget.count()-1)
                while self.stacked_widget.count() > 2:
                    widget = self.stacked_widget.widget(self.stacked_widget.count() - 1)  # 取得最頂層的頁面
                    print('Remaining Pages:', self.stacked_widget.count() - 1)
                    if widget:
                        self.stacked_widget.removeWidget(widget)
                        widget.deleteLater()
                print('Back to First Pages:', self.stacked_widget.count())
            
            else:
                print('First Pages:', self.stacked_widget.count())

            self.stacked_widget.setCurrentIndex(self.plot_page_index)
            self.current_page_index = self.plot_page_index
            
            # print('Current Index:', self.plot_page_index)

            self.lock_button.setVisible(not self.isLogin)
            self.return_button.setVisible(False)
            self.menu_button.setVisible(True)
        else:
            return
        

    def conect_modbus_RTU(self):
        connectGUI=ModbusRTUConfigurator(self)
        # connectGUI.value_updated.connect(self.set_main_values)
        # self.data_updated.connect(self.update_main_label)
        # connectGUI.exec_()

    # @pyqtSlot(float)
    # def update_main_label(self, temperature):
    #     self.main_label.setText(f'O₂: {oxygen_concentration:.2f} ppb, T: {temperature:.2f} °C')

    # def set_main_values(self, temperature):
    #     # 設定 oxygen_concentration 和 temperature_test 的值
    #     # oxygen_concentration = round(oxygen, 2)
    #     temperature_test = round(temperature, 2)
    #     # 發送 oxygen_concentration 和 temperature_test 更新的信號
    #     self.data_updated.emit(temperature_test)


    # 取得模擬RTU數據測試畫面
    def switch_to_TestRTU(self):
        print(self.test_RTU_button.text())
        if self.tsRTU_page_index is None:
            tsRTU_page = testRTU_Frame(self.test_RTU_button.text(),"background-color: orange;")
            self.tsRTU_page_index = self.stacked_widget.addWidget(tsRTU_page)

        if self.current_page_index != self.tsRTU_page_index:
            self.stacked_widget.setCurrentIndex(self.tsRTU_page_index)
            self.current_page_index = self.tsRTU_page_index

        else:
            # 如果當前已經是主選單索引，再次切換到主選單
            self.stacked_widget.setCurrentIndex(self.tsRTU_page_index)

        # 根據當前的畫面索引顯示或隱藏按鈕
        self.menu_button.setVisible(self.current_page_index == self.plot_page_index)
        self.test_RTU_button.setVisible(self.current_page_index == self.plot_page_index)
        self.return_button.setVisible(self.current_page_index == self.tsRTU_page_index)

        print('Current Page Index:', self.current_page_index)


    # 在MyWindow類別中新增一個方法用於切換畫面
    def switch_to_menu(self):
        if self.isLogin == False:
            print('請先登入解鎖')
            self.is_login_dialog()
            
        else:
            print('進入目錄成功')
            if self.menu_page_index is None:
                menu_page = self.create_menu_page()
                self.menu_page_index = self.stacked_widget.addWidget(menu_page)

            if self.current_page_index != self.menu_page_index:
                self.stacked_widget.setCurrentIndex(self.menu_page_index)
                self.current_page_index = self.menu_page_index

            else:
                # 如果當前已經是主選單索引，再次切換到主選單
                self.stacked_widget.setCurrentIndex(self.menu_page_index)

            # 根據當前的畫面索引顯示或隱藏按鈕
            self.menu_button.setVisible(self.current_page_index == self.plot_page_index)
            # self.test_RTU_button.setVisible(self.current_page_index == self.plot_page_index)
            self.return_button.setVisible(self.current_page_index == self.menu_page_index)

            print('Current Page Index:', self.current_page_index)

    
    # 在MyWindow中新增一個方法用於創建選單畫面
    def create_menu_page(self):       

        menu_page = QFrame(self)
        menu_page.setStyleSheet("background-color: green;")  # 選單畫面背景顏色

        font.setPointSize(32)
        # menu_label = QLabel('選單')
        # menu_label.setAlignment(Qt.AlignCenter)  # 文字置中
        # menu_label.setFont(font)
        menu_page_layout = QGridLayout(menu_page)
        menu_page_layout.setSpacing(0)
        # menu_page_layout.addWidget(menu_label)

        # 顯示四個按鈕
        self.set_button = QPushButton('設定', menu_page)
        self.calibrate_button = QPushButton('校正', menu_page)
        self.record_button = QPushButton('記錄', menu_page)
        self.identify_button = QPushButton('識別', menu_page)

            # 設定按鈕大小
        button_width, button_height = 300, 300

        self.set_button.setFixedSize(button_width, button_height)
        self.calibrate_button.setFixedSize(button_width, button_height)
        self.record_button.setFixedSize(button_width, button_height)
        self.identify_button.setFixedSize(button_width, button_height)

        # 設定按鈕的背景顏色，方便檢查它們的可見性
        self.set_button.setStyleSheet("background-color: pink;")
        self.calibrate_button.setStyleSheet("background-color: lightgreen;")
        self.record_button.setStyleSheet("background-color: lightblue;")
        self.identify_button.setStyleSheet("background-color: yellow;")

        self.set_button.setFont(font)
        self.calibrate_button.setFont(font)
        self.record_button.setFont(font)
        self.identify_button.setFont(font)

        # 連接按鈕點擊事件
        self.set_button.clicked.connect(lambda: self.show_sub_page(self.set_button.text(),self.set_button.styleSheet()))
        self.calibrate_button.clicked.connect(lambda: self.show_sub_page(self.calibrate_button.text(),self.calibrate_button.styleSheet()))
        self.record_button.clicked.connect(lambda: self.show_sub_page(self.record_button.text(),self.record_button.styleSheet()))
        self.identify_button.clicked.connect(lambda: self.show_sub_page(self.identify_button.text(),self.identify_button.styleSheet()))

        # 將按鈕添加到GridLayout中
        menu_page_layout.addWidget(self.set_button, 0, 0, 1, 1)
        menu_page_layout.addWidget(self.calibrate_button, 0, 1, 1, 1)
        menu_page_layout.addWidget(self.record_button, 1, 0, 1, 1)
        menu_page_layout.addWidget(self.identify_button, 1, 1, 1, 1)

        # print('登入：',self.logout_button.isVisible())
        return menu_page


    def show_sub_page(self, page_name, _style):
        print('登入：',self.logout_button.isVisible())

        # if self.logout_button.isVisible()==False and page_name!='識別':
        #     print(self.logout_button.isVisible(),page_name!='識別')
        #     self.is_login_dialog(page_name)
        # else:

        # 隱藏選單按鈕
        self.menu_button.setVisible(False)

        # 判斷是否已經創建了該子畫面
        if page_name not in self.sub_pages or not self.stacked_widget.widget(self.sub_pages[page_name]):
            # 如果還沒有，則創建一個新的子畫面
            sub_page = menuSubFrame(page_name, _style, self.sub_pages, self.stacked_widget, self)

            # 添加到堆疊中
            sub_page_index = self.stacked_widget.addWidget(sub_page)
            self.sub_pages[page_name] = sub_page_index
        else:
            # 如果已經存在，取得子畫面的索引
            sub_page_index = self.sub_pages[page_name]

            # 強制刷新子畫面
            sub_page = self.stacked_widget.widget(sub_page_index)
            # sub_page.update()  # 假設您的子畫面有 update 方法

        # # 設定當前顯示的子畫面索引
        self.stacked_widget.setCurrentIndex(sub_page_index)
        self.current_page_index = sub_page_index
        print('Current Page Index:', self.current_page_index)

        # 觸發標題的 print
        print('進入：', page_name)

        # 顯示返回按鈕
        self.return_button.setVisible(True)

    def is_login_dialog(self):
        # 顯示確認對話框
        message_text="你要先登入解鎖才能進入目錄"
        QMessageBox.critical(self, '請先登入', message_text)
        print('目錄不可用')


    # 在 MyWindow 中新增一個方法用於返回上一個畫面
    def switch_to_previous_page(self):
        if self.stacked_widget is not None:
        
            # 如果當前是選單畫面，直接返回主畫面
            if self.current_page_index == self.menu_page_index:
                self.stacked_widget.setCurrentIndex(self.plot_page_index)
                self.current_page_index = self.plot_page_index

            # RTU測試畫面返回主畫面
            elif self.current_page_index == self.tsRTU_page_index:
                self.stacked_widget.setCurrentIndex(self.plot_page_index)
                self.current_page_index = self.plot_page_index
                
            else:
                # 清除之前的子畫面
                previous_sub_frame = self.stacked_widget.currentWidget()
                self.stacked_widget.removeWidget(previous_sub_frame)

                # 更新當前的畫面索引
                self.current_page_index = self.stacked_widget.currentIndex()

                # 如果返回主畫面，將menu_page_index設為None
                if self.current_page_index == self.plot_page_index:
                    self.menu_page_index = None

                # 刪除已經移除的子畫面的索引
                for title, sub_page_index in list(self.sub_pages.items()):
                    if sub_page_index not in range(self.stacked_widget.count()):
                        del self.sub_pages[title]

                # 切換到更新後的畫面索引
                self.stacked_widget.setCurrentIndex(self.current_page_index)

            # 根據當前的畫面索引顯示或隱藏按鈕
            self.menu_button.setVisible(self.current_page_index == self.plot_page_index)
            # self.test_RTU_button.setVisible(self.current_page_index == self.plot_page_index)
            self.return_button.setVisible(self.current_page_index != self.plot_page_index)

        print('Current Page Index:', self.current_page_index) 


if __name__ == '__main__':

    print("Current working directory:", os.getcwd())

    try:
        app = QApplication(sys.argv)
        window = MyWindow()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        input("Press Enter to exit")
        # 等待使用者按 Enter 鍵


    # app = QApplication(sys.argv)
    # window = MyWindow()
    # sys.exit(app.exec_())

        