from qr_scanner import QRScanner
import os


def screenshot_test(qr_scanner):
    screenshot = qr_scanner.take_screenshot()
    folder_path = 'test/temp'
    file_name = 'screenshot.png'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    full_path = os.path.join(folder_path, file_name)
    screenshot.save(full_path)
    
def qrscan_test(qr_scanner):
    pass


def main():
    scanner = QRScanner()
    screenshot_test(scanner)
    qrscan_test(scanner)

if __name__=="__main__":
    main()
