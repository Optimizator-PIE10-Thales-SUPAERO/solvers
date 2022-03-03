
"""
Get a dictionary of non-visibility information.
keys are task id and antenne id
"""
def get_dict_non_visib(dict_visib):

    dict_non_visib = {}
    for element in dict_visib:
        list_no_sort = dict_visib[element]
        list_sort = sorted(list_no_sort)
        for i in range(len(list_sort)):
            if i == 0: 
                dict_non_visib[element] = [(-1,list_sort[i][0]-1)]
            else:
                dict_non_visib[element].append((list_sort[i-1][1]+1,list_sort[i][0]-1))
            i += 1 # increase the index
    #print(dict_non_visib)
    return dict_non_visib

# function to get unique values
def unique(list1):
 
    # initialize a null list
    unique_list = []
     
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
