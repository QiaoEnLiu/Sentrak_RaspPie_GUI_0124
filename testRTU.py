#zh-tw
# testEndFrame.py

#此程式碼為測試模擬RTU數據取得

try:
    import minimalmodbus, traceback, serial

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
    from PyQt5.QtGui import QFont
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")


font = QFont()
class testRTU_Frame(QWidget):
    def __init__(self, title, _style):
        super().__init__()
        print('RTU測試畫面：', title)

        self.title = title
        font = QFont()
        
        # testRTU_label = QLabel(title, self)
        # testRTU_label.setAlignment(Qt.AlignCenter)  
        # font.setPointSize(72)
        # testRTU_label.setFont(font)
        # testRTU_label.setStyleSheet(_style)

        # 標題列
        title_layout = QVBoxLayout()        
        self.title_label = QLabel(self.title, self)
        # title_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(36)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(_style)
        title_layout.addWidget(self.title_label)

        self.testRTU_layout = QVBoxLayout()

        self.RTU_Info_label = QLabel()
        # title_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(24)
        self.RTU_Info_label.setFont(font)
        # self.deviceInfo_label.setStyleSheet(_style) 

        # 將 deviceInfo_label 放入 QScrollArea
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(self.RTU_Info_label)

        self.testRTU_layout.addWidget(scroll_area)

        # 整體佈局
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(self.testRTU_layout)

        self.RTU_Info_label.setText('RTU測試數據')

        # 設置串列通訊
        ser = serial.Serial('COM3', 19200, timeout=1)  # 替換 'COM3' 為你的串列埠，9600 是波特率

        # 設置Modbus裝置
        instrument = minimalmodbus.Instrument(ser.port, 1)  # 1 是裝置地址

        try:
            # 讀取保持寄存器中的數據（根據你的模擬軟體設定）
            value = instrument.read_register(0, functioncode=3)  # 0 是寄存器地址，3 是功能碼（根據模擬軟體的設定）

            # 處理讀取到的數據
            print(f'Read value: {value}')

        except Exception as e:
            print(f'Error: {e}')

        finally:
            # 關閉串列通訊
            ser.close()
        