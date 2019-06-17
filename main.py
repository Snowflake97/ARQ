import random
import imageio
# import Functions
import numpy as np
import copy
from PIL import Image
import datetime
from selective_repeat import selective_repeat
from stop_and_wait import stop_and_wait
from go_back_n import go_back_n


random.seed(5000)


def main():
    """
    Main
    :return:
    """

    """
    variables to count errors,error corrections, and uncorrected errors;
    dictionaries to choose error model, protocol, and check type
    """

    tframes = 0
    errors = 0
    dframes = 0
    cframes = 0
    error_models_dict = {'1': 'Binary Symmetric Channel', '2': "Gilbert's"}
    protocols_dict = {'1': 'Stop and Wait', '2': 'Selective Repeat', '3': 'Go Back n'}
    checks_dict = {'1': 'Parity bit', '2': 'Crc32'}

    packet_size = 1
    process_time = 0

    """
    Setting probability of error during transmission
    """
    probability = float(input('Enter error probability in % (0.00 - 100.00): '))

    """
    Read jpg image from a file, into a nympy array
    """
    img_in = imageio.imread('assets/input/image.jpg')

    """
    Unpacking array in axis2 (3rd dimension - depth; 3 values 0-255, each for one of RGB color channels) into bits.
    from shape (___,___,3) to (___,___,24) - 24bit long coding of all colours (lumped together in one sequence, 
    8 bits per one color channel), And creating an empty canvas for receiving packets
    """
    img_in = np.unpackbits(img_in, axis=2)

    img_out = copy.deepcopy(img_in) * 0   # (Copy of input img) * 0 => empty pic with the same parameters as input img

    """
    Stop and Wait Protocol - sending frames one by one, resending them if one arrives distorted.
    
    resends value - limit of resend tries, after which a preset errorframe [0,0,0,0,0,0,0,0] is saved to reciever
    
    e.g. 
    resends = 5 => after 5th failed send try, errorframe is saved, and function moves to the next frame
    resends = 0 => no error correction, every frame is saved no matter if correct or not
    resends = '' = -1 => 100% error correction, frame is being resent, untill correct transmission
    """
    resends = input('Enter number of possible resends (for unlimited press [Enter]): ')   # enter natural number
    if resends == '':
        resends = -1
    else:
        resends = int(resends)

    """
    Choosing protocol, error model, and check type
    """

    print('Choose protocol')
    protocol = protocols_dict[input('1. Stop and Wait\n'
                                    '2. Selective Repeat\n'
                                    '3. Go Back n\n')]

    print('Choose error model')
    model = error_models_dict[input('1. Binary Symetric Channel\n'
                                    "2. Gilbert's model\n")]

    print('Choose check type')
    check = checks_dict[input('1. Parity bit\n'
                              '2. Crc32\n')]

    # returns processed image, and process statistics
    if protocol == 'Stop and Wait':
        packet_size, resends, process_time, tframes, errors, dframes, img_out = \
            stop_and_wait(probability, img_in, img_out,
                          resends_possible=resends, check_type=check, error_model=model)

    elif protocol == 'Selective Repeat':
        packet_size, resends, process_time, tframes, errors, dframes, img_out = \
            selective_repeat(probability, img_in, img_out,
                             resends_possible=resends, check_type=check, error_model=model)

    elif protocol == 'Go Back n':
        packet_size, resends, process_time, tframes, errors, dframes, img_out = \
            go_back_n(probability, img_in, img_out,
                      resends_possible=resends, check_type=check, error_model=model)
    else:
        quit(0)

    height, width, depth = img_in.shape
    for h in range(height):  # iterating by height
        for w in range(width):  # width
            for d in range(0, depth, 8):  # and depth, step=8 to create three 1-byte packets from color sequence
                x = np.array(img_in[h, w, d:d+8])
                y = np.array(img_out[h, w, d:d+8])
                if not np.array_equal(x, y):
                    cframes += 1
                tframes += 1

    print(f"time: {round(process_time, 2)} seconds")

    """
    Packing the array in axis2 back from bits, to create 3 color values for each pixel (0-255)
    """
    img_out = np.packbits(img_out, axis=2)

    """
    Writing changed image to file
    """
    file_name = datetime.datetime.today()  # getting current time and date
    imageio.imwrite(f'assets/output/{file_name.strftime("%Y.%m.%d %H%M%S")}.jpg', img_out)

    """
    Writing process log, and showing image
    """

    if resends == -1:
        resends = 'unlimited'               # so the log says "unlimited" instead of "-1"

    with open(f'logs/{file_name.strftime("%Y.%m.%d %H%M%S")}.txt', mode='w') as file:     # writing log to file
        file.write(f'Image transfer {file_name.strftime("%Y/%m/%d %H:%M:%S")}\n'          # strftime() - formating
                   f'Error probability - {probability}%\n'
                   f'Number of possible resends - {resends}\n'
                   f'{protocol} protocol\n')

        if packet_size != 1:
            file.write(f'sent sequences of {packet_size} frames\n')

        file.write(f'{model} error model\n'
                   f'{check} check type\n'
                   f'send frames - {tframes}\n'
                   f'correctly transferred frames - {tframes-cframes}\n'
                   f'incorrectly transferred frames - {cframes}\n'
                   f'detected errors(including repeated transmissions) - {errors}\n'
                   f'detected and corrected errors(including repeated transmissions) - {errors-dframes}\n'
                   f'detected and uncorrected errors - {dframes}\n'
                   f'undetected errors - {cframes-dframes}\n'
                   f'process time - {round(process_time, 2)}\n')

    Image.Image.show(Image.open(f'assets/output/{file_name.strftime("%Y.%m.%d %H%M%S")}.jpg'))         # showing image


if __name__ == '__main__':
    main()
