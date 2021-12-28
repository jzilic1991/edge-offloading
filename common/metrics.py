import math
import numpy as np

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score


class Metrics(object):

    @staticmethod
    def nrmse(actual, predicted):
        sum_error = 0

        if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
            actual = np.array((actual,))
            predicted = np.array((predicted,))

        for i in range(len(actual)):
            sum_error += (actual[i] - predicted[i]) ** 2

        mse = sum_error / len(actual)
        rmse = math.sqrt(mse)

        return rmse / actual.mean()


    @staticmethod
    def rmse(actual, predicted):
        sum_error = 0

        if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
            actual = np.array((actual,))
            predicted = np.array((predicted,))

        for i in range(len(actual)):
            sum_error += ((actual[i] - predicted[i]) ** 2)

        mse = sum_error / len(actual)
        return math.sqrt(mse)


    @staticmethod
    def r2_score(actual, predicted):
        if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
            actual = np.array((actual,))
            predicted = np.array((predicted,))

        return r2_score(actual, predicted)


    @staticmethod
    def mean_absolute_error(actual, predicted):
        if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
            actual = np.array((actual,))
            predicted = np.array((predicted,))

        return mean_absolute_error(actual, predicted)


    @staticmethod
    def empirical_risk(actual, predicted, epsilon):
        emp_risk = tuple()

        if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
            actual = np.array((actual,))
            predicted = np.array((predicted,))

        for i in range(len(predicted)):
            if abs(predicted[i] - actual[i]) < epsilon:
                emp_risk += (0,)
            else:
                emp_risk += (abs(predicted[i] - actual[i]) - epsilon,)

        return np.mean(np.array(emp_risk))
