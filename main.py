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

    """
    Unpacking array in axis2 (depth; 3 values 0-255, each for one of RGB color channels) into bits.
    from shape (400,248,3) to (400,248,24) - 24bit long coding of all colours (lumped together in one sequence),
    And creating an empty canvas for receiving packets
    """

    img_in = np.unpackbits(img_in, axis=2)

    img_out = copy.deepcopy(img_in) * 0   # (Copy of input img) * 0 => empty pic with the same parameters as input img

    """
    SAW - frames are "send" to the receiver through function distorting them by
    BSC model, after frame is received, check is performed (parity bit)
    to see if frame was distorted,
    if it was, frame is resend, until it arrives properly
    """

    height, width, depth = img_in.shape

    for h in range(height):                     # iterating by height
        for w in range(width):                  # width
            for d in range(0, depth, 8):        # and depth, step=8 to create three 1-byte packets from color sequence

                frame = Frame(None, np.array(img_in[h, w, d:d+8]))      # constructing a frame from 8 bits
                frame.set_ctrlbit()                                     # setting its control bit

                while True:                                             # Stop and Wait loop

                    # Copy of the frame is run through BSC function and saved as sent packet
                    sent_packet = Functions.binary_symmetric_channel(probability, copy.deepcopy(frame))

                    if sent_packet.checksum():                      # if bits are in agreement with parity bit they're
                        img_out[h, w, d:d+8] = sent_packet.packet   # saved to a receiver, if not, frame is "re-sent"
                        break
                    else:
                        continue

    """
    Packing the array in axis2 back from bits, to create 3 color values for each pixel (0-255)
    """
    img_out = np.packbits(img_out, axis=2)

    """
    Writing changed image to file
    """
    imageio.imwrite('assets/output/cat.jpg', img_out)


if __name__ == '__main__':
    main()
