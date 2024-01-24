#zh-tw 現在關掉線程不會再停止回應了，但我需要在成功連線後關閉介面時要持續讀取，因為我稍早提過此介面是由另一個介面開啟。
import sys, minimalmodbus, traceback, time
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QWidget,\
      QPushButton, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer


class ModbusThread(QThread):
    reading_finished = pyqtSignal(float)

    def __init__(self, instrument, parent=None):
        super(ModbusThread, self).__init__(parent)
        self.instrument = instrument
        self.max_retries = 3
        self.stop_requested = False
        

    def run(self):
        retries = 0
        while retries < self.max_retries and not self.stop_requested:
            try:
                time.sleep(1)
                value_read_float = self.instrument.read_float(2, functioncode=3)
                self.reading_finished.emit(value_read_float)
            except minimalmodbus.NoResponseError as e:
                print(f"No response from the instrument: {e}")
                retries += 1
                time.sleep(1)  # 等待一秒後進行重試
            except Exception as e:
                print(f"Unexpected error: {e}")
                traceback.print_exc()

        print("ModbusThread stopped.")

    def stop(self):
        self.stop_requested = True
        self.wait()



class ModbusRTUConfigurator(QDialog):

    value_updated = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial_port = QSerialPort(self)  # 初始化 QSerialPort 實例

        self.setWindowTitle("Modbus RTU Configurator")
        self.setFixedSize(420, 400)

        self.init_ui()
        # 最後，顯示對話框
        self.exec_()

        self.modbus_thread = ModbusThread(instrument, self)
        self.modbus_thread.reading_finished.connect(self.handle_reading_finished)
        self.modbus_thread.start()

    def init_ui(self):

        layout = QVBoxLayout()

        # COM Port
        com_layout = QHBoxLayout()
        com_label = QLabel('COM Port:')
        self.com_combo = QComboBox()
        self.populate_com_ports()
        com_layout.addWidget(com_label)
        com_layout.addWidget(self.com_combo)
        layout.addLayout(com_layout)

        # Baud Rate
        baud_layout = QHBoxLayout()
        baud_label = QLabel('Baud Rate:')
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200'])
        # 設定預設選項為 '9600'
        default_baud_rate = '9600'
        default_baud_index = self.baud_combo.findText(default_baud_rate)
        self.baud_combo.setCurrentIndex(default_baud_index)
        baud_layout.addWidget(baud_label)
        baud_layout.addWidget(self.baud_combo)
        layout.addLayout(baud_layout)

        # Data Bits
        data_bits_layout = QHBoxLayout()
        data_bits_label = QLabel('Data Bits:')
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(['5', '6', '7', '8'])
        # 設定預設選項為 '8'
        default_data_bits = '8'
        default_data_bits_index = self.data_bits_combo.findText(default_data_bits)
        self.data_bits_combo.setCurrentIndex(default_data_bits_index)
        data_bits_layout.addWidget(data_bits_label)
        data_bits_layout.addWidget(self.data_bits_combo)
        layout.addLayout(data_bits_layout)

        # Stop Bits
        stop_bits_layout = QHBoxLayout()
        stop_bits_label = QLabel('Stop Bits:')
        self.stop_bits_combo = QComboBox()
    
        stop_bits_mapping = {
            '1': QSerialPort.OneStop,
            '1.5': QSerialPort.OneAndHalfStop,
            '2': QSerialPort.TwoStop,
        }
        for stop_bit, stop_bits_enum in stop_bits_mapping.items():
            self.stop_bits_combo.addItem(stop_bit, stop_bits_enum)
        # 設定預設選項為 '1'
        default_stop_bit = '1'
        default_stop_bit_index = self.stop_bits_combo.findText(default_stop_bit)
        self.stop_bits_combo.setCurrentIndex(default_stop_bit_index)
        
        stop_bits_layout.addWidget(stop_bits_label)
        stop_bits_layout.addWidget(self.stop_bits_combo)
        layout.addLayout(stop_bits_layout)

        # Parity
        parity_layout = QHBoxLayout()
        parity_label = QLabel('Parity:')
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        # 設定預設選項為 'None'
        default_parity = 'None'
        default_parity_index = self.parity_combo.findText(default_parity)
        self.parity_combo.setCurrentIndex(default_parity_index)
        parity_layout.addWidget(parity_label)
        parity_layout.addWidget(self.parity_combo)
        layout.addLayout(parity_layout)

        # Connect Button
        self.connect_btn = QPushButton('Connect', self)
        self.connect_btn.clicked.connect(self.connect_serial)
        layout.addWidget(self.connect_btn)

        # Disconnect Button
        self.disconnect_btn = QPushButton('Disconnect', self)
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.disconnect_btn.setVisible(False)
        layout.addWidget(self.disconnect_btn)

        self.quit=  QPushButton('關閉', self)
        self.quit.clicked.connect(self.handle_quit_button_clicked)
        layout.addWidget(self.quit)

        self.state_label=QLabel('未連線')
        layout.addWidget(self.state_label)

        self.setLayout(layout)

        # 調整字型大小
        self.adjust_font_size()

    def populate_com_ports(self):
        com_ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.com_combo.addItems(com_ports)
        print('COM Ports:',com_ports)

    def connect_serial(self):
        global instrument
        com_port = self.com_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        data_bits = int(self.data_bits_combo.currentText())
        stop_bits = int(self.stop_bits_combo.currentData())
        parity_text = self.parity_combo.currentText()

        try:

            instrument = minimalmodbus.Instrument(com_port, 1)
            instrument.serial.baudrate = baud_rate
            instrument.serial.bytesize = data_bits
            instrument.serial.stopbits = stop_bits

            serial_parity=None

            if parity_text == 'None':
                serial_parity = minimalmodbus.serial.PARITY_NONE
            elif parity_text == 'Even':
                serial_parity = minimalmodbus.serial.PARITY_EVEN
            elif parity_text == 'Odd':
                serial_parity = minimalmodbus.serial.PARITY_ODD
            elif parity_text == 'Mark':
                serial_parity = minimalmodbus.serial.PARITY_MARK
            elif parity_text == 'Space':
                serial_parity = minimalmodbus.serial.PARITY_SPACE
            else:
                raise ValueError("Invalid parity option")
            
            instrument.serial.parity = serial_parity

            print(f'Serial port {com_port} connected successfully!')
            # 啟動線程
            self.modbus_thread = ModbusThread(instrument, self)
            self.modbus_thread.reading_finished.connect(self.handle_reading_finished)
            self.modbus_thread.start()

            self.connect_btn.setVisible(False)
            self.disconnect_btn.setVisible(True)
            self.state_label.setText('連線成功')
            
        except (IOError, ValueError) as e:
            print(f'Failed to connect to serial port {com_port}. Error: {e}')
            self.state_label.setText('連線失敗')
            
    def is_connected(self):
        return hasattr(self, 'modbus_thread') and self.modbus_thread.isRunning()
    
    def handle_reading_finished(self, value):
        print(f"成功讀取浮點數值：{round(value, 2)}")
        self.state_label.setText(f'測試讀取：{round(value, 2)}')
        # self.value_updated.emit(value)

    def disconnect_serial(self):
        # 停止線程
        self.modbus_thread.stop()
        self.modbus_thread.wait()
        # self.modbus_thread.quit()
        # del self.modbus_thread
        self.serial_port.close()
        print('Port Disconnect.')
        self.state_label.setText('關閉連線')


        self.connect_btn.setVisible(True)
        self.disconnect_btn.setVisible(False)


    def handle_quit_button_clicked(self):
        # 在介面關閉時不斷開連接，但停止線程
        if hasattr(self, 'modbus_thread'):
            if self.modbus_thread.isRunning():
                # 線程正在運行，不需要停止或等待
                print('Interface Closed. Thread will continue reading.')
            else:
                # 線程未運行，可以進行必要的清理操作
                print('Interface Closed. Thread is not running.')



    def adjust_font_size(self):
        font = QFont()
        font.setPointSize(32)  # 設置字型大小

        for widget in self.findChildren(QLabel):
            widget.setFont(font)

        for widget in self.findChildren(QPushButton):
            widget.setFont(font)

        for widget in self.findChildren(QComboBox):
            widget.setFont(font)

