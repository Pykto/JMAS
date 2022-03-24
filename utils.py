import os
import sys
import time
import random
from dtw import *
import numpy as np
import networkx as nx
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.base import clone
from sklearn.metrics import f1_score
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from karateclub.graph_embedding import Graph2Vec, SF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from datetime import datetime
import _pickle as pk


def load_pickle(name):
    with open("{}.pickle".format(name), 'rb') as file:
        model = pk.load(file)
        return model
def save_pickle(args, name):
    with open('{}.pickle'.format(name), 'wb') as file:
        pk.dump(args, file)
def filter_unconnected(graphs):
    new_graphs = []
    for g in graphs:
        new_g = g
        new_g.remove_nodes_from( list(nx.isolates(new_g)) )
        new_graphs.append( new_g )
    return new_graphs
def avg(l: list) -> float:
    return sum(l)/len(l)
    
def align_data(graphs, time_graph, hourly_label, time_label):
    data, target, timestamp = [], [], []
    count = 0
    for graph, time_ in zip(graphs, time_graph):
        if time_ == str(time_label[count]) :
            data.append(graph)
            target.append(hourly_label[count])
            timestamp.append(time_)
            count += 1
    return data, target, timestamp

def separate_by_class(X, Y):
    classes_ = list(set(Y))
    data = [[] for _ in classes_]
    target = [[] for _ in classes_]

    for x, y in zip(X, Y):
        data[classes_.index(y)].append(x)
        target[classes_.index(y)].append(y)

    return(data, target)

def get_embeddings(data, dimensions=128, epochs=10, method='graph2vec', k=0.75):
    if method == "g2v":
        g2v = Graph2Vec(dimensions=dimensions, wl_iterations=1, epochs=epochs)
        g2v.fit(data)
        embeddings = g2v.get_embedding()
    if method == "rg2v":
        rg2v = RanGraph2Vec(dimensions=dimensions, wl_iterations=1, epochs=epochs, k=k)
        rg2v.fit(data)
        embeddings = rg2v.get_embedding()
    if method == 'sf':
        sf = SF(dimensions = dimensions)
        sf.fit(data)
        embeddings = sf.get_embedding()
    return embeddings