import csv
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
import smtplib, ssl


class QRScanner:

    def __init__(self, inventory_items, database_file, camera, wframe):
        self.inv_items = self.collect_inventory_items(inventory_items)
        self.db = database_file
        self.cam = camera
        self.read_codes = True
        self.read_items = []
        self.c_data = []
        self.file_data = []
        self.wait_frames = wframe

    def collect_inventory_items(self, inventory_items):

        current_items = []

        with open(f'{inventory_items}', 'r') as inv_items:

            reader = csv.reader(inv_items)

            for row in reader:
                current_items.append(row)

        inv_items.close()
        print(current_items)
        return current_items

    def scan_qr_codes(self):

        wait_frames = self.wait_frames

        while True:
            _, frame = self.cam.read()

            if self.read_codes:
                read_item = pyzbar.decode(frame)
                if read_item:
                    self.read_codes = False
                    for item in read_item:
                        print("Read item: ", item.data)
                        self.read_items.append(item.data)
            else:
                wait_frames -= 1

            if wait_frames <= 0:
                self.read_codes = True
                wait_frames = self.wait_frames

            cv2.imshow("Cam", frame)
            key = cv2.waitKey(1)
            
            if key == 27:
                break

    def clean_data(self):

        for i in range(len(self.read_items)):
            if self.read_items[i] in self.c_data:
                for j in range(len(self.c_data) - 1):
                    if self.read_items[i] == self.c_data[j]:
                        self.c_data[j + 1] += 1

            else:
                for k in range(len(self.inv_items)):
                    if f"{self.read_items[i]}" in self.inv_items[k]:
                        self.c_data.append(self.read_items[i])
                        self.c_data.append(1)

        for i in range(0, len(self.c_data) - 1, 2):
            self.file_data.append([self.c_data[i], self.c_data[i + 1]])


    def write_data(self):

        with open(f'{self.db}', 'w') as db:
            fieldnames = ['id', 'amount']
            writer = csv.DictWriter(db, fieldnames=fieldnames)
            writer.writeheader()

            for row in self.file_data:
                writer.writerow({'id': row[0], 'amount': row[1]})

        db.close()

    def notify_low_amount(self):
        # Starting on email, if using Gmail emails and servers,
        port = 587
        password = input("Email password, then press enter:  ")
        smtp_server = "smtp.gmail.com"
        sender_email = "JetsonBotGroup6@gmail.com"  # Make a email for Jetson Bot, password = Passord1.
        receiver_email = "Group6Stock@gmail.com"  # Make a test email for our "accountant"
        message = """\
            Subject: Stock Order
            // Add .csv file
            // Add "Warning low amount"
            // Add date
            """

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


def main():

    scanner = QRScanner('data.csv', 'database.csv', cv2.VideoCapture(0), 30)
    scanner.scan_qr_codes()
    scanner.clean_data()
    scanner.write_data()


if __name__ == '__main__':
    main()
