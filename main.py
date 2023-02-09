
import sys
sys.path.append("/usr/share/python3-mscl")
import mscl
from libs.data_streamer import DataStreamer

from libs.saver import Saver
from time import time
import threading
from datetime import datetime

import argparse

if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--port', default='/dev/ttyUSB0')
    argparser.add_argument('--hz', default='30')

    args = argparser.parse_args()
    COM_PORT = args.port
    MASTER_RATE = int(args.hz) ## Hz

    d = datetime.now()
    date = f"{d.year}-{d.month:02}-{d.day:02}-{d.hour:02}-{d.minute:02}-{d.second:02}"

    try:
        ## Init classes
        streamer = DataStreamer(COM_PORT, MASTER_RATE)
        saver = Saver(filename=date)

        ## Create subthread loop with shared flag
        class Shared:
            isDone = False
        shared = Shared()
        th_stream = threading.Thread(target=streamer.run, args=(time(), shared))
        th_stream.start()

        ## Wait for interruption
        input(f"Press Enter to Stop and Save")
        shared.isDone = True

        ## Save packets
        packets_list = streamer.get_packets_list()
        saver.run(packets_list)


    except mscl.Error as e:
        print("---Error:", e)

