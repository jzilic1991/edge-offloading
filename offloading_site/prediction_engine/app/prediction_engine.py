import sys
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR

from metrics import Metrics


class PredictionEngine:

    def __init__(self):
        self._regressor_type = "rbf"
        self._degree = 0
        self._epsilon = 0
        self._C = 0
        self._random_state = 5725
        self._x_train = None
        self._x_test = None
        self._y_train = None
        self._y_test = None
        self._predicted = None
        self._svr = None

        print ('Prediction engine created!', file = sys.stdout)
    

    def train(cls, dataset):
        cls.__separate_dataset(dataset)

        cls._svr.fit(cls._x_train, cls._y_train)
        predicted = cls._svr.predict(cls._x_train)

        cls._C = cls.__compute_C(cls._y_train)
        res_error = np.subtract(cls._y_train, predicted)
        cls._epsilon = cls.__compute_epsilon(res_error)
        cls._svr = SVR(kernel = cls._regressor_type, degree = cls._degree, C = cls._C, epsilon = cls._epsilon)


    def estimate(cls):
        cls._predicted = cls._svr.predict (cls._x_test)
        cls.__print_results (cls._y_test, cls._predicted)
        return cls._predicted


    def __separate_dataset(cls, dataset):
        cls._x_train, cls._x_test, cls._y_train, cls._y_test = \
            train_test_split(range(len(data)), data, train_size = 0.8, random_state = cls._random_state)
        cls._x_train = np.array(cls._x_train).reshape(-1, 1)
        cls._y_train = np.array(cls._y_train).reshape(-1, 1)
        cls._x_test = np.array(cls._x_test).reshape(-1, 1)
        cls._y_test = np.array(cls._y_test).reshape(-1, 1)


    def __print_results (cls, actual, predicted):
        print('###### REGRESSION RESULTS ######', file = sys.stdout)
        print('NRMSE: ' + str(Metrics.nrmse(actual, predicted)), file = sys.stdout)
        print('RMSE: ' + str(Metrics.rmse(actual, predicted)), file = sys.stdout)
        print('MAE: ' + str(Metrics.mean_absolute_error(actual, predicted)), file = sys.stdout)
        print('R2: ' + str(Metrics.r2_score(actual, predicted)), file = sys.stdout)
        print('Empirical risk: ' + str(Metrics.empirical_risk(actual, predicted, cls._epsilon)), file = sys.stdout)


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
