import sys
from time import sleep
import json
import argparse
from dateutil.parser import parse
from datetime import datetime
import operator

parser = argparse.ArgumentParser(description='filters/counters')

parser.add_argument("-f", "--fields", help="show keys from json in order of arguments provided", nargs='*')
parser.add_argument("-c", "--count", help="count with percentage for terms", nargs='*')
parser.add_argument("-x", "--and_filters", help="filter the logs with 'and' condition for given arguments", nargs='*')
parser.add_argument("-y", "--reverse_filters", help="filter the logs for given arguments", nargs='*')
parser.add_argument("-z", "--or_filters", help="filter the logs with 'or' condition for given arguments", nargs='*')
parser.add_argument("-t", "--time_bucket", help="show the log volume for given bucket time", nargs='*')

args = parser.parse_args()

fields = vars(args)['fields']
count = vars(args)['count']
and_raw_filters = vars(args)['and_filters']
raw_reverse_filter = vars(args)['reverse_filters']
time_bucket = vars(args)['time_bucket']
or_raw_filters = vars(args)['or_filters']


counter = {}
total_counter = {}
wait_seconds = 1
wait = wait_seconds
log_time_list = []
NORMALIZED_VISUAL_VALUE = 125
MAX_BUCKETS = 40
buckets = ""


def perform_filters_or(json_log, passed):
    if or_filters:
        for k,v in or_filters.items():
            if k in json_log and str(json_log[k]) in v:
                passed = True
                break
    else:
        passed = True
    return passed


def perform_filters_and(json_log, passed):
    if and_filters:
        for k,v in and_filters.items():
            if k not in json_log or str(json_log[k]) not in v:
                passed = False
                break
    return passed


def perform_filters_not(json_log, passed):
    if reverse_filter:
        for k,v in reverse_filter.items():
            if k in json_log and str(json_log[k]) in v:
                passed = False
                break
    return passed


def set_time_histogram_counter(json_data):
    if 'date' in json_data:
        log_time_list.append(parse(json_data['date'].split(".")[0]))

def set_counter(json_log):
    if count:
        for c in count:
            if c in json_log:
                if c not in counter:
                    counter[c] = {}
                    counter[c]['counts'] = {}
                if json_log[c] not in counter[c]['counts']:
                    counter[c]['counts'][json_log[c]] = 0
                counter[c]['counts'][json_log[c]] += 1
                if 'total' not in counter[c]:
                    counter[c]['total'] = 0
                counter[c]['total'] += 1


def print_fields(json_log):
    message = ""
    if fields:
        for f in fields:
            if f not in json_log:
                json_log[f] = ""
            message += str(json_log[f]) + "\t"

    if message:
        print(message)


def print_time_histgram():
    if time_bucket is not None and len(log_time_list) is not 0:
        log_time_list.sort()
        start_t = log_time_list[0]
        end_t = log_time_list[-1]
        diff = ( end_t - start_t) / MAX_BUCKETS
        time_windows = []
        for i in range(1, MAX_BUCKETS + 1):
            time_windows.append((start_t + i * diff))
        time_windows.append(parse('9999-07-06T13:40:46.799'))
        freq = [0] * MAX_BUCKETS
        id_x = 0
        for time in log_time_list:
            if time <= time_windows[id_x]:
                freq[id_x] += 1
            else:
                while time > time_windows[id_x]:
                    id_x += 1

        maxx = freq[0]
        for i in range (1, MAX_BUCKETS):
            if maxx < freq[i]:
                maxx = freq[i]

        factor = 1
        if maxx > NORMALIZED_VISUAL_VALUE:
            factor = maxx / float(NORMALIZED_VISUAL_VALUE)

        normalized_freq = [0] * MAX_BUCKETS
        for i in range (0, MAX_BUCKETS):
            normalized_freq[i] = int(freq[i] / factor)

        buckets = ""
        for i in range (0, MAX_BUCKETS):
            buckets += time_windows[i].strftime("%Y-%m-%d %H:%M:%S") + " - "
            for j in range (0, normalized_freq[i]):
                buckets += "|"
            buckets += " "  + str(freq[i]) + "\n"

        print(buckets)


def print_counts():
    for item, data in counter.items():
        print "\n-------------------------------" + item + "-------------------------------"
        counter_list = sorted(data['counts'].items(), key=operator.itemgetter(1), reverse=True)
        total = data['total']
        for key_value in counter_list:
            key = key_value[0]
            value = key_value[1]
            print("{:.1f}%".format((value * 100.0 / total)) + "\t" + str(value) + "\t" +  str(key))


def get_filters_from_args(raw_filters):
    result_filters = {}
    if raw_filters:
        for f in raw_filters:
            key_value = f.split('=')
            if len(key_value) == 2:
                if key_value[0] not in result_filters:
                    result_filters[key_value[0]] = []
                result_filters[key_value[0]].append(key_value[1])
    return result_filters

and_filters = get_filters_from_args(and_raw_filters)
or_filters = get_filters_from_args(or_raw_filters)
reverse_filter = get_filters_from_args(raw_reverse_filter)

while True:
    data = sys.stdin.readline()
    data = data.replace('\n', '')
    data = data.replace('\f', '')
    data = data.replace('\b', '')
    data = data.replace('\r', '')
    if not data:
        if wait < 0:
            break
        wait -= 1
        sleep(1)
        continue

    try:
        json_data = json.loads(data)
    except ValueError as e:
        exit()

    wait = wait_seconds
    try:
        json_log = json.loads(json_data['log'])
    except ValueError as e:
        json_log = {}
        pass

########################################### NOT of filters ########################################
    passed = perform_filters_not(json_log, True)

    if not passed:
        continue


######################################### AND of filters #########################################
    passed = perform_filters_and(json_log, True)

    if not passed:
        continue


######################################## OR of filters ##########################################
    passed = perform_filters_or(json_log, False)

    if not passed:
        continue



    set_time_histogram_counter(json_data)

    set_counter(json_log)

    print_fields(json_log)


print_time_histgram()

print_counts()

