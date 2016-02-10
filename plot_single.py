#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
import goslate
import textblob
from textblob import TextBlob
import os
import calendar
import codecs
import copy
import json

gs = goslate.Goslate()
result_path = "./"
sourcePath = "/Users/ramiel/Workspace/GraphIHT/data/mexico/"


def calculate_lambda(data_path, fname, nodelist):
    month = fname[5:7]
    num = int(fname.split("_")[2])
    fname_window = open(data_path + fname[0:8] + "results.txt").readlines()[num].split(",")[1]
    fullpath_window = sourcePath + "2014_" + month + "/" + fname_window
    words_dict = json.loads(codecs.open(fullpath_window.replace('graph', 'index'), 'r', 'utf-8').read())
    lambdas_dict = json.loads(codecs.open(fullpath_window.replace('graph', 'lambda'), 'r', 'utf-8').read())
    lambdas_dict = {words_dict[k]: float(v) for k,v in lambdas_dict.items()}
    lambdas = [lambdas_dict[l] for l in nodelist]
    return lambdas


def get_window_length(data_path, fname):
    num = int(fname.split("_")[2])
    fname_window = open(data_path + fname[0:8] + "results.txt").readlines()[num].split(",")[1]
    return int(fname_window.split("_")[1])


def translate_node(node):
    try:
        return str(TextBlob(node).translate(from_lang="es", to='en'))
    except:
        return node


def draw_graph(edges, up_words, down_words, node_size, node_color='blue', node_alpha=0.3,
               node_text_size=12, edge_color='blue', edge_alpha=0.3, edge_tickness=2,
               text_font='sans-serif', file_name="graph"):
    plt.clf()
    g = nx.Graph()

    for edge in edges:
        g.add_edge(edge[0], edge[1])

    graph_pos = nx.shell_layout(g)  # layout for the network

    # up_words = map(lambda x: translate_node(x), up_words)
    # down_words = map(lambda x: x + "(" + translate_node(x) + ")", down_words)  # add translated nodes to graph

    try:
        nx.draw_networkx_nodes(g, graph_pos, nodelist=up_words, node_size=node_size,
                               alpha=node_alpha, node_color='red')
        nx.draw_networkx_nodes(g, graph_pos, nodelist=down_words, node_size=node_size,
                               alpha=node_alpha, node_color=node_color)
        nx.draw_networkx_edges(g, graph_pos, width=edge_tickness,
                               alpha=edge_alpha, edge_color=edge_color)
        nx.draw_networkx_labels(g, graph_pos, font_size=node_text_size,
                                font_family=text_font)
    except:
        print 'draw error'

    plt.savefig(result_path + file_name, format="PNG")


def adjust_nodes_sizes(nodes_sizes):
    nodes_sizes_sort = sorted(nodes_sizes)
    lower_pivot = nodes_sizes_sort[int(len(nodes_sizes_sort)/3)]
    upper_pivot = nodes_sizes_sort[int(len(nodes_sizes_sort)*2/3)]
    for i in range(len(nodes_sizes_sort)):
        if nodes_sizes[i] <= lower_pivot:
            nodes_sizes[i] = 150
        elif lower_pivot < nodes_sizes[i] <= upper_pivot:
            nodes_sizes[i] = 400
        else:
            nodes_sizes[i] = 600
    return nodes_sizes


def adjust_lambdas(lambdas, weights, fname, data_path):
    num_days = calendar.monthrange(2014, int(fname[5:7]))[1]
    num_days_window = get_window_length(data_path, fname)
    num_days_window = get_window_length(data_path, fname)
    results = []
    for i in range(len(lambdas)):
        results.append((lambdas[i] * num_days - weights[i])/(num_days - num_days_window))
    return results


def run(data_path, fname):
    f = open(data_path + fname)
    nodes = f.readline()
    if nodes.find('\t') >= 0:
        nodes = nodes.strip().split('\t')
    else:
        nodes = f.readline().strip().split('\t')
    lambdas = calculate_lambda(data_path, fname, nodes)
    nodes = map(lambda x: x.replace("u00", "\u00").decode('unicode_escape'), nodes)
    nodes_weights = [float(i) for i in f.readline().strip().split('\t')]
    #lambdas = adjust_lambdas(lambdas, nodes_weights, fname, data_path)
    nodes_sizes = adjust_nodes_sizes(copy.copy(nodes_weights))
    nodes_weights = map(lambda x: x/get_window_length(data_path, fname), nodes_weights)


    edges = []
    for line in f:
        info = map(lambda x: x.replace("u00", "\u00").decode('unicode_escape'), line.strip().split('\t'))
        edges.append((info[0], info[1]))
    f.close()

    up_words = []
    down_words = []
    for i in range(len(nodes)):
        if nodes_weights[i] > lambdas[i]:
            up_words.append(nodes[i])
        else:
            down_words.append(nodes[i])

    draw_graph(edges, file_name=fname.replace("txt", "png"),
               node_size=nodes_sizes, up_words=up_words, down_words=down_words)


def run_all():
    data_path = "./data/"+country+"/down/"
    data_all = os.listdir(data_path)

    for fname in data_all:
        if fname.find("graph") > 0:
            print fname
            run(data_path, fname)


if __name__ == "__main__":
    data_path = "/Users/ramiel/Workspace/GraphIHT/outputs/mexico_down/"
    files= os.listdir(data_path)
    files = filter(lambda x: x.find("graph") > 0, files)
    for f in files:
        run(data_path, f)

