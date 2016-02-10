#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import goslate
import re
import os
import math
from datetime import timedelta, date


gs = goslate.Goslate()
country="brazil"
data_path="./data/"+country+"/down/"
graph_path="./graph/"+country+"/down/"
top_words_path='./data/'+country+'/top_words/'
data=os.listdir(data_path)
mynodesize=[]
monthly_freq=[]

def daterange(start_date,n):
    for i in range(n):
        yield (start_date+timedelta(i)).strftime("%Y-%m-%d")


def get_word_freq(fid):
    try:
        lines = open(top_words_path + fid, 'r').readlines()[1:]
        words_freq_dict={w.split('\t')[0]: int(w.split('\t')[1]) for w in lines}
        return words_freq_dict
    except:
        return {}

    
def calculate_lambda(month,nodelist):
    nodes_sum={}
    beginning=date(2014,month,1)
    for fid in daterange(beginning,30):
        for node in nodelist:
            try:
                word_freq=get_word_freq(fid)
                # print word_freq
                f=word_freq[node]
            except KeyError:
                f=0
            try:
                nodes_sum[node]+=f
            except KeyError:
                nodes_sum[node]=f
    for node in nodes_sum:
        nodes_sum[node]=nodes_sum[node]/30
    return nodes_sum


def draw_graph(edges, labels=None, graph_layout='shell', nodelist = [], 
               node_size=[], node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif',file_name="graph",up_words=[],down_words=[]):

    # create networkx graph
    plt.clf()
    G=nx.Graph()

    # add edges
    for edge in edges:
        G.add_edge(edge[0], edge[1])
    print len(G.nodes())
    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)


    # draw graph
    print "nodesize:" +str(len(nodelist))
    print "downsize:" +str(len(down_words))
    print G.nodes()
    print down_words

    try:
        nx.draw_networkx_nodes(G,graph_pos,nodelist = up_words, node_size=node_size, 
                               alpha=node_alpha, node_color='red')
        nx.draw_networkx_nodes(G,graph_pos,nodelist = down_words, node_size=node_size, 
                               alpha=node_alpha, node_color=node_color)
        nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                               alpha=edge_alpha,edge_color=edge_color)
        nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                                font_family=text_font)
    except:
        print 'draw error'

    # show graph
    #plt.show(block=False)
    # graph=open("graph_path+file_name",'w')
    plt.savefig(graph_path+file_name, format="PNG")
    # plt.show()

    
def run(sub):
    f=open(data_path+sub)
    mynodelist = f.readline()
    if mynodelist.find('\t')>=0:
        mynodelist=mynodelist.strip().split('\t')
    else:
        mynodelist=f.readline().strip().split('\t')
    #mynodelisttrans = [gs.translate(i, 'en') for i in mynodelist]
    mynodesize = [int(float(i)) for i in f.readline().strip().split('\t')]
    
    data={}
    for i in range(len(mynodelist)):
        data[mynodelist[i]]=mynodesize[i]

    month=sub[5:7]
    mean=calculate_lambda(int(month),mynodelist)
    up_words=[]
    down_words=[]
    for i in mynodelist:
        try:
            if data[i]>mean[i]*10:
                up_words.append(i.replace("u00","\u00").decode('unicode_escape'))
            else:
                down_words.append(i.replace("u00","\u00").decode('unicode_escape'))
        except:
            continue
    """
    calculate node size
    """
    sort=sorted(mynodesize)
    lower_pivot=sort[int(len(sort)/3)]
    upper_pivot=sort[int(len(sort)*2/3)]
    for i in range(len(sort)):
        print mynodesize[i]
        if mynodesize[i]<=lower_pivot:
            mynodesize[i]=50
        elif lower_pivot<mynodesize[i]<=upper_pivot:
            mynodesize[i]=150
        else:
            mynodesize[i]=300
    #print mynodelisttrans
    edges = []
    for line in f:
        info = line.strip().split('\t')
        edges.append((info[0].replace("u00","\u00").decode('unicode_escape'), info[1].replace("u00","\u00").decode('unicode_escape')))

    draw_graph(edges,file_name=sub.replace("txt","png"),node_size=mynodesize,nodelist=mynodelist,up_words=up_words,down_words=down_words)


if __name__=="__main__":
    for sub in data:
        if sub.find("graph")>0:
            run(sub)

