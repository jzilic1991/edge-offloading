import re
import sys
import numpy as np
import time
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR

from metrics import Metrics


class PredictionEngine:

    def __init__(self):
        self._regressor_type = "rbf"
        self._svr = SVR (kernel = self._regressor_type)
        self._epsilon = 0
        self._C = 0
        self._random_state = 5725
        self._x_train = None
        self._x_test = None
        self._y_train = None
        self._y_test = None
        self._predicted = None
        self._node_candidate = ''

        print ('Prediction engine created!', file = sys.stdout)
    

    def train_and_estimate (cls, node_candidate, dataset):
        print ('Train and estimate node candidate : ' + node_candidate, file = sys.stdout)
        cls._node_candidate = node_candidate
        cls.__separate_dataset(dataset)

        cls._svr.fit(cls._x_train, cls._y_train)
        predicted = cls._svr.predict(cls._x_train)

        cls._C = cls.__compute_C(cls._y_train)
        res_error = np.subtract(cls._y_train, predicted)
        cls._epsilon = cls.__compute_epsilon(res_error)
        cls._svr = SVR(kernel = cls._regressor_type, C = cls._C, epsilon = cls._epsilon)

        cls._svr.fit(cls._x_train, cls._y_train)
        predicted = cls._svr.predict(cls._x_train)
        cls.__print_results (cls._y_train, predicted, 'TRAINING')
        # cls.__plot_results (cls._x_train, cls._y_train, predicted, 'Training result')
        
        cls._predicted = cls._svr.predict (cls._x_test)
        cls.__print_results (cls._y_test, cls._predicted, 'TEST')
        cls.__cache_avail_data (cls._node_candidate, cls._y_test, cls._predicted)
        # cls.__plot_results (cls._x_test, cls._y_test, cls._predicted, 'Test result')
        
        return cls._predicted.tolist()

    
    def check_cached_files (cls, node_candidate):
        filepath_actual = 'actual_data/' + node_candidate + '.txt'
        filepath_predicted = 'predicted_data/' + node_candidate + '.txt'

        if Path(filepath_actual).exists() and \
                Path(filepath_predicted).exists():
            print ('Availability files do exist!', file = sys.stdout)
            return cls.__read_cached_files (filepath_actual, filepath_predicted)

        print ('Avaialbility files do not exist and returning empty data!', file = sys.stdout)
        return {'actual': [], 'predicted': []}


    def __cache_avail_data (cls, node_candidate, actual_data, predicted_data):
        filepath_actual = 'actual_data/' + node_candidate + '.txt'
        filepath_predicted = 'predicted_data/' + node_candidate + '.txt'
        
        actual_data = cls.__write_avail_file (filepath_actual, actual_data)
        predicted_data = cls.__write_avail_file (filepath_predicted, predicted_data)


    def __write_avail_file (cls, filepath, data):
        print ('Writing availaiblity file (' + filepath + ')', file = sys.stdout)
        with open (filepath, 'w') as filewriter:
            for point in data:
                filewriter.write(str(point) + '\n')

            filewriter.close()


    def __read_cached_files (cls, filepath_actual, filepath_predicted):
        actual_data = cls.__read_avail_file (filepath_actual)
        predicted_data = cls.__read_avail_file (filepath_predicted)

        return {'actual': actual_data, 'predicted': predicted_data}


    def __read_avail_file (cls, filepath):
        print ('Reading cached availaiblity file (' + filepath + ')', file = sys.stdout)
        data = list ()

        with open (filepath, 'r') as filereader:
            line = filereader.readline()

            while line:
                if re.search ('\d+.\d+', line):
                    data.append (float (line))
                
                line = filereader.readline()

            filereader.close()
        
        return data


    def __separate_dataset (cls, dataset):
        cls._x_train, cls._x_test, cls._y_train, cls._y_test = \
            train_test_split(range(len(dataset)), dataset, train_size = 0.8, test_size = 0.2, random_state = cls._random_state)
        cls._x_train = np.array(cls._x_train).reshape(-1, 1)
        cls._y_train = np.ravel(cls._y_train, order = 'C')
        cls._x_test = np.array(cls._x_test).reshape(-1, 1)
        cls._y_test = np.ravel(cls._y_test, order = 'C')


    def __print_results (cls, actual, predicted, title):
        print('###### ' + title  + ' REGRESSION RESULTS ######', file = sys.stdout)
        print('NRMSE: ' + str(Metrics.nrmse(actual, predicted)), file = sys.stdout)
        print('RMSE: ' + str(Metrics.rmse(actual, predicted)), file = sys.stdout)
        print('MAE: ' + str(Metrics.mean_absolute_error(actual, predicted)), file = sys.stdout)
        print('R2: ' + str(Metrics.r2_score(actual, predicted)), file = sys.stdout)
        print('Empirical risk: ' + str(Metrics.empirical_risk(actual, predicted, cls._epsilon)), file = sys.stdout)


    def __plot_results(cls, x_data, y_data, y_predicted, title):
        fig, ax = plt.subplots(constrained_layout = True)
        ax.scatter(x_data, y_data, color = 'magenta')
        ax.scatter(x_data, y_predicted, color = 'green')
        ax.set_title(title)
        ax.set_xlabel('Day')
        ax.set_ylabel('Availability (per day)')
        plt.show()

    def __compute_C(cls, data):
        mean_ = np.mean(data)
        std_ = np.std(data)

        if mean_ == 0 or std_ == 0:
            return 1

        return max(abs(mean_ + 3 * std_), abs(mean_ - 3 * std_))
        #return 1


    def __compute_epsilon(cls, data):
        std = np.std(data)
        n = len(data)

        if std == 0 or n == 0:
            return 0.1

        return 0.001
        #return 3 * std * math.sqrt(np.log(n) / n)
