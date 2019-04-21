import numpy as np
import time
from Frame import Frame
import copy
from Functions import cls
from bsc import binary_symmetric_channel
from gilberts import gilberts_model

def go_back_n(probability, img_in, img_out, resends_possible=None):
    """
    Go back and - frames are "send" in sequances to the receiver through function distorting them by
    BSC, or Gilbert's model, after frame is received, check is performed (parity bit)
    to see if frame was distorted, if it was, frame is resend but another frames are send in the same time.
    When first frame in sequence is distorted, the whole packet is resend. If first frame is out of possible resends
    all frames in packet are out of ressends and whole packet is filled with zeros

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

    height, width, depth = img_in.shape                 # setting variables based on sizes of each axis in array

    packet_size = int(input("Enter packet size: "))
    error_model = input("1. Binary Symetric Channel Model\n"    # choosing error model
                        "2. Gilbert's Model\n")

    if error_model == '1':                  # ------------------------------------------------
        model = 'Binary symetric chanel'    #
    else:                                   #
        model = "Gilbert's"                 #
                                            # formating for print below and process statistics
                                            # ------------------------------------------------

    cls()

    print('Transmission using Selective Repeat protocol\n'     # print with process info
          '{err_model} error model\n'                       # while process is running
          'error probability: {p}%\n'
          'possible resends: {r}\n'
          'sending sequences of {ps} frames'.format(err_model=model, p=probability, r=resends_possible, ps=packet_size))
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

                frame = Frame(None, np.array(img_in[h, w, d:d + 8]),h,w,d, resends_possible)    # constructing a frame from 8 bits
                frame.set_ctrlbit()                            # setting its control bit

                frame_list.append(frame)        # keeping few frames in memory

                if error_model == '1':
                    sent_packet = binary_symmetric_channel(probability, copy.deepcopy(frame))
                elif error_model == '2':
                    state, sent_packet = gilberts_model(probability, copy.deepcopy(frame), state)

                sent_packets.append(sent_packet)

                while (len(frame_list) == packet_size) and ('erase' not in frame_list):
                    # filling list as prepering to sending, check if frame was already send
                    if sent_packets[0].crc_check(frame_list[0].reminder) == False:
                        # check if reminder of sent frame match reminder of true/not distoretd frame
                    # if sent_packets[0].checksum() == False:
                        errors += 1
                        if frame_list[0].resends == 0:      # check for possible resend
                            for position, _ in enumerate(sent_packets): # if there arent fill packet with zeros
                                frame_h = frame_list[position].h
                                frame_w = frame_list[position].w
                                frame_d = frame_list[position].d
                                img_out[frame_h, frame_w, frame_d:frame_d + 8] = np.zeros(8)
                                sent_packets[position] = 'erase'       #prepare for delate
                                frame_list[position] = 'erase'
                                dframes += 1                       # increase number of disorted frames
                        else:                                  # resending whole packet
                            for i in range(packet_size):
                                frame_list[i].resends -= 1
                                if error_model == '1':
                                    sent_packets[i] = binary_symmetric_channel(probability, copy.deepcopy(frame_list[i]))
                                elif error_model == '2':
                                    state, sent_packets[i] = gilberts_model(probability, copy.deepcopy(frame_list[i]), state)

                    else:                           # for good frame, send it and erase
                        frame_h = frame_list[0].h
                        frame_w = frame_list[0].w
                        frame_d = frame_list[0].d
                        img_out[frame_h, frame_w, frame_d:frame_d + 8] = sent_packets[0].packet  # send packet in proper position
                        sent_packets[0] = 'erase'  # remove from list if packet was sended
                        frame_list[0] = 'erase'
                        tframes += 1



    proccess_time = time.clock() - proccess_time                        # getting process time
    print(f"time: {round(proccess_time, 2)} seconds")

    return packet_size, resends_possible, 'Selective Repeat', model, proccess_time, tframes, errors, dframes, img_out