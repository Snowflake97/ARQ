import numpy as np
import time
from Frame import Frame
import copy
from Functions import cls
from bsc import binary_symmetric_channel
from gilberts import gilberts_model


def go_back_n(probability, img_in, img_out, resends_possible=None, check_type='', error_model=''):
    """
    Go back and - frames are "send" in sequances to the receiver through function distorting them by
    BSC, or Gilbert's model, after frame is received, check is performed (parity bit)
    to see if frame was distorted, if it was, frame is resend but another frames are send in the same time.
    When first frame in sequence is distorted, the whole packet is resend. If first frame is out of possible resends
    all frames in packet are out of ressends and whole packet is filled with zeros


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

    print('Transmission using Go Back n protocol\n'     # print with process info
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

                if error_model == 'Binary Symmetric Channel':
                    sent_packet = binary_symmetric_channel(probability, copy.deepcopy(frame))
                elif error_model == "Gilbert's":
                    state, sent_packet = gilberts_model(probability, copy.deepcopy(frame), state)
                else:
                    sent_packet = copy.deepcopy(frame)

                sent_packets.append(sent_packet)

                # filling list as prepering to sending, check if frame was already send
                while (len(frame_list) == packet_size) and ('erase' not in frame_list):
                    if check_type == 'Parity bit':
                        check_result = sent_packets[0].checksum()
                    elif check_type == 'Crc32':
                        check_result = sent_packets[0].crc_check(frame_list[0].reminder)
                    else:
                        check_result = True

                    if check_result is False:

                        if frame_list[0].resends == 0:      # check for possible resend
                            for position, _ in enumerate(sent_packets):     # if there arent fill packet with zeros
                                error_packet = np.array([0, 0, 0, 0, 0, 0, 0, 0])

                                for bit in range(frame_list[position].__len__()):
                                    if frame_list[position].packet[bit] == 0:
                                        error_packet[bit] = 1
                                    elif frame_list[position].packet[bit] == 1:
                                        error_packet[bit] = 0

                                frame_h = frame_list[position].h
                                frame_w = frame_list[position].w
                                frame_d = frame_list[position].d
                                img_out[frame_h, frame_w, frame_d:frame_d + 8] = error_packet
                                sent_packets[position] = 'erase'       # prepare for delate
                                frame_list[position] = 'erase'
                                dframes += 1                    # increase number of disorted frames
                                errors += 1
                        else:                                  # resending whole packet
                            errors += 1
                            for i in range(packet_size):
                                frame_list[i].resends -= 1
                                if error_model == 'Binary Symmetric Channel':
                                    sent_packets[i] = binary_symmetric_channel(probability,
                                                                               copy.deepcopy(frame_list[i]))
                                elif error_model == "Gilbert's":
                                    state, sent_packets[i] = gilberts_model(probability,
                                                                            copy.deepcopy(frame_list[i]), state)

                    else:                           # for good frame, send it and erase
                        # send packet in proper position
                        frame_h = frame_list[0].h
                        frame_w = frame_list[0].w
                        frame_d = frame_list[0].d
                        img_out[frame_h, frame_w, frame_d:frame_d + 8] = sent_packets[0].packet
                        sent_packets[0] = 'erase'  # remove from list if packet was sent
                        frame_list[0] = 'erase'

    proccess_time = time.clock() - proccess_time                        # getting process time

    return packet_size, resends_possible, proccess_time, tframes, errors, dframes, img_out
