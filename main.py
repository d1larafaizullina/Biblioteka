import sys
import sqlite3
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit, QTabWidget
from PyQt5.QtWidgets import QDialog, QMessageBox, QHeaderView


DATABASE = 'DATA/biblio_db.db'
DIALOG1 = 'Dialog1.ui'  # Диалог однострочный (авторы, жанры)
DIALOG3 = 'Dialog3.ui'  # Диалог трехстрочный книги


class BiblioMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('biblio1.ui', self)  # Загружаем дизайн comboBox
        self.setWindowTitle("Библиотека 2.0")
        self.sel_author()
        self.sel_genre()
        self.pushButton.clicked.connect(self.filter1)
        self.pushButton_2.clicked.connect(self.find_by_name)
        self.pushButton_5.clicked.connect(self.del_genre)
        self.pushButton_4.clicked.connect(self.edit_genre)
        self.pushButton_3.clicked.connect(self.add_genre)
        self.pushButton_6.clicked.connect(self.add_author)
        self.pushButton_7.clicked.connect(self.edit_author)
        self.pushButton_8.clicked.connect(self.del_author)
        self.pushButton_9.clicked.connect(self.add_dialog)
        self.pushButton_10.clicked.connect(self.edit_dialog)
        self.pushButton_11.clicked.connect(self.del_dialog)

    def add_dialog(self):
        dlg = AddBookDialog()
        dlg.exec_()
        self.filter1()

    def edit_dialog(self):
        if self.tableB.currentRow() > -1:
            row = self.tableB.currentRow()
            id_ = int(self.tableB.item(row, 0).text())
            title = self.tableB.item(row, 1).text()
            author = self.tableB.item(row, 2).text()
            genre = self.tableB.item(row, 3).text()
            dlg = EditBookDialog(id_, title, author, genre)
            dlg.exec_()
            self.filter1()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def del_dialog(self):
        if self.tableB.currentRow() > -1:
            row = self.tableB.currentRow()
            id_ = int(self.tableB.item(row, 0).text())
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Удалить элемент")
            dlg.setText("Вы действительно хотите удалить запись " +
                        str(id_) + " ?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()
            if button == QMessageBox.Yes:
                db = DATABASE
                con = sqlite3.connect(db)
                cur = con.cursor()
                sql = f"""DELETE FROM books WHERE id = {id_};"""
                result = cur.execute(sql)
                con.commit()
                con.close()
            self.filter1()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def cb_author_fill(self, authors):
        self.comboBox.clear()
        # добавляем пустую строчку
        self.comboBox.addItem(("Все"))
        for i, item in authors:
            self.comboBox.addItem(item)

    def cb2_genre_fill(self, genres):
        self.comboBox_2.clear()
        self.comboBox_2.addItem(("Все"))
        for i, item in genres:
            self.comboBox_2.addItem(item)

    def filter1(self):
        self.tableB.clearContents()
        self.tableB.setRowCount(1)
        self.tableB.setColumnCount(1)
        self.tableB.setItem(0, 0, QTableWidgetItem("Данные отсутствуют"))
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()

        sql = f"""
                SELECT id FROM author
                WHERE FIO = '{self.comboBox.currentText()}';
                """
        cur.execute(sql)
        authorId = cur.fetchone()

        sql = f"""
                SELECT id FROM genres
                WHERE genre = '{self.comboBox_2.currentText()}';
                """
        cur.execute(sql)
        genreId = cur.fetchone()

        sql = f"""SELECT b.id, b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                    ON b.id_author = a.id
                    LEFT JOIN genres as g
                    ON b.id_genre = g.id;"""

        if authorId and genreId:
            sql = f"""SELECT b.id, b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id and b.id_author =
                        {authorId[0]}
                    JOIN genres as g
                        ON b.id_genre = g.id and b.id_genre =
                        {genreId[0]};"""
        elif authorId:
            sql = f"""SELECT b.id, b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id and b.id_author =
                        {authorId[0]}
                    JOIN genres as g
                        ON b.id_genre = g.id;"""
        elif genreId:
            sql = f"""SELECT b.id, b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id
                    JOIN genres as g
                        ON b.id_genre = g.id and b.id_genre =
                        {genreId[0]};"""

        result = cur.execute(sql).fetchall()
        # проверяем на пустой результат
        if result:
            self.tableB.setRowCount(len(result))
            self.tableB.setColumnCount(len(result[0]))
            self.tableB.setHorizontalHeaderItem(0, QTableWidgetItem(
                                                     "Id"))
            self.tableB.setHorizontalHeaderItem(1, QTableWidgetItem(
                                                     "Название книги"))
            self.tableB.setHorizontalHeaderItem(2, QTableWidgetItem(
                                                     "Автор произведения"))
            self.tableB.setHorizontalHeaderItem(3, QTableWidgetItem(
                                                     "Жанр"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableB.setItem(i, j, QTableWidgetItem(str(val)))

    def find_by_name(self):
        self.tableB.clearContents()
        self.tableB.setRowCount(1)
        self.tableB.setColumnCount(1)
        self.tableB.setItem(0, 0, QTableWidgetItem("Данные отсутствуют"))
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT b.id, b.name, a.FIO, g.genre
                    FROM books as b JOIN author a
                        ON b.id_author = a.id
                    JOIN genres as g
                        ON b.id_genre = g.id
                    WHERE b.name like '%{self.lineEdit.text()}%'"""
        result = cur.execute(sql).fetchall()
        # проверяем на пустой результат
        if result:
            self.tableB.setRowCount(len(result))
            self.tableB.setColumnCount(len(result[0]))
            self.tableB.setHorizontalHeaderItem(0, QTableWidgetItem(
                                                     "Id"))
            self.tableB.setHorizontalHeaderItem(1, QTableWidgetItem(
                                                     "Название книги"))
            self.tableB.setHorizontalHeaderItem(2, QTableWidgetItem(
                                                     "Автор произведения"))
            self.tableB.setHorizontalHeaderItem(3, QTableWidgetItem(
                                                     "Жанр"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableB.setItem(i, j, QTableWidgetItem(str(val)))

    def sel_genre(self):
        self.tableG.clearContents()
        self.tableG.setRowCount(1)
        self.tableG.setColumnCount(1)
        self.tableG.setItem(0, 0,
                            QTableWidgetItem("Данные отсутствуют"))
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT id, genre FROM genres;"""
        result = cur.execute(sql).fetchall()
        if result:
            self.cb2_genre_fill(result)

            self.tableG.setRowCount(len(result))
            self.tableG.setColumnCount(len(result[0]))
            self.tableG.setHorizontalHeaderItem(0, QTableWidgetItem(
                "Id"))
            self.tableG.setHorizontalHeaderItem(1, QTableWidgetItem(
                "Название жанра"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableG.setItem(i, j,
                                        QTableWidgetItem(str(val)))

    def add_genre(self):
        dlg = AddGenreDialog()
        dlg.exec_()
        self.sel_genre()

    def edit_genre(self):
        if self.tableG.currentRow() > -1:
            row = self.tableG.currentRow()
            id_ = int(self.tableG.item(row, 0).text())
            title = self.tableG.item(row, 1).text()
            dlg = EditGenreDialog(id_, title)
            dlg.exec_()
            self.sel_genre()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def del_genre(self):
        if self.tableG.currentRow() > -1:
            row = self.tableG.currentRow()
            id_ = int(self.tableG.item(row, 0).text())
            if self.check_del_genre(id_):
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Удаление записи не возможно.")
                dlg.setText("Сначала удалите все книги с этим жанром!")
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.exec()
                return
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Удалить запись")
            dlg.setText("Вы действительно хотите удалить запись " +
                        str(id_) + " ?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()
            if button == QMessageBox.Yes:
                db = DATABASE
                con = sqlite3.connect(db)
                cur = con.cursor()
                sql = f"""DELETE FROM genres WHERE id = {id_};"""
                result = cur.execute(sql)
                con.commit()
                con.close()
            self.sel_genre()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def check_del_genre(self, id_):
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT id FROM books WHERE id_genre = {id_};"""
        result = cur.execute(sql).fetchone()
        if result:
            return True
        return False

    def sel_author(self):
        self.tableA.clearContents()
        self.tableA.setRowCount(1)
        self.tableA.setColumnCount(1)
        self.tableA.setItem(0, 0,
                            QTableWidgetItem("Данные отсутствуют"))
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT id, FIO FROM author;"""
        result = cur.execute(sql).fetchall()
        if result:
            self.cb_author_fill(result)

            self.tableA.setRowCount(len(result))
            self.tableA.setColumnCount(len(result[0]))
            self.tableA.setHorizontalHeaderItem(0, QTableWidgetItem(
                "Id"))
            self.tableA.setHorizontalHeaderItem(1, QTableWidgetItem(
                "ФИО автора"))

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableA.setItem(i, j,
                                        QTableWidgetItem(str(val)))

    def add_author(self):
        dlg = AddAuthorDialog()
        dlg.exec_()
        self.sel_author()

    def edit_author(self):
        if self.tableA.currentRow() > -1:
            row = self.tableA.currentRow()
            id_ = int(self.tableA.item(row, 0).text())
            title = self.tableA.item(row, 1).text()
            dlg = EditAuthorDialog(id_, title)
            dlg.exec_()
            self.sel_author()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def del_author(self):
        if self.tableA.currentRow() > -1:
            row = self.tableA.currentRow()
            id_ = int(self.tableA.item(row, 0).text())
            if self.check_del_author(id_):
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Удаление записи не возможно.")
                dlg.setText("Сначала удалите все книги с этим автором!")
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.exec()
                return
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Удалить запись")
            dlg.setText("Вы действительно хотите удалить запись " +
                        str(id_) + " ?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()
            if button == QMessageBox.Yes:
                db = DATABASE
                con = sqlite3.connect(db)
                cur = con.cursor()
                sql = f"""DELETE FROM author WHERE id = {id_};"""
                result = cur.execute(sql)
                con.commit()
                con.close()
            self.sel_author()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ошибка!")
            dlg.setText("Не выбрана запись для редактирования")
            dlg.exec()

    def check_del_author(self, id_):
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = f"""SELECT id FROM books WHERE id_author = {id_};"""
        result = cur.execute(sql).fetchone()
        if result:
            return True
        return False


class Dialog1(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(DIALOG1, self)
        self.valid_err = "Поле не заполнено"

    def valid_record(self):
        if len(self.lineEdit.text()) == 0:
            self.label_5.setText(self.valid_err)
            return False
        return True


class AddGenreDialog(Dialog1):
    def __init__(self):
        super().__init__()
        self.valid_err = "Поле жанр не заполнено"
        self.setWindowTitle("Добавить запись")
        self.pushButton.setText("Добавить")
        self.pushButton.clicked.connect(self.add_record)

    def add_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()
            sql = f"""INSERT INTO genres (genre)
                      VALUES('{self.lineEdit.text()}');"""
            result = cur.execute(sql)
            con.commit()
            con.close()
            self.close()


class EditGenreDialog(Dialog1):
    def __init__(self, id_, title):
        super().__init__()
        self.id = id_
        self.lineEdit.setText(title)
        self.valid_err = "Поле жанр не заполнено"
        self.setWindowTitle("Редактировать запись")
        self.pushButton.setText("Изменить")
        self.pushButton.clicked.connect(self.edit_record)

    def edit_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()
            sql = f"""UPDATE genres
                    SET genre='{self.lineEdit.text()}'
                    WHERE id={self.id};"""
            result = cur.execute(sql)
            con.commit()
            con.close()
            self.close()


class AddAuthorDialog(Dialog1):
    def __init__(self):
        super().__init__()
        self.valid_err = "Поле автор не заполнено"
        self.setWindowTitle("Добавить запись")
        self.pushButton.setText("Добавить")
        self.pushButton.clicked.connect(self.add_record)

    def add_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()
            sql = f"""INSERT INTO author (FIO)
                      VALUES('{self.lineEdit.text()}');"""
            result = cur.execute(sql)
            con.commit()
            con.close()
            self.close()


class EditAuthorDialog(Dialog1):
    def __init__(self, id_, title):
        super().__init__()
        self.id = id_
        self.lineEdit.setText(title)
        self.valid_err = "Поле автор не заполнено"
        self.setWindowTitle("Редактировать запись")
        self.pushButton.setText("Изменить")
        self.pushButton.clicked.connect(self.edit_record)

    def edit_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()
            sql = f"""UPDATE author
                    SET FIO='{self.lineEdit.text()}'
                    WHERE id={self.id};"""
            result = cur.execute(sql)
            con.commit()
            con.close()
            self.close()


class BookDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(DIALOG3, self)
        self.genres_fill()

    def genres_fill(self):
        db = DATABASE
        con = sqlite3.connect(db)
        cur = con.cursor()

        result = cur.execute("""SELECT FIO
                                FROM author""").fetchall()
        self.comboBox.clear()
        for item in result:
            self.comboBox.addItems(item)

        result = cur.execute("""SELECT genre
                                FROM genres""").fetchall()
        self.comboBox_2.clear()
        for item in result:
            self.comboBox_2.addItems(item)

    def valid_record(self):
        if len(self.lineEdit.text()) == 0:
            self.label_5.setText("Не все поля заполнены")
            return False
        return True


class EditBookDialog(BookDialog):
    def __init__(self, id_, title, author, genre):
        super().__init__()
        self.id = id_
        self.lineEdit.setText(title)
        self.comboBox.setCurrentIndex(self.comboBox.findText(author))
        self.comboBox_2.setCurrentIndex(self.comboBox_2.findText(genre))
        self.setWindowTitle("Редактировать книгу")
        self.pushButton.setText("Изменить")
        self.pushButton.clicked.connect(self.edit_record)

    def edit_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()

            sql = f"""
                      SELECT id FROM author
                      WHERE FIO = '{self.comboBox.currentText()}';
                    """
            cur.execute(sql)
            authorId = cur.fetchone()

            sql = f"""
                      SELECT id FROM genres
                      WHERE genre = '{self.comboBox_2.currentText()}';
                    """
            cur.execute(sql)
            genreId = cur.fetchone()

            if authorId and genreId:
                sql = f"""UPDATE books
                        SET name='{self.lineEdit.text()}',
                            id_author={authorId[0]},
                            id_genre={genreId[0]}
                        WHERE id={self.id};"""
                result = cur.execute(sql)
                con.commit()
                con.close()
            self.close()


class AddBookDialog(BookDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить книгу")
        self.pushButton.setText("Добавить")
        self.pushButton.clicked.connect(self.add_record)

    def add_record(self):
        if self.valid_record():
            db = DATABASE
            con = sqlite3.connect(db)
            cur = con.cursor()

            sql = f"""
                      SELECT id FROM author
                      WHERE FIO = '{self.comboBox.currentText()}';
                    """
            cur.execute(sql)
            authorId = cur.fetchone()

            sql = f"""
                      SELECT id FROM genres
                      WHERE genre = '{self.comboBox_2.currentText()}';
                    """
            cur.execute(sql)
            genreId = cur.fetchone()

            if genreId and authorId:

                sql = f"""
                          SELECT id FROM books
                          WHERE name = '{self.lineEdit.text()}' and
                           id_author = {authorId[0]};
                        """
                cur.execute(sql)
                bookId = cur.fetchone()
                if bookId:  # книга существует
                    dlg = QMessageBox(self)
                    dlg.setIcon(QMessageBox.Warning)
                    dlg.setWindowTitle("Ошибка!")
                    dlg.setText("Книга уже существует.")
                    dlg.exec()
                    con.close()
                    return
                sql = f"""
                    INSERT INTO books(name, id_author, id_genre)
                    VALUES('{self.lineEdit.text()}', {authorId[0]},
                            {genreId[0]});"""
                result = cur.execute(sql)
                con.commit()
                con.close()
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BiblioMainWindow()
    ex.show()
    sys.exit(app.exec_())
