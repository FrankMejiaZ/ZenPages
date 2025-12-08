import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QStackedWidget, QGridLayout, QFrame, QToolButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

# Importamos módulos
from core.pdf_engine import PDFEngine
from database.db_manager import DBManager
from core.library_scanner import LibraryScanner

# VISTA 1: LA BIBLIOTECA
class LibraryView(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main = main_window_ref # Referencia para poder cambiar de pantalla
        self.scanner = LibraryScanner()
        self.layout = QVBoxLayout(self)
        
        title = QLabel("Mi Biblioteca Zen")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(title)

        # Área de Scroll para los libros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.grid = QGridLayout(self.content_widget)
        scroll.setWidget(self.content_widget)
        self.layout.addWidget(scroll)

        self.refresh_library()

    def refresh_library(self):
        """Escanea la carpeta, genera portadas y crea la grilla visual."""
        books = self.scanner.scan_books()
        
        # Limpiar grid anterior
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)

        row = 0
        col = 0
        max_cols = 3 
        
        # Ruta donde guardamos las portadas
        covers_dir = os.path.join("assets", "covers")
        if not os.path.exists(covers_dir):
            os.makedirs(covers_dir)
            
        # Motor temporal solo para generar portadas sin afectar al lector principal
        thumb_engine = PDFEngine() 

        for book_path in books:
            book_name = os.path.basename(book_path)
            
            # Definir ruta de la imagen de portada (nombre_del_pdf.png)
            cover_filename = book_name + ".png"
            cover_path = os.path.join(covers_dir, cover_filename)
            
            # 1. Si la portada no existe, la creamos
            if not os.path.exists(cover_path):
                # Generamos la imagen
                thumb_engine.save_cover(book_path, cover_path)
            
            # 2. Configurar el botón visual (QToolButton es mejor para Icono + Texto)
            btn = QToolButton()
            btn.setText(book_name)
            
            # Cargar el icono desde el archivo generado
            if os.path.exists(cover_path):
                btn.setIcon(QIcon(cover_path))
            else:
                # Si falló, quizás un icono genérico o nada
                pass
                
            # Configuración visual del botón
            btn.setIconSize(QSize(140, 200)) # Tamaño de la imagen
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon) # Texto abajo
            btn.setFixedSize(160, 240) # Tamaño total del botón
            
            # Estilo CSS para que se vea elegante y el texto sea negro
            btn.setStyleSheet("""
                QToolButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 5px;
                    font-size: 11px;
                }
                QToolButton:hover {
                    background-color: #e6f7ff;
                    border: 1px solid #1890ff;
                }
            """)
            
            # Conectar clic
            btn.clicked.connect(lambda ch, path=book_path: self.main.open_book(path))
            
            self.grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

# VISTA 2: EL LECTOR (LO QUE YA SE TENÍA)
class ReaderView(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main = main_window_ref
        self.engine = PDFEngine()
        self.db = DBManager()
        
        self.current_file = None
        self.current_page_num = 0
        self.total_pages = 0

        # Layout principal
        layout = QVBoxLayout(self)

        # Barra superior con botón "Volver"
        top_bar = QHBoxLayout()
        btn_back = QPushButton("🔙 Volver a Biblioteca")
        btn_back.clicked.connect(self.go_back)
        top_bar.addWidget(btn_back)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Área de lectura
        self.scroll_area = QScrollArea()
        self.image_label = QLabel("Cargando...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Controles de abajo
        controls = QHBoxLayout()
        self.btn_prev = QPushButton("<< Anterior")
        self.btn_prev.clicked.connect(self.prev_page)
        self.lbl_info = QLabel("0 / 0")
        self.btn_next = QPushButton("Siguiente >>")
        self.btn_next.clicked.connect(self.next_page)
        
        controls.addWidget(self.btn_prev)
        controls.addWidget(self.lbl_info)
        controls.addWidget(self.btn_next)
        layout.addLayout(controls)

    def load_file(self, path):
        self.current_file = path
        if self.engine.open_file(path):
            self.total_pages = self.engine.get_total_pages()
            # Recuperar memoria
            self.current_page_num = self.db.get_book_progress(path)
            self.render_page()
        else:
            self.image_label.setText("Error al abrir PDF")

    def render_page(self):
        pixmap = self.engine.get_page_image(self.current_page_num, zoom=1.5)
        if pixmap:
            self.image_label.setPixmap(pixmap)
            self.lbl_info.setText(f"Página: {self.current_page_num + 1} / {self.total_pages}")
            self.db.update_book_progress(self.current_file, self.current_page_num, self.total_pages)
        
        self.btn_prev.setEnabled(self.current_page_num > 0)
        self.btn_next.setEnabled(self.current_page_num < self.total_pages - 1)

    def next_page(self):
        if self.current_page_num < self.total_pages - 1:
            self.current_page_num += 1
            self.render_page()

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.render_page()

    def go_back(self):
        # Avisa al Main Window que vuelva a la pantalla 0
        self.main.show_library()

# VENTANA PRINCIPAL (El Contenedor)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZenPages Reader")
        self.resize(1000, 800)

        # Gestiona las pantallas como
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las dos vistas
        self.library_view = LibraryView(self)
        self.reader_view = ReaderView(self)

        # Añade al stack
        self.stack.addWidget(self.library_view) # Índice 0
        self.stack.addWidget(self.reader_view)  # Índice 1

        # Mostrar biblioteca primero
        self.stack.setCurrentIndex(0)

    def open_book(self, file_path):
        print(f"Abriendo libro: {file_path}")
        self.reader_view.load_file(file_path) # Cargar el libro en la vista lector
        self.stack.setCurrentIndex(1) # Cambia a vista lector

    def show_library(self):
        self.stack.setCurrentIndex(0) # Vuelve a la vista biblioteca

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())