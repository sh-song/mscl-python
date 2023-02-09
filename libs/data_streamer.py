
import sys
sys.path.append("/usr/share/python3-mscl")
import mscl
from time import time


class MipNode:
    """
    _mt : _miptype

    """
    def __init__(self, class_mt):

        self.class_mt = class_mt
        self.channels = mscl.MipChannels()
    
    def add(self, channel_mt, rate=100):
        self.channels.append(mscl.MipChannel(channel_mt, mscl.SampleRate.Hertz(rate)))


class DataStreamer:
    def __init__(self, COM_PORT, MASTER_RATE=30):


        connection = mscl.Connection.Serial(COM_PORT, 115200)
        print(f"---Try connection with {COM_PORT} at baudrate {115200}")

        self.node = mscl.InertialNode(connection)
        print(f"---Init InertialNode")

        if not self.node.ping():
            print('---Connection invalid. Rebooting may help.')
            exit(0)
        else:
            print('---Connection valid.')

        
        self.mip_nodes = []

        self._init_nodes(MASTER_RATE)
        self._set_current_config()
        self._start_sampling()

        self.packets_list = []

    def _init_nodes(self, MASTER_RATE):

        ## Init nodes
        ahrs_imu = MipNode(mscl.MipTypes.CLASS_AHRS_IMU)
        est_filter = MipNode(mscl.MipTypes.CLASS_ESTFILTER)

        ## Set channel fields
        ahrs_imu.add(mscl.MipTypes.CH_FIELD_SENSOR_EULER_ANGLES, rate=MASTER_RATE)

        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_GPS_TIMESTAMP, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_LLH_POS, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_LLH_UNCERT, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_NED_VELOCITY, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_NED_UNCERT, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_ORIENT_EULER, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_ATT_UNCERT_EULER, rate=MASTER_RATE)
        est_filter.add(mscl.MipTypes.CH_FIELD_ESTFILTER_FILTER_STATUS, rate=MASTER_RATE)

        ## upload nodes
        self.mip_nodes.append(ahrs_imu)
        self.mip_nodes.append(est_filter)

        print(f"--Init {len(self.mip_nodes)} nodes")

    def _set_current_config(self):

        for i, mn in enumerate(self.mip_nodes):
            self.node.setActiveChannelFields(mn.class_mt, mn.channels)

        print(f"--Set {i+1} channels")

    def _start_sampling(self):

        for i, mn in enumerate(self.mip_nodes):
            self.node.enableDataStream(mn.class_mt)

        print(f"--Start {i+1} streams")

    def _stream_data(self, timeout=500):
        ## timeout: milliseconds
        packets = self.node.getDataPackets(timeout)

        return packets


    def get_packets_list(self):
        return self.packets_list

    def run(self, start_time,shared):

        cnt = 1
        while not shared.isDone:
            packets = self._stream_data()
            self.packets_list.append(packets)


            print(f"PRESS ENTER TO STOP AND SAVE\n{time() - start_time : .2f}s, {cnt} packets")
            cnt += 1