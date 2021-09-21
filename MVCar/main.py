import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar


def qr_camera():
    cap = cv2.VideoCapture(0)
    read_code = True

    while True:
        _, frame = cap.read()

        if read_code:
            decodeQR = pyzbar.decode(frame)
            if decodeQR: # Stop if it finds a QR code
                read_code = False   # Read QR code only once
                for obj in decodeQR:
                    print("Data", obj.data) # Print whatever QR code it found

        cv2.imshow("Cam", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == ord("k"): # While driving it should not read codes.
            read_code = False

        if key == ord("s"): # If stopping, read QR code
            read_code = True


def main():
    qr_camera()


if __name__ == '__main__':
    main()
