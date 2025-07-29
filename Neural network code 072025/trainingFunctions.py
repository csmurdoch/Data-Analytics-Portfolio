"""
Training Functions
"""

import netFunctions as nF
import numpy as np

def RunEvoAlgorithm(Nets, gen, gen_max, fit, mut_max = 0.5):
    'For cohort of nets remiz the top 2 into more nets'
    
    mut_rate = max(round(mut_max*(1 - (gen/gen_max)),2) , 0.001) #dynamic mutation rate
    N = len(Nets)
    
    Nets.sort(reverse = True, key=nF.myFunc) #sort nets in order of fitness
    fit.append(max(Nets[0][-1],0))
    print(f"Gen {gen+1} | Fitness: {max(round(fit[-1]-fit[0]),0)} [a.u.], Mutation: {mut_rate}") #Generation and loop
    
    '***************************************************************'

    Nets[0][-1] = 0 #reset fitness of top performers
    Nets[1][-1] = 0
    
    N_ = int( (N/2) * (1 + (gen/gen_max)) ) #for dymanic evolution and random cohort proportions
    
    for i in range(2,N_): #loop over nets, keep top 2 best performers, only mutate top 50%
        
        for j, layer in enumerate(Nets[i][0:-1]): #ignore fitness
            layer.Mutate(Nets[0][j], Nets[1][j], mut_rate) #mix and mutate params for new nets
        Nets[i][-1] = 0 #reset fitness
        
    for i in range(N_,N): #loop over nets, bottom 50% randomised
    
        for layer in Nets[i][0:-1]: #ignore fitness
            layer.SetParams(state = 'random') #randomise params for new nets
        Nets[i][-1] = 0 #reset fitness
        
    return Nets, mut_rate, fit

def printTrainResult(N_in, N_hid, N_out, fit, t):
    t = round(t/60,1)
    print(f'Network structure: {N_in}, {N_hid}, {N_out}\n')
    base_fit = abs(fit[1]-fit[0])
    print(f'Fitness: {max(round(fit[1] - fit[0]),0)} --> {round(fit[-1] - fit[0])}, {round((fit[-1]-base_fit)/base_fit)}% inc.\n')
    print(f'Training time: {t} [mins]\n')
    

#%%
'Training senarios: not really reuasable code but just specific senarios that could be reused'

def pointTracking_2d(Nets,itt,t,step_sz,s_max,g,Gens):
    for i_ave in range(itt): #averaging loop. Run each net in 10 senarios to avoid random chance
        for Net in Nets: # run each net to get its fitness
            'reset net and target position'
            tx, nx = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0]   
            ty, ny = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0] 
            for t_ in range(t): #run 1 net for t time steps
                
                ins = np.array([tx-nx,ty-ny]) # net input, distance net from target
                'Run net layers'
                out = nF.runNet(Net, ins)
                'Update net position'
                nx += (0.5 - out[0]) * step_sz #update next position over a continious range
                ny += (0.5 - out[1]) * step_sz
                'Confine net'
                nx, ny = nF.hardConfine([nx,ny])
                'Update net individual fitness'
                s =  ((tx-nx)**2 + (ty-ny)**2 )**0.5
                Net[-1] += (s_max - s) #/ (s_max*t*itt)    #np.exp(-abs(ins[0]))
    
    return Nets

def angle_2dTracking(Nets,itt,t,step_sz,s_max,g,Gens):
    for i_ave in range(itt): #averaging loop. Run each net in 10 senarios to avoid random chance
        for Net in Nets: # run each net to get its fitness
            'reset net and angle, target position'
            tx, nx = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0]   
            ty, ny = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0] 
            theta = np.random.uniform(0,2*np.pi,1)
            phi, d_vec = GetAngle([tx,ty], [nx,ny], theta) #phi is angle between net_target and net line of slight
            phi = phi/np.pi #normalise phi
            
            for t_ in range(t): #run 1 net for t time steps
                
                'Net input'
                FOV = np.pi / 2
                if phi*np.pi > FOV: #can net 'see' target. Is in 120 degree FOV?
                    ins = np.array([-1,-1,-1]) 
                else:
                    ins = np.array([phi[0],(tx-nx)/s_max,(ty-ny)/s_max]) # net input, distance net from target
                    
                'Run net layers'
                out = nF.runNet(Net, ins)
                
                'Update net position'
                theta += (np.pi - out[0]*np.pi) * 0.05
                nx += (0.5 - out[1]) * step_sz #update next position over a continious range
                ny += (0.5 - out[2]) * step_sz
                'Confine net'
                if theta > 2*np.pi: #confine theta
                    theta = theta - 2*np.pi 
                elif theta < 0:
                    theta = 2*np.pi - theta 
                nx, ny = nF.hardConfine([nx,ny])
                
                'Update net individual fitness'
                phi, d_vec = GetAngle([tx,ty], [nx,ny], theta) #Get new angle between
                phi = phi/np.pi #normalise phi
                s = ((tx-nx)**2 + (ty-ny)**2 )**0.5
                s_ang = (1 - phi[0])
                
                Net[-1] += ((s_max - s)**2 + s_ang**2)**0.5
    
    return Nets, d_vec

def GetAngle(pos_t, net_t, theta):
    'angle between dir vec and n_t vec'
    n_t = np.subtract(pos_t, net_t) #vector from net to target
    dx, dy = 0.1*np.cos(theta), 0.1*np.sin(theta) #compoents of net line of sight direction
    n_hat = [dy,dx] #vector along net central vision
    phi = np.arccos( np.dot(n_t, n_hat) 
                    / ( np.linalg.norm(n_t) * np.linalg.norm(n_hat)) ) #angle between n_t and n_hat
    
    return phi, [dy, dx]