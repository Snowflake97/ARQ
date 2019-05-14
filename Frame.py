import numpy as np


class Frame:
    """
    Frame contains packet of bits e.g. [0. 1. 1. 1.]
    and control (parity) bit indicating if the "1" bit no. is even
    """

    def __init__(self, packet=np.array([]), h=0, w=0, d=0, resends=0, polynomial_bitstring='1011'):
        self.packet = packet
        self.control_bit = self.set_ctrlbit()
        self.h = h
        self.w = w
        self.d = d
        self.resends = resends
        self.polynomial_bitstring = polynomial_bitstring        # polynomial used to devision in crc
        self.reminder = self.crc_remainder()                    # reminder sets by function crc.reminder()

    def checksum(self):
        """
        checks if the number of "1" bits in packet is even/odd,
        and if it agrees with control bit
        (ctrl_bit=1 for even number of "1" bits)
        :return:
        """

        if (sum(self.packet) % 2 == 0) and (self.control_bit == 1) or\
                (sum(self.packet) % 2 == 1) and (self.control_bit == 0):
            return True
        else:
            return False

    def set_ctrlbit(self):
        """
        sets ctrl_bit based on the contents of a packet
        :return:
        """

        if sum(self.packet) % 2 == 0:
            return 1
        else:
            return 0

    def __len__(self):
        return self.packet.size

    def __str__(self):
        return f'{self.packet} ctrl bit = {self.control_bit}'

    def change_packet_to_string(self):
        """
        changing array to bitstring to crc operations
        :return:
        """
        mystring = ''
        for element in self.packet:
            mystring += str(element)
        return mystring

    def crc_remainder(self, initial_filler='0'):
        """
        Calculates the CRC remainder of a string of bits using a chosen polynomial.
        initial_filler should be '1' or '0'.

        :param initial_filler:
        :return:
        """

        input_bitstring = self.change_packet_to_string()
        bitstring = self.polynomial_bitstring
        bitstring = bitstring.lstrip('0')
        len_input = len(input_bitstring)
        initial_padding = initial_filler * (len(bitstring) - 1)
        input_padded_array = list(input_bitstring + initial_padding)
        while '1' in input_padded_array[:len_input]:
            cur_shift = input_padded_array.index('1')
            for i in range(len(bitstring)):
                input_padded_array[cur_shift + i] = str(
                    int(bitstring[i] != input_padded_array[cur_shift + i]))
        return ''.join(input_padded_array)[len_input:]

    def crc_check(self, check_value):
        """
        Calculates the CRC check of a string of bits using a chosen polynomial.

        :param check_value:
        :return:
        """

        input_bitstring = self.change_packet_to_string()
        bitstring = self.polynomial_bitstring
        bitstring = bitstring.lstrip('0')
        len_input = len(input_bitstring)
        initial_padding = check_value
        input_padded_array = list(input_bitstring + initial_padding)
        while '1' in input_padded_array[:len_input]:
            cur_shift = input_padded_array.index('1')
            for i in range(len(bitstring)):
                input_padded_array[cur_shift + i] = str(
                    int(bitstring[i] != input_padded_array[cur_shift + i]))
        return '1' not in ''.join(input_padded_array)[len_input:]
