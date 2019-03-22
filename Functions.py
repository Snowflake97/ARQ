import imageio
import numpy as np
import time
import pyautogui
import os
from Frame import Frame
import random


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

    time.sleep(0.1)
    pyautogui.click(x=778, y=832)
    pyautogui.hotkey('ctrl', 'l')

    # os.system('cls' if os.name == 'nt' else 'clear')


def convert_to_bitmap(img):
    """
    takes read image in RGB scale and converts it to
    a black and white bitmap

    :param img:
    :return:
    """

    arr = np.array(img)

    # Split the three channels
    r, g, b = np.split(arr, 3, axis=2)
    r = r.reshape(-1)
    g = r.reshape(-1)
    b = r.reshape(-1)

    # Standard RGB to grayscale
    bitmap = list(map(lambda x: 0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2],
                      zip(r, g, b)))
    bitmap = np.array(bitmap).reshape([arr.shape[0], arr.shape[1]])
    bitmap = np.dot((bitmap > 128).astype(float), 255)

    return bitmap.astype(np.uint8)


def binary_symmetric_channel(probability, frame=None):
    """
    Takes a frame and distorts it based on probabilty;


    :param probability:
    :param frame:
    :return:
    """

    if frame is None:
        frame = Frame(1, np.zeros(4,))          # failsafe if frame is not given

    probability *= 100                          # gives probability in percent and parses it to int
    probability = int(probability)              # e.g. prob = 0.1 => prob = 10

    rand = random.randint(1, 100)

    if rand in range(probability):                      # if rand is in range of probability
        rand = random.randrange(0, frame.__len__())     # then it rands again to choose which bit to modify
        if frame.packet[rand] == 1:                     # and then changes this bit's value
            frame.packet[rand] = 0
        else:
            frame.packet[rand] = 1

    return frame



