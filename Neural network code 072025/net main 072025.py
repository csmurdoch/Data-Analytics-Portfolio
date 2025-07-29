import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'none'
import os
os.chdir('C:\\Users\\craig\\Desktop\\pyhton\\1d tracking')
import netFunctions as nF
import visualisationFunctions as vF
import trainingFunctions as tF
import time 

file_path = 'C:\\Users\\craig\\Desktop\\pyhton\\1d tracking\\saved nets\\'
file_name = 'TrackNet1D.txt'

'Initalise nets'
N = 100
N_in, N_hid, N_out = 3, [4,4], 3
step_sz = 0.2

#%%
'User choice to load a saved net or to start training a new one'

user_in = input("Enter 1 into terminal to load a saved net or 2 to train a new net \n")
if user_in == "1":
    'load saved net'
    Net = nF.loadNet(file_path,file_name)
elif user_in == "2":
    'Create cohort of nets and initalise v1isual'
    Nets = nF.BuildNetCohort(N, N_in, N_hid, N_out).Nets
    Net = Nets[0]
        
    'init visualise net'
    C = vF.NodeCoords(Net) 
    ax, fig = vF.init_view() #initalise net visualisation
    vF.drawNet(Net, C, ax)
    ax.set_xlim(0,1);
    ax.set_ylim(0,1);
    
    '*******************************************************************************************************************************'
    
    user_in = input("Enter y into terminal when ready for training to proceed \n") 
    if user_in == 'y':
        'Train net'
        Gens, t, itt, fit = 100, 100, 10, [] #Generations, time for 1 net time loop
        s_max = 2**0.5 #max net distance from target
        t_start = time.time()
        for g in range(Gens): #generation loop, run generation -> genetic algorthim -> run next generation

            #Nets = tF.pointTracking_2d(Nets, itt, t, step_sz, s_max, g, Gens)
            Nets, d_vec = tF.angle_2dTracking(Nets, itt, t, step_sz, s_max, g, Gens)
            Nets, mut_rate, fit = tF.RunEvoAlgorithm(Nets, g, Gens, fit) #run genetic algorithm
            
            vF.drawNet(Nets[0], C, ax) #update visualisation
            ax.set_xlim(0,1)
            ax.set_ylim(0,1)
            plt.pause(0.01)
            
        t_end = time.time()
        Net = Nets[0]
        tF.printTrainResult(N_in, N_hid, N_out, fit, t_end-t_start)
        
        plt.figure(3)
        plt.scatter(np.linspace(1,Gens,Gens),fit-fit[0])
        plt.xlabel('Generation')
        plt.ylabel('Fitness [a.u.]')
        #plt.xscale('log')
      
    else: 
        print("Error: incorrect user input! \n")   
else:
    print("Error: incorrect user input! \n")

#%%
'Run best net: running the trained net'
tx, ty = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0]
nx, ny = np.random.uniform(0,1,1)[0], np.random.uniform(0,1,1)[0]
theta = 0
phi, d_vec = tF.GetAngle([tx,ty], [nx,ny], theta)

t = 1000
for i in range(t):
    
    rnd = np.random.randint(0,21,1)
    if rnd == 20:
       tx = np.random.uniform(0,1,1)[0]
       ty = np.random.uniform(0,1,1)[0]

    plt.figure(2)
    plt.clf()
    plt.scatter(x=tx,y=ty,c='r')
    plt.scatter(x=nx,y=ny,c='k')   
    plt.arrow(nx, ny, d_vec[0], d_vec[1], head_width = 0.025, fc = 'red', ec='red')
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.axis('off')
    plt.pause(0.1)

    'run net'
    FOV = np.pi / 2
    if phi*np.pi > FOV: #can net 'see' target. Is in 120 degree FOV?
        ins = np.array([-1,-1,-1]) 
    else:
        ins = np.array([phi,(tx-nx)/s_max,(ty-ny)/s_max]) # net input, distance net from target
    
    out = nF.runNet(Net, ins)

    'Update net position'
    theta += (np.pi - out[0]*np.pi) * 0.05
    nx += (0.5 - out[1]) * step_sz
    ny += (0.5 - out[2]) * step_sz
    
    'Confine net'
    if theta > 2*np.pi: #confine theta
        theta = theta - 2*np.pi 
    elif theta < 0:
        theta = 2*np.pi - theta 
    nx, ny = nF.hardConfine([nx,ny])
    
    phi, d_vec = tF.GetAngle([tx,ty], [nx,ny], theta)
    phi = phi/np.pi
        
#%%
'Save net in flat file'
user_in = input("Enter s into the terminal to save this net \n")
if user_in == "s":
    name = '2d tracking net'
    nF.saveNet(file_path,file_name,Net,[N_in,N_hid,N_out],name)
    print('Net was saved! \n')
else:
    print('Net was NOT saved! \n')
