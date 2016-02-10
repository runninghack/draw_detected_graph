from datetime import timedelta, date
import networkx as nx
import codecs
from sets import Set
import json
import yaml
import time
config=yaml.load(open("config.yaml").read())
print config
path="reduce_graph/outputs/"
top_words_path="top_words/"
output_path=config["graph_path"]
target_month=config["target_month"]
protest_keywords = [a.strip() for a in codecs.open('protest_keywords', 'r').readlines()]


print protest_keywords

def daterange(start_date,n):
	for i in range(n):
		yield (start_date+timedelta(i)).strftime("%Y-%m-%d")
def get_word_freq(fid):
	try:
		lines = codecs.open(top_words_path + fid, 'r').readlines()[1:]
		words_freq_dict={w.split('\t')[0]: int(w.split('\t')[1]) for w in lines}
		return words_freq_dict
	except:
		return {}
def graph_plus(g1,g2):
	start=time.clock()
	g=nx.Graph()
	e1=[(edge[0],edge[1]) for edge in g1.edges()]
	e2=[(edge[0],edge[1]) for edge in g2.edges()]
	e=list(Set(e1)|Set(e2))
	g.add_edges_from(e)
	print time.clock()-start
	print len(g1.nodes()),len(g2.nodes()),len(g.nodes())
	return g
def remove_up_node(g,fid):
	try:
		up_keywords = [a.strip() for a in codecs.open('./filter/up/'+fid,"r").readlines()]
	except:
		up_keyword = [] 
	for node in g.nodes():
		if len(node)<3 and node not in up_keywords:
			g.remove_node(node)
	return g
def remove_down_node(g,fid):
	try:
		down_keywords = [a.strip() for a in codecs.open('./filter/down/'+fid, 'r').readlines()]
	except:
		down_keywords = []
	for node in g.nodes():
		if len(node)<3 and node not in down_keywords:
			g.remove_node(node)
	return g

def remove_node(g):
	for node in g.nodes():
		if len(node)<3:
			g.remove_node(node)
	return g
def union(a,b):
    return list(set(a) | set(b))
def run(start_date,n,month):
	start=time.clock()
	G=nx.Graph()
	word_freq={}
	items=start_date.split('-')
	start=date(int(items[0]),int(items[1]),int(items[2]))
	for fid in daterange(start,n):
		G=graph_plus(G,graph(fid))
		word_freq[fid]=get_word_freq(fid)
	print len(G.nodes())
	G=remove_node(G)
	G=max(nx.connected_component_subgraphs(G),key=len)
	print len(G.nodes())
	print "start_date:"+start.strftime("%Y-%m-%d")
	print "time_window_legth:" + str(n)
	print "subgraph_length:"+ str(len(G.nodes()))
	"""
	transfer node name from keyword to number id
	"""
	data={}
	data_key={}
	for i,node in enumerate(G.nodes()):
		data[node]=i
		data_key[i]=node	
	edges_list=[(data.get(edge[0]),data.get(edge[1])) for edge in G.edges(data=True) ]
	G.clear()
	G.add_edges_from(edges_list)
	nodes_weight={}
	nodes_sum={}
	for fid in daterange(start,n):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_weight[node]+=f
			except KeyError:
				nodes_weight[node]=f
	"""
	calculate lambda of a month for each word 
	"""
	beginning=date(2014,month,1)
	for fid in daterange(beginning,30):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_sum[node]+=f
			except KeyError:
				nodes_sum[node]=f
	for node in nodes_sum:
		nodes_sum[node]=nodes_sum[node]/30
	write_graph(start_date,G,n,nodes_weight,data)
	with open(output_path+start_date+'_'+str(n)+'_lambda.txt','w') as fp:
		json.dump(nodes_sum,fp)
	with open(output_path+start_date+'_'+str(n)+'_index.txt','w') as fp:
		json.dump(data_key,fp)
def find_down(start_date,n,month):
	start=time.clock()
	G=nx.Graph()
	word_freq={}
	items=start_date.split('-')
	start=date(int(items[0]),int(items[1]),int(items[2]))
	for fid in daterange(start,n):
		G=graph_plus(G,remove_up_node(graph(fid),fid))
		word_freq[fid]=get_word_freq(fid)
	print len(G.nodes())
	G=remove_node(G)
	G=max(nx.connected_component_subgraphs(G),key=len)
	print len(G.nodes())
	print "start_date:"+start.strftime("%Y-%m-%d")
	print "time_window_legth:" + str(n)
	print "subgraph_length:"+ str(len(G.nodes()))
	"""
	transfer node name from keyword to number id
	"""
	data={}
	data_key={}
	for i,node in enumerate(G.nodes()):
		data[node]=i
		data_key[i]=node	
	edges_list=[(data.get(edge[0]),data.get(edge[1])) for edge in G.edges(data=True) ]
	G.clear()
	G.add_edges_from(edges_list)
	nodes_weight={}
	nodes_sum={}
	for fid in daterange(start,n):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_weight[node]+=f
			except KeyError:
				nodes_weight[node]=f
	"""
	calculate lambda of a month for each word 
	"""
	beginning=date(2014,month,1)
	for fid in daterange(beginning,30):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_sum[node]+=f
			except KeyError:
				nodes_sum[node]=f
	for node in nodes_sum:
		nodes_sum[node]=nodes_sum[node]/30
	write_graph(start_date,G,n,nodes_weight,data)
	with open(output_path+start_date+'_'+str(n)+'_lambda.txt','w') as fp:
		json.dump(nodes_sum,fp)
	with open(output_path+start_date+'_'+str(n)+'_index.txt','w') as fp:
		json.dump(data_key,fp)


def find_up(start_date,n,month):
	start=time.clock()
	G=nx.Graph()
	word_freq={}
	items=start_date.split('-')
	start=date(int(items[0]),int(items[1]),int(items[2]))
	for fid in daterange(start,n):
		G=graph_plus(G,remove_down_node(graph(fid),fid))
		word_freq[fid]=get_word_freq(fid)
	print len(G.nodes())
	G=remove_node(G)
	G=max(nx.connected_component_subgraphs(G),key=len)
	print len(G.nodes())
	print "start_date:"+start.strftime("%Y-%m-%d")
	print "time_window_legth:" + str(n)
	print "subgraph_length:"+ str(len(G.nodes()))
	"""
	transfer node name from keyword to number id
	"""
	data={}
	data_key={}
	for i,node in enumerate(G.nodes()):
		data[node]=i
		data_key[i]=node	
	edges_list=[(data.get(edge[0]),data.get(edge[1])) for edge in G.edges(data=True) ]
	G.clear()
	G.add_edges_from(edges_list)
	nodes_weight={}
	nodes_sum={}
	for fid in daterange(start,n):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_weight[node]+=f
			except KeyError:
				nodes_weight[node]=f
	"""
	calculate lambda of a month for each word 
	"""
	beginning=date(2014,month,1)
	for fid in daterange(beginning,30):
		for node in G.nodes():
			try:
				f=word_freq[fid][data_key[node]]
			except KeyError:
				f=0
			try:
				nodes_sum[node]+=f
			except KeyError:
				nodes_sum[node]=f
	for node in nodes_sum:
		nodes_sum[node]=nodes_sum[node]/30
	write_graph(start_date,G,n,nodes_weight,data)
	with open(output_path+start_date+'_'+str(n)+'_lambda.txt','w') as fp:
		json.dump(nodes_sum,fp)
	with open(output_path+start_date+'_'+str(n)+'_index.txt','w') as fp:
		json.dump(data_key,fp)

def graph(fid):
	G=nx.Graph()
	edges=[]
	try:
		with codecs.open(path+fid,'r') as fin:
			for l in fin.readlines():
				item = l.split("\t")
				item = [_i.strip() for _i in item]
				edges.append((item[0],item[1]))
		G.add_edges_from(edges)
	except:
		print "error"
	return G
def protest_subgraph(G):
	start=time.clock()
	nodes=protest_keywords
	i=0
	while i <config["protest_keywords_distance_threshold"]:
		temp=[]
		for node in nodes:
			if G.has_node(node):
				temp=union(temp,nx.all_neighbors(G,node))
		i+=1
        nodes=union(temp,nodes)
#	nodes=protest_keywords
#	result=[]
#	start=time.clock()
#	for node in G.nodes():
#		flag=0
#		for protest_node in nodes:
#			if G.has_node(protest_node):
#				try:
#					dist=nx.shortest_path_length(G,node,protest_node)
#					if dist<config["protest_keywords_distance_threshold"]:
#						flag +=1
#				except:
#					continue	
#		if flag>=config["protest_keywords_adjacent_threshold"]:
#			result.append(node)
	print time.clock()-start
	return remove_edge(G.subgraph(nodes))
	
def remove_edge(g):
	start=time.clock()
	edges_list=[(edge[0],edge[1],edge[2]) for edge in g.edges(data=True) if edge[2]>config["edge_threshold"]]
	g.clear()
	g.add_weighted_edges_from(edges_list)
	return g
def write_graph(start_date,G,n,nodes_weight,data):
	output_graph=open(output_path+start_date+'_'+str(n)+'_graph.txt','w')
	lines=get_sec1(G)+get_sec2(nodes_weight)+get_sec3(G)+get_sec4(G,data)
	for line in lines:
		output_graph.write(line + '\n')
			
def get_sec1(G):
    lines = []
    lines.append("#################################################################")
    lines.append("#APDM Input Graph, this input graph includes 3 sections:")
    lines.append("#section1 : general information")
    lines.append("#section2 : nodes")
    lines.append("#section3 : edges")
    lines.append("#section4 : trueSubGraph (Optional)")
    lines.append("#")
    lines.append("#if nodes haven't information set weight to null")
    lines.append("#if nodes haven't information set weight to null")
    lines.append("#################################################################")
    lines.append("SECTION1 (General Information)")
    lines.append("numNodes = " + str(len(G.nodes())))
    lines.append("numEdges = " + str(len(G.edges())))
    lines.append("usedAlgorithm = NULL")
    lines.append("dataSource = GridDataset")
    lines.append("END")
    return lines


def get_sec2(nodes_weight):
    lines = []
    lines.append("#################################################################")
    lines.append("SECTION2 (Nodes Information)")

    lines.append("NodeID Weight")
    for item in nodes_weight:
        lines.append(str(item) + " " + str(nodes_weight[item]))
    lines.append("END")
    return lines


def get_sec3(G):
    lines = []
    lines.append("#################################################################")
    lines.append("SECTION3 (Edges Information)")
    lines.append("EndPoint0 EndPoint1 Weight")
    for edge in G.edges():
        lines.append(str(edge[0]) + " " + str(edge[1]) + " 1.000000")
    lines.append("END")
    return lines

def get_sec4(g,data):
    lines = []
    lines.append("#################################################################")
    lines.append("SECTION4 (TrueSubGraph Information)")
    lines.append("EndPoint0 EndPoint1 Weight")
    lines.append("null")	
    lines.append("END")
    lines.append("#################################################################")
    return lines
def up_down(item):
	start=time.clock()
	items=item.split("\t")
	begin = items[0]
	t=int(items[1])
	month=int(items[2])
	print "month "+str(month)+" start"
	global output_path
	if month<10:
		strm="0"+str(month)
	else:
		strm=str(month)
	output_path=config["graph_path"]+"2014_"+strm+"/"
	run(begin,t,month)
	print time.clock()-start
def up(item):
	start=time.clock()
	items=item.split("\t")
	begin = items[0]
	t=int(items[1])
	month=int(items[2])
	print "month "+str(month)+" start"
	global output_path
	if month<10:
		strm="0"+str(month)
	else:
		strm=str(month)
	output_path='./aggregate_graph/up/'+"2014_"+strm+"/"
	find_up(begin,t,month)
	print time.clock()-start
def down(item):
	start=time.clock()
	items=item.split("\t")
	begin = items[0]
	t=int(items[1])
	month=int(items[2])
	print "month "+str(month)+" start"
	global output_path
	if month<10:
		strm="0"+str(month)
	else:
		strm=str(month)
	output_path='./aggregate_graph/down/'+"2014_"+strm+"/"
	find_down(begin,t,month)
	print time.clock()-start
def main(item):
	up_down(item)
	up(item)
	down(item)
if __name__=="__main__":
	up("2014-09-02\t3\t9")
	down("2014-09-02\t3\t9")
