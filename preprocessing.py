#!/home/owner/Downloads/venvs/jmas_graph/bin/python
import os
import sys
import argparse
from utils import *

def make_instalaciones(path, name):
    installations = []
    filepath = os.path.join(path, f"{name}.csv")
    with open(filepath, "r") as file:
        for i, line in enumerate(file):
            if i > 0:
                timestamp, valor, clave_inst, *_ = line.strip("\n").split(",")
                if clave_inst not in installations:
                    installations.append(clave_inst)
    output = os.path.join(path, "installations.pickle")
    with open(output, "wb") as pickle:
        pk.dump(installations, pickle)

def make_time_series(path, name):
    filepath = os.path.join(path, f"{name}.csv")
    timestamp, value, names = [], [], []
    with open(filepath, "r") as file:
        for i, line in enumerate(file):
            if i > 0:
                ts, v, n, *_ = line.strip("\n").split(",")
                ts = ts.strip("\"")
                ts = datetime.strptime(ts[:18], '%Y-%m-%d %H:%M:%S')
                timestamp.append(ts)
                value.append(v)
                names.append(n)   
                 
    inst_data = os.path.join(path, f"{name}.pickle")
    with open(inst_data, "wb") as pickle:
        pk.dump([timestamp, value, names], pickle)

def make_graphs(name, method='dtw'):

    instalations = load_pickle(f"data/{name}/installations")
    dates, values, names = load_pickle(f"data/{name}/{name}")

    current_day  = dates[0]
    daily_data = []
    diff_dates = []
    hourly_data = [ [] for _ in range(len(instalations))]

    time_dataset =[]
    graph_dataset = []

    for date, val, clave_inst in zip(dates, values, names):
        if date.hour != current_day.hour:
            timestamp = datetime.strptime( f"{current_day.year}-{current_day.month}-{current_day.day} {current_day.hour}", "%Y-%m-%d %H" )
            print(timestamp)
            hourly_data = [ h if len(h) > 1 else -1 for h in hourly_data ]
            matrix = [[0 for _ in range(len(instalations))] for _ in range(len(instalations))]
            for i in range(len(instalations)):
                for j in range(len(instalations)):
                    if hourly_data[i] == -1 or hourly_data[j] == -1:
                        matrix[i][j] = float('inf')
                    else:
                        hi, hj = hourly_data[i], hourly_data[j]                    
                        if method == "dtw":
                            matrix[i][j] = calculate_dtw(hi, hj)
                        if method == "corrcoef":
                            hi = list(map(float, hi))
                            hj = list(map(float, hj))
                            matrix[i][j] = calculate_corcoef(hi, hj)

            matrix = np.array(matrix)
            matrix_1d = []
            for i in range(len(matrix)):
                for j in range(len(matrix)):
                    if i == j:
                        break
                    if matrix[i][j] != float('inf'):
                        matrix_1d.append(matrix[i][j])

            len_matrix1d = 1 if len(matrix_1d) < 2 else len(matrix_1d)
            matrix_avg = sum(matrix_1d)/len_matrix1d
            adj_matrix = [[ 1 if col >= 0.8 else 0 for col in row ] for row in matrix] 

            Graph = nx.from_numpy_matrix(np.array(adj_matrix))
            timestamp = str(timestamp)
            graph_dataset.append(Graph)
            time_dataset.append(timestamp)
            hourly_data = [ [] for _ in range(len(instalations))]
            current_day = date

    graph_dataset = filter_unconnected(graph_dataset)
    pickle_name = os.path.join("data", "labels", f"Timed Graph Data_{method}")
    pickle_data = {"graphs":graph_dataset, "timestamps":time_dataset}
    save_pickle(pickle_data, pickle_name)

def generate_labels(zn):
    path = "reportesfaltaAgua/csv_files/"
    dates = []
    jun = []
    for file in os.listdir(path):
        with open(os.path.join(path, file), 'r', encoding='UTF-8') as f:
            for i, line in enumerate(f):
                line = line.strip("\n").split(",")
                if file == "jun2018.csv" :
                    if len(line[0]) > 0:
                        line = [ 1 if len(l) > 0 else 0 for l in line  ]
                    jun.append(line[1:])
                else:
                    if i > 0 and str(zn) in line[4]:
                        try:
                            yr, mo, dy = line[-2].split("-")
                            dates.append([ int(yr), int(mo), int(dy) ])
                        except Exception as e:
                            print('error aqui')
                            continue
    reports = {}
    head = jun[0] 
    jun = np.array(jun[1:])  

    for i in range(30):
        reports[ head[i] ] = Counter(jun[:,i])[1]

    store = {}
    for date in dates:
        today = "-".join([ str(d) for d in date ])
        if today not in store:
            store[today] = 0
        store[today] += 1

    tmp = {**reports, **store}
    yearly = {}
    for i in sorted(tmp.keys()):
        yearly[i] = tmp[i]

    tmp = 0
    avg = {}
    for day, fail in yearly.items():
        yr, mo, dy = day.split('-')
        month = f"{yr}-{mo}"
        if month not in avg:
            avg[month] = []
        avg[month].append(fail)

    for k,v in avg.items():
        avg[k] = np.mean(v)

    target = []
    d_target = []
    for k,v in yearly.items():
        mo = k.split("-")
        mo = f"{mo[0]}-{mo[1]}"
        #print(k, v, mo, avg[mo])
        d_target.append(datetime.strptime(k, '%Y-%m-%d'))
        label = 1 if v > avg[mo] else 0
        target.append(label)

    save_pickle([d_target, target], f"data/labels/labels_zone_{zn}")
    print('Saved pickle as:', f"data/labels/labels_zone_{zn}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for creating the graph datasets from the sensed values of different JMAS water souorces')
    parser.add_argument('name', metavar='name_inst', type=str, 
                    help='Name without extension. Must be a csv file and must be inside data folder.')
    parser.add_argument('-m', '--method', metavar='method', type=str, 
                    help='Similarity method to generate the adjacency matrix. Options: (corrcoef, dtw), default: dtw.')
    args = parser.parse_args()

    name = args.name
    method = args.method

    if not os.path.isdir(os.path.join('data', name)):
        os.system(f"mkdir data/{name}")
        if sys.platform == 'win32':
            os.system(f"move data/{name}.csv ./data/{name}")
        else:
            os.system(f"mv data/{name}.csv ./data/{name}")
    
    if not os.path.isdir(os.path.join('data', "labels")):
        os.system(f"mkdir data/labels")

    path = os.path.join("data", name)
    make_instalaciones(path, name)
    make_time_series(path, name)
    if method:
        make_graphs(name, method=method)
    else:
        make_graphs(name)

    for zn in range(1, 7):
        generate_labels(int(zn))

# ########################################################

# graphs     = load_pickle(f'data/{source}/GD_graphs_corrcoef_val')
# time_graph = load_pickle(f'data/{source}/GD_times_corrcoef_val')

# for zn in range(1,7):    
#     # time_label, hourly_label =  load_pickle(f"output/DTWCORR/GT_hourly_labels_zone{zn}")
#     time_label, hourly_label =  load_pickle(f"data/GT_hourly_labels_zone{zn}")

#     data, target, timestamp = align_data(graphs, time_graph, hourly_label, time_label)
#     X1, X2, Y1, Y2 = separate_by_class(data, target)

#     anomalies =  len(Y2)
#     data   = [ *X1[:anomalies], *X2[:] ] 
#     target = [ *Y1[:anomalies], *Y2[:] ] 

