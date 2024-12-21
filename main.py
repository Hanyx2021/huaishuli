import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import imageio.v2 as imageio
import os
import shutil
from tqdm import tqdm

mapbox = [[1, 1, 'R', 1, 1, 1, 1], 
          [1, 1, 0, 0, 0, -1, -1], 
          [1, 1, 0, 1, 1, 1, 1], 
          [1, -1, 0, 0, 'D', 'D', 0],
          [-1, 1, 1, 1, 1, 1, 1]]
totaltime = 1501

harm = [[0 for _ in row] for row in mapbox]
maxharm = [[0 for _ in row] for row in mapbox]
harmcache = [[0 for _ in row] for row in mapbox]

row = len(mapbox)
column = len(mapbox[0])
direction = {'U':'↑','D':'↓','L':'←','R':'→'}

def draw_colored_grid(rows, cols, colored_cells, time):
    fig, ax = plt.subplots()
    for row in range(rows + 1):
        ax.plot([0, cols], [row, row], color='black')
    for col in range(cols + 1):
        ax.plot([col, col], [0, rows], color='black')
    for (r, c, color) in colored_cells:
        if color == 'L' or color == 'R' or color == 'U' or color == 'D':
            ax.text(c + 0.5, r + 0.5, direction[color], ha='center', va='center', fontsize=24)
            ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=True, color='green'))
        else:
            ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=True, color=color))
    plt.title("%ds" % time, loc="center", fontsize=24)
    ax.set_xticks(np.arange(0, cols + 1, 1))
    ax.set_yticks(np.arange(0, rows + 1, 1))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.invert_yaxis()
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(False)
    plt.savefig(f'figs/{time - 1}.png')
    plt.close(fig)

def produce_colored_cell():
    colored_cells = []
    for i in range(row):
        for j in range(column):
            if mapbox[i][j] == 1:
                colored_cells.append((i,j,cm.OrRd(harm[i][j] / 75)))
            elif mapbox[i][j] == 0:
                colored_cells.append((i,j,'black'))
            elif mapbox[i][j] == -1:
                colored_cells.append((i,j,'gray'))
            else:
                colored_cells.append((i,j,mapbox[i][j]))
    return colored_cells

def process_video():
    png_path = './figs'
    png_files = os.listdir(png_path)
    image_list = [png_path + "/%d.png" % frame_id for frame_id in range(len(png_files))]
    gif_name = './output.gif'
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))
    # Save them as frames into a gif
    imageio.mimsave(gif_name, frames, 'GIF', duration=0.01)

def validwater(i,j):
    if i < 0 or i >= row or j < 0 or j >= column or mapbox[i][j] != 1:
        return False
    return True

def updatemaxharm(i,j,found,value):
    if (not validwater(i,j)) or found[i][j] == 1:
        return
    maxharm[i][j] = max(min(maxharm[i][j] + value,100),0)
    found[i][j] = 1
    updatemaxharm(i - 1,j,found,value)
    updatemaxharm(i + 1,j,found,value)
    updatemaxharm(i,j - 1,found,value)
    updatemaxharm(i,j + 1,found,value)

def spreadmaxharm(i,j,found):
    if (not validwater(i,j)) or found[i][j] == 1:
        return
    res = maxharm[i][j]
    if validwater(i - 1,j):
        res = max(res,maxharm[i - 1][j])
    if validwater(i + 1,j):
        res = max(res,maxharm[i + 1][j])
    if validwater(i,j - 1):
        res = max(res,maxharm[i][j - 1])
    if validwater(i,j + 1):
        res = max(res,maxharm[i][j + 1])
    maxharm[i][j] = res
    found[i][j] = 1
    spreadmaxharm(i - 1,j,found)
    spreadmaxharm(i + 1,j,found)
    spreadmaxharm(i,j - 1,found)
    spreadmaxharm(i,j + 1,found)
    

def operate(op):
    code = op[0]
    i = int(op[1])
    j = int(op[2])
    if code == "Block":
        mapbox[i][j] = -1
        harm[i][j] = 0
        maxharm[i][j] = 0
        harmcache[i][j] = 0
    if code == "Unblock":
        mapbox[i][j] = 1
        spreadmaxharm(i,j,[[0 for _ in row] for row in mapbox])
    if code == "PutUp":
        mapbox[i][j] = 'U'
    if code == "PutDown":
        mapbox[i][j] = 'D'
    if code == "PutLeft":
        mapbox[i][j] = 'L'
    if code == "PutRight":
        mapbox[i][j] = 'R'
    if code == "Unput":
        mapbox[i][j] = 0
    if code == "Pollute":
        updatemaxharm(i,j,[[0 for _ in row] for row in mapbox],int(op[3]))
        harm[i][j] = min(int(op[3]) + harm[i][j], maxharm[i][j])

def timestamp(operates):
    for time in tqdm(range(1,totaltime)):
        if time % 5 and time // 5 in operates:
            operate(operates[time // 5] * 5)
        for i in range(row):
            for j in range(column):
                if mapbox[i][j] == 1:
                    if harmcache[i][j] > 0:
                        harmcache[i][j] -= 1
                        updatemaxharm(i,j,[[0 for _ in row] for row in mapbox],1)
                    if time % 5 == 0:
                        updateharm = ((maxharm[i][j] - harm[i][j]) + 24) // 25
                        harm[i][j] = min(updateharm + harm[i][j], maxharm[i][j])
                if type(mapbox[i][j]) is not int:
                    if mapbox[i][j] == 'L':
                        srci = i
                        srcj = j + 1
                        dsti = i
                        dstj = j - 1
                    elif mapbox[i][j] == 'R':
                        srci = i
                        srcj = j - 1
                        dsti = i
                        dstj = j + 1
                    elif mapbox[i][j] == 'U':
                        srci = i + 1
                        srcj = j
                        dsti = i - 1
                        dstj = j
                    elif mapbox[i][j] == 'D':
                        srci = i - 1
                        srcj = j
                        dsti = i + 1
                        dstj = j
                    if time % 5 == 0 and validwater(srci,srcj) and validwater(dsti,dstj):
                        if harm[srci][srcj] == 0:
                            updatemaxharm(dsti,dstj,[[0 for _ in row] for row in mapbox],-1)
                        else:
                            if maxharm[dsti][dstj] < maxharm[srci][srcj]:
                                updatemaxharm(dsti,dstj,[[0 for _ in row] for row in mapbox],1)
                                harm[i][j] = min(1 + harm[i][j], maxharm[i][j])
        if time % 5 == 0:
            draw_colored_grid(row, column, produce_colored_cell(), time // 5)

if __name__ == "__main__":
    if not os.path.exists('./figs'):
        os.mkdir('./figs')
    else:
        shutil.rmtree('./figs')
        os.mkdir('./figs')
    operates = {}
    with open('./operate.txt', 'r') as file: 
        lines = file.readlines() 
        for line in lines:
            params = line.split()
            operates.update({int(params[0]):params[1:]})
    print("drawing maps...")
    timestamp(operates)
    print("producing video...")
    process_video()
                    