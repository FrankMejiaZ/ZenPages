import sqlite3
import os

class DBManager:
    def __init__(self, db_name="library.db"):
        # Esto crea el archivo en la carpeta database si no existe
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Crea la tabla de libros si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                file_path TEXT PRIMARY KEY,
                title TEXT,
                total_pages INTEGER,
                current_page INTEGER,
                last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def update_book_progress(self, file_path, current_page, total_pages):
        """Guarda o actualiza el progreso de lectura."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Usamos REPLACE para insertar si no existe, o actualizar si ya existe
        # Para evitar lógica compleja
        cursor.execute('''
            INSERT INTO books (file_path, current_page, total_pages, last_read)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path) DO UPDATE SET
                current_page=excluded.current_page,
                last_read=CURRENT_TIMESTAMP
        ''', (file_path, current_page, total_pages))
        
        conn.commit()
        conn.close()

    def get_book_progress(self, file_path):
        """Devuelve la última página leída. Retorna 0 si el libro es nuevo."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT current_page FROM books WHERE file_path = ?', (file_path,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return 0

    def get_book_full_info(self, file_path):
        """
        Devuelve una tupla (current_page, total_pages).
        Si el libro no existe, devuelve (0, 0).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT current_page, total_pages FROM books WHERE file_path = ?', (file_path,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return (row[0], row[1])
        return (0, 0)