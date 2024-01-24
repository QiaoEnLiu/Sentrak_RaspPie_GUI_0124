#zh-tw
# deviceInFo.py

#此程式碼為「識別」底下「儀器資訊」
#--「儀器資訊」為deviceInfoFrame
#--「感測器資訊」暫時進入testEndFrame.py

try:
    
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
    from PyQt5.QtGui import QFont

    import platform, os, subprocess, re, traceback, psutil
    # import RPi.GPIO as GPIO

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    input("Press Enter to exit")

font = QFont()

class deviceInfoFrame(QWidget):
    def __init__(self, title, _style, user, stacked_widget, sub_pages):
        super().__init__()
        # print(title)
        print('測試畫面：', title)
        self.title = title
        self.user=user
        self.sub_pages=sub_pages

        # 標題列
        title_layout = QVBoxLayout()        
        self.title_label = QLabel(self.title, self)
        # title_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(36)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(_style)
        title_layout.addWidget(self.title_label)
        # font.setPointSize(72)

        # title_layout.setContentsMargins(0, 0, 0, 0)
        # title_layout.setSpacing(0)

        deviceInfo_layout = QVBoxLayout()
        # deviceInfo_layout.setContentsMargins(0, 0, 0, 0)
        # deviceInfo_layout.setSpacing(0)

        self.deviceInfo_label = QLabel()
        # title_label.setAlignment(Qt.AlignCenter)  
        font.setPointSize(24)
        self.deviceInfo_label.setFont(font)
        # self.deviceInfo_label.setStyleSheet(_style) 

        # 將 deviceInfo_label 放入 QScrollArea
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(self.deviceInfo_label)

        deviceInfo_layout.addWidget(scroll_area)

        # 整體佈局
        main_layout = QVBoxLayout(self)
        # main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(deviceInfo_layout)


        cpu_info = 'CPU 資訊:' + self.get_cpu_info() + '\n'
        # print(cpu_info)

        gpu_info = 'GPU 資訊:' + self.get_gpu_info() + '\n'
        # print(gpu_info)

        # memory_info ='記憶體資訊:' + '暫未提供' + '\n'
        memory_info ='記憶體資訊:' + self.get_memory_info() + '\n'
        # print(memory_info)

        disk_info = '硬碟資訊:' + '暫未提供' + '\n'
        # for info in self.get_disk_info(): 
            # disk_info += info + '\n'
        # print(disk_info)

        # network_info = '網路介面資訊:' + '暫未提供' + '\n'
        network_info = '網路介面資訊:' + '\n'
        for line in self.get_network_info():
            network_info += line + '\n'
        # print(network_info)

        gpio_info = 'GPIO 資訊:' + '暫未提供' + '\n'
        # gpio_info = 'GPIO 資訊:' + self.get_gpio_info()
        # print(gpio_info) 

        self.deviceInfo_label.setText(cpu_info + gpu_info + memory_info + disk_info + network_info + gpio_info)

        
        print(title ,user.userInfo())


        self.stacked_widget = stacked_widget
        deviceInfo_index = self.stacked_widget.addWidget(self)
        self.current_page_index = deviceInfo_index # 將當前的畫面索引設為 plot_page_index
        # 設定當前顯示的子畫面索引
        print('Current Page Index:', self.current_page_index)


    def get_cpu_info(self):
        if platform.system() == 'Windows':
            return platform.processor()
        elif platform.system() == 'Linux':
            # 在 Linux 中，可以讀取 /proc/cpuinfo 檔案
            with open('/proc/cpuinfo', 'r') as file:
                cpu_info = file.read()
            return cpu_info
        elif platform.system() == 'Darwin':
            # 在 macOS 中，可以使用命令行工具 sysctl
            return os.popen('sysctl -n machdep.cpu.brand_string').read().strip()
        else:
            return '無法取得 CPU 資訊'
        
    
    def get_gpu_info(self):
        try:
            system_platform = platform.system()

            if system_platform == 'Windows':
                # 在Windows上使用wmic命令來取得GPU資訊
                result = subprocess.run(['wmic', 'path', 'win32_videocontroller', 'get', 'caption'], capture_output=True, text=True)
                gpu_info = result.stdout.strip()
                
                # 使用正則表達式保留第一個 "Caption"
                match = re.search(r'Caption\s*(.+)', gpu_info)
                if match:
                    gpu_info = match.group(1).strip()
                else:
                    gpu_info = '無法取得 GPU 資訊'
                    
                # 移除可能存在的空行
                gpu_info = gpu_info.replace('\n\n', '\n')
                
                # 使用正則表達式刪除所有不可見的字符
                gpu_info = re.sub(r'\s+', ' ', gpu_info).strip()

                
            elif system_platform == 'Linux':
                try:
                    # 在Linux上使用lshw命令來取得GPU資訊
                    result = subprocess.run(['lshw', '-c', 'video'], capture_output=True, text=True)
                    gpu_info = result.stdout.strip()
                except FileNotFoundError:
                    # 如果 lshw 命令不存在，嘗試讀取 /proc/device-tree/model
                    with open('/proc/device-tree/model', 'r') as file:
                        gpu_info = file.read()
            else:
                gpu_info = '不支援的操作系統'

            # 在 GPU 資訊開頭插入一行空行
            gpu_info = '\n' + gpu_info if gpu_info else gpu_info

            # 將 GPU 資訊中的換行符號替換為空字符串
            gpu_info = gpu_info.replace('\n', ' ')

            return gpu_info
        except Exception as e:
            return f'無法取得 GPU 資訊: {e}'
        

    def get_memory_info(self):
        # 使用 psutil 取得記憶體資訊
        memory = psutil.virtual_memory()
        return f'Total: {memory.total} bytes, Available: {memory.available} bytes'
    

    # def get_disk_info(self):
    #     # 使用 psutil 取得硬碟資訊
    #     partitions = psutil.disk_partitions()
    #     disk_info = []
    #     for partition in partitions:
    #         disk_usage = psutil.disk_usage(partition.mountpoint)
    #         disk_info.append(f'{partition.device}: Total={disk_usage.total} bytes, Free={disk_usage.free} bytes')
    #     return disk_info
    
    def get_network_info(self):
        try:
            interfaces = psutil.net_if_addrs()
            result = []
            for interface, addresses in interfaces.items():
                result.append(f' Interface: {interface}')
                for address in addresses:
                    result.append(f'   Address Family: {address.family}')
                    result.append(f'     Address: {address.address}')
                    result.append(f'     Netmask: {address.netmask}')
                    result.append(f'     Broadcast: {address.broadcast}')
            return result
        except Exception as e:
            return f'無法取得網路介面資訊: {e}'
        
    # def get_gpio_info(self):
    #     try:
    #         # 初始化 GPIO
    #         GPIO.setmode(GPIO.BCM)
            
    #         # 獲得 GPIO 狀態
    #         gpio_status = GPIO.input(17)  # 這裡的 17 是一個範例，請根據實際情況更改
            
    #         return f'GPIO 17 狀態: {gpio_status}'
    #     except Exception as e:
    #         return f'無法取得 GPIO 資訊: {e}'
    #     finally:
    #         # 清理 GPIO 設定
    #         GPIO.cleanup()