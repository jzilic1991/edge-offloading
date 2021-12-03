import operator
import datetime

from utilities import OffloadingSiteCode, Uptime


class Dataset:

    def __init__ (self, offloading_site):
    
        self._data = tuple()
        self._plot_title = ''
        self._logs_path = ''
        self._offloading_site = offloading_site
            
        self.__determine_miscellaneous(offloading_site)
    
        self._mtbf = 0  


    def add_item (cls, row):
        row['Prob Started'] = datetime.datetime.strptime(row['Prob Started'], '%m/%d/%Y %H:%M')
        row['Prob Fixed'] = datetime.datetime.strptime(row['Prob Fixed'], '%m/%d/%Y %H:%M')
        cls._data += (row,)


    def get_node_avail_data (cls, system_id, node_num):
        rows = cls.__get_data_rows(system_id, node_num)
        cls._mtbf = cls.__compute_mtbf(rows)
        return cls.__evaluate_failure_data(system_id, node_num)


    def get_offloading_site_code (cls):
        return cls._offloading_site
        

    def __determine_miscellaneous (cls, offloading_site):
        if offloading_site == OffloadingSiteCode.EDGE_REGULAR_SERVER:
            cls._plot_title = 'Edge Regular Server'
            cls._logs_path = 'logs/LANL/regular/'

        elif offloading_site == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
            cls._plot_title = "Edge Computational Server"
            cls._logs_path = 'logs/LANL/computational/'

        elif offloading_site == OffloadingSiteCode.EDGE_DATABASE_SERVER:
            cls._plot_title = "Edge Database Server"
            cls._logs_path = 'logs/LANL/database/'

        elif offloading_site == OffloadingSiteCode.CLOUD_DATA_CENTER:
            cls._plot_title = "Cloud Data Center"
            cls._logs_path = 'logs/LANL/cloud/'
    
        else:
            raise ValueError ("Offloading site code " + str(offloading_site) + " does not exist!")


    def __compute_mtbf (cls, data):
        if len (data) == 0:
            return -1

        total_time = (cls.__get_max_failure_date(data) - cls.__get_min_failure_date(data)).days * 24
        return total_time / len(cls._data)
       

    def __get_min_failure_date (cls, data):
        return min(row['Prob Started'] for row in data if isinstance(row['Prob Started'], datetime.datetime))


    def __get_max_failure_date (cls, data):
        return max(row['Prob Started'] for row in data if isinstance(row['Prob Started'], datetime.datetime))


    def __evaluate_failure_data (cls, system_id, node_num):
        # collect failures only that happend on the node candidate
        avail = tuple()
        node_dataset = tuple()

        for row in cls._data:
            if int(row['System']) == int(system_id) and int(row['nodenum']) == int(node_num):
                node_dataset += (row,)
        
        if len (node_dataset) == 0:
            return avail

        node_dataset = sorted(node_dataset, key = operator.itemgetter('Prob Started'), reverse = False)

        # take first failure date as starting point
        date_time = node_dataset[0]['Prob Started']

        # iterate all failures that happend on the node candidate
        downtime_transit = 0
    
        while date_time.date() <= node_dataset[-1]['Prob Started'].date():
            failures_per_date = tuple()
            downtime_acc = 0

            #if transit downtime is greater then single day duration then node was unavailable for entire day
            if downtime_transit > Uptime.DAY_IN_MINUTES:
                downtime_transit = downtime_transit - Uptime.DAY_IN_MINUTES
                avail += (0,)
                date_time += datetime.timedelta(days = 1)
                continue

            # if transit downtime exists then accumulate it for current day
            elif downtime_transit != 0:
                downtime_acc += downtime_transit
                downtime_transit = 0
    
            # filter out failures that did not happen on specific date
            for failure_row in node_dataset:
                if failure_row['Prob Started'].date() == date_time.date():
                    failures_per_date += (failure_row,)

                elif failure_row['Prob Started'].date() > date_time.date():
                    break

            for failure in failures_per_date:
                continue

            failures_per_date = cls.__duplicate_overlap_check(failures_per_date, downtime_acc)
            for failure in failures_per_date:
                continue

            # failures that happen on the same date classify into two groups based on the date when failure is removed
            # 1st group takes into account failures that are removed on the current day
            # 2nd group takes into account failures which downtime exhibits the current day
            for failure in failures_per_date:
                # failures that happend and recovered on the same date accumulate downtime to compute availability for the current day
                if failure['Prob Started'].date() == failure['Prob Fixed'].date():
                    downtime_acc += failure['Down Time']

                # failures which downtime exhibits current day are memorized to compute availability for following days
                elif downtime_transit == 0:
                    downtime_until_end_of_day = (date_time + datetime.timedelta(days = 1)).replace(hour = 0, minute = 0) - failure['Prob Started']
                    downtime_acc += (downtime_until_end_of_day.seconds // 60)
                    downtime_transit = failure['Down Time'] - (downtime_until_end_of_day.seconds // 60)

                else:
                    continue

            uptime = Uptime.DAY_IN_MINUTES - downtime_acc
            uptime = uptime / (uptime + downtime_acc)
            avail += (uptime,)
        
            # update datetime to next day for next iteration
            date_time += datetime.timedelta(days = 1)

        return avail


    def __get_data_rows (cls, system_id, node_num):
        data = tuple()

        for row in cls._data:
            if int(row['System']) == int(system_id) and int(row['nodenum']) == int(node_num):
                data += (row,)

        return data
    

    def __duplicate_overlap_check(cls, failures, downtime_acc):
        tmp_data = list()

        for failure in failures:
            add_flag = True
            if ((failure['Prob Fixed'] - failure['Prob Started'].replace(hour = 0, minute = 0)).seconds // 60) < downtime_acc:
                continue

            elif ((failure['Prob Started'] - failure['Prob Started'].replace(hour = 0, minute = 0)).seconds // 60) < downtime_acc:
                failure['Prob Started'] = failure['Prob Started'].replace(hour = downtime_acc // 60, minute = downtime_acc % 60)

            if len(tmp_data) == 0:
                tmp_data.append(failure)

            for i in range(len(tmp_data)):
                if failure['Prob Started'] < tmp_data[i]['Prob Started'] and failure['Prob Fixed'] > tmp_data[i]['Prob Started']\
                    and failure['Prob Fixed'] < tmp_data[i]['Prob Fixed']:
                    tmp_data[i]['Prob Started'] = failure['Prob Started']
                    tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
                    add_flag = False

                elif failure['Prob Started'] > tmp_data[i]['Prob Started'] and failure['Prob Started'] < tmp_data[i]['Prob Fixed']\
                    and failure['Prob Fixed'] > tmp_data[i]['Prob Fixed']:
                    tmp_data[i]['Prob Fixed'] = failure['Prob Fixed']
                    tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
                    add_flag = False

                elif failure['Prob Started'] < tmp_data[i]['Prob Started'] and failure['Prob Fixed'] > tmp_data[i]['Prob Fixed']:
                    tmp_data[i]['Prob Started'] = failure['Prob Started']
                    tmp_data[i]['Prob Fixed'] = failure['Prob Fixed']
                    tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
                    add_flag = False

                elif failure['Prob Started'] > tmp_data[i]['Prob Started'] and failure['Prob Fixed'] < tmp_data[i]['Prob Fixed']:
                    add_flag = False

                elif failure['Prob Started'] == tmp_data[i]['Prob Started'] and failure['Prob Fixed'] == tmp_data[i]['Prob Fixed']:
                    add_flag = False

            if add_flag:
                tmp_data.append(failure)

        return tuple(tmp_data)
