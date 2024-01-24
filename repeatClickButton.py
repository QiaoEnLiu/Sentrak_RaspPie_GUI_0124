
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import pyqtSignal

class RepeatClickButton(QPushButton):
    repeated_click = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.emit_repeated_click)

    def emit_repeated_click(self):
        print("repeated_click emitted")
        self.repeated_click.emit()
    
    def update(self):
        # 實現子畫面的更新邏輯
        print('SubFrame updated!')
        super.update()
        pass