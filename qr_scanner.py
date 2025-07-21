from PIL import Image

import cv2 
import mss
import numpy as np


class QRScanner:
    def __init__(self) -> None:
        self.QRDetector = cv2.QRCodeDetector()
        self.screenshot_frame = None

    def take_screenshot(self) -> Image:    
        '''
        takes a full-screen screenshot for the qr detector
        overwrites self.screenshot_frame
        returns the screenshot image (PIL.Image)
        '''    
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img_pil = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            
            frame_np = np.array(img_pil)
            frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
            self.screenshot_frame = frame_bgr
            
        return img_pil

    def detect_decode_multi(self, image = None) -> tuple:
        '''
        detects and decodes multiple qr codes in self.screenshot_frame 
            or from the provided image (converted to BGR)
        returns a tuple (ok, data, points, straight_qrcode)
        '''
        if image is not None:
            results = self.QRDetector.detectAndDecodeMulti(image)
        else:
            if self.screenshot_frame is None:
                return
            results = self.QRDetector.detectAndDecodeMulti(self.screenshot_frame)
        
        return results
        

