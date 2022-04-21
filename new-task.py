import json

final_dict = {}

def load_json_file(file_name):
    with open(file_name) as f:  #load json data
        return json.load(f)

def fetch_all_duty_ids(data):
    """
    updates the final dict keys with the duty_id values.
    :param data:
    :return:
    """
    temp_data = data['duties']
    for i in temp_data:
        if 'duty_id' in i.keys():
            final_dict[i['duty_id']] = ""


def get_start_end_time_for_duty_id(full_data, duty_id): #TODO
    """find start time for specific duty id"""
    start_time = False
    temp_data = full_data['duties']
    for i in temp_data:
        if i['duty_id'] == duty_id:
            duty_events_data = i['duty_events']
    total_vehicale_ids = get_total_vehicale_ids(duty_events_data)
    if total_vehicale_ids == 1:
        # logic - first search for sign-on
        # if not sign-on -> search for pre trip
        # return start time
        start_time = search_sign_on_return_start_value(duty_events_data)
        if start_time != False:
            end_time = search_sign_on_return_end_value(full_data, duty_id)
            if end_time != False:
                return start_time, end_time

        else:
            temp_data = full_data['vehicles']
            start_time = search_pre_trip_return_start_value(temp_data, duty_id)
            end_time = search_pre_trip_return_end_value(full_data, duty_id)
            return start_time, end_time

    elif total_vehicale_ids == 2:
        ########################
        temp_dict = {}
        dict1 = get_lowest_seq_id_per_vehicle_id(duty_events_data)
        key = list(dict1.keys())[0]
        temp_dict[key] = dict1[key]
        start_time = get_start_time_from_two_vehicle_ids(temp_dict, full_data,duty_id)
        key = list(dict1.keys())[-1]
        temp_dict[key] = dict1[key]
        end_time = get_end_time_from_two_vehicle_ids(temp_dict, full_data)
        return start_time, end_time
       ########################


def search_sign_on_return_start_value(data):
    """
    searching for 'sign_on' value in 'duty_event_type' within 'duty_events'
    if found - return start time
    if not return false
    """
    start_time = False
    for i in data:
        if 'duty_event_type' in i.keys():
            if i['duty_event_type'] == 'sign_on':
                start_time = i['start_time']
    return start_time

def search_sign_on_return_end_value(data, duty_id):
    '''
   input data = 'vehicles' value
    searching for 'deadhead' value in 'vehicle_event_type' within 'vehicle_events' (in 'vehicles')
    if found - return first end_time value found
    if not return false
    '''
    end_time = False
    for i in data['vehicles']:
        temp_data = i['vehicle_events']
        for j in temp_data:
            if 'vehicle_event_type' in j.keys():
                if j['duty_id'] == duty_id and j['vehicle_event_type'] == 'deadhead':
                    end_time = j['end_time']
                else:
                    if j['duty_id'] == duty_id and j['vehicle_event_type'] == 'attendance':
                        end_time = j['end_time']
    return end_time

def search_pre_trip_return_start_value(data, duty_id):
    """
    input data = 'vehicles' value
    searching for 'pre_trip' value in 'vehicle_event_type' within 'vehicle_events' (in 'vehicles')
    if found - return first start_time value found
    if not return false
    """
    start_time = False
    for i in data:
        temp_data = i['vehicle_events']
        for j in temp_data:
            if 'vehicle_event_type' in j.keys():
                if j['duty_id'] == duty_id and j['vehicle_event_type'] == 'pre_trip':
                    start_time = j['start_time']
                    return start_time

def search_pre_trip_return_end_value(data, duty_id):
    """
        input data = 'vehicles' value
        searching for 'pre_trip' value in 'vehicle_event_type' within 'vehicle_events' (in 'vehicles')
        if found - return first end_time value found
        if not return false
        """
    end_time = False
    for a in data['duties']:
        if a["duty_id"] == duty_id:
            b = a['duty_events']
            for c in b:
                if 'duty_event_type' in c.keys():
                    if c['duty_event_type'] == "taxi":
                        end_time = c['end_time']
                    else:
                        for i in data['vehicles']:
                            temp_data = i['vehicle_events']
                            for j in temp_data:
                                if 'vehicle_event_type' in j.keys():
                                    if j['duty_id'] == duty_id and j['vehicle_event_type'] == 'pre_trip':
                                        end_time = j['end_time']
                                        return end_time

def get_total_vehicale_ids(data):
    """searching for the total of vics ids in 'duty_events'
    """
    temp_lst = []
    for i in data:
        if 'vehicle_id' in i.keys():
            temp_lst.append(i['vehicle_id'])
    temp_lst = list(set(temp_lst))
    return len(temp_lst)

def get_lowest_seq_id_per_vehicle_id(data):
    """
    returns the lowest seq id for each vehicle id
    :param data: list of 'duty_events'
    :return:
    """
    if get_total_vehicale_ids(data) > 1:
        temp_dict = {}
        for i in data: # run on the items in the list (items are dict each)
            if not 'vehicle_id' in i.keys() and not 'vehicle_event_sequence' in i.keys():  #
                continue  #
            if i['vehicle_id'] in temp_dict.keys():
                temp_lst = temp_dict[i['vehicle_id']]
                temp_lst.append(i['vehicle_event_sequence'])
                temp_dict[i['vehicle_id']] = temp_lst
            else:
                temp_dict[i['vehicle_id']] = [i['vehicle_event_sequence']]

        for key,val in temp_dict.items():
            temp_dict[key] = val[0]
    return temp_dict

def get_start_time_from_two_vehicle_ids(input_dict, data, duty_id):
    """
    data = 'vehicles'
    :param dict1:
    :return:
    """
    start_time = False
    for key, val in input_dict.items():
        for i in data['vehicles']:
            j = i['vehicle_events']
            if i['vehicle_id'] == str(key):
                for each in j:
                    if each['vehicle_event_sequence'] == str(val):
                        start_time = each['start_time']
                    return start_time


def get_end_time_from_two_vehicle_ids(input_dict, data):   ###
    """
       data = 'vehicles'
       :param dict1:
       :return:
       """
    end_time = False
    for key, val in input_dict.items():
        for i in data['vehicles']:
            j = i['vehicle_events']
            if i['vehicle_id'] == str(key):
                for each in j:
                    if each['vehicle_event_sequence'] == str(val):
                        if 'end_time' in each.keys():
                            end_time = each['end_time']
    return end_time
                    #return False

def print_result(input_dict):
    i = 1
    total_lst = [['DUTY ID','START TIME', 'END TIME']]
    while i < 145:
        temp_lst = []
        for j in input_dict.keys():
            if int(j) == i:
                temp_lst.append(j)
                a = input_dict[j]['start_time']
                if type(a) == str:
                    a = a.split(".")[1]
                #a = input_dict[j]['start_time'].split(".")[1]
                temp_lst.append(a)
                b = input_dict[j]['end_time']
                if type(b) == str:
                    b = b.split(".")[1]
                #b = input_dict[j]['end_time'].split(".")[1]
                temp_lst.append(b)
                continue
        i += 1
        total_lst.append(temp_lst)
    for i in total_lst:
        for j in i:
            print(str(j), end=" ")
        print()

def main():
    print("start script")
    full_json_data = load_json_file("mini_json_dataset.json")

    #fetch_all_duty_ids(full_json_data, final_dict)
    fetch_all_duty_ids(full_json_data)
    for key in final_dict.keys():
        start_time, end_time = get_start_end_time_for_duty_id(full_json_data, key)
        final_dict[key] = {'start_time': start_time,
                           'end_time' : end_time}
    print_result(final_dict)

    print("end script")


if __name__ == "__main__":
    main()