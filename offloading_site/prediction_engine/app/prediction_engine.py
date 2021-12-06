import sys
import numpy as np
import time
import matplotlib.pyplot as plt
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

        print ('Prediction engine created!', file = sys.stdout)
    

    def train(cls, dataset):
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


    def estimate(cls):
        cls._svr.fit (cls._x_train, cls._y_train)
        cls._predicted = cls._svr.predict (cls._x_test)
        cls.__print_results (cls._y_test, cls._predicted, 'TEST')
        # cls.__plot_results (cls._x_test, cls._y_test, cls._predicted, 'Test result')
        return cls._predicted.tolist()


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
