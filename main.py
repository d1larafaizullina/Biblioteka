import sys
import sqlite3
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('biblio1.ui', self)  # Загружаем дизайн comboBox
        self.cb_fill()
        self.cb2_fill()
        self.pushButton.clicked.connect(self.filter1)
        self.pushButton_2.clicked.connect(self.find_by_name)

    def cb_fill(self):
        db = 'biblio_db.db'
        con = sqlite3.connect(db)
        cur = con.cursor()
        result = cur.execute("""SELECT FIO
                                FROM author""").fetchall()
        self.comboBox.clear()
        # добавляем пустую строчку
        self.comboBox.addItem((""))
        for item in result:
            self.comboBox.addItems(item)

    def cb2_fill(self):
        db = 'biblio_db.db'
        con = sqlite3.connect(db)
        cur = con.cursor()
        result = cur.execute("""SELECT genre
                                FROM genres""").fetchall()
        self.comboBox_2.clear()
        self.comboBox_2.addItem((""))
        for item in result:
            self.comboBox_2.addItems(item)

    def filter1(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Данные отсутствуют"))
        db = 'biblio_db.db'
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                    ON b.id_author = a.id
                    LEFT JOIN genres as g
                    ON b.id_genre = g.id;"""

        if self.comboBox.currentIndex() > 0 and \
           self.comboBox_2.currentIndex() > 0:
            sql = f"""SELECT b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id and b.id_author =
                        {self.comboBox.currentIndex()}
                    JOIN genres as g
                        ON b.id_genre = g.id and b.id_genre =
                        {self.comboBox_2.currentIndex()};"""
        elif self.comboBox.currentIndex() > 0:
            sql = f"""SELECT b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id and b.id_author =
                        {self.comboBox.currentIndex()}
                    JOIN genres as g
                        ON b.id_genre = g.id;"""
        elif self.comboBox_2.currentIndex() > 0:
            sql = f"""SELECT b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id
                    JOIN genres as g
                        ON b.id_genre = g.id and b.id_genre =
                        {self.comboBox_2.currentIndex()};"""

        result = cur.execute(sql).fetchall()
        # проверяем на пустой результат
        if result:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(
                                                     "Название книги"))
            self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem(
                                                     "Автор произведения"))
            self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem(
                                                     "жанр"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def find_by_name(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Данные отсутствуют"))
        db = 'biblio_db.db'
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id
                    JOIN genres as g
                        ON b.id_genre = g.id
                    WHERE b.name like '%{self.lineEdit.text()}%'"""
        result = cur.execute(sql).fetchall()
        # проверяем на пустой результат
        if result:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(
                                                     "Название книги"))
            self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem(
                                                     "Автор произведения"))
            self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem(
                                                     "жанр"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
