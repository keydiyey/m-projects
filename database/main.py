from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Master Data")
        self.setGeometry(100, 100, 400, 300)

        self.buildUI()

    def buildUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.label = Q
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        central_widget.setLayout(layout)

    

if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec()