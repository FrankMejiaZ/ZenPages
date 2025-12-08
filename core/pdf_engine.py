import fitz
from PyQt6.QtGui import QImage, QPixmap

class PDFEngine:
    def __init__(self):
        self.doc = None
    
    def open_file(self, file_path):
        try:
            self.doc = fitz.open(file_path)
            return True
        except Exception as e:
            print(f"Error al abrir PDF: {e}")
            return False
    
    def get_page_image(self, page_num, zoom=1.0):
        if not self.doc:
            return None
        
        if page_num < 0 or page_num >= len(self.doc):
            return None
        
        page = self.doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_format = QImage.Format.Format_RGB888
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        return QPixmap.fromImage(qimg)
    
    def get_total_pages(self):
        if self.doc:
            return len(self.doc)
        return 0
    
    def save_cover(self, pdf_path, save_path, width=200):
        """
        Abre el PDF, toma la primera página y la guarda como imagen PNG.
        Retorna True si tuvo éxito.
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0) # Primera página
            
            zoom = width / 600
            mat = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=mat)
            pix.save(save_path) # Guardar en disco
            doc.close()
            return True
        except Exception as e:
            print(f"No se pudo generar portada para {pdf_path}: {e}")
            return False