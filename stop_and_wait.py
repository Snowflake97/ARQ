import numpy as np
import time
from Frame import Frame
import copy
from Functions import cls
from bsc import binary_symmetric_channel
from gilberts import gilberts_model



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

    if resends_possible is None:            # failsafe if possible resends number is not given
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

                    if sent_packet.crc_check(frame.reminder):
                    # if sent_packet.checksum():                       # if bits are in agreement with parity bit they're
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
    return 1, resends_possible, 'Stop and Wait', model, proccess_time, tframes, errors, dframes, img_out