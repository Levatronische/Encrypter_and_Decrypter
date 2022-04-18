from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class ParamsWidget(QWidget):
    def __init__(self, ui_file):
        super(ParamsWidget, self).__init__()
        uic.loadUi(ui_file, self)


class CryptAlg:
    def __init__(self, name, ui_file, parent_widget, index):
        self.name = name
        self.params_widget = ParamsWidget(ui_file)
        parent_widget.addWidget(self.params_widget, index)
        self.params_widget.setHidden(True)

    def get_name(self):
        return self.name

    def show_hide_params(self, b_hidden):
        self.params_widget.setHidden(b_hidden)


class Caesar(CryptAlg):
    def __init__(self, parent_widget):
        super().__init__("Шифр Цезаря", "Caesar.ui", parent_widget, 0)
        self.alphabet = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.shift = 3
        self.params_widget.lineEditAlphabet.setText(self.alphabet.decode("UTF8"))
        self.params_widget.spinBoxShift.setValue(self.shift)

    def caesar_take_index(self, sim, shift):
        len_alphabet = len(self.alphabet)
        if abs(shift) > len_alphabet:
            shift = shift % len_alphabet
        index = self.alphabet.index(sim) + shift
        if index > len_alphabet - 1:
            index -= len_alphabet
        elif index < 0:
            index += len_alphabet
        return index

    def encode(self, buff, buff_size, shift):
        for i in range(buff_size):
            if buff[i] in self.alphabet:
                buff[i] = self.alphabet[self.caesar_take_index(buff[i], shift)]
        return

    def decrypt(self, buff, buff_size):
        return self.encode(buff, buff_size, -self.shift)

    def encrypt(self, buff, buff_size):
        return self.encode(buff, buff_size, self.shift)

    def __str__(self):
        return f"Alphabet: {self.alphabet}\nShift: {self.shift}"

    def set_alphabet(self, alphabet):
        self.alphabet = alphabet

    def set_shift(self, shift):
        self.shift = shift

    def return_alphabet(self):
        return self.alphabet

    def return_shift(self):
        return self.shift

    def set_params(self):
        self.alphabet = bytearray(self.params_widget.lineEditAlphabet.text(), "utf8")
        self.shift = int(self.params_widget.spinBoxShift.value())


class Xor(CryptAlg):
    def __init__(self, parent_widget):
        super().__init__("Шифр XOR", "Xor.ui", parent_widget, 1)
        self.key = 3
        self.params_widget.lineEditPassword.setText(str(self.key))

    def encrypt(self, buff, buff_size):
        try:
            for i in range(buff_size):
                buff[i] = buff[i] ^ self.key
        except BaseException as err:
            print(err)
        return

    def decrypt(self, buff, buff_size):
        self.encrypt(buff, buff_size)

    def return_key(self):
        return self.key

    def set_params(self):
        self.key = self.params_widget.lineEditPassword.text()


class Transposition(CryptAlg):
    def __init__(self, parent_widget):
        super().__init__("Шифр Транспонирования", "Transposition.ui", parent_widget, 2)
        self.len_m = 3
        self.params_widget.spinBoxLenM.setValue(self.len_m)

    def set_params(self):
        self.len_m = int(self.params_widget.spinBoxLenM.value())

    def encrypt(self, buff, buff_size):
        list_of_bytes = []
        buff_list = []

        for i in range(buff_size):
            if len(buff_list) != self.len_m:
                buff_list.append(buff[i])
            else:
                list_of_bytes.append(buff_list.copy())
                buff_list = [buff[i]]
        if buff_list:
            list_of_bytes.append(buff_list.copy())
        t = 0
        for i in range(self.len_m):
            for j in list_of_bytes:
                if t != buff_size:
                    if len(j) - 1 >= i:
                        buff[t] = j[i]
                        t += 1
                else:
                    break
        return

    def decrypt(self, buff, buff_size):
        buff_list = buff.copy()
        raw = buff_size // self.len_m
        n_last = buff_size - self.len_m * raw
        i = 0
        col = 0
        while i < buff_size:
            if n_last == 0:
                raw_range = raw
            else:
                raw_range = raw + 1
                n_last -= 1
            for j in range(raw_range):
                index = col + j * self.len_m
                buff[index] = buff_list[i]
                i += 1
            col += 1
        return buff
