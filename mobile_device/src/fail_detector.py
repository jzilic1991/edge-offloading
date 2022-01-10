import numpy as np


class FailureDetector (object):

    @staticmethod
    def eval_fail_event (off_sites, ode_type):
        for site in off_sites:
            avail_prob = 1 - site.get_actual_fail_prob()
            sample = np.random.choice (2, 1, p = (avail_prob, 1 - avail_prob))[0]
            site.update_fail_event (sample)

        return off_sites
