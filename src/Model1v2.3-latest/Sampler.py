import sys
import parse
import random

def MkSampleFile(input_path,output_path):
    with open(input_path) as f:
        lines = f.readlines()
        list_sat = [i for i in lines[1].strip().split('\t')]

    new_lines = []
    new_sats = []
    samples_indexs = random.sample(range(0,len(lines)-3),number_of_sat)
    for i in samples_indexs:
        new_sats.append(list_sat[i])
        new_lines.append(lines[i+3])
    to_write_sats = ""
    for sat in new_sats:
        to_write_sats = to_write_sats + sat + '\t'
    to_write_sats = to_write_sats + '\n'

    with open(output_path,'w') as of:
        print(samples_indexs)
        of.write(lines[0])
        of.write(to_write_sats)
        of.write(lines[2])
        of.writelines(new_lines)

if __name__ == '__main__':
    arguments = sys.argv
    print('start')
    if len(arguments) == 2:
        number_of_sat = int(arguments[1])
        n = 0
    elif len(arguments) == 3:
        number_of_sat = int(arguments[1])
        n = int(arguments[2])
    else:
        print("please write how many satellites you want as arguments !")
        sys.exit(0)
    input_path = './PIE_SXS10_data/nominal/random_sample/scenario_40SAT_nominal_base.txt'
    
    for i in range(n):
        output_path = './PIE_SXS10_data/nominal/random_sample/'+str(i)+'/scenario_random'+str(number_of_sat)+'SAT_nominal_testi'+str(i)+'.txt'
        print(input_path,output_path)
        MkSampleFile(input_path,output_path)

    
