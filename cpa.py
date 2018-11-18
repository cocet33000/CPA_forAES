import matplotlib.pyplot as plt
import numpy as np
import pickle 
import yaml
from mpl_toolkits.mplot3d import Axes3D


keys = []
guess_keys = []

# load chiper text
with open('./pkl/aes.pkl',mode = 'rb') as f:
    data = np.array(pickle.load(f))
    print('load power data')


for num in range(16):
    
    # load profiling data
    with open('./pkl/b' + str(num) + '.pkl',mode = 'rb') as f:
        guess = np.array(pickle.load(f))
        print('load' + str(num))
    
    max_conf = 0
    key = ''
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    guess_key = []
    
    for i in range(256):
        x = []
        v1 = guess[:,i]
        for j in range(2800,3000,1):
            v2 = data[:,j]
            conf = np.corrcoef(np.vstack((v1,v2)))[1][0]
            x.append(conf)
            guess_key.append(conf)
            if(max_conf < conf):
                print(i)
                key = format(i,'02x')
                print(hex(i),key)
                max_conf = conf
                print(key,j,max_conf)
        x = range(2800,3000,1)
        y = [i for loop in range(200)]
        plt.plot(x, y, guess_key, "-o", color="#00aa00", ms=4, mew=0.5)
        ax.legend()
        guess_key = []
    
    print(str(num) + ' key is ' + key + ', conf:' + str(max_conf))
    keys.append(key)
    print(keys)
    plt.savefig('./fig/conf'+str(num))
    plt.close()

#write text
with open('10Rkey.txt', mode='w') as f:
    key10R = '0x'
    for i in keys:
        key10R += i
    f.write(key10R)
