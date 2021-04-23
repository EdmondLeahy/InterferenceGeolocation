import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const
import copy

savefig_dpi = 300
savefig_quality = 100
figure_size = 84

def distance_function(position1, position2 ):
    return np.sqrt((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2)

def pdoa_set_data(easting, northing, data, transmitter_x, transmitter_y, transmitter_power=10, min_value=7.5):
    # Caculate the receive power for all of the data:
    for d in data:
        distance = np.sqrt((transmitter_x - d[0]) ** 2 + (transmitter_y - d[1]) ** 2)
        d[2] = transmitter_power - (20 * np.log(distance) + 20 * np.log(1575.42) - 27.55)
        # transmit_power = distance - d[2]
    return data

def pdoa_get_map_value(easting, northing, data, min_value=7.5):
    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum = 0
            sum2 = 0
            count = 0
            for d in data:
                distance = np.sqrt((e - d[0]) ** 2 + (n - d[1]) ** 2)
                transmit_power = d[2] + 20 * np.log(distance) + 20 * np.log(1575.42) - 27.55
                #transmit_power = distance - d[2]
                sum += transmit_power
                sum2 += transmit_power ** 2
                count += 1
            rms2 = sum2 / count
            mean2 = sum ** 2 / count ** 2
            variance = rms2 - mean2

            potential_value = np.sqrt(variance)
            # potential_value = np.abs(range_value)
            row.append(min(min_value, potential_value))
        map_value.append(row)
    return map_value

def pdoa_map(easting, northing, data, label, lines=False):
    map_value = pdoa_get_map_value(easting, northing, data)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50

    ax1.contourf(easting, northing, map_value, 25)

    if lines is True:
        plt.set_cmap('binary_r')
        ax1.contour(easting, northing, map_value, 25, alpha=.25, linewidths=1)

    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'yo')
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('pdoa_map_f_{}.{}.png'.format(label, lines), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

    # fig = plt.figure(figsize=(figure_size,figure_size))
    # ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # # plt.plot(coordinates[0][1], coordinates[0][0])
    # # plt.plot(coordinates[1][1], coordinates[1][0])
    # # plt.plot(coordinates[2][1], coordinates[2][0])
    # extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # for c in data:
    #     plt.plot(c[0], c[1], 'yo')
    # # plt.plot(max_value_lon, max_value_lat, 'ro')
    # fig.savefig('pdoa_map_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

def pdoa_map_with_transmitter(easting, northing, data, label, transmitter_x, transmitter_y, transmitter_power=10, lines=False):
    data = pdoa_set_data(easting, northing, data, transmitter_x, transmitter_y, transmitter_power)
    map_value = pdoa_get_map_value(easting, northing, data)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50

    ax1.contourf(easting, northing, map_value, 25)

    if lines is True:
        plt.set_cmap('binary_r')
        ax1.contour(easting, northing, map_value, 25, alpha=.25, linewidths=1)

    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'yo')
    plt.plot(transmitter_x, transmitter_y, 'ko')
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('pdoa_map_wt_f_{}.{}.png'.format(label, lines), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

pure_cmap = []
pure_cmap.append('Reds_r')
pure_cmap.append('copper')
pure_cmap.append('BuGn_r')
pure_cmap.append('Greens_r')
pure_cmap.append('Blues_r')
pure_cmap.append('Purples_r')
pure_cmap.append('Oranges_r')
pure_cmap.append('Greys_r')

def artistic_pdoa_map_with_transmitter(easting, northing, data, label, transmitter_x, transmitter_y, transmitter_power=10):
    data = pdoa_set_data(easting, northing, data, transmitter_x, transmitter_y, transmitter_power)
    paired_map_values = []
    for i in xrange(1,len(data)):
        paired_map_values.append(pdoa_get_map_value(easting, northing, [data[0], data[i]]))
    map_value_all = pdoa_get_map_value(easting, northing, data)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50

    ax1.contourf(easting, northing, map_value_all, 25)

    cmap_index = 0
    for map_value in paired_map_values:
        plt.set_cmap(pure_cmap[cmap_index])
        cmap_index += 1
        ax1.contour(easting, northing, map_value, 25, alpha=.75, linewidths=1)

    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'yo')
    plt.plot(transmitter_x, transmitter_y, 'ko')
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('art_pdoa_map_wt_f_{}.{}.{}.png'.format(label, transmitter_x, transmitter_y), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

def color_transition(start, end, steps):
    color_values = []

    for x in xrange(steps):
        r = start[0] + (end[0] - start[0]) * (x + 1) / float(steps + 1)
        g = start[1] + (end[1] - start[1]) * (x + 1) / float(steps + 1)
        b = start[2] + (end[2] - start[2]) * (x + 1) / float(steps + 1)
        a = start[3] + (end[3] - start[3]) * (x + 1) / float(steps + 1)
        color_values.append((r,g,b,a))
    return color_values

def create_colors():
    hexagon_dark_blue = (0 / 255.0, 151 / 255.0, 186 / 255.0, 1)
    hexagon_dark_blue_75 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .75)
    hexagon_dark_blue_50 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .5)
    hexagon_dark_blue_25 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .25)
    hexagon_light_blue = (133 / 255.0, 205 / 255.0, 219 / 255.0, 1)
    hexagon_light_blue_75 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .75)
    hexagon_light_blue_50 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .5)
    hexagon_light_blue_25 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .25)
    hexagon_green = (165 / 255.0, 216 / 255.0, 103 / 255.0, 1)
    hexagon_green_75 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .75)
    hexagon_green_50 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .5)
    hexagon_green_25 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .25)
    hexagon_dark_green = (80 / 255.0, 158 / 255.0, 47 / 255.0, 1)
    hexagon_dark_green_75 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .75)
    hexagon_dark_green_50 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .5)
    hexagon_dark_green_25 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .25)
    hexagon_orange = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    hexagon_orange_75 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .75)
    hexagon_orange_50 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .5)
    hexagon_orange_25 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .25)
    hexagon_red = (220 / 255.0, 107 / 225.0, 47 / 255.0, 1)
    hexagon_red_75 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .75)
    hexagon_red_50 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .5)
    hexagon_red_25 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .25)
    hexagon_black = (0, 0, 0, 1)
    hexagon_grey = (84 / 255.0, 85 / 255.0, 89 / 255.0, 1)
    hexagon_yellow = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    white = (1, 1, 1, 1)

    layers_per_color = 1
    layers_per_transition = 100
    #main_colors = [hexagon_light_blue, hexagon_dark_blue, hexagon_green, hexagon_dark_green, hexagon_orange]
    main_colors = [hexagon_dark_blue, hexagon_dark_blue, white, hexagon_dark_green, hexagon_dark_green]
    transitions = [layers_per_transition] * (len(main_colors) - 1)
    #transitions[-1] = 25

    min_intensity = .8
    color_array = []
    layers = range(layers_per_color)
    order = -1
    color_index = 0
    for c in main_colors:
        if len(color_array) is not 0:
            color_array += color_transition(color_array[-1], c, transitions[color_index-1])
        for layer in layers[::order]:
            new_color = (c[0], c[1], c[2], c[3] * (np.round((layer + 1) / float(layers_per_color) * min_intensity + 1 - min_intensity, 2)))
            color_array.append(new_color)

        order *= -1
        color_index += 1
    for c in color_array[::-1]:
        print c

    return color_array[::-1]
    #hexagon_colors = [(0 / 255.0, 151 / 255.0, 186 / 255.0), (133 / 255.0, 205 / 255.0, 219 / 255.0),
    #                  (165 / 255.0, 216 / 255.0, 103 / 255.0)]

def create_colors_set1():
    hexagon_dark_blue = (0 / 255.0, 151 / 255.0, 186 / 255.0, 1)
    hexagon_light_blue = (133 / 255.0, 205 / 255.0, 219 / 255.0, 1)
    hexagon_green = (165 / 255.0, 216 / 255.0, 103 / 255.0, 1)
    hexagon_green_50 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .5)
    hexagon_green_25 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .25)
    hexagon_dark_green = (80 / 255.0, 158 / 255.0, 47 / 255.0, 1)
    hexagon_orange = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    hexagon_black = (0, 0, 0, 1)
    hexagon_grey = (84 / 255.0, 85 / 255.0, 89 / 255.0, 1)
    white = (1, 1, 1, 1)

    layers_per_color = 1
    layers_per_transition = 100
    #main_colors = [hexagon_light_blue, hexagon_dark_blue, hexagon_green, hexagon_dark_green, hexagon_orange]
    main_colors = [hexagon_black, hexagon_black, hexagon_dark_blue, hexagon_dark_blue, hexagon_green, white]

    min_intensity = .8
    color_array = []
    layers = range(layers_per_color)
    order = -1
    for c in main_colors:
        if len(color_array) is not 0:
            color_array += color_transition(color_array[-1], c, layers_per_transition)
        for layer in layers[::order]:
            new_color = (c[0], c[1], c[2], c[3] * (np.round((layer + 1) / float(layers_per_color) * min_intensity + 1 - min_intensity, 2)))
            color_array.append(new_color)

        order *= -1
    for c in color_array[::-1]:
        print c

    return color_array[::-1]

def create_colors_set2():
    darker_blue = (0 / 255.0, 100 / 255.0, 200 / 255.0, 1)
    hexagon_dark_blue = (0 / 255.0, 151 / 255.0, 186 / 255.0, 1)
    hexagon_dark_blue_75 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .75)
    hexagon_dark_blue_50 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .5)
    hexagon_dark_blue_25 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .25)
    hexagon_light_blue = (133 / 255.0, 205 / 255.0, 219 / 255.0, 1)
    hexagon_light_blue_75 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .75)
    hexagon_light_blue_50 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .5)
    hexagon_light_blue_25 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .25)
    hexagon_green = (165 / 255.0, 216 / 255.0, 103 / 255.0, 1)
    hexagon_green_75 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .75)
    hexagon_green_50 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .5)
    hexagon_green_25 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .25)
    hexagon_dark_green = (80 / 255.0, 158 / 255.0, 47 / 255.0, 1)
    hexagon_dark_green_75 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .75)
    hexagon_dark_green_50 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .5)
    hexagon_dark_green_25 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .25)
    hexagon_orange = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    hexagon_orange_75 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .75)
    hexagon_orange_50 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .5)
    hexagon_orange_25 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .25)
    hexagon_red = (220 / 255.0, 107 / 225.0, 47 / 255.0, 1)
    hexagon_red_75 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .75)
    hexagon_red_50 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .5)
    hexagon_red_25 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .25)
    hexagon_black = (0, 0, 0, 1)
    hexagon_grey = (84 / 255.0, 85 / 255.0, 89 / 255.0, 1)
    hexagon_yellow = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    white = (1, 1, 1, 1)

    layers_per_color = 1
    layers_per_transition = 25
    # main_colors = [hexagon_dark_blue, hexagon_dark_blue, white, hexagon_dark_green, hexagon_dark_green]
    main_colors = [white, hexagon_dark_blue]
    transitions = [layers_per_transition] * (len(main_colors) - 1)
    #transitions[-1] = 25

    min_intensity = .8
    color_array = []
    layers = range(layers_per_color)
    order = -1
    color_index = 0
    for c in main_colors:
        if len(color_array) is not 0:
            color_array += color_transition(color_array[-1], c, transitions[color_index-1])
        for layer in layers[::order]:
            new_color = (c[0], c[1], c[2], c[3] * (np.round((layer + 1) / float(layers_per_color) * min_intensity + 1 - min_intensity, 2)))
            color_array.append(new_color)

        order *= -1
        color_index += 1
    for c in color_array[::-1]:
        print c

    return color_array[::-1]

def create_colors_set4():
    darker_blue = (0 / 255.0, 100 / 255.0, 200 / 255.0, 1)
    hexagon_dark_blue = (0 / 255.0, 151 / 255.0, 186 / 255.0, 1)
    hexagon_dark_blue_75 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .75)
    hexagon_dark_blue_50 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .5)
    hexagon_dark_blue_25 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .25)
    hexagon_light_blue = (133 / 255.0, 205 / 255.0, 219 / 255.0, 1)
    hexagon_light_blue_75 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .75)
    hexagon_light_blue_50 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .5)
    hexagon_light_blue_25 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .25)
    hexagon_green = (165 / 255.0, 216 / 255.0, 103 / 255.0, 1)
    hexagon_green_75 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .75)
    hexagon_green_50 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .5)
    hexagon_green_25 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .25)
    hexagon_dark_green = (80 / 255.0, 158 / 255.0, 47 / 255.0, 1)
    hexagon_dark_green_75 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .75)
    hexagon_dark_green_50 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .5)
    hexagon_dark_green_25 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .25)
    hexagon_orange = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    hexagon_orange_75 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .75)
    hexagon_orange_50 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .5)
    hexagon_orange_25 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .25)
    hexagon_red = (220 / 255.0, 107 / 225.0, 47 / 255.0, 1)
    hexagon_red_75 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .75)
    hexagon_red_50 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .5)
    hexagon_red_25 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .25)
    hexagon_black = (0, 0, 0, 1)
    hexagon_grey = (84 / 255.0, 85 / 255.0, 89 / 255.0, 1)
    hexagon_yellow = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    white = (1, 1, 1, 1)

    layers_per_color = 1
    layers_per_transition = 25
    # main_colors = [hexagon_dark_blue, hexagon_dark_blue, white, hexagon_dark_green, hexagon_dark_green]
    main_colors = [white, hexagon_dark_blue]
    transitions = [layers_per_transition] * (len(main_colors) - 1)
    #transitions[-1] = 25

    min_intensity = .8
    color_array = []
    layers = range(layers_per_color)
    order = -1
    color_index = 0
    for c in main_colors:
        if len(color_array) is not 0:
            color_array += color_transition(color_array[-1], c, transitions[color_index-1])
        for layer in layers[::order]:
            new_color = (c[0], c[1], c[2], c[3] * (np.round((layer + 1) / float(layers_per_color) * min_intensity + 1 - min_intensity, 2)))
            color_array.append(new_color)

        order *= -1
        color_index += 1
    for c in color_array[::-1]:
        print c

    return color_array[::-1]

def create_colors_set3():
    darker_blue = (0 / 255.0, 100 / 255.0, 200 / 255.0, 1)
    hexagon_dark_blue = (0 / 255.0, 151 / 255.0, 186 / 255.0, 1)
    hexagon_dark_blue_75 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .75)
    hexagon_dark_blue_50 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .5)
    hexagon_dark_blue_25 = (0 / 255.0, 151 / 255.0, 186 / 255.0, .25)
    hexagon_light_blue = (133 / 255.0, 205 / 255.0, 219 / 255.0, 1)
    hexagon_light_blue_75 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .75)
    hexagon_light_blue_50 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .5)
    hexagon_light_blue_25 = (133 / 255.0, 205 / 255.0, 219 / 255.0, .25)
    hexagon_green = (165 / 255.0, 216 / 255.0, 103 / 255.0, 1)
    hexagon_green_75 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .75)
    hexagon_green_50 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .5)
    hexagon_green_25 = (165 / 255.0, 216 / 255.0, 103 / 255.0, .25)
    hexagon_dark_green = (80 / 255.0, 158 / 255.0, 47 / 255.0, 1)
    hexagon_dark_green_75 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .75)
    hexagon_dark_green_50 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .5)
    hexagon_dark_green_25 = (80 / 255.0, 158 / 255.0, 47 / 255.0, .25)
    hexagon_orange = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    hexagon_orange_75 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .75)
    hexagon_orange_50 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .5)
    hexagon_orange_25 = (241 / 255.0, 196 / 255.0, 0 / 255.0, .25)
    hexagon_red = (220 / 255.0, 107 / 225.0, 47 / 255.0, 1)
    hexagon_red_75 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .75)
    hexagon_red_50 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .5)
    hexagon_red_25 = (220 / 255.0, 107 / 225.0, 47 / 255.0, .25)
    hexagon_black = (0, 0, 0, 1)
    hexagon_grey = (84 / 255.0, 85 / 255.0, 89 / 255.0, 1)
    hexagon_yellow = (241 / 255.0, 196 / 255.0, 0 / 255.0, 1)
    white = (1, 1, 1, 1)

    alt_orange = ( 255/255.0, 150 / 255.0, 111 / 255.0, 1)
    alt_dark_green = ( 67/255.0, 100/255.0, 89/255.0, 1)
    alt_yellow = ( 252/255.0, 249/255.0, 129/255.0, 1)
    poster_blue = ( 0, 31 / 255.0, 122 /255.0, 1)

    layers_per_color = 1
    layers_per_transition = 25
    main_colors = [white, hexagon_dark_blue, poster_blue]
    # main_colors = [white, hexagon_dark_blue]
    transitions = [layers_per_transition] * (len(main_colors) - 1)
    transitions[-1] = 5

    min_intensity = .8
    color_array = []
    layers = range(layers_per_color)
    order = -1
    color_index = 0
    for c in main_colors:
        if len(color_array) is not 0:
            color_array += color_transition(color_array[-1], c, transitions[color_index - 1])
        for layer in layers[::order]:
            new_color = (c[0], c[1], c[2], c[3] * (
                np.round((layer + 1) / float(layers_per_color) * min_intensity + 1 - min_intensity, 2)))
            color_array.append(new_color)

        order *= -1
        color_index += 1
    for c in color_array[::-1]:
        print c

    return color_array[::-1]
    #hexagon_colors = [(0 / 255.0, 151 / 255.0, 186 / 255.0), (133 / 255.0, 205 / 255.0, 219 / 255.0),
    #                  (165 / 255.0, 216 / 255.0, 103 / 255.0)]

# hexagon_colors = create_colors()
# print len(hexagon_colors)

def tdoa_get_map_value(easting, northing, data):
    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum = 0
            sum2 = 0
            count = 0
            min_value = 999999
            max_value = 0
            for d in data:
                distance = np.sqrt((e-d[0])**2 + (n-d[1])**2)
                #transmit_power = d[2] + 20 * np.log(distance) + 20 * np.log(1575.42) - 27.55
                transmit_power = distance - d[2]
                sum += transmit_power
                sum2 += transmit_power ** 2
                count += 1
                min_value = min(min_value, transmit_power)
                max_value = max(max_value, transmit_power)
            rms2 = sum2 / count
            mean2 = sum ** 2 / count ** 2
            variance = rms2 - mean2
            range_value = max_value - min_value

            potential_value = np.sqrt(variance)
            #potential_value = np.abs(range_value)
            row.append(min(7.5, potential_value))
        map_value.append(row)
    return map_value

def tdoa_map(easting, northing, data, label):
    map_value = tdoa_get_map_value(easting, northing, data)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 25


    ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    #ax1.contourf(easting, northing, map_value, len(hexagon_colors))
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'o', color=(165 / 255.0, 216 / 255.0, 103 / 255.0, 1))
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('tdoa_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)
    plt.clf()

    fig = plt.figure(figsize=(figure_size,figure_size))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'o', color=(165 / 255.0, 216 / 255.0, 103 / 255.0, 1))
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('tdoa_map_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)
    plt.clf()

def ptdoa_get_map_value(easting, northing, data):
    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum_power = 0
            sum2_power = 0
            count_power = 0
            min_power = 999999
            max_power = 0
            sum_time = 0
            sum2_time = 0
            count_time = 0
            min_time = 999999
            max_time = 0
            for d in data:
                distance = np.sqrt((e - d[0]) ** 2 + (n - d[1]) ** 2)
                transmit_power = d[2] + 20 * np.log(distance) + 20 * np.log(1575.42) - 27.55
                transmit_time = distance - d[3]
                sum_power += transmit_power
                sum2_power += transmit_power ** 2
                count_power += 1
                min_power = min(min_power, transmit_power)
                max_power = max(max_power, transmit_power)

                sum_time += transmit_time
                sum2_time += transmit_time ** 2
                count_time += 1
                min_time = min(min_time, transmit_time)
                max_time = max(max_time, transmit_time)

            rms2_power = sum2_power / count_power
            mean2_power = sum_power ** 2 / count_power ** 2
            variance_power = rms2_power - mean2_power
            range_power = max_power - min_power
            potential_power = np.sqrt(variance_power)

            rms2_time = sum2_time / count_time
            mean2_time = sum_time ** 2 / count_time ** 2
            variance_time = rms2_time - mean2_time
            range_time = max_time - min_time
            potential_time = np.sqrt(variance_time)

            # potential_value = np.abs(range_value)
            row.append(min(15, potential_time + potential_power))
        map_value.append(row)
    return map_value

def ptdoa_map(easting, northing, data, transmitter, label, color_map='viridis_r'):
    map_value = ptdoa_get_map_value(easting, northing, data)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap(color_map)
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 150
    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contourf(easting, northing, map_value, layers, cmap=color_map)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'o', color=(226/255.0, 215/255.0, 26/255.0, 1))
    plt.plot(transmitter[0], transmitter[1], 'o', color=(66/255.0, 7/255.0, 86/255.0, 1))
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('ptdoa_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

    fig = plt.figure(figsize=(figure_size,figure_size))
    ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contour(easting, northing, map_value, layers, cmap=color_map)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'o', color=(226 / 255.0, 215 / 255.0, 26 / 255.0, 1))
    plt.plot(transmitter[0], transmitter[1], 'o', color=(66 / 255.0, 7 / 255.0, 86 / 255.0, 1))
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('ptdoa_map_{}.png'.format(label), bbox_inches=extent)


std = 10

def gnss_adr_map(easting, northing, satellites, receiver, label):
    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum_power = 0
            sum2_power = 0
            count_power = 0
            min_power = 999999
            max_power = 0
            for s in satellites:
                distance = np.sqrt((e - s[0]) ** 2 + (n - s[1]) ** 2)
                measurement_distance = np.sqrt((receiver[0] - s[0]) ** 2 + (receiver[1] - s[1]) ** 2)
                wavelength = 50
                difference = np.mod((distance - measurement_distance), wavelength)
                if(difference > wavelength / 2.0):
                    difference -= wavelength
                sum_power += difference
                sum2_power += difference ** 2
                count_power += 1
                min_power = min(min_power, difference)
                max_power = max(max_power, difference)

            rms2_power = sum2_power / count_power
            mean2_power = sum_power ** 2 / count_power ** 2
            variance_power = rms2_power - mean2_power
            range_power = max_power - min_power
            # potential_power = np.sqrt(variance_power)
            potential_power = np.power(rms2_power, 1.0 / 2.0)

            # potential_value = np.abs(range_value)
            # The min value in the next line will limit the size of the colours. Higher will include more data
            # (further away)
            row.append(min(100, potential_power))
        map_value.append(row)
    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50
    ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_adr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)
    # fig = plt.figure(figsize=(figure_size,figure_size))
    # ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # # plt.plot(coordinates[0][1], coordinates[0][0])
    # # plt.plot(coordinates[1][1], coordinates[1][0])
    # # plt.plot(coordinates[2][1], coordinates[2][0])
    # extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # for c in data:
    #     plt.plot(c[0], c[1], 'yo')
    # plt.plot(transmitter[0], transmitter[1], 'ko')
    # # plt.plot(max_value_lon, max_value_lat, 'ro')
    # fig.savefig('ptdoa_map_{}.png'.format(label), bbox_inches=extent)


def gnss_psr_adr_get_map_value(easting, northing, satellites, receiver, label, min_value=15, max_value=100 ):
    min_all = None
    max_all = None
    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum_power = 0
            sum2_power = 0
            count_power = 0
            min_power = 999999
            max_power = 0
            for s in satellites:
                distance = np.sqrt((e - s[0]) ** 2 + (n - s[1]) ** 2)
                measurement_distance = np.sqrt((receiver[0] - s[0]) ** 2 + (receiver[1] - s[1]) ** 2)
                wavelength = 50
                difference = np.mod((distance - measurement_distance), wavelength)
                if (difference > wavelength / 2.0):
                    difference -= wavelength
                difference = np.abs(difference)
                difference += np.abs(distance - measurement_distance) / 2.0
                sum_power += difference
                sum2_power += difference ** 2
                count_power += 1
                min_power = min(min_power, difference)
                max_power = max(max_power, difference)

            rms2_power = sum2_power / count_power
            mean2_power = sum_power ** 2 / count_power ** 2
            variance_power = rms2_power - mean2_power
            range_power = max_power - min_power
            # potential_power = np.sqrt(variance_power)
            potential_power = max(min_value, min(max_value, np.power(rms2_power, 1.0 / 2.0)))

            # potential_value = np.abs(range_value)
            # The min value in the next line will limit the size of the colours. Higher will include more data
            # (further away)
            row.append(potential_power)
            if min_all is None or potential_power < min_all:
                min_all = potential_power
            if max_all is None or potential_power > max_all:
                max_all = potential_power

        map_value.append(row)
    print '{} {} {}'.format(label, min_all, max_all)
    return map_value

def gnss_psr_adr_map(easting, northing, satellites, receiver, label):
    map_value = gnss_psr_adr_get_map_value(easting, northing, satellites, receiver, label)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50
    ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_psr_adr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)
    # fig = plt.figure(figsize=(figure_size,figure_size))
    # ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # # plt.plot(coordinates[0][1], coordinates[0][0])
    # # plt.plot(coordinates[1][1], coordinates[1][0])
    # # plt.plot(coordinates[2][1], coordinates[2][0])
    # extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # for c in data:
    #     plt.plot(c[0], c[1], 'yo')
    # plt.plot(transmitter[0], transmitter[1], 'ko')
    # # plt.plot(max_value_lon, max_value_lat, 'ro')
    # fig.savefig('ptdoa_map_{}.png'.format(label), bbox_inches=extent)

def rotate_radians(position, angle_rad):
    ret_value = []
    ret_value.append( np.cos(angle_rad) * position[0] - np.sin(angle_rad) * position[1] )
    ret_value.append( np.sin(angle_rad) * position[0] + np.cos(angle_rad) * position[1] )
    return ret_value

def rotate_degrees(position, angle_deg):
    angle_rad = angle_deg * np.pi / 180.0
    return rotate_radians(position, angle_rad)

def gnss_psr_map_with_lines(easting, northing, satellites, receiver, label):
    min_all = None
    max_all = None

    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum_power = 0
            sum2_power = 0
            count_power = 0
            min_power = 999999
            max_power = 0
            for s in satellites:
                distance = distance_function([e, n], s)
                measurement_distance = distance_function(receiver, s)
                sum_power += np.abs(distance - measurement_distance)
                sum2_power += (distance - measurement_distance) ** 2
                count_power += 1
                min_power = min(min_power, (distance - measurement_distance))
                max_power = max(max_power, (distance - measurement_distance))

            rms2_power = sum2_power / count_power
            mean2_power = sum_power ** 2 / count_power ** 2
            variance_power = rms2_power - mean2_power
            range_power = max_power - min_power
            #potential_power = np.sqrt(variance_power)
            potential_power = max(15, min(60, np.power(rms2_power, 1.0/2.0)))

            # potential_value = np.abs(range_value)
            # The min value in the next line will limit the size of the colours. Higher will include more data
            # (further away)
            row.append(potential_power)

            if min_all is None or potential_power < min_all:
                min_all = potential_power
            if max_all is None or potential_power > max_all:
                max_all = potential_power

        map_value.append(row)

    print '{} {} {}'.format(label, min_all, max_all)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('jet_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 25
    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contourf(easting, northing, map_value, layers)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_psr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contour(easting, northing, map_value, layers)
    # # plt.plot(coordinates[0][1], coordinates[0][0])
    # # plt.plot(coordinates[1][1], coordinates[1][0])
    # # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # for c in data:
    #     plt.plot(c[0], c[1], 'yo')
    # plt.plot(transmitter[0], transmitter[1], 'ko')
    # # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_psr_map_{}.png'.format(label), bbox_inches=extent)


def ptdoa_map_prep(transmitter_x, transmitter_y, data, easting, northing, color_map='viridis_r'):
    # The location of the transmitter is at x,y.  Calculate the power and time difference.
    distance1 = np.sqrt((transmitter_x - data[0][0]) ** 2 + (transmitter_y - data[0][1]) ** 2)
    distance2 = np.sqrt((transmitter_x - data[1][0]) ** 2 + (transmitter_y - data[1][1]) ** 2)
    power_difference = - 20 * np.log(distance1) + 20 * np.log(distance2)
    time_difference = (distance1 - distance2)
    data[0][2] = power_difference
    data[0][3] = time_difference
    # print 'Location {} {}, distances {:.1f} {:.1f}, differences {:.1f} {:.1f}'.format(x, y, distance1, distance2, power_difference, time_difference)
    ptdoa_map(easting, northing, data, (transmitter_x, transmitter_y), '{:.2f}_{:.2f}'.format(transmitter_x, transmitter_y), color_map)


def artistic_ptdoa_map(transmitter_x, transmitter_y, data, easting, northing, color_map='viridis_r', label='art', draw_lines=True):
    tdoa_data = copy.deepcopy(data)
    pdoa_data = copy.deepcopy(data)
    ptdoa_data = copy.deepcopy(data)

    distance1 = np.sqrt((transmitter_x - data[0][0]) ** 2 + (transmitter_y - data[0][1]) ** 2)
    distance2 = np.sqrt((transmitter_x - data[1][0]) ** 2 + (transmitter_y - data[1][1]) ** 2)
    power_difference = - 20 * np.log(distance1) + 20 * np.log(distance2)
    time_difference = (distance1 - distance2)
    ptdoa_data[0][2] = power_difference
    pdoa_data[0][2] = power_difference
    ptdoa_data[0][3] = time_difference
    tdoa_data[0][2] = time_difference

    pdoa_map_values = pdoa_get_map_value(easting, northing, pdoa_data, 2.5)
    tdoa_map_values = tdoa_get_map_value(easting, northing, tdoa_data)
    ptdoa_map_values = ptdoa_get_map_value(easting, northing, ptdoa_data)

    # fig = plt.figure(figsize=(figure_size,figure_size))
    fig = plt.figure()
    plt.set_cmap('viridis_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 50

    ax1.contourf(easting, northing, ptdoa_map_values, 25)

    if draw_lines:
        plt.set_cmap('binary_r')
        ax1.contour(easting, northing, tdoa_map_values, 25, alpha=.75, linewidths=1)
        plt.set_cmap('binary_r')
        ax1.contour(easting, northing, pdoa_map_values, 25, alpha=.75, linewidths=1)

    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    for c in data:
        plt.plot(c[0], c[1], 'yo')
    plt.plot(transmitter_x, transmitter_y, 'ko')
    fig.savefig('art_ptdoa_map_f_{}.{}.{}.{}.png'.format(label, transmitter_x, transmitter_y, draw_lines), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

def gnss_psr_get_map_value(easting, northing, satellites, receiver, label, min_value=15, max_value=60):
    min_all = None
    max_all = None

    map_value = []
    for n in northing:
        row = []
        for e in easting:
            sum_power = 0
            sum2_power = 0
            count_power = 0
            min_power = 999999
            max_power = 0
            for s in satellites:
                distance = distance_function([e, n], s)
                measurement_distance = distance_function(receiver, s)
                sum_power += np.abs(distance - measurement_distance)
                sum2_power += (distance - measurement_distance) ** 2
                count_power += 1
                min_power = min(min_power, (distance - measurement_distance))
                max_power = max(max_power, (distance - measurement_distance))

            rms2_power = sum2_power / count_power
            mean2_power = sum_power ** 2 / count_power ** 2
            variance_power = rms2_power - mean2_power
            range_power = max_power - min_power
            # potential_power = np.sqrt(variance_power)
            potential_power = max(min_value, min(max_value, np.power(rms2_power, 1.0 / 2.0)))

            # potential_value = np.abs(range_value)
            # The min value in the next line will limit the size of the colours. Higher will include more data
            # (further away)
            row.append(potential_power)

            if min_all is None or potential_power < min_all:
                min_all = potential_power
            if max_all is None or potential_power > max_all:
                max_all = potential_power

        map_value.append(row)

    print '{} {} {}'.format(label, min_all, max_all)
    return map_value

def gnss_psr_map(easting, northing, satellites, receiver, label):
    map_value = gnss_psr_get_map_value(easting, northing, satellites, receiver, label)

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap('jet_r')
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 25
    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contourf(easting, northing, map_value, layers)
    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_psr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)

    fig = plt.figure(figsize=(figure_size,figure_size))
    ax1 = fig.add_subplot(1, 1, 1)
    # ax1.contour(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contour(easting, northing, map_value, layers)
    # # plt.plot(coordinates[0][1], coordinates[0][0])
    # # plt.plot(coordinates[1][1], coordinates[1][0])
    # # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # for c in data:
    #     plt.plot(c[0], c[1], 'yo')
    # plt.plot(transmitter[0], transmitter[1], 'ko')
    # # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('gnss_psr_map_{}.png'.format(label), bbox_inches=extent)


def print_gnss_maps():
    #easting = [i for i in np.linspace(-1, 1, 3)]
    easting = [i for i in np.linspace(-150, 150, 201)]
    #easting = [0]
    northing = [i for i in np.linspace(-150, 150, 201)]
    receiver = [0, 0]

    # angles = [15, 30, 45, 60, 75, 80, 85]
    angles = [15, 30, 45, 60]
    sv_distance = 20000000

    gnss_psr_map(easting, northing, [rotate_degrees((0, sv_distance), 25)], receiver, '{}'.format(0))
    # gnss_psr_adr_map(easting, northing, [(0, sv_distance)], receiver, '{}'.format(0))
    # gnss_adr_map(easting, northing, [(0, sv_distance)], receiver, '{}'.format(0))

    zenith_satellite = rotate_degrees((0, 20000000), 25)
    all_satellites = [ zenith_satellite]


    for a in angles:
        satellites = []
        satellites.append(zenith_satellite)
        sv1 = rotate_degrees(zenith_satellite, a)
        satellites.append(sv1)
        all_satellites.append(sv1)
        sv2 = rotate_degrees(zenith_satellite, -a)
        satellites.append(sv2)
        all_satellites.append(sv2)

        gnss_psr_map(easting, northing, satellites, receiver, '{}'.format(a))
        # gnss_adr_map(easting, northing, satellites, receiver, '{}'.format(a))
        # gnss_psr_adr_map(easting, northing, satellites, receiver, '{}'.format(a))
    gnss_psr_map(easting, northing, all_satellites, receiver, 'all')
    # gnss_adr_map(easting, northing, all_satellites, receiver, 'all')
    # gnss_psr_adr_map(easting, northing, all_satellites, receiver, 'all')


def artistic_gnss_psr_maps(overall_angle, sv_angle, cmap='jet_r'):
    easting = [i for i in np.linspace(-150, 150, 2001)]
    northing = [i for i in np.linspace(-150, 150, 2001)]
    receiver = [0, 0]

    sv_distance = 20000000

    reference_satellite = rotate_degrees((0, sv_distance), overall_angle)
    sv1 = rotate_degrees(reference_satellite, sv_angle)
    sv2 = rotate_degrees(reference_satellite, -sv_angle)

    sv1_map = gnss_psr_get_map_value(easting, northing, [sv1], receiver, 'sv1', min_value=20, max_value=135)
    sv2_map = gnss_psr_get_map_value(easting, northing, [sv2], receiver, 'sv2', min_value=20, max_value=135)
    sv12_map = gnss_psr_get_map_value(easting, northing, [sv1, sv2], receiver, 'sv12')

    label = '{}.{}.{}'.format(cmap, str(overall_angle), str(sv_angle))

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap(cmap)
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 25
    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contourf(easting, northing, sv12_map, layers)

    plt.set_cmap('binary_r')
    ax1.contour(easting, northing, sv1_map, 9, alpha=.75, linewidths=1)
    plt.set_cmap('binary_r')
    ax1.contour(easting, northing, sv2_map, 9, alpha=.75, linewidths=1)

    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('artistic_gnss_psr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)


def artistic_gnss_psr_adr_maps(overall_angle, sv_angle, cmap='jet_r'):
    easting = [i for i in np.linspace(-150, 150, 2001)]
    northing = [i for i in np.linspace(-150, 150, 2001)]
    receiver = [0, 0]

    sv_distance = 20000000

    reference_satellite = rotate_degrees((0, sv_distance), overall_angle)
    sv1 = rotate_degrees(reference_satellite, sv_angle)
    sv2 = rotate_degrees(reference_satellite, -sv_angle)

    sv1_map = gnss_psr_get_map_value(easting, northing, [sv1], receiver, 'sv1', min_value=20, max_value=135)
    sv2_map = gnss_psr_get_map_value(easting, northing, [sv2], receiver, 'sv2', min_value=20, max_value=135)
    sv12_map = gnss_psr_adr_get_map_value(easting, northing, [sv1, sv2], receiver, 'sv12', min_value=7, max_value=40)

    label = '{}.{}.{}'.format(cmap, str(overall_angle), str(sv_angle))

    fig = plt.figure(figsize=(figure_size,figure_size))
    plt.set_cmap(cmap)
    ax1 = fig.add_subplot(1, 1, 1)
    layers = 25
    # ax1.contourf(easting, northing, map_value, len(hexagon_colors), colors=hexagon_colors)
    ax1.contourf(easting, northing, sv12_map, layers)

    plt.set_cmap('binary_r')
    ax1.contour(easting, northing, sv1_map, 9, alpha=.75, linewidths=1)
    plt.set_cmap('binary_r')
    ax1.contour(easting, northing, sv2_map, 9, alpha=.75, linewidths=1)

    # plt.plot(coordinates[0][1], coordinates[0][0])
    # plt.plot(coordinates[1][1], coordinates[1][0])
    # plt.plot(coordinates[2][1], coordinates[2][0])
    extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # plt.plot(max_value_lon, max_value_lat, 'ro')
    fig.savefig('artistic_gnss_psr_adr_map_f_{}.png'.format(label), bbox_inches=extent, dpi=savefig_dpi, quality=savefig_quality)


# PSR maps
# savefig_dpi = None
# savefig_quality = None
# figure_size = 12
#
# print_gnss_maps()
# quit()

data = []
data.append([-10, 0, 0, 0])
data.append([10, 0, 0, 0])

#easting = [i for i in np.linspace(-1, 1, 3)]
#easting = [0]
# easting = [i for i in np.linspace(-150, 150, 1001)]
# northing = [i for i in np.linspace(-150, 150, 1001)]

easting = [i for i in np.linspace(-150, 150, 201)]
northing = [i for i in np.linspace(-150, 150, 201)]

# print len(hexagon_colors)

# Uncomment for high quality
# savefig_dpi = 2400
# savefig_quality = 100
# figure_size = 12

# Uncomment for fast processing samples.
savefig_dpi = None
savefig_quality = None
# figure_size = 12

# # Selected tdoa images
# hexagon_colors = create_colors_set1()
# tdoa_map(easting, northing, data, str(0))
# data[0][2] = -6
# tdoa_map(easting, northing, data, str(6))
# data[0][2] = 6
# tdoa_map(easting, northing, data, str(-6))
# plt.clf()
# #

# InsideGNSS Webinar plots
data = []
data.append([110, 0, 0, 0])
data.append([130, 0, 0, 0])

locations = [-120, -100, -60, 0, 60, 100, 120]

for x in locations:
    for y in locations:
        artistic_ptdoa_map(x, y, data, easting, northing, draw_lines=True )
        plt.clf()
        artistic_ptdoa_map(x, y, data, easting, northing, draw_lines=False)
        plt.clf()
# # plt.clf()
# # artistic_ptdoa_map(-50, -25, data, easting, northing )
# # plt.clf()
# artistic_ptdoa_map(-35, -35, data, easting, northing )
# plt.clf()
# artistic_ptdoa_map(0, -25, data, easting, northing )
# plt.clf()
quit()

scale = 1.5
data = []
# data.append([-10 * scale, 0 * scale, 0, 0])
# data.append([5 * scale, 8.66 * scale, 0, 0])
# data.append([5 * scale, -8.66 * scale, 0, 0])
data.append([0 * scale, 10 * scale, 0, 0])
data.append([-8.66 * scale, -5 * scale, 0, 0])
data.append([8.66 * scale, -5 * scale, 0, 0])

artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', -50, 0)
transmitter = rotate_degrees([-50, 0], 30)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 45)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 60)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 90)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])

transmitter = rotate_degrees([-50, 0], -30)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -45)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -60)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -90)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', transmitter[0], transmitter[1])


data = []
# data.append([-10 * scale, 0 * scale, 0, 0])
# data.append([5 * scale, 8.66 * scale, 0, 0])
# data.append([5 * scale, -8.66 * scale, 0, 0])
data.append([0 * scale, 0 * scale, 0, 0])
data.append([0 * scale, -10 * scale, 0, 0])
data.append([0 * scale, 10 * scale, 0, 0])

artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', -50, 0)
transmitter = rotate_degrees([-50, 0], 30)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 45)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 60)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], 90)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])

transmitter = rotate_degrees([-50, 0], -30)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -45)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -60)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])
transmitter = rotate_degrees([-50, 0], -90)
artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_line', transmitter[0], transmitter[1])


# artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', -100, 0)

# artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', -25, 0)
# artistic_pdoa_map_with_transmitter(easting, northing, data, 'art_', -15, 0)
quit()

# # Selected pdoa images
data = []
data.append([0, 10, 0, 0])
data.append([0, -10, 0, 0])
#
data[0][2] = 5
pdoa_map(easting, northing, data, str('{}.{}'.format('v1',data[0][2])), lines=False)
pdoa_map(easting, northing, data, str('{}.{}'.format('v1',data[0][2])), lines=True)
data[0][2] = 1
pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=False)
pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=True)

plt.clf()
quit()

#
# data = []
# data.append([0, -90, 0, 0])
# data.append([0, -110, 0, 0])
#
# data[0][2] = 5
# pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=False)
# pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=True)
# data[0][2] = 3
# pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=False)
# pdoa_map(easting, northing, data, str('{}.{}'.format('v2',data[0][2])), lines=True)
#
# plt.clf()
# Selected ptdoa images
# data = []
# data.append([0, -90, 0, 0])
# data.append([0, -110, 0, 0])
#
# # artistic_ptdoa_map(-50, -50, data, easting, northing )
# # plt.clf()
# # artistic_ptdoa_map(-25, -25, data, easting, northing )
# # plt.clf()
# # artistic_ptdoa_map(-50, 0, data, easting, northing )
# # plt.clf()
# # artistic_ptdoa_map(-50, -25, data, easting, northing )
# # plt.clf()
# artistic_ptdoa_map(-35, -35, data, easting, northing )
# plt.clf()
# artistic_ptdoa_map(0, -25, data, easting, northing )
# plt.clf()


# Experimenting with different placements.
data = []
data.append([90, -10, 0, 0])
data.append([90, 10, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.10')
plt.clf()
data = []
data.append([90, -35, 0, 0])
data.append([90, -15, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.35' )
plt.clf()
data = []
data.append([90, -60, 0, 0])
data.append([90, -40, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.60' )
plt.clf()
data = []
data.append([90, -110, 0, 0])
data.append([90, -90, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.90' )
plt.clf()

# Spread out Rx
data = []
data.append([90, -7.5, 0, 0])
data.append([90, 7.5, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.s7.5')
plt.clf()
data = []
data.append([90, -5, 0, 0])
data.append([90, 5, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.s5')
plt.clf()
data = []
data.append([90, -3, 0, 0])
data.append([90, 3, 0, 0])
artistic_ptdoa_map(0, 0, data, easting, northing, label='art.s3')
plt.clf()

quit()

data = []
data.append([0, 10, 0, 0])
data.append([0, -10, 0, 0])
ptdoa_map_prep(-60, 0, data, easting, northing, 'viridis_r' )
ptdoa_map_prep(-60, -20, data, easting, northing, 'viridis_r' )
plt.clf()

# # Proposed GNSS plots.
overall = 35
artistic_gnss_psr_adr_maps(overall, 20, cmap='copper_r')
plt.clf()
artistic_gnss_psr_maps(overall, 20, cmap='copper_r')
plt.clf()
artistic_gnss_psr_adr_maps(overall, 20, cmap='hot_r')
plt.clf()
artistic_gnss_psr_maps(overall, 20, cmap='hot_r')
plt.clf()
artistic_gnss_psr_adr_maps(overall, 20, cmap='jet_r')
plt.clf()
artistic_gnss_psr_maps(overall, 20, cmap='jet_r')
plt.clf()
artistic_gnss_psr_adr_maps(overall, 20, cmap='gray_r')
plt.clf()
artistic_gnss_psr_maps(overall, 20, cmap='gray_r')
plt.clf()

# artistic_gnss_psr_adr_maps(overall, 25)
# artistic_gnss_psr_adr_maps(overall, 35)
# artistic_gnss_psr_adr_maps(overall, 45)

# artistic_gnss_psr_maps(overall, 20)
# artistic_gnss_psr_maps(overall, 25)
# artistic_gnss_psr_maps(overall, 35)
# artistic_gnss_psr_maps(overall, 45)

# overall = -10
# artistic_gnss_psr_maps(overall, 20)
# artistic_gnss_psr_maps(overall, 25)
# artistic_gnss_psr_maps(overall, 35)
# artistic_gnss_psr_maps(overall, 45)

quit()

# savefig_dpi = None
# savefig_quality = None
# figure_size = 12




#
# for power in xrange(0, 22, 2):
#     data[0][2] = -power
#     tdoa_map(easting, northing, data, str(power))


# for power in xrange(0, 12, 1):
#     data[0][2] = power
#     pdoa_map(easting, northing, data, str(power))


# hexagon_colors = create_colors_set3()
color_map = 'ocean_r'
data = []
data.append([0, 90, 0, 0])
data.append([0, 110, 0, 0])
ptdoa_map_prep(0, -45, data, easting, northing, color_map )
ptdoa_map_prep(-80, 60, data, easting, northing, color_map )

# hexagon_colors = create_colors_set2()
data = []
data.append([0, 10, 0, 0])
data.append([0, -10, 0, 0])
ptdoa_map_prep(-60, 0, data, easting, northing, color_map )
ptdoa_map_prep(-60, -20, data, easting, northing, color_map )
quit()


print len(hexagon_colors)

data = []
data.append([0, 90, 0, 0])
data.append([0, 110, 0, 0])

ptdoa_map_prep(0, 75, data, easting, northing )

data = []
data.append([0, 80, 0, 0])
data.append([0, 130, 0, 0])
ptdoa_map_prep(-50, 30, data, easting, northing )
ptdoa_map_prep(0, 30, data, easting, northing )
ptdoa_map_prep(-80, 60, data, easting, northing )


data = []
data.append([0, 70, 0, 0])
data.append([0, 90, 0, 0])
for x in np.linspace(-100, 0, 6):
    for y in np.linspace(-100, 100, 11):
        ptdoa_map_prep(x, y, data, easting, northing)
