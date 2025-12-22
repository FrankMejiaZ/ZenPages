import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QStackedWidget, QGridLayout, QFrame, QToolButton, QProgressBar, QTabBar)
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
        self.main = main_window_ref 
        self.scanner = LibraryScanner()
        self.layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Mi Biblioteca")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(title)

        # Tabs para filtros (Usamos QTabBar directamente para no tener el "cuerpo" vacío del QTabWidget)
        self.tabs = QTabBar()
        self.tabs.addTab("Todos")
        self.tabs.addTab("Leyendo")
        self.tabs.addTab("Terminados")
        self.tabs.setShape(QTabBar.Shape.RoundedNorth)
        self.tabs.setDrawBase(False) # Quitar la línea base para que se vea más limpio
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Contenedor para los tabs para darles un poco de estilo/margen si es necesario
        tabs_container = QWidget()
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(10, 0, 10, 0)
        tabs_layout.addWidget(self.tabs)
        tabs_layout.addStretch() # Alinear a la izquierda
        
        self.layout.addWidget(tabs_container)


        # Área de Scroll (Compartida para todos los libros, se repuebla según el tab)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;") # Quitar borde para limpieza
        self.content_widget = QWidget()
        self.grid = QGridLayout(self.content_widget)
        self.grid.setSpacing(15)
        self.scroll.setWidget(self.content_widget)
        
        # Añadimos el scroll al layout principal (debajo de los tabs)
        self.layout.addWidget(self.scroll)

        # Cache de libros para no re-escanear constantmente
        self.cached_books = []
        self.load_books_data()
        self.refresh_library() # Pinta el tab actual (Todos)

    def on_tab_changed(self, index):
        self.refresh_library()

    def load_books_data(self):
        """Escanea y prepara los datos básicos de libros (progreso, etc)"""
        raw_books = self.scanner.scan_books()
        self.cached_books = []
        
        db = DBManager()
        thumb_engine = PDFEngine()
        covers_dir = os.path.join("assets", "covers")
        if not os.path.exists(covers_dir):
            os.makedirs(covers_dir)

        for book_path in raw_books:
            book_name = os.path.basename(book_path)
            
            # Datos DB
            current, total = db.get_book_full_info(book_path)
            progress_pct = 0
            if total > 0:
                progress_pct = int((current / total) * 100)
            
            # Portada
            cover_filename = book_name + ".png"
            cover_path = os.path.join(covers_dir, cover_filename)
            if not os.path.exists(cover_path):
                thumb_engine.save_cover(book_path, cover_path)
            
            self.cached_books.append({
                "path": book_path,
                "name": book_name,
                "cover": cover_path,
                "progress": progress_pct
            })

    def refresh_library(self):
        # 1. Limpiar Grid
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # 2. Filtrar libros según Tab
        current_tab_idx = self.tabs.currentIndex()
        # 0: Todos, 1: Leyendo (0 < p < 100), 2: Terminados (p == 100)
        
        filtered_books = []
        for book in self.cached_books:
            p = book["progress"]
            if current_tab_idx == 0: # Todos
                filtered_books.append(book)
            elif current_tab_idx == 1: # Leyendo
                if 0 < p < 100:
                    filtered_books.append(book)
            elif current_tab_idx == 2: # Terminados
                if p == 100:
                    filtered_books.append(book)

        # 3. Renderizar
        row = 0
        col = 0
        max_cols = 4 # Un poco más ancho el grid

        for book_data in filtered_books:
            self.create_book_card(book_data, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Alineación para que no se expandan feo si hay pocos
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    def create_book_card(self, data, row, col):
        card_container = QWidget()
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(2)

        # Botón
        btn = QToolButton()
        btn.setText(data["name"])
        if os.path.exists(data["cover"]):
            btn.setIcon(QIcon(data["cover"]))
        
        btn.setIconSize(QSize(130, 190))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setFixedSize(150, 230)
        
        # Estilo mejorado
        btn.setStyleSheet("""
            QToolButton {
                background-color: #ffffff;
                color: #222; 
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QToolButton:hover {
                border: 2px solid #2196F3;
                background-color: #e3f2fd;
            }
        """)
        btn.clicked.connect(lambda ch, path=data["path"]: self.main.open_book(path))
        
        # Barra
        pbar = QProgressBar()
        pbar.setFixedHeight(8)
        pbar.setValue(data["progress"])
        pbar.setTextVisible(False)
        
        color = "#4CAF50" if data["progress"] == 100 else "#2196F3"
        pbar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #e0e0e0;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

        card_layout.addWidget(btn)
        card_layout.addWidget(pbar)
        
        self.grid.addWidget(card_container, row, col)

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
        # Actualizar datos antes de mostrar (para que los filtros y barras estén al día)
        self.library_view.load_books_data()
        self.library_view.refresh_library()
        self.stack.setCurrentIndex(0) # Vuelve a la vista biblioteca

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())