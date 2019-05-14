import numpy as np
from Frame import Frame
import random


def gilberts_model(probability, frame=None, state=True):
    """
    Takes a frame and distorts it based on probabilty(param);
    every frame has a chance to become distorted, and to arrive correctly
    P(error) + P(no error) = 100%
    After error occurence, probabilities are swapped;
    and swapped again after correct transmission.
    errors and correct transmissions are grouped together.

    e.g.
    P(error) = 10%
    P(no error) = 90%

    *error occures*

    P(error) = 90%
    P(no error) = 10%

    *correct transmission*

    P(error) = 10%
    P(no error) = 90%


    :param probability:
    :param frame:
    :param state:
    :return:
    """

    probability = int(probability*100)

    if frame is None:
        frame = Frame(1, np.zeros(8))          # failsafe if frame is not given

    for index in range(frame.__len__()):
        rand = random.randint(1, 10000)

        if state:                                               # if previous frame was sent correctly
            if rand in range(1, probability + 1):                      # if rand is in range of probability

                if frame.packet[index] == 1:                     # and then changes this bit's value
                    frame.packet[index] = 0
                else:
                    frame.packet[index] = 1
                state = False                       # changing the state after error; False -> error occured
                                                    # when sending the previous frame

        elif not state:                             # if previous frame was sent with error
            if rand in range(10000 - probability):                      # if rand is in range of new probability

                if frame.packet[index] == 1:                     # and then changes this bit's value
                    frame.packet[index] = 0
                else:
                    frame.packet[index] = 1

            else:
                state = True                        # changing the state after no error; True -> successful transmission
                                                    # when sending the prefious frame
    return state, frame                             # returns frame, and state after transmission
