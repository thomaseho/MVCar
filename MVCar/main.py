import csv
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
import smtplib, ssl


class QRScanner:

    def __init__(self, customers_inventory_list, database_files, camera, wframe):
        self.inv_items = []
        for inventory_list in customers_inventory_list:
            self.inv_items.append(self.collect_inventory_items(inventory_list))
        self.db = database_files
        self.cam = camera
        self.read_codes = True
        self.read_items = []
        self.c_data = []
        self.file_data = []
        self.inventory_data = []
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

        if self.cam.isOpened():
            window_name = "FindingGeirCam"
            window_handle = cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

            while cv2.getWindowProperty(window_name, 0) >= 0:

                _, frame = self.cam.read()
                newframe = cv2.resize(frame,(1280,720),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                cv2.imshow(window_name, newframe)

                if self.read_codes:
                    read_item = pyzbar.decode(frame)
                    if read_item:
                        self.read_codes = False
                        for item in read_item:
                            print("------------------")
                            print("Read item: ", item.data)
                            print("------------------")
                            self.read_items.append(item.data)
                else:
                    wait_frames -= 1

                if wait_frames <= 0:
                    self.read_codes = True
                    wait_frames = self.wait_frames


                key = cv2.waitKey(1)

                if key == 27:
                    break

    def clean_data(self):
        for inv_items in self.inv_items:
            self.c_data = []
            self.file_data = []
            for i in range(len(self.read_items)):
                if self.read_items[i] in self.c_data:
                    for j in range(len(self.c_data) - 1):
                        if self.read_items[i] == self.c_data[j]:
                            self.c_data[j + 1] += 1

                else:
                    for k in range(len(inv_items)):
                        if f"{self.read_items[i]}" in inv_items[k]:
                            self.c_data.append(self.read_items[i])
                            self.c_data.append(1)

            for i in range(0, len(self.c_data) - 1, 2):
                self.file_data.append([self.c_data[i], self.c_data[i + 1]])

            for item in inv_items:
                if item[0] not in self.file_data:
                    self.file_data.append([item[0], 0])

            self.inventory_data.append(self.file_data)


    def write_data(self):

        i = 0
        for inventory in self.inventory_data:
            with open(f'{self.db[i]}', 'w', newline='') as db:
                fieldnames = ['id', 'amount']
                writer = csv.DictWriter(db, fieldnames=fieldnames)
                writer.writeheader()

                for row in inventory:
                    writer.writerow({'id': row[0], 'amount': row[1]})
            i += 1
            db.close()

    def notify_low_amount(self, low_stock_items):
        # Starting on email, if using Gmail emails and servers,
        port = 587
        password = 'Passord1.'
        #password = input("Email password, then press enter:  ")
        smtp_server = "smtp.gmail.com"
        sender_email = "JetsonBotGroup6@gmail.com"  # Make a email for Jetson Bot, password = Passord1.
        receiver_email = "Group6Stock@gmail.com"  # Make a test email for our "accountant"
        message = f"""\n
            Subject: Stock Order\n
            -----------------------------------------------\n
            There are items in your inventory low in stock\n.
            """
        for item in low_stock_items:
            message += """\n------------------------------------------------------\n"""
            message += f"""{item[0]}: there are {item[1]} currently in stock.\n"""
            message += """------------------------------------------------------\n"""

        print(message)
             # Add.csv file
             # Add Warning low amount
             # Add date


        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    def check_low_stock(self):

        for db in self.db:
            low_stock = []
            with open(f'{db}', 'r') as db_items:
                reader = csv.reader(db_items)

                for row in reader:
                    if row[1] == '0':
                        print(row[0])
                        low_stock.append(row)
                db_items.close()

            if len(low_stock) > 0:
                self.notify_low_amount(low_stock)

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def main():
    customers = ['customer1.csv', 'customer2.csv', 'customer3.csv']
    databases = ['database1.csv', 'database2.csv', 'database3.csv']
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    #scanner = QRScanner(customers, databases, cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER), 30)
    scanner = QRScanner(customers, databases, cap, 90)
    scanner.scan_qr_codes()
    scanner.clean_data()
    scanner.write_data()
    scanner.check_low_stock()



if __name__ == '__main__':
    main()
