import re
import math
import matplotlib.pyplot as plt
import numpy as np
import operator
import datetime
import pandas as pd


MDP_SVR_STR = 'MDP-SVR'
EFPO_STR = 'EFPO'


def plot_r2_nrmse(r2_dict, nrmse_dict):
    r2_list = list()
    for key, value in r2_dict.items():
        r2_list.append(value)

    r2_list = sorted(r2_list, key = lambda tup: tup[0])

    training_sample_sizes = list()
    r2_scores = list()

    for value in r2_list:
        training_sample_sizes.append(value[0])
        r2_scores.append(value[1])

    nrmse_list = list()
    for key, value in nrmse_dict.items():
        nrmse_list.append(value)

    nrmse_list = sorted(nrmse_list, key = lambda tup: tup[0])
    nrmse_scores = list()

    for value in nrmse_list:
        nrmse_scores.append(value[1])

    plt.rcParams.update({'font.size': 16})
    fig, ax1 = plt.subplots()
    #ax1 = fig.add_axes([0.1, 0.1, 0.6, 0.75])

    ax1.set_xlabel('Training sample sizes', fontsize = 16)
    ax1.set_ylabel('R2 (%)', color = 'black', fontsize = 16)
    ax1.set_ylim([min(r2_scores) - 5, 100])
    ax1.scatter(training_sample_sizes, r2_scores, marker = 'o', color = 'black', label = 'R2')
    ax1.tick_params(axis = 'y', labelcolor = 'black')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    #ax2 = fig.add_axes([0.1, 0.1, 0.6, 0.75])

    ax2.set_ylabel('NRMSE (%)', color = 'blue', fontsize = 16)  # we already handled the x-label with ax1
    ax2.scatter(training_sample_sizes, nrmse_scores, marker = '+', color = 'blue', label = 'NRMSE')
    ax2.tick_params(axis = 'y', labelcolor = 'blue')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    #ax1.legend(h1 + h2, l1 + l2, framealpha = 1, frameon = True)
    ax1.legend()
    ax2.legend()
    plt.show()


def parse_r2_nrmse_svr_data():
    r2_dict = dict()
    nrmse_dict = dict()
    key = None
    train_sample_size = 0

    ec_node_candidate_list = [(19, 1), (19, 11), (19, 4), (19, 8), (20, 41)]
    ed_node_candidate_list = [(1, 0), (5, 158), (5, 165), (5, 243), (5, 48), (7, 1), (7, 154), (7, 242), (7, 32)]
    er_node_candidate_list = [(3, 0), (16, 80), (4, 55), (4, 1), (4, 3)]
    cd_node_candidate_list = [(22, 0)]

    ed_data_stats = data_storage.get_ed_data_stats()
    ec_data_stats = data_storage.get_ec_data_stats()
    er_data_stats = data_storage.get_er_data_stats()
    cloud_data_stats = data_storage.get_cd_data_stats()

    file_reader = open('svr_log.txt', 'r')
    for line in file_reader:
        #print(line)
        matched = re.search("Node candidate: \((\d+, \d+)\)", line)
        if matched:
            key = matched.group(1)
            continue

        matched = re.search("Training sample size: (\d+)", line)
        if matched:
            train_sample_size = int(matched.group(1))
            continue

        matched = re.search("R2: (\d+\.\d+)", line)
        if matched:
            r2_dict[key] = (train_sample_size, float(matched.group(1)) * 100)
            continue

        matched = re.search("NRMSE: (\d+\.\d+)", line)
        if matched:
            nrmse_dict[key] = (train_sample_size, float(matched.group(1)) * 100)
            continue

    # plot_r2_score(r2_dict)
    # plot_nrmse(nrmse_dict)
    plot_r2_nrmse(r2_dict, nrmse_dict)


def plot_r2_score(r2_dict):
    r2_list = list()
    for key, value in r2_dict.items():
        r2_list.append(value)

    r2_list = sorted(r2_list, key = lambda tup: tup[0])

    training_sample_sizes = list()
    r2_scores = list()

    for value in r2_list:
        training_sample_sizes.append(value[0])
        r2_scores.append(value[1])

    plt.rcParams.update({'font.size': 16})
    plt.scatter(training_sample_sizes, r2_scores)
    plt.xlabel('Training sample sizes')
    plt.ylabel('R2 scores (%)')
    plt.title('Good-of-fitness of the SVR availability prediction')
    plt.legend()
    plt.show()


def plot_nrmse(nrmse_dict):
    nrmse_list = list()
    for key, value in nrmse_dict.items():
        nrmse_list.append(value)

    nrmse_list = sorted(nrmse_list, key = lambda tup: tup[0])

    training_sample_sizes = list()
    nrmse_scores = list()

    for value in nrmse_list:
        training_sample_sizes.append(value[0])
        nrmse_scores.append(value[1])

    plt.rcParams.update({'font.size': 16})
    plt.scatter(training_sample_sizes, nrmse_scores)
    plt.xlabel('Training sample sizes')
    plt.ylabel('NRMSE scores (%)')
    plt.title('Error accuracy of the SVR availability prediction')
    plt.legend()
    plt.show()


def stacked_bar(data, series_labels, color_labels, category_labels = None, 
                show_values = False, value_format = "{}", y_label = None, 
                grid = False, reverse = False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will 
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis = 1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        axes.append(plt.bar(ind, row_data, bottom = cum_size, color = color_labels[i],
                            label = series_labels[i]))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend(bbox_to_anchor = (1.04,1), loc = "upper left", prop = {'size': 14}, framealpha = 1, frameon = True)

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                if h != 0.0:
                    plt.text(bar.get_x() + w/2, bar.get_y() + h/2, 
                             value_format.format(h), ha = "center", 
                             va = "center")


def plot_offloading_distribution(offload_dist_dict):
    plt.rcParams.update({'font.size': 16})
    category_labels = ['EFPO', 'MDP-SVR']

    for i in range(5):
        data = list()

        if i != 1:
            data.append([offload_dist_dict[EFPO_STR][i][0], offload_dist_dict[MDP_SVR_STR][i][0]])
            data.append([offload_dist_dict[EFPO_STR][i][1], offload_dist_dict[MDP_SVR_STR][i][1]])
            data.append([offload_dist_dict[EFPO_STR][i][2], offload_dist_dict[MDP_SVR_STR][i][2]])
            data.append([offload_dist_dict[EFPO_STR][i][3], offload_dist_dict[MDP_SVR_STR][i][3]])
            data.append([offload_dist_dict[EFPO_STR][i][4], offload_dist_dict[MDP_SVR_STR][i][4]])
            series_labels = ['MD', 'Cloud', 'ED', 'ER', 'EC']
            color_labels = ['y', 'lightyellow', 'pink', 'mediumslateblue', 'slateblue']
        else:
            data.append([offload_dist_dict[EFPO_STR][i][0], offload_dist_dict[MDP_SVR_STR][i][0]])
            data.append([offload_dist_dict[EFPO_STR][i][1], offload_dist_dict[MDP_SVR_STR][i][3]])
            data.append([offload_dist_dict[EFPO_STR][i][2], offload_dist_dict[MDP_SVR_STR][i][2]])
            data.append([offload_dist_dict[EFPO_STR][i][3], offload_dist_dict[MDP_SVR_STR][i][1]])
            data.append([offload_dist_dict[EFPO_STR][i][4], offload_dist_dict[MDP_SVR_STR][i][4]])
            series_labels = ['MD', 'ER', 'ED', 'Cloud', 'EC']
            color_labels = ['y', 'mediumslateblue', 'pink',  'lightyellow', 'slateblue']

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])

        stacked_bar(data,
                    series_labels,
                    color_labels,
                    category_labels = category_labels, 
                    show_values = True, 
                    value_format = "{:.2f}",
                    y_label = "Quantity (units)") 

        ax.set_xlabel('Offloading decision engines', fontsize = 16)
        ax.set_ylabel('Distribution (%)', fontsize = 16)
        ax.set_ylim(0, 102)
        plt.show()


def print_time_confidence_intervals(resp_time_var_dict):
    for i in range(5):
        print(str(i + 1) + '. dataset configuration (response time):')
        print('MDP-SVR: +/- ' + str(compute_yerr(resp_time_var_dict[MDP_SVR_STR][i])))
        print('EFPO: +/- ' + str(compute_yerr(resp_time_var_dict[EFPO_STR][i])))
        print('')


def print_battery_confidence_intervals(battery_consum_var_dict):
    for i in range(5):
        print(str(i + 1) + '. dataset configuration (battery consumption):')
        print('MDP-SVR: +/- ' + str(compute_yerr(battery_consum_var_dict[MDP_SVR_STR][i])))
        print('EFPO: +/- ' + str(compute_yerr(battery_consum_var_dict[EFPO_STR][i])))
        print('')


def print_failure_rate_intervals(failure_rates_var_dict):
    for i in range(5):
        print(str(i + 1) + '. dataset configuration (failure rates):')
        print('MDP-SVR: +/- ' + str(compute_yerr(failure_rates_var_dict[MDP_SVR_STR][i])))
        print('EFPO: +/- ' + str(compute_yerr(failure_rates_var_dict[EFPO_STR][i])))
        print('')


def compute_yerr(data_var):
    return 1.96 * (math.sqrt(data_var)) / math.sqrt(10000)


def plot_response_time_graph(data_mean, i):
    x = np.arange(i)

    plt.rcParams.update({'font.size': 14})
    ax = plt.subplot(111)
    ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'b', align = 'center', label = 'MDP-SVR')
    ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'pink', align = 'center', label = 'EFPO')

    plt.xlabel('Dataset configurations')
    plt.ylabel('Response time (seconds)')
    #plt.title('Average response time')
    plt.xticks(x, ['DS1', 'DS2', 'DS3', 'DS4', 'DS5'], fontsize = 14)
    plt.legend()
    plt.show()


def plot_battery_consumption_graph(data_mean, i):
    x = np.arange(i)

    plt.rcParams.update({'font.size': 14})
    ax = plt.subplot(111)
    ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'b', align = 'center', label = 'MDP-SVR')
    ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'pink', align = 'center', label = 'EFPO')
    ax.set_ylim([96,100])

    plt.xlabel('Dataset configurations')
    plt.ylabel('Battery lifetime (percentage)')
    #plt.title('Average battery lifetime')
    plt.xticks(x, ['DS1', 'DS2', 'DS3', 'DS4', 'DS5'], fontsize = 14)
    plt.legend()
    plt.show()


def plot_nw_bw_graph(data_mean, i):
    x = np.arange(i)

    plt.rcParams.update({'font.size': 14})
    ax = plt.subplot(111)
    ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'g', align = 'center', label = 'MDP-SVR')
    ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'r', align = 'center', label = 'EFPO')

    plt.xlabel('Dataset configurations')
    plt.ylabel('Network bandwidth consumption (kbps)')
    plt.title('Average network bandwidth consumption')
    plt.xticks(x, ['DC1', 'DC2', 'DC3', 'DC4', 'DC5'], fontsize = 14)
    plt.legend()
    plt.show()


def plot_service_avail_graph(data_mean, i):
    x = np.arange(i)

    plt.rcParams.update({'font.size': 14})
    fig = plt.figure()
    ax = plt.subplot(111)
    # ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'b', align = 'center', label = 'MDP-SVR')
    ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'pink', align = 'center', label = 'EFPO')
    ax.set_ylim([95.5,100])

    plt.xlabel('Dataset configurations')
    plt.ylabel('Service availability (%)')
    #plt.title('Average service availability')
    plt.xticks(x, ['DS1', 'DS2', 'DS3', 'DS4', 'DS5'], fontsize = 14)
    # plt.legend(bbox_to_anchor = (1.04,1), loc = "upper left", prop = {'size': 14}, framealpha = 1, frameon = True)
    plt.show()


def plot_failure_rates(data_mean, i):
    x = np.arange(i)

    plt.rcParams.update({'font.size': 14})
    ax = plt.subplot(111)
    ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'g', align = 'center', label = 'MDP-SVR')
    ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'r', align = 'center', label = 'EFPO')

    plt.xlabel('Dataset configurations')
    plt.ylabel('Offloading failure rates (%)')
    plt.title('Offloading failure rates over all application executions')
    plt.xticks(x, ['DC1', 'DC2', 'DC3', 'DC4', 'DC5'], fontsize = 14)
    plt.legend()
    plt.show()


def plot_training_times(training_sample_size, training_times):
    plt.rcParams.update({'font.size': 16})
    plt.scatter(training_sample_size, training_times, label = 'Time')
    plt.xlabel('Training sample sizes')
    plt.ylabel('Training time (seconds)')
    # plt.title('SVR training time')
    plt.legend()
    plt.show()


def plot_test_times(test_sample_size, test_times):
    plt.rcParams.update({'font.size': 16})
    plt.scatter(test_sample_size, test_times)
    plt.xlabel('Test sample sizes')
    plt.ylabel('Test time (seconds)')
    plt.title('SVR prediction time')
    plt.legend()
    plt.show()


def plot_svr_overall_time(sample_size, overall_times):
    plt.rcParams.update({'font.size': 16})
    plt.scatter(sample_size, overall_times, label = 'Time')
    plt.xlabel('Sample sizes')
    plt.ylabel('Time consumption')
    # plt.title('Overall MDP-SVR time consumption')
    plt.legend()
    plt.show()


def parse_simulation_log():
    file_reader = open('logs/simulation2.txt', 'r+')
    mdp_svr_flag = False
    efpo_flag = False
    flags = [False, False]
    i = 0

    resp_time_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    battery_consum_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    resp_time_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    battery_consum_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    service_avail_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    service_avail_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    off_rel_dict = {MDP_SVR_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
        EFPO_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]}
    num_of_off_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    fail_freq_rel = {MDP_SVR_STR: [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)], \
        EFPO_STR: [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)]}
    num_of_fail = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    off_fail_freq_rel = {MDP_SVR_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
        EFPO_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]}
    num_of_off_fail = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    failure_rate_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    failure_rate_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0]}
    offload_dist_dict = {MDP_SVR_STR: [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], 
        EFPO_STR: [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]}

    for line in file_reader:
        # print(line)
        matched = re.search("(#+) (MDP_SVR OFFLOADING RESULT SUMMARY) (#+)", line)
        if matched:
            mdp_svr_flag = True
            efpo_flag = False
            flags[0] = True
            continue

        matched = re.search("(#+) (EFPO OFFLOADING RESULT SUMMARY) (#+)", line)
        if matched:
            mdp_svr_flag = False
            efpo_flag = True
            flags[1] = True
            continue

        matched = re.search("Time mean: (\d+\.\d+) s", line)
        if matched:
            if mdp_svr_flag:
                resp_time_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                resp_time_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Time variance: (\d+\.\d+) s", line)
        if matched:
            if mdp_svr_flag:
                resp_time_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                resp_time_var_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Battery lifetime mean: (\d+\.\d+)%", line)
        if matched:
            if mdp_svr_flag:
                battery_consum_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                battery_consum_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Battery lifetime variance: (\d+\.\d+) J", line)
        if matched:
            if mdp_svr_flag:
                battery_consum_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                bettery_consum_var_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Network bandwidth consumption mean: (\d+\.\d+) kbps", line)
        if matched:
            if mdp_svr_flag:
                nw_bw_consum_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                nw_bw_consum_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Network bandwidth consumption variance: (\d+\.\d+) kbps", line)
        if matched:
            if mdp_svr_flag:
                nw_bw_consum_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                nw_bw_consum_var_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Service availability rate mean: (\d+\.\d+)%", line)
        if matched:
            if mdp_svr_flag:
                service_avail_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                service_avail_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Service availability rate variance: (\d+\.\d+)%", line)
        if matched:
            if mdp_svr_flag:
                service_avail_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

            elif efpo_flag:
                service_avail_var_dict[EFPO_STR][i] = float(matched.group(1))

        matched = re.search("Offloading distribution relative: {'MOBILE_DEVICE': (\d+\.\d+), 'EDGE_DATABASE_SERVER_A': (\d+\.\d+), 'EDGE_COMPUTATIONAL_SERVER_A': (\d+\.\d+), 'EDGE_REGULAR_SERVER_A': (\d+\.\d+), 'CLOUD_DATA_CENTER_A': (\d+\.\d+)}", line)
        if matched:
            if mdp_svr_flag:
                off_rel_dict[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

            elif efpo_flag:
                off_rel_dict[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

        matched = re.search("Num of offloadings: (\d+)", line)
        if matched:
            if mdp_svr_flag:
                num_of_off_dict[MDP_SVR_STR][i] = int(matched.group(1))

            elif efpo_flag:
                num_of_off_dict[EFPO_STR][i] = int(matched.group(1))

        matched = re.search("Relative failure frequency occurence: EDGE_DATABASE_SERVER_A: (\d+\.\d+), EDGE_COMPUTATIONAL_SERVER_A: (\d+\.\d+), EDGE_REGULAR_SERVER_A: (\d+\.\d+), CLOUD_DATA_CENTER_A: (\d+\.\d+)", line)
        if matched:
            if mdp_svr_flag:
                fail_freq_rel[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)))

            elif efpo_flag:
                fail_freq_rel[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)))

        matched = re.search("Num of failures: (\d+)", line)
        if matched:
            if mdp_svr_flag:
                num_of_fail[MDP_SVR_STR][i] = int(matched.group(1))

            elif efpo_flag:
                num_of_fail[EFPO_STR][i] = int(matched.group(1))

        matched = re.search("Offloading failure frequency relative: {'MOBILE_DEVICE': (\d+\.\d+), 'EDGE_DATABASE_SERVER_A': (\d+\.\d+), 'EDGE_COMPUTATIONAL_SERVER_A': (\d+\.\d+), 'EDGE_REGULAR_SERVER_A': (\d+\.\d+), 'CLOUD_DATA_CENTER_A': (\d+\.\d+)}", line)
        if matched:
            if mdp_svr_flag:
                off_fail_freq_rel[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

            elif efpo_flag:
                off_fail_freq_rel[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), \
                        float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

        matched = re.search("Num of offloading failures: (\d+)", line)
        if matched:
            if mdp_svr_flag:
                num_of_off_fail[MDP_SVR_STR][i] = int(matched.group(1))

            elif efpo_flag:
                num_of_off_fail[EFPO_STR][i] = int(matched.group(1))
            
            if flags[0] and flags[1]:
                flags[0] = False
                flags[1] = False
                i += 1

        matched = re.search("Offloading failure rate mean: (\d+\.\d+) failures", line)
        if matched:
            if mdp_svr_flag:
                failure_rate_dict[MDP_SVR_STR][i] = float(matched.group(1)) / 1000 * 100

            elif efpo_flag:
                failure_rate_dict[EFPO_STR][i] = float(matched.group(1)) / 1000 * 100

        matched = re.search("Offloading failure rate variance: (\d+\.\d+) failures", line)
        if matched:
            if mdp_svr_flag:
                failure_rate_var_dict[MDP_SVR_STR][i] = float(matched.group(1)) / 1000 * 100

            elif efpo_flag:
                failure_rate_var_dict[EFPO_STR][i] = float(matched.group(1)) / 1000 * 100

        matched = re.search("Offloading distribution relative: {'MOBILE_DEVICE': (\d+\.\d+), 'EDGE_DATABASE_SERVER_A': (\d+\.\d+), " + \
            "'EDGE_COMPUTATIONAL_SERVER_A': (\d+\.\d+), 'EDGE_REGULAR_SERVER_A': (\d+\.\d+), 'CLOUD_DATA_CENTER_A': (\d+\.\d+)}", line)
    
        if matched:
            if mdp_svr_flag:
                offload_dist_dict[MDP_SVR_STR][i][0] = float(matched.group(1))
                offload_dist_dict[MDP_SVR_STR][i][1] = float(matched.group(5))
                offload_dist_dict[MDP_SVR_STR][i][2] = float(matched.group(2))
                offload_dist_dict[MDP_SVR_STR][i][3] = float(matched.group(4))
                offload_dist_dict[MDP_SVR_STR][i][4] = float(matched.group(3))

            elif efpo_flag:
                offload_dist_dict[EFPO_STR][i][0] = float(matched.group(1))
                offload_dist_dict[EFPO_STR][i][1] = float(matched.group(5))
                offload_dist_dict[EFPO_STR][i][2] = float(matched.group(2))
                offload_dist_dict[EFPO_STR][i][3] = float(matched.group(4))
                offload_dist_dict[EFPO_STR][i][4] = float(matched.group(3))

    file_reader.close()

    return (resp_time_dict, battery_consum_dict, offload_dist_dict, service_avail_dict, i)


def plot_results (resp_time_dict, battery_consum_dict, offload_dist_dict, service_avail_dict, i):
    plot_response_time_graph(resp_time_dict, i)
    plot_battery_consumption_graph(battery_consum_dict, i)
    # plot_failure_rates(failure_rate_dict, i)
    plot_offloading_distribution(offload_dist_dict)
    # plot_nw_bw_graph(nw_bw_consum_dict, i)
    plot_service_avail_graph(service_avail_dict, i)


def parse_inference_logs():
    # print_time_confidence_intervals(resp_time_var_dict)
    # print_battery_confidence_intervals(battery_consum_var_dict)
    # print_failure_rate_intervals(failure_rate_var_dict)

    file_reader = open('logs/svr_log.txt', 'r')
    node_candidate_svr_train_dict = {}
    node_candidate_train_sample_size_dict = {}
    node_candidate_svr_test_dict = {}
    node_candidate_test_sample_size_dict = {}
    mdp_inference_time_list = list()
    current_key = None

    for line in file_reader:
        # print(line)
        matched = re.search("Node candidate: (\(\d+\, \d+\))", line)
        if matched:
            current_key = matched.group(1)
            if not (matched.group(1) in node_candidate_svr_train_dict):
                node_candidate_svr_train_dict[matched.group(1)] = list()

            if not (matched.group(1) in node_candidate_svr_test_dict):
                node_candidate_svr_test_dict[matched.group(1)] = list()

        matched = re.search("Training CPU time \(.+\): (\d+\.\d+)s", line)
        if matched:
            node_candidate_svr_train_dict[current_key].append(float(matched.group(1)))

        matched = re.search("Training sample size: (\d+)", line)
        if matched:
            node_candidate_train_sample_size_dict[current_key] = int(matched.group(1))

        matched = re.search("Prediction CPU time \(.+\): (\d+\.\d+)s", line)
        if matched:
            node_candidate_svr_test_dict[current_key].append(float(matched.group(1)))

        matched = re.search("Test sample size: (\d+)", line)
        if matched:
            node_candidate_test_sample_size_dict[current_key] = int(matched.group(1))

        matched = re.search("MDP inference time: (\d+)", line)
        if matched:
            mdp_inference_time_list.append(float(matched.group(1)))

    training_time_list = list()
    test_time_list = list()
    overall_time_list = list()

    for key, value in node_candidate_svr_train_dict.items():
        # print('Min time for ' + key + ' is ' + str(min(value)) + ' s')
        # print('Max time for ' + key + ' is ' + str(max(value)) + ' s')
        # print('Mean time for ' + key + ' is ' + str(round(sum(value) / len(value), 4)) + 's')
        # print('Training sample size: ' + str(node_candidate_train_sample_size_dict[key]))
        # print('\n')
        training_time_list.append((node_candidate_train_sample_size_dict[key], round(sum(value) / len(value), 4)))

    for key, value in node_candidate_svr_test_dict.items():
        # print('Min time for ' + key + ' is ' + str(min(value)) + 's')
        # print('Max time for ' + key + ' is ' + str(max(value)) + 's')
        # print('Mean time for ' + key + ' is ' + str(round(sum(value) / len(value), 4)) + ' s')
        # print('Test sample size: ' + str(node_candidate_test_sample_size_dict[key]))
        # print('\n')
        test_time_list.append((node_candidate_test_sample_size_dict[key], round(sum(value) / len(value), 4)))

    print('Min time for MDP inference is ' + str(min(mdp_inference_time_list)) + 's')
    print('Max time for MDP inference is ' + str(max(mdp_inference_time_list)) + 's')
    print('Mean time for MDP inference is ' + str(round(sum(mdp_inference_time_list) / len(mdp_inference_time_list), 4)) + ' s') 

    for key, value in node_candidate_svr_train_dict.items():
        overall_time_list.append((node_candidate_train_sample_size_dict[key] + node_candidate_test_sample_size_dict[key],
            (sum(node_candidate_svr_train_dict[key]) + sum(node_candidate_svr_test_dict[key])) / len(value)))

    training_time_list = sorted(training_time_list, key = lambda tup: tup[0])
    test_time_list = sorted(test_time_list, key = lambda tup: tup[0])
    overall_time_list = sorted(overall_time_list, key = lambda tup: tup[0])

    training_sample_size = list()
    training_times = list()

    test_sample_size = list()
    test_times = list()

    overall_sample_size = list()
    overall_times = list()

    for ele in training_time_list:
        training_sample_size.append(ele[0]) 
        training_times.append(ele[1])

    for ele in test_time_list:
        test_sample_size.append(ele[0]) 
        test_times.append(ele[1])

    for ele in overall_time_list:
        overall_sample_size.append(ele[0]) 
        overall_times.append(ele[1])

    file_reader.close()

    return (training_sample_size, training_times, test_samples_size, test_times, overall_sample_size, overall_times)


def plot_inference (training_sample_size, training_times, test_samples_size,\
        test_times, overall_sample_size, overall_times):
    plot_training_times(training_sample_size, training_times)
    plot_test_times(test_sample_size, test_times)
    plot_svr_overall_time(overall_sample_size, overall_times)
    parse_r2_nrmse_svr_data()


def main():
    (resp_time_dict, battery_consum_dict, offload_dist_dict, service_avail_dict, i) = parse_simulation_log()
    plot_results(resp_time_dict, battery_consum_dict, offload_dist_dict, service_avail_dict, i)

    # (training_sample_size, training_times, test_samples_size, test_times, \
    #        overall_sample_size, overall_times) = parse_inference_logs()
    # plot_inference(training_sample_size, training_times, test_samples_size, test_times,\
    #        overall_sample_size, overall_times)


if __name__ == "__main__":
    main()
