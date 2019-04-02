import numpy as np
import time
import pyautogui
import os
from Frame import Frame
import random
import copy


def cls():
    """
    Commented out - bootleg "clear console" for Pycharm,
    use while writing, and switch to "os.system..." line when
    packing into .exe

    for getting coordinates:
    time.sleep(2)
    print(pyautogui.position())

    launch program, and move cursor to the simulated console window,
    after 2s you'll get coordinates to put as pyautogui.click() arguments
    :return:
    """

    # time.sleep(0.1)
    pyautogui.click(x=778, y=832)
    pyautogui.hotkey('ctrl', 'l')

    # os.system('cls' if os.name == 'nt' else 'clear')


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

    if frame is None:
        frame = Frame(1, np.zeros(8))          # failsafe if frame is not given

    rand = random.randint(1, 100)

    if state:                                               # if previous frame was sent correctly
        if rand in range(1, probability + 1):                      # if rand is in range of probability
            rand = random.randrange(0, frame.__len__())     # then it rands again to choose which bit to modify

            if frame.packet[rand] == 1:                     # and then changes this bit's value
                frame.packet[rand] = 0
            else:
                frame.packet[rand] = 1
            state = False                       # changing the state after error; False -> error occured
                                                # when sending the previous frame

    elif not state:                             # if previous frame was sent with error
        if rand in range(100 - probability):                      # if rand is in range of new probability
            rand = random.randrange(0, frame.__len__())     # then it rands again to choose which bit to modify

            if frame.packet[rand] == 1:                     # and then changes this bit's value
                frame.packet[rand] = 0
            else:
                frame.packet[rand] = 1

        else:
            state = True                        # changing the state after no error; True -> successful transmission
                                                # when sending the prefious frame
    return state, frame                         # returns frame, and state after transmission


def stop_and_wait(probability, img_in, img_out, resends_possible=None):
    """
    Stop an Wait - frames are "send" to the receiver through function distorting them by
    BSC, or Gilbert's model, after frame is received, check is performed (parity bit)
    to see if frame was distorted, if it was, frame is resend. number of possible resends
    for one frame determined param.

    :param resends_possible:
    :param probability:
    :param img_in:
    :param img_out:
    :return:
    """

    tframes = 0                             # number of transferred frames
    errors = 0                              # number of errors during transmission
    dframes = 0                             # number of uncorrected errors

    state = True                            # 'state' saves if frame became distorted or not (Gilbert's model)

    if resends_possible is None:            # failsafe if timeout is not given
        resends_possible = -1

    resends_left = copy.deepcopy(resends_possible)      # initialize counter for left resends

    height, width, depth = img_in.shape                 # setting variables based on sizes of each axis in array

    error_model = input("1. Binary Symetric Channel Model\n"    # choosing error model
                        "2. Gilbert's Model\n")

    if error_model == '1':                  # ------------------------------------------------
        model = 'Binary symetric chanel'    #
    else:                                   #
        model = "Gilbert's"                 #
                                            # formating for print below and process statistics
    if resends_possible == -1:              #
        resendsstr = 'unlimited'            #
    else:                                   #
        resendsstr = resends_possible       # ------------------------------------------------

    cls()

    print('Transmission using Stop and Wait protocol\n'     # print with process info
          '{err_model} error model\n'                       # while process is running
          'error probability: {p}%\n'
          'possible resends: {r}'.format(err_model=model, p=probability, r=resendsstr))
    print('Processing...')

    proccess_time = time.clock()            # getting current time

    for h in range(height):                 # iterating by height
        for w in range(width):              # width
            for d in range(0, depth, 8):    # and depth, step=8 to create three 1-byte packets from color sequence

                frame = Frame(None, np.array(img_in[h, w, d:d + 8]))    # constructing a frame from 8 bits
                frame.set_ctrlbit()                                     # setting its control bit

                while True:                             # Stop and Wait loop

                    if error_model == '1':
                        # Copy of the frame is run through BSC function and saved as sent packet
                        sent_packet = binary_symmetric_channel(probability, copy.deepcopy(frame))
                    elif error_model == '2':
                        # Copy of the frame is run through gilbert's model function and saved as sent packet
                        state, sent_packet = gilberts_model(probability, copy.deepcopy(frame), state)
                    else:
                        break                               # placeholder

                    if sent_packet.checksum():                       # if bits are in agreement with parity bit they're
                        img_out[h, w, d:d + 8] = sent_packet.packet  # saved to a receiver
                        break
                    else:
                        errors += 1                                     # errors counter++

                        if resends_left > 0:                            # if not, frame is resent if there are possible
                            resends_left -= 1                           # resends left and no. of resends is decreased.
                        elif resends_left == 0:                         # If there are no more resends left,
                            dframes += 1                                # distorted frames counter++
                            img_out[h, w, d:d + 8] = np.zeros(8)        # errorframe is saved to the image;
                            resends_left = resends_possible             # resends are re-set; loop breaks,
                            break                                       # and next frame is sent

                        continue
                tframes += 1                                            # transfered frames counter++

    print("Transmission Complete")

    proccess_time = time.clock() - proccess_time                        # getting process time
    print(f"time: {round(proccess_time, 2)} seconds")

    # returning image, and process statistics
    return resends_possible, 'Stop and Wait', model, proccess_time, tframes, errors, dframes, img_out
