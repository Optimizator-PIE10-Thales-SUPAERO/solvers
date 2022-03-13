
import xlwt


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
    # print("@dict non visiblities: ", dict_non_visib)
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

# This function aims to save the data calculated from ortools into a excel file
def write_file(dict_visib, dict_res, dict_req,data_output_path):

    book = xlwt.Workbook(encoding='utf-8')
    sheet1 = book.add_sheet(u'datasheet', cell_overwrite_ok=True)

    sheet1.write(0, 0, 'Task') 
    sheet1.write(0, 1, 'Start')  
    sheet1.write(0, 2, 'Finish')
    sheet1.write(0, 3, 'Name')
    sheet1.write(0, 4, 'Color')
    sheet1.write(0, 5, 'Opacity')
    sheet1.write(0, 6, 'Information')
    i = 1
    sat_ant_list = []
    antname_index = 0

    for task_id in dict_req['Satellite']:
        task = dict_req['Task number'][task_id]
        sat = dict_req['Satellite'][task_id]
        for element in dict_res[task]:
            ant = element['antenne']
            # add visibilité
            if element['end'] == element['start']:
                continue
            elif (sat,ant) not in sat_ant_list:
                sat_ant_list.append((sat,ant))
                color_index = len(sat_ant_list)
                # get the list of windows of visibility
                list_visibility = dict_visib[sat,ant]
                # print("@list visiblity :", list_visibility,"for ",sat,":",ant)
                for s,e in list_visibility:
                    sheet1.write(i, 0, str(sat)+":"+str(ant))
                    sheet1.write(i, 1, int(s))
                    sheet1.write(i, 2, int(e))
                    sheet1.write(i, 3, str(list_visibility.index((s,e))) + " "+ sat + " " + ant)
                    sheet1.write(i, 4, color_index*5)
                    sheet1.write(i, 5, 0.2)
                    sheet1.write(i, 6, "Start Time="+str(s)+ "; End Time: " + str(e))
                    i = i+1
            
            sheet1.write(i, 0, str(sat)+":"+str(ant))
            sheet1.write(i, 1, element['start'])
            sheet1.write(i, 2, element['end'])
            sheet1.write(i, 3, sat+ant+str(element['start']))
            # print(sat_ant_list.index((sat,ant)))
            sheet1.write(i, 4, (sat_ant_list.index((sat,ant))+1)*5)
            sheet1.write(i, 5, 1)
            sheet1.write(i, 6, "Start Time="+str(element['start'])+ "; End Time: " + str(element['end']))
            i = i + 1
    book.save(data_output_path)


