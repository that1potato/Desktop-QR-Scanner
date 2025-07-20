from qr_scanner import QRScanner
from PIL import Image

import os
import cv2
import numpy as np


def screenshot_test(qr_scanner):
    screenshot = qr_scanner.take_screenshot()
    folder_path = 'test/temp'
    file_name = 'screenshot.png'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    full_path = os.path.join(folder_path, file_name)
    screenshot.save(full_path)
    
def qrscan_test(qr_scanner):
    qr_path = 'test/test_qr.png'
    test_qr = Image.open(qr_path)
    frame = np.array(test_qr)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    tuple = qr_scanner.detect_decode_multi(frame)
    print(tuple)


def main():
    scanner = QRScanner()
    screenshot_test(scanner)
    qrscan_test(scanner)

if __name__=="__main__":
    main()
