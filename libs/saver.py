import pandas as pd
class Saver:
    def __init__(self,filename):

        self.filename = filename




    def _init_dataDict(self, first_packets):

        dataDict = {}
        for packet in first_packets:
            for dataPoint in packet.data():
                cn = dataPoint.channelName()
                if cn not in dataDict.keys():
                    dataDict[cn] = []
                
        print(f"\n---Create dataDict with {len(dataDict.keys())} items")
        print(dataDict.keys())

        return dataDict
 
    def _parse_data(self, packets, dataDict):

        cnt_notvalid = 0
        cnt_success = 0
        for packet in packets:

            for dataPoint in packet.data():
                cn = dataPoint.channelName()
                if not dataPoint.valid():
                    cnt_notvalid +=1

                    dataDict[cn].append(None)
                else:

                    dataDict[cn].append(dataPoint.as_float())
                    cnt_success +=1

                
        print(f"------------------------{cnt_notvalid}, {cnt_success}")

                #print out the channel data
                #Note: The as_string() function is being used here for simplicity. 
                #      Other methods (ie. as_float, as_uint16, as_Vector) are also available.
                #      To determine the format that a dataPoint is stored in, use dataPoint.storedAs().

                # print(dataPoint.channelName() + ":", dataPoint.as_float())

                # print(dataPoint.channelName() + ":", dataPoint.as_Vector())
                # print(dataPoint.channelName() + ":", dataPoint.storedAs())
                
            
    def _check_same_lengths(self, dataDict):

        lengthDict = {}

        for key, values in dataDict.items():
            lengthDict[key]= len(values)
        
        max_length = max(lengthDict.values())

        for key, length in lengthDict.items():
            delta = max_length - length
            while delta > 0:
                dataDict[key].append(None)
                delta = max_length - len(dataDict[key])
            

    def run(self, packets_list):

        first_packets = packets_list[0]
        dataDict = self._init_dataDict(first_packets)

        for packets in packets_list:
            self._parse_data(packets, dataDict)
        

        self._check_same_lengths(dataDict)

        df = pd.DataFrame(data=dataDict)
        print(df)
        df.to_csv(f"csvs/{self.filename}.csv", index=False)
        print(f"\n{self.filename}.csv saved in csvs/")


# tags = []
# checked = []
# selected = []
# for i, name in enumerate(names):
#     tag = CONF_NAME + "-" + YEAR + "-" + str(i)
#     tags.append(tag) 
#     checked.append(0)
#     selected.append(0)

# dict = {'tag': tags, 'name':names, 'checked':checked, 'selected': selected}

        print(f"---[Saver] Saved {1} in {self.filename}")