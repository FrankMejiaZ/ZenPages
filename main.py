import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt6.QtCore import Qt
from core.pdf_engine import PDFEngine

class LectorPDF(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Renderizado")
        self.setGeometry(100, 100, 1000, 800)

        self.scroll_area = QScrollArea()
        self.setCentralWidget(self.scroll_area)

        self.image_label = QLabel("Cargando PDF...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)

        # INICIAR EL MOTOR
        self.engine = PDFEngine()
        
        ruta_pdf = "demo.pdf"
        
        if os.path.exists(ruta_pdf):
            if self.engine.open_file(ruta_pdf):
                # Pedimos la página 0
                pixmap = self.engine.get_page_image(0, zoom=1.5)
                if pixmap:
                    self.image_label.setText("") # Borrar texto
                    self.image_label.setPixmap(pixmap) # Poner imagen
                else:
                    self.image_label.setText("Error al renderizar página.")
            else:
                self.image_label.setText("No se pudo abrir el PDF (formato inválido).")
        else:
            self.image_label.setText("¡Falta el archivo 'demo.pdf' en la carpeta!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = LectorPDF()
    ventana.show()
    sys.exit(app.exec())