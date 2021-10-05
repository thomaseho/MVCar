import csv

import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar


def qr_camera():
    cap = cv2.VideoCapture(0)
    read_code = True
    collected_data = []

    while True:
        _, frame = cap.read()

        if read_code:
            decodeQR = pyzbar.decode(frame)
            if decodeQR: # Stop if it finds a QR code
                read_code = False   # Read QR code only once
                for obj in decodeQR:
                    print("Data", obj.data) # Print whatever QR code it found
                    collected_data.append(obj.data)

        cv2.imshow("Cam", frame)
        key = cv2.waitKey(1)
        if key == 27:
            return collected_data
        if key == ord("k"): # While driving it should not read codes.
            read_code = False

        if key == ord("s"): # If stopping, read QR code
            read_code = True


def clean_data(data):

    c_data = []
    f_data = []

    for i in range(len(data)):
        if data[i] in c_data:
            for j in range(len(c_data) - 1):
                if data[i] == c_data[j]:
                    c_data[j + 1] += 1
        else:
            c_data.append(data[i])
            c_data.append(1)
    for i in range(0, len(c_data) - 1, 2):
        a = [c_data[i], c_data[i + 1]]
        f_data.append(a)

    return f_data


def write_data(data):

    with open('database.csv', 'w') as database:
        fieldnames = ['id', 'amount']
        writer = csv.DictWriter(database, fieldnames=fieldnames)

        writer.writeheader()

        for row in data:
            writer.writerow({'id': row[0], 'amount': row[1]})


def notify_low_amount(item, amount):
    # Future notification by email or something
    pass


def main():
    inventory_count = qr_camera()
    result = clean_data(inventory_count)
    write_data(result)


if __name__ == '__main__':
    main()
