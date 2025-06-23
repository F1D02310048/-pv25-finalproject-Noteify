import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QStatusBar, QFileDialog, QMenuBar, QAction, QTextEdit
)
from PyQt5.QtCore import Qt
from datetime import datetime

class NoteifyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noteify")
        self.setGeometry(100, 100, 600, 400)

        self.init_db() # inisialisasi database
        self.create_menu() # buat menu bar
        self.create_status_bar() 
        self.create_main_layout() # tampilan utama
        self.setStyleSheet("""
    QPushButton {
        padding: 8px;
        font-weight: bold;
        background-color: #FFB6C1;  
        color: black;
        border: none;
        border-radius: 6px;
    }

    QPushButton:hover {
        background-color: #FF69B4;  
        color: white;
    }

""") 
    def init_db(self):  # menghubungkan ke database SQLite
        self.conn = sqlite3.connect("notes.db")
        self.cursor = self.conn.cursor() # membuat tabel
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                date TEXT,
                status TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def create_menu(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File") # menu file berisi export CSV
        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)

        help_menu = menubar.addMenu("Help")  # menu help berisi about
        help_menu.addAction("About", lambda: QMessageBox.information(self, "About", "Noteify adalah aplikasi catatan harian digital yang dirancang untuk membantu "
                                                                     "pengguna mencatat aktivitas harian, ide, status tugas, atau memo penting secara terorganisir"))
        
        exit_menu = menubar.addMenu("Exit")
        exit_action = QAction("Keluar Aplikasi", self)
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)

        self.setMenuBar(menubar)

    def create_status_bar(self):  # buat status bar 
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        info = QLabel("Fadila Rahmania (F1D02310048)")
        status_bar.addPermanentWidget(info)

    def create_main_layout(self): # tampilan utama aplikasi (input dan tabel)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.title_input = QLineEdit()  # menginput judul, kategori, catatan, dan status
        self.title_input.setPlaceholderText("Judul")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Kategori")
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("Status")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Catatan")

        self.save_btn = QPushButton("Simpan") # tombol untuk menyimpan
        self.save_btn.clicked.connect(self.save_note)

        self.delete_btn = QPushButton("Hapus")
        self.delete_btn.clicked.connect(self.delete_note)

        self.table = QTableWidget(0, 5)  # tabel untuk menampilkan data 
        self.table.setHorizontalHeaderLabels(["Judul", "Kategori", "Tanggal", "Status", "Catatan"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.title_input) # menambahkan semua widget ke layout
        layout.addWidget(self.category_input)
        layout.addWidget(self.status_input)
        layout.addWidget(self.notes_input)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.table)
        layout.addWidget(self.delete_btn)

        self.setCentralWidget(widget)
        self.load_notes() # tampilkan data yang ada di database

    def save_note(self):  # ambil data yang di input
        title = self.title_input.text()
        category = self.category_input.text()
        status = self.status_input.text()
        notes = self.notes_input.toPlainText()
        date = datetime.now().strftime("%Y-%m-%d")

        if not title :
            QMessageBox.warning(self, "Judul wajib diisi")
            return

        self.cursor.execute("INSERT INTO notes (title, category, date, status, notes) VALUES (?, ?, ?, ?, ?)",
                            (title, category, date, status, notes)) # simpan data ke database
        self.conn.commit()
        
        # kosongkan dan muat ulang tabel input
        self.clear_inputs()
        self.load_notes()
     
    def clear_inputs(self):  # kosongkan semua input
        self.title_input.clear()
        self.category_input.clear()
        self.status_input.clear()
        self.notes_input.clear()

    def load_notes(self):    # tampilkan semua catatan dari database ke tabel
        self.table.setRowCount(0)
        self.note_ids = []  # simpan id catatan untuk mempermudah hapus
        self.cursor.execute("SELECT id, title, category, date, status, notes FROM notes ORDER BY date DESC")
        for row_idx, row_data in enumerate(self.cursor.fetchall()):
            self.table.insertRow(row_idx)
            self.note_ids.append(row_data[0])  # simpan id ke list 
            for col_idx, col_data in enumerate(row_data[1:]):  # lewati kolom id (tidak ditampilkan)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
    
    def delete_note(self):
        selected = self.table.currentRow() # hapus catatan yang dipilih 
        if selected < 0:
            QMessageBox.warning(self, "Hapus Catatan", "Pilih catatan yang ingin dihapus.")
            return
        note_id = self.note_ids[selected]  # ambil id catatan yang sudah dipilih
        confirm = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus catatan ini?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self.conn.commit()
            self.load_notes() # muat ulang tabel 

    def export_to_csv(self):   # ekspor semua catatan ke file CSV
        file_name, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "catatan_terbaru.csv", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Judul", "Kategori", "Tanggal", "Status", "Catatan"])
                self.cursor.execute("SELECT title, category, date, status, notes FROM notes")
                for row in self.cursor.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, f"Catatan berhasil diekspor ke {file_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NoteifyApp()
    window.show()
    sys.exit(app.exec_())