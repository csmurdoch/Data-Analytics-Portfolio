"""
Visualisation functions
"""
import numpy as np
import matplotlib.pyplot as plt

def NodeCoords(Net): #function to get node coordinates
    'Get number of layers in Net'
    Layers = np.shape(Net)[0] # -1 for fitness +1 for input
    'Get y coordinates'
    dy = 0.5/Layers
    y_coords = np.linspace(0+dy,1-dy,Layers) #horizontal layer coords
    
    'Get x coordinates'
    x_coords = []
    dx = 0.5/Net[0].N_in 
    x_coords.append( np.linspace( 0+dx,1-dx, Net[0].N_in ) ) #input layer
    for layer in Net[0:-2]: #exclude fitness
        dx = 0.5/layer.N_hid
        x_coords.append( np.linspace( 0+dx,1-dx, layer.N_hid ) ) #hidden layers  
    dx = 0.5/Net[-2].N_hid
    x_coords.append( np.linspace( 0+dx,1-dx,Net[-2].N_hid ) ) #output layer
    
    C = [] #combine x and y coords
    for x_list, y in zip(x_coords,y_coords):
        C_ = []
        for x in x_list:
            C_.append([x,y])
        C.append(C_) 
    return C

def init_view():
    fig, ax = plt.subplots() 
    ax.axis('off')
    fig.subplots_adjust(0, 0, 1, 1) 
    plt.ion()
    return ax, fig 
    
def DrawNode(Net, layer, node, C_node, ax):
    idx = layer - 1 #maps layer to net layer
    if idx == -1:
        circle = plt.Circle((C_node[1],C_node[0]), 0.05 ,color='r', zorder=2)
        ax.add_patch(circle) #zorder tell plt what order to draw elements in
        ax.text(C_node[1]
               ,C_node[0]
               ,'IN'
               ,color = 'white'
               , fontsize = 14
               , ha='center', va='center')
    else:
        node_color = [Net[idx].NormBiases[node],0,0]
        circle = plt.Circle((C_node[1],C_node[0]), 0.05 ,color=node_color, zorder=2)
        ax.add_patch(circle) #zorder tell plt what order to draw elements in
        if node_color[0] > 0.1:
            node_text = round(Net[idx].biases[node],2)
            ax.text(C_node[1]
                   ,C_node[0]
                   ,node_text
                   ,color = 'white'
                   , fontsize = 14
                   , ha='center', va='center')
        
    
def DrawEdge(Net, prev_layer, node, prev_node, C_node1, C_node2, ax):
    edge_alpha = (Net[prev_layer].NormWeights)[prev_node][node]
    
    if edge_alpha >= 0.1:
        ax.plot([C_node1[1],C_node2[1]], [C_node1[0],C_node2[0]], color='blue', alpha = edge_alpha, linewidth=10, zorder=1)
        edge_text = round((Net[prev_layer].weights)[prev_node][node],2)
    
        if edge_alpha < 0.5:
            text_color = 'black'
        else:
            text_color = 'orange'
            
        ax.text( ((C_node1[1] + C_node2[1]*3) / 4) 
               , ((C_node1[0] + C_node2[0]*3) / 4) 
               ,edge_text
               ,color = text_color
               ,fontsize = 14
               ,fontweight = 'bold'
               , ha='center', va='center'
               ,rotation = -45)
    
def drawNet(Net,C,ax):
    ax.clear() #clear axis
   
    for layer in Net[0:-1]: #get normalised weights/biases to colour visualisation
        layer.NormParams()

    prev_layer = -1 #init prev layer, -1 means input layer
    for layer in range(len(C)):
        for node in range(len(C[layer])):  
            DrawNode(Net, layer, node, C[layer][node], ax)
            
            if prev_layer != -1: #conect nodes to all nodes in previous layer
                for prev_node in range(len(C[prev_layer])): 
                    DrawEdge(Net, prev_layer, node, prev_node, C[layer][node], C[prev_layer][prev_node],ax) 
                    
        prev_layer = layer #update prev layer index