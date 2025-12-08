import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt


class LectorPDF(QMainWindow):
    def __init__(self):
        super().__init__()
        #Configuración de la ventana principal
        self.setWindowTitle("ZenPages - Versión Alpha")
        self.setGeometry(100, 100, 800, 600)
        #Texto de prueba
        self.label = QLabel("Probando pantalla principal", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)

#Bloque de ejecución
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = LectorPDF()
    ventana.show()
    sys.exit(app.exec())
