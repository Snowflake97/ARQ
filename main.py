import imageio
import Functions
import numpy as np
import copy
from PIL import Image
import datetime


def main():
    """
    Main
    :return:
    """

    """
    Setting probability of error during transmission
    """
    probability = int(input('Enter error probability in % (0 - 100): '))    # probability of error; from 0 to 100 %

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

    # returnes processed image, and process statistics
    resends, protocol, model, process_time, tframes, errors, dframes, img_out = \
        Functions.selective_repeat(probability, img_in, img_out, resends_possible=resends)

    """
    Packing the array in axis2 back from bits, to create 3 color values for each pixel (0-255)
    """
    img_out = np.packbits(img_out, axis=2)

    """
    Writing changed image to file
    """
    imageio.imwrite('assets/output/image.jpg', img_out)

    """
    Writing process log, and showing image
    """
    logtime = datetime.datetime.today()     # getting current time and date

    if resends == -1:
        resends = 'unlimited'               # so the log says "unlimited" instead of "-1"

    with open(f'logs/{logtime.strftime("%Y.%m.%d %H%M%S")}.txt', mode='w') as file:     # writing log to file
        file.write(f'Image transfer {logtime.strftime("%Y/%m/%d %H:%M:%S")}\n'          # strftime() - formating
                   f'Error probability - {probability}%\n'
                   f'Number of possible resends - {resends}\n'
                   f'{protocol} protocol\n'
                   f'{model} error model\n'
                   f'send frames - {tframes}\n'
                   f'correctly transferred frames - {tframes-dframes}\n'
                   f'error occurences - {errors}\n'
                   f'corrected errors - {errors-dframes}\n'
                   f'uncorrected errors - {dframes}\n'
                   f'process time - {round(process_time, 2)}')

    Image.Image.show(Image.open('assets/output/image.jpg'))         # showing image


if __name__ == '__main__':
    main()
