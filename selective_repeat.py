import numpy as np
import time
from Frame import Frame
import copy
from Functions import cls
from bsc import binary_symmetric_channel
from gilberts import gilberts_model


def selective_repeat(probability, img_in, img_out, resends_possible=None, check_type='', error_model=''):
    """
    Selective Repeat - frames are "send" in sequances to the receiver through function distorting them by
    BSC, or Gilbert's model, after frame is received, check is performed (parity bit)
    to see if frame was distorted, if it was, frame is resend but another frames are send in the same time

    :param probability:
    :param img_in:
    :param img_out:
    :param resends_possible:
    :param check_type:
    :param error_model:
    :return:
    """

    tframes = 0                             # number of transferred frames
    errors = 0                              # number of errors during transmission
    dframes = 0                             # number of uncorrected errors

    state = True                            # 'state' saves if frame became distorted or not (Gilbert's model)

    if resends_possible is None:            # failsafe if possible resends number is not given
        resends_possible = -1

    height, width, depth = img_in.shape                 # setting variables based on sizes of each axis in array

    packet_size = int(input("Enter packet size: "))

    if resends_possible == -1:               # ------------------------------------------------
        resends_str = 'unlimited'            # formating for print below and process statistics
    else:                                    #
        resends_str = resends_possible       # ------------------------------------------------

    cls()

    print('Transmission using Selective Repeat protocol\n'     # print with process info
          '{err_model} error model\n'                       # while process is running
          'error probability: {p}%\n'
          'check type: {c}\n'
          'possible resends: {r}\n'
          'sending sequences of {ps} frames'.format(err_model=error_model, p=probability, r=resends_str,
                                                    ps=packet_size, c=check_type))
    print('Processing...')

    proccess_time = time.clock()            # getting current time

    frame_list = []
    sent_packets = []

    for h in range(height):                 # iterating by height
        for w in range(width):              # width
            for d in range(0, depth, 8):    # and depth, step=8 to create three 1-byte packets from color sequence

                # Cleaning lists - removing packets that were accepted by receiver
                # Filtering out positions which have been replaced by 'erase' marker,
                # leaving only packets that have not yet been accepted by receiver,
                # and making place for next packets to be added
                frame_list = list(filter(lambda element: element != 'erase', frame_list))
                sent_packets = list(filter(lambda element: element != 'erase', sent_packets))

                # constructing a frame from 8 bits
                frame = Frame(np.array(img_in[h, w, d:d + 8]), h, w, d, resends_possible)

                frame_list.append(frame)        # keeping few frames in memory

                if error_model == 'Binary Symmetric Channel':                    sent_packet = binary_symmetric_channel(probability, copy.deepcopy(frame))
                elif error_model == "Gilbert's":
                    state, sent_packet = gilberts_model(probability, copy.deepcopy(frame), state)
                else:
                    sent_packet = Frame(np.zeros(8))

                sent_packets.append(sent_packet)

                while (len(frame_list) == packet_size) and ('erase' not in frame_list):   # sending packets in sequences
                    for i in range(packet_size):                      # for every frame set position

                        frame_h = frame_list[i].h
                        frame_w = frame_list[i].w
                        frame_d = frame_list[i].d

                        if check_type == 'Parity bit':
                            check_result = sent_packets[i].checksum()
                        elif check_type == 'Crc32':
                            check_result = sent_packets[i].crc_check(frame_list[i].reminder)
                        else:
                            check_result = True

                        if check_result is True:
                            # send packet in proper position
                            img_out[frame_h, frame_w, frame_d:frame_d + 8] = sent_packets[i].packet

                            sent_packets[i] = 'erase'           # remove from list if packet was sended
                            frame_list[i] = 'erase'             # makes room for next packets

                        else:
                            errors += 1

                            if frame_list[i].resends == 0:
                                img_out[frame_h, frame_w, frame_d:frame_d + 8] = np.zeros(8)    # send 'error packet'

                                sent_packets[i] = 'erase'           # makes room for next packets
                                frame_list[i] = 'erase'

                                dframes += 1

                            else:
                                frame_list[i].resends -= 1          # decrement possible resends value

                                # send again exactly the same frame
                                if error_model == 'Binary Symmetric Channel':
                                    sent_packets[i] = binary_symmetric_channel(probability,
                                                                               copy.deepcopy(frame_list[i]))
                                elif error_model == "Gilbert's":
                                    state, sent_packets[i] = gilberts_model(probability,
                                                                            copy.deepcopy(frame_list[i]), state)

                tframes += 1

    proccess_time = time.clock() - proccess_time                        # getting process time

    return packet_size, resends_possible, proccess_time, tframes, errors, dframes, img_out
