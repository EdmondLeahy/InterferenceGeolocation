import sys
import numpy as np
import argparse
import time
import matplotlib.pyplot as plt
import itertools

#NovAtel imports
from nov_coordinates.common import great_circle_distance as dist

# p1 = [-17.68146368022545, -6.557751684725212 ]
# p2 = [-84.57003376514466, -158.95648920830791]
# p3 = [103.03446283754748, 50.416573178409934]
# p4 = [36.46169651222223, 1.1506615337249584]
# p5 = [31.597150028742966, -77.94252395819225]

p1 = [51.14885905448, -114.03555301633, 0]
p2 = [51.15074076048, -114.03287235675, 0]
p3 = [51.1495871932, -114.03389309155, 0]
p4 = [51.15022875936, -114.03459732999, 0]
p5 = [51.15029795655, -114.03382355, 0]

TRUTH = [51.15028763264, -114.03434460864, 0]


POINTS = [p1, p2, p3, p4, p5]
COMBINATIONS = [[1, 2, 17.7123091132287, -17.472155936203503, 35.184465049432205, 322846.0],
                [1, 3, 80.06742421665987, 77.98866127635407, 2.0787629403058077, 322846.0],
                [1, 4, 50.22371445304169, 47.407626683426734, 2.8160877696149527, 322846.0],
                [2, 3, 95.50132127408648, 95.46081721255757, 0.04050406152890673, 322846.0],
                [2, 4, 65.39992426044967, 64.87978261963023, 0.5201416408194319, 322846.0],
                [3, 4, 34.97196442028923, -30.581034592927338, 65.55299901321658, 322846.0],
                [1, 2, 17.51663174266794, -17.471136132979126, 34.987767875647066, 322845.0],
                [1, 3, 81.4085114262775, 77.98689163336468, 3.4216197929128214, 322845.0],
                [2, 3, 100.05722022617867, 95.4580277663438, 4.5991924598348675, 322845.0],
                [2, 4, 69.32033819525606, 64.87913897616707, 4.441199219088986, 322845.0]]

# COMBINATIONS = [[2, 3, 81.53288001596006, True, 10.849304565172238]]

# def dist(p1, p2):
#     d = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
#     return d

def find_extents(positions, scale=0.5):
    lats = [p[0] for p in positions]
    lons = [p[1] for p in positions]
    range_lats = (max(lats)-min(lats))
    range_lons = (max(lons)-min(lons))
    return min(lats)-scale*range_lats, max(lats)+scale*range_lats, min(lons)-scale*range_lons, max(lons)+scale*range_lons

def create_px_map(p1, p2, d, map_ranges):
    px_map = []
    for i in map_ranges[0]:
        row = []
        for j in map_ranges[1]:
            dist_p1 = dist(p1,(i,j))
            dist_p2 = dist(p2,(i,j))
            del_dist = (dist_p2-dist_p1)
            if np.abs(del_dist-d)<0.5:
                val = 2
            else:
                val = np.abs(1/(d-del_dist))
            row.append(val)
        px_map.append(row)
    return np.array(px_map)

def plot_px_map(px_map, points, extents):
    print('plotting')
    fig, ax = plt.subplots()
    fig.canvas.draw()
    ax.imshow(px_map[0], interpolation='nearest',
               extent=[extents[2], extents[3], extents[0], extents[1]], origin='lower')
    for i, p in enumerate(points):
        ax.scatter(p[1], p[0])
        ax.annotate(i, (p[1], p[0]))
    ax.plot(px_map[1][2], px_map[1][1], marker='*', color='green')
    ax.plot(TRUTH[1], TRUTH[0], marker='*', color='red')
    yticks = np.arange(np.round(extents[0], 3), round(extents[1],3), 0.001)
    xticks = np.arange(np.round(extents[2], 3), round(extents[3],3), 0.001)
    ax.set_xticklabels([f'{np.round(c,2)}' for c in xticks])
    # ax.set_yticklabels([f'{np.round(c,2)}' for c in yticks])
    plt.show()
    # time.sleep(60)

def combine_px_maps(all_maps, space):
    max_val = [0,0,0]
    total_map = []
    for i,p in enumerate(space[0]):
        total_map_row = []
        for j,k in enumerate(space[1]):
            val = sum([x[i][j] for x in all_maps])
            if val > max_val[0]:
                max_val=(val, p, k)
            total_map_row.append(val)
        total_map.append(total_map_row)
    return np.array(total_map), max_val

def perform_batch_process(args, extents, grid):
    maps = []
    print(f'making maps {len(grid[0])*len(grid[1])}')
    if not args.combination_file:
        combinations = COMBINATIONS
    else:
        combinations = np.loadtxt(args.combination_file)
    for x in combinations:
        x = [int(i) for i in list(x)]
        px_map = create_px_map(POINTS[x[0]], POINTS[x[1]], x[2], grid)
        maps.append([px_map, x[-1]])
    return maps

def combine_maps(maps, grid, extents):
    print('combining maps')
    total_map = combine_px_maps([m[0] for m in maps], grid)
    print(f'max at {total_map[1]}')
    print('plotting total map')
    plot_px_map(total_map, POINTS, extents)

def combine_epochs(maps, grid, extents):
    epochs = np.unique([m[1] for m in maps])
    all_epochs_merged_maps = []
    for e in epochs:
        epoch_maps = []
        for m in maps:
            if e == m[-1]:
                epoch_maps.append(m)
        all_epochs_merged_maps.append(combine_px_maps([m[0] for m in epoch_maps], grid))
    return all_epochs_merged_maps

def make_gif(maps):
    print('wounld make gif here')

def main(args):
    step = args.step/100000
    extents = find_extents(POINTS)
    grid = [np.arange(extents[0], extents[1],step),
            np.arange(extents[2], extents[3], step)]
    maps = perform_batch_process(args, extents, grid)
    if args.gif:
        epoch_combined_maps = combine_epochs(maps, grid, extents)
        make_gif(epoch_combined_maps)
    else:
        combine_maps(maps, grid, extents)
    return 1

def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('-step', type=float, default=0.5, help='space step')
    args.add_argument('-combination_file', type=str, default=None, help='file to load combinations')
    args.add_argument('-gif', action='store_true', help='make a gif of each epoch')
    return args.parse_args()


if __name__=="__main__":
    args = get_args()
    sys.exit(main(args))
