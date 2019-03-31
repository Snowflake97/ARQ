import imageio
import Functions
import numpy as np
import copy


def main():
    """
    Main
    :return:
    """

    """
    Setting probability of error during transmission
    """
    probability = float(input('Enter probability (0.00-1.00): '))          # probability of error; from 0.00 to 1.00

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
    resends = input('Enter number of possible resends (for infinite number press [Enter]): ')   # enter natural number
    if resends == '':
        resends = -1
    else:
        resends = int(resends)

    img_out = Functions.stop_and_wait(probability, img_in, img_out, resends_possible=resends)

    """
    Packing the array in axis2 back from bits, to create 3 color values for each pixel (0-255)
    """
    img_out = np.packbits(img_out, axis=2)

    """
    Writing changed image to file
    """

    imageio.imwrite('assets/output/image.jpg', img_out)


if __name__ == '__main__':
    main()
