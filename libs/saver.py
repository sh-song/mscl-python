import pandas as pd
import numpy as np
class Saver:
    def __init__(self,filename):
        self.filename = filename

    def run(self, timeline_list):
       
        full_channels = []
        for timeline in timeline_list:
            for key in timeline.keys():
                if key not in full_channels:
                    full_channels.append(key)

        channels = full_channels[1:] ## except for 'TIME'

        len_timelines = len(timeline_list)
        len_channels = len(channels)

        data_arr = np.zeros([len_timelines, len_channels])

        timestamp_list = []
        for t in range(len_timelines):
            timeline = timeline_list[t]
            timestamp_list.append(timeline['TIME'])

            for i, cn in enumerate(channels):
                try:
                    data_arr[t, i] = timeline[cn]
                except KeyError:
                    data_arr[t, i] = None
            
        data_df = pd.DataFrame(data=data_arr)
        time_df = pd.DataFrame(data=timestamp_list)

        try:
            df = pd.concat([time_df, data_df], axis=1)
        except ValueError:
            df = data_df
            print("---[ERROR] Save without timestamp")

        df.to_csv(f"csvs/{self.filename}.csv", index=False, header=full_channels)
        print(f"\n--- {self.filename}.csv saved in csvs/")
