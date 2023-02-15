
import pandas as pd
import numpy as np

def extract_latlon(csv):


    filename = 1



    dataDict = {}
    df = pd.DataFrame(data=dataDict)
    print(df)
    df.to_csv(f"csvs/{filename}.csv", index=False)
    print(f"\n{filename}.csv saved in csvs/")





if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--', default='/dev/ttyUSB0')
    argparser.add_argument('--hz', default='30')

    args = argparser.parse_args()
    target = 
    raw = pd.read_csv(target)
    pass