from PIL import Image

import cv2 
import pyautogui
import numpy as np


class QRScanner:
    def __init__(self) -> None:
        self.QRDetector = cv2.QRCodeDetector()
        self.screenshot_frame = None

    def take_screenshot(self) -> Image:    
        '''
        takes a full-screen screenshot for the qr detector
        overwrites self.screenshot_frame
        returns the screenshot from pyautogui
        '''    
        screenshot = pyautogui.screenshot()
        
        # convert from RGB to BGR for cv2
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self.screenshot_frame = frame
        
        return screenshot

    def detect_decode_multi(self, image) -> tuple:
        '''
        detects and decodes multiple qr codes from the image
        returns a tuple (ok, data, points, straight_qrcode)
        '''
        results = self.QRDetector.detectAndDecodeMulti(image)
        return results

