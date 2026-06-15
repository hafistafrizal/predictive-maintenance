import sys
from PySide6.QtWidgets import *

from database.db_koneksi import DatabaseKendaraan
from ui.torque_view import TampilanTorque

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SISTEM MANAJEMEN TORSI")
        self.resize(1000, 600)

        self.db = DatabaseKendaraan()

        self.view = TampilanTorque(self.db)

        self.setCentralWidget(self.view)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
