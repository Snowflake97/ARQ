import random
from Frame import Frame
import numpy as np

def binary_symmetric_channel(probability, frame=None):
    """
    Takes a frame and distorts it based on probabilty;
    every frame has a given (by param) chance of being
    distorted.

    :param probability:
    :param frame:
    :return:
    """

    if frame is None:
        frame = Frame(1, np.zeros(8))          # failsafe if frame is not given

    rand = random.randint(1, 100)

    if rand in range(1, probability + 1):                      # if rand is in range of probability
        rand = random.randrange(0, frame.__len__())            # then it rands again to choose which bit to modify

        if frame.packet[rand] == 1:                     # and then changes this bit's value
            frame.packet[rand] = 0
        else:
            frame.packet[rand] = 1

    return frame