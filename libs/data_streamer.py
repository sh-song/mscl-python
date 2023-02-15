
import sys
sys.path.append("/usr/share/python3-mscl")
import mscl
from time import time, sleep


class MipNode:
    """
    _mt : _miptype

    """
    def __init__(self, class_mt):

        self.class_mt = class_mt
        self.channels = mscl.MipChannels()
        self.channel_cnt = 0
    
    def add(self, channel_mt, rate=100):
        self.channels.append(mscl.MipChannel(channel_mt, mscl.SampleRate.Hertz(rate)))
        self.channel_cnt += 1


class DataStreamer:
    def __init__(self, COM_PORT, MASTER_RATE=30):


        self.connection = mscl.Connection.Serial(COM_PORT, 115200)
        print(f"---Try connection with {COM_PORT} at baudrate {115200}")

        self.node = mscl.InertialNode(self.connection)
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
        self.timestamp_list = []

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

        channel_cnts = 0
        for i, mn in enumerate(self.mip_nodes):
            self.node.setActiveChannelFields(mn.class_mt, mn.channels)
            channel_cnts += mn.channel_cnt

        print(f"--Set {channel_cnts} channels")

    def _start_sampling(self):

        for i, mn in enumerate(self.mip_nodes):
            self.node.enableDataStream(mn.class_mt)

        print(f"--Start {i+1} streams")

    def _stream_data(self, timeout=500):
        ## timeout: milliseconds
        packets = self.node.getDataPackets(timeout)

        timestamp = self._get_current_time()

        return timestamp, packets

    def _parse_data(self, timestamp, packets):
        
        timeline = {'TIME': timestamp}
        for packet in packets:
            for dataPoint in packet.data():
                cn = dataPoint.channelName()
                if not dataPoint.valid():
                    timeline[cn] = None
                else:
                    timeline[cn] = dataPoint.as_float()

        return timeline

    def _get_current_time(self):
        return str(mscl.Timestamp.timeNow()).replace(' ', '-').replace(':', '-')

    def get_packets_list(self):
        return self.packets_list
    def get_timeline_list(self):

        timeline_list = []
        for i in range(len(self.timestamp_list)):
            timestamp = self.timestamp_list[i]
            packets = self.packets_list[i]
            timeline = self._parse_data(timestamp, packets)
            timeline_list.append(timeline)

        return timeline_list


    def run(self, start_time,shared):

        cnt = 1
        while not shared.isDone:
            timestamp, packets = self._stream_data()
            self.timestamp_list.append(timestamp)
            self.packets_list.append(packets)

            cnt += 1
        if shared.isDone:
            sleep(2)
        
        print('--- End logging')


        logging_time = time() - start_time
        hz = cnt / logging_time

        print(f"\n{logging_time : .2f}s, {cnt} packets, {hz} Hz")

        self.connection.disconnect()
        print('--- Disconnect serial')