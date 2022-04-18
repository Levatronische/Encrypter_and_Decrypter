import datetime
import sqlite3
import ctypes
import platform
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from crypt_alg import Xor, Caesar, Transposition


def get_os_error(os_error):
    if platform.system() == "Windows":
        if os_error.winerror is not None:
            mess = ctypes.FormatError(os_error.winerror)
        else:
            mess = ctypes.FormatError(os_error.errno)
    else:
        mess = os_error.strerror
    return f"[Errno {os_error.errno}] {mess}: '{os_error.filename}'"


class MainWnd(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isRadioButtonEncrypt = False
        self.isRadioButtonDecrypt = False

        self.ui = uic.loadUi('EncrypterAndDecrypter.ui', self)
        self.ui.setWindowIcon(QIcon("LogoENC.png"))

        self.con = sqlite3.connect("SQData.db")
        self.cur = self.con.cursor()

        self.list_enc_alg = [Caesar(self.verticalLayoutForParams),
                             Transposition(self.verticalLayoutForParams),
                             Xor(self.verticalLayoutForParams)]

        self.cb_index = 0

        self.comboBoxCryptType.addItems([i.get_name() for i in self.list_enc_alg])
        self.comboBoxCryptType.currentIndexChanged.connect(self.show_hide_params)

        self.list_enc_alg[self.cb_index].show_hide_params(False)

        self.progressBarCrypt.setValue(0)

        self.radioButtonEncrypt.setChecked(True)
        self.pushButtonStartCrypt.setText("Зашифровать")

        self.radioButtonEncrypt.toggled.connect(self.set_start)

        self.pushButtonInport.clicked.connect(self.select_file_open)
        self.pushButtonExport.clicked.connect(self.select_file_save)

        self.pushButtonStartCrypt.clicked.connect(self.do_crypt)

        self.show()

    def save_db(self, is_encrypt, enc_alg):
        try:
            action = "Decrypt"
            if is_encrypt:
                action = "Encrypt"

            self.cur.execute(f"""INSERT INTO log_table(import_file, export_file, action, time, alg)
               VALUES('{self.lineEditInport.text()}',
                '{self.lineEditExport.text()}',
                 '{action}',
                  '{str(datetime.datetime.now())}',
                    '{str(enc_alg.get_name())}');""")
            self.con.commit()
        except BaseException as err:
            QMessageBox.critical(self, "Ошибка БД", f"{err}")

    def set_start(self):
        if self.radioButtonEncrypt.isChecked():
            self.pushButtonStartCrypt.setText("Зашифровать")
        else:
            self.pushButtonStartCrypt.setText("Расшифровать")

    def show_hide_params(self, index):
        self.list_enc_alg[self.cb_index].show_hide_params(True)
        self.list_enc_alg[index].show_hide_params(False)
        self.cb_index = index

    def select_file_open(self):
        filename, filetype = QFileDialog.getOpenFileName(self,
                                                         "Выбрать файл",
                                                         ".",
                                                         "All Files(*.*)")

        if filename:
            self.lineEditInport.setText(f"{filename}")

    def select_file_save(self):
        filename, filetype = QFileDialog.getSaveFileName(self,
                                                         "Сохранить файл",
                                                         "untitled",
                                                         "enc(*.enc);;\
                                                         All Files(*.*)")
        if filename:
            self.lineEditExport.setText(f"{filename}")

    def do_crypt(self):
        try:
            enc_alg = self.list_enc_alg[self.comboBoxCryptType.currentIndex()]

            enc_alg.set_params()

            self.pushButtonStartCrypt.setDisabled(True)
            buff_size = 5242880

            is_encrypt = self.radioButtonEncrypt.isChecked()

            self.progressBarCrypt.setValue(0)

            file_input = open(self.lineEditInport.text(), mode="rb")
            file_export = open(self.lineEditExport.text(), mode="wb")

            file_input.seek(0, 2)
            file_size = file_input.tell()
            file_input.seek(0)

            if file_size <= buff_size:
                buff_size = file_size
                buff = bytearray(file_input.read(buff_size))
                if is_encrypt:
                    enc_alg.encrypt(buff, buff_size)
                else:
                    enc_alg.decrypt(buff, buff_size)
                file_export.write(buff)
            else:
                n = file_size // buff_size
                for i in range(n):
                    buff = bytearray(file_input.read(buff_size))
                    if is_encrypt:
                        enc_alg.encrypt(buff, buff_size)
                    else:
                        enc_alg.decrypt(buff, buff_size)
                    file_export.write(buff)
                    self.progressBarCrypt.setValue(int((i / n) * 100))
                buff = bytearray(file_input.read(file_size - (n * buff_size)))
                buff_size = file_size - (n * buff_size)
                if is_encrypt:
                    enc_alg.encrypt(buff, buff_size)
                else:
                    enc_alg.decrypt(buff, buff_size)
                file_export.write(buff)
            self.progressBarCrypt.setValue(100)
            file_input.close()
            file_export.close()
            self.save_db(is_encrypt, enc_alg)

        except OSError as err:
            QMessageBox.critical(self, "Ошибка файла", f"{get_os_error(err)}")
        self.pushButtonStartCrypt.setDisabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWnd()
    sys.exit(app.exec_())
