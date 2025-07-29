"""
Net functions
"""
import numpy as np
import re

#%% Network cohort wrapper class

class BuildNetCohort:
    def __init__(self, N, N_in, N_hid, N_out):
        """
        N: Number of networks
        N_in: Number of input neurons
        N_hid: List of hidden layer sizes, e.g., [3, 4, 3] for 3 hidden layers
        N_out: Number of output neurons
        """
        self.N = N
        self.N_in = N_in
        self.N_hid = N_hid
        self.N_out = N_out
        self.Nets = []

        for _ in range(N):
            layers = []
            layer_sizes = [N_in] + N_hid + [N_out]

            for i in range(len(layer_sizes) - 2):
                layers.append(HiddenLayer(layer_sizes[i], layer_sizes[i+1], 'random'))

            # Last layer is output layer
            layers.append(OutLayer(layer_sizes[-2], layer_sizes[-1], 'random'))

            # Add fitness score at the end
            layers.append(0)  
            
            self.Nets.append(layers)


#%% Neural net classes and functions

def runNet(Net,ins):
    'wrapper function to run all net layers'
    ins_ = ins
    for layer in Net[0:-1]: #exclude fitness
        layer.Run(ins_)
        ins_ = layer.out
        
    return ins_

class Layer: #Common class for Hidden and Out classes to inherit from
    def __init__(self, N_in, N_hid, state='default'):
        self.N_in = N_in
        self.N_hid = N_hid
        if state == 'random':
            self.weights = np.random.uniform(-1,1,(N_in,N_hid))
            self.biases = np.random.uniform(-1,1,N_hid)

    def SetParams(self, weights = 'NULL', biases = 'NULL', state='default'):
         if state == 'random':
             self.weights = np.random.uniform(-1,1,(self.N_in,self.N_hid))
             self.biases = np.random.uniform(-1,1,self.N_hid) 
         else:
             'Check provided params are the right size'
             if np.shape(weights) == (self.N_in,self.N_hid):
                 self.weights = weights
             else:
                 print('Error: weights matrix is incorrect shape!')
             if np.shape(biases) == (self.N_hid,):
                 self.biases = biases
             else:
                 print('Error: biases vector is incorrect length!')

    def Mutate(self, Net1, Net2, mut_rt):
        'idx is the layer of the net'
        if mut_rt > 1:
            print('Mutation rate cannot be >1. Rate set to 1')
            mut_rt = 1
        elif mut_rt < 0:
            print('Mutation rate cannot be <0. Rate set to 0')
            mut_rt = 0
        'Mutate weights'
        shape = np.shape(self.weights)
        for i in range( shape[0] ):
            for j in range( shape[1] ):
                rnd = np.random.uniform(0,1,1)[0] #randomly pick a parent to take a weight from
                rnd2 = np.random.uniform(-mut_rt,mut_rt,1)[0] #mutation factor
                self.weights[i][j] = ( (Net1.weights[i][j]*rnd) + (Net2.weights[i][j]*(1-rnd)) ) + rnd2
        'Mutate Biases'
        for i in range( np.shape(self.biases)[0] ):
            rnd = np.random.uniform(0,1,1)[0]
            rnd2 = np.random.uniform(-mut_rt,mut_rt,1)[0]
            self.biases[i] = ( (Net1.biases[i]*rnd) + (Net2.biases[i]*(1-rnd)) ) + rnd2   

    def NormParams(self): #for visualisations
        AbsWeights = np.abs(self.weights)
        self.NormWeights = np.divide( AbsWeights, np.max(AbsWeights) )    
        AbsBiases = np.abs(self.biases)        
        self.NormBiases = np.divide( AbsBiases, np.max(AbsBiases) )
    
class HiddenLayer(Layer):
            
    def Run(self, in_vec):
        'Check that in is the correct length'
        if np.shape(in_vec) == (self.N_in,):
            out = np.zeros((self.N_hid,))
            for i in range(self.N_hid):
                out[i] = np.dot(self.weights[:,i],in_vec) + self.biases[i]
            out[out<0] = 0 #RelU
            self.out = out
        else:
            print('Error: input vector is incorrect length!') 
            
class OutLayer(Layer):
            
    def Run(self, in_vec):
        'Check that in is the correct length'
        if np.shape(in_vec) == (self.N_in,):
            out = np.zeros((self.N_hid,))
            for i in range(self.N_hid):
                out[i] = 1/( 1 + np.exp(- (np.dot(self.weights[:,i],in_vec) + self.biases[i]) ))  #sigmoid
            self.out = out
        else:
            print('Error: input vector is incorrect length!')

                      
def myFunc(e): #for sorting list of nets
    return e[-1]   
         
#%%

def saveNet(file_path,file_name,Net,Struct,Name):
    with open(file_path + file_name, 'w') as file:
        
        file.write('Name: ' + Name)
        file.write('\n')
        
        file.write(f'Structure: {Struct[0]} {Struct[1]} {Struct[2]}')
        file.write('\n')
        
        for i in range(len(Net[0:-1])):    
            file.write(f'Hid_W_{i} ')
            for hidWeights in Net[i].weights:
                for hidWeight in hidWeights:
                    file.write(str(hidWeight)+' ')
            file.write('\n')
            
            file.write(f'Hid_B_{i} ')
            for hidBias in Net[i].biases:
                file.write(str(hidBias)+' ')
            file.write('\n')    
          
        file.write('Out_W ')
        for outWeights in Net[-2].weights:
            for outWeight in outWeights:
                file.write(str(outWeight)+' ')
        file.write('\n')
        
        file.write('Out_B ')
        for outBias in Net[-2].biases:
            file.write(str(outBias)+' ')
        file.write('\n')
        file.write('End')
        
def loadNet(file_path,file_name):      
    'Get lines from saved file'
    f = open(file_path + file_name, "r")  
    lines, params = (f.read()).splitlines(), []
    for i, line in enumerate(lines):
        params.append( line.split() )
    
    'Get parameters and structure from lines'
    for line in params:
        if line[0] == 'Name:':
            pass
        elif line[0] == 'Structure:':
            struct = []
            for i in range(1,len(line)):
                struct.append( int(re.sub( r"[\[\],]", "", line[i])) ) 
                
    'Create Net for weights and biases to go in'
    struct = [struct[0], struct[1:-1], struct[-1]]
    Net = BuildNetCohort(1, struct[0], struct[1], struct[2]).Nets[0]
    
    'Set Net weights and biases'
    p_idx = 2 #start at first weight list in params
    for layer in Net[0:-1]: #ignore the fitness
         
        weight_shape = np.shape(layer.weights)
        weight_temp = np.zeros(weight_shape)
        idx = 1 # index of the value in the params list, start after the param label
        for i in range(weight_shape[0]):
            for j in range(weight_shape[1]):
                weight_temp[i,j] = params[p_idx][idx]
                idx += 1
                
        p_idx += 1 #move to next param list        
        bias_len = len(layer.biases)   
        print(bias_len)     
        bias_temp = np.zeros(bias_len,)
        for i in range(1,bias_len+1):
            bias_temp[i-1] = params[p_idx][i]
            
        print(bias_temp)
            
        layer.SetParams(weight_temp,bias_temp)
        p_idx += 1 #move to next param list      
        
    return Net

#%%
'other'
def hardConfine(d_vec):
    'confine a net that can move in 0 to 1'
    for i, nd in enumerate(d_vec): #loop over dimensions
        if nd > 1:
            nd = 1
        elif nd < 0:
            nd = 0
        d_vec[i] = nd
    return tuple(d_vec)
