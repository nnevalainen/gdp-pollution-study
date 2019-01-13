
import os
import shutil

src = 'dest'
dest = 'gdp_data' 

if not os.path.exists(dest):
    os.makedirs(dest)

for d in os.listdir(src):
    files = os.listdir(os.path.join('dest', d))
    df = [f for f in files if f[:3] == "API"][0]
    
    with open(os.path.join(src, d, df), 'r') as f:
        content = f.read()

    with open(os.path.join(dest, d + '.csv'), 'w') as f:
        f.write(content)
