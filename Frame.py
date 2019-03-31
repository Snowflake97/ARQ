import numpy as np


class Frame:
    """
    Frame contains packet of bits e.g. [0. 1. 1. 1.]
    and control (parity) bit indicating if the "1" bit no. is even
    """

    def __init__(self, control_bit=None, packet=np.array([])):
        self.packet = packet
        self.control_bit = control_bit

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
            self.control_bit = 1
        else:
            self.control_bit = 0

    def __len__(self):
        return self.packet.size

    def __str__(self):
        return f'{self.packet} ctrl bit = {self.control_bit}'
