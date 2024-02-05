import os

F=[]
for root, ds, fs in os.walk('./CKAN-meta-master'):
    for f in fs:
        F.append(os.path.join(root,f))

for i,fp in enumerate(F):
    data=''
    with open(fp,'r',encoding='utf-8') as f:
        data=f.read()
    datar=data.replace('"download": "https://github.com','"download": "https://ghproxy.org/https://github.com')
    '''
    print(fp)
    print(data)
    print('')
    print(datar)
    print('')
    '''
    with open(fp,'w',encoding='utf-8') as f:
        f.write(datar)
    
    print(i/len(F)*100,'%')