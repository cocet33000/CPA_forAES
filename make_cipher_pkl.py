import matplotlib.pyplot as plt
import pickle 

def split_n(text, n):
    return [ '0x' + text[i*n:i*n+n] for i in xrange(len(text)/n) ]

data = []

with open('file/aes_tv_0000001-0005000_power.csv',mode = 'r') as f:
    for line in f:
        line = line.strip()
        line = line.split(',')
        data.append(list(map(int, line)))
    print('complete 1-1')

with open('file/aes_tv_0005001-0010000_power.csv',mode = 'r') as f:
    for line in f:
        line = line.strip()
        line = line.split(',')
        data.append(list(map(int, line)))
    print('complete 1-2')

with open('aes.pkl',mode = 'wb') as f:
    print('writing 1')
    pickle.dump(data,f)

data = []

with open('file/cipher.txt',mode = 'r') as f:
    for line in f:
        line = line.strip()
        line = line[2:]
        li = split_n(line,4)
        li = [int(n,0) for n in li]
        data.append(li)
    print('complete 2')

with open('cipher.pkl',mode = 'wb') as f:
    pickle.dump(data,f)
    print('writed 2')
