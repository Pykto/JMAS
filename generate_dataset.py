import os
import sys
import argparse
from utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the final dataset for the graphs. The output is a pickle file with two lists: A list of networkx graphs, and a list corresponding to each graph\'s label.')
    parser.add_argument('name', metavar='name_inst', type=str, 
                    help='Name of the water installation.')
    parser.add_argument('--z', metavar='zone', type=int, nargs='+')

    args = parser.parse_args()

    path = os.path.join("data", args.name, "Timed Graph Data_dtw")
    data = load_pickle(path)
    graphs = data["graphs"] 
    timestamps = data["timestamps"]
    graphs = filter_unconnected(graphs)
    zones = args.z if args.z else  (1, 2, 3, 4, 5, 6)

    for zn in zones:
        time_label, hourly_label =  load_pickle(f"data/labels/labels_zone_{zn}")

        data, target, timestamp = align_data(graphs, timestamps, hourly_label, time_label)
        (X1, X2), (Y1, Y2) = separate_by_class(data, target)

        anomalies =  len(Y2)
        data   = [ *X1[:anomalies], *X2[:] ] 
        target = [ *Y1[:anomalies], *Y2[:] ]
        path = os.path.join("data", args.name, f"jmas_dataset_{zn}") 
        save_pickle([data, target], path)