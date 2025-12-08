import os

class LibraryScanner:
    def __init__(self, library_path="libros"):
        # Detecta la ruta absoluta de la carpeta 'libros'
        self.base_path = os.path.join(os.getcwd(), library_path)
        
        # Si la carpeta no existe, la crea
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def scan_books(self):
        """Retorna una lista de rutas completas a archivos PDF."""
        pdf_files = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    pdf_files.append(full_path)
        return pdf_files