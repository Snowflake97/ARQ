import imageio
from Frame import Frame
import Functions
import numpy as np
import copy


def main():

    """
    Main
    :return:
    """

    probability = 0.1               # probability of error; from 0.00 to 1.00

    """
    Read jpg image from a file, into a nympy array
    """
    img_in = imageio.imread('assets/input/cat.jpg')
    # print(img.dtype, img.shape)     # prints 'uint8 (400, 248, 3)'

    """
    Convert to a bitmap,
    black pixel is 0, white 255
    divide by 255 to get matrix of 1's and 0's
    """
    img_bit = (Functions.convert_to_bitmap(img_in)) / 255

    img_out = np.zeros(img_bit.shape)   # Creating white picture - canvas for receiving packets

    """
    SAW - frames are "send" to the receiver through function distorting them by
    BSC model, after frame is received, check is performed (parity bit)
    to see if frame was distorted,
    if it was, frame is resend, until it arrives properly
    """

    height, width = img_bit.shape

    for h in range(height):                                     # iterating by height
        for w in range(0, width, 4):                            # and by width

            frame = Frame(None, np.array(img_bit[h, w:w+4]))    # constructing a frame from 4 bits
            frame.set_ctrlbit()                                 # setting its control bit

            while True:                                         # Stop and Wait loop

                # Copy of the frame is run through BSC function and saved as sent packet
                sent_packet = Functions.binary_symmetric_channel(probability, copy.deepcopy(frame))

                if sent_packet.checksum():                  # if bits are in agreement with parity bit they're saved
                    img_out[h, w:w+4] = sent_packet.packet  # to a receiver, if not, frame is "re-sent"
                    break
                else:
                    continue

    # converting matrix back to one made of 255's and 0's and saving as 'uint8'
    img_out = (img_out * 255).astype(np.uint8)

    """
    Writing changed image to file
    """
    imageio.imwrite('assets/output/cat_bitmap.jpg', img_out)


if __name__ == '__main__':
    main()
