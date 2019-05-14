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

    probability = int(probability*100)

    if frame is None:
        frame = Frame(1, np.zeros(8))          # failsafe if frame is not given

    for index in range(frame.__len__()):
        rand = random.randint(1, 10000)
        if rand in range(1, probability + 1):                      # if rand is in range of probability

            if frame.packet[index] == 1:                     # and then changes this bit's value
                frame.packet[index] = 0
            else:
                frame.packet[index] = 1

    return frame
