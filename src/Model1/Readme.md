# Readme

## Simple version

We assume that, each task is related to a unique satelite, which means that the index of task
and the index of satelite is corresponding.

### To execute the simple version

```
python main.py
```

Example : 

```
@Requirements are: 
   Task number Satellite  Priority  Duration  Earliest   Latest  Repetitive  Number occ  Min time lag  Max time lag
0       TASK0      SAT1         8      3000         0  1207749           1          -1         25200         43200
1       TASK1      SAT2         8      3000         0  1207620           1          -1         25200         43200
2       TASK2      SAT3         8      3000         0  1207790           1          -1         25200         43200
@list of antennes: 
 [1, 2, 3]

==>START MODEL<==

-->Initialization for the matrix of visibility<--
-->FINISED<--

-->ARGUMENTS<--
@Requirements dictionary : 
 {'Task number': {0: 'TASK0', 1: 'TASK1', 2: 'TASK2'}, 'Satellite': {0: 'SAT1', 1: 'SAT2', 2: 'SAT3'}, 'Priority': {0: 8, 1: 8, 2: 8}, 'Duration': {0: 3000, 1: 3000, 2: 3000}, 'Earliest': {0: 0, 1: 0, 2: 0}, 'Latest': {0: 1207749, 1: 1207620, 2: 1207790}, 'Repetitive': {0: 1, 1: 1, 2: 1}, 'Number occ': {0: -1, 1: -1, 2: -1}, 'Min time lag': {0: 25200, 1: 25200, 2: 25200}, 'Max time lag': {0: 43200, 1: 43200, 2: 43200}}
-->FINISHED<--


-->MODEL PARAMETERS<--
-->CONTRAINTS<--
Contraint1: duration for each task
Contraint2: No overlap for all intervals of each task/satellite
Contraint3: No overlap for all intervals of each antenne
Contraint4: No overlap for interval variable and non-visib intervals (not variables) 
-->FINISED<--

-->Statistics<--
  status   : OPTIMAL
  conflicts: 0
  branches : 0
  wall time: 0.025165735 s
-->FINISED<--

-->RESULTS<--
Optimal time usage : 3000.0
TASK0:SAT1_ANT1                     SAT1_ANT2                     SAT1_ANT3                     
           [0,3000]                      [0,0]                         [0,0]                         
TASK1:SAT2_ANT1                     SAT2_ANT2                     SAT2_ANT3                     
           [0,0]                         [0,0]                         [0,3000]                      
TASK2:SAT3_ANT1                     SAT3_ANT2                     SAT3_ANT3                     
           [0,0]                         [0,3000]                      [0,0]                         

-->FINISHED<--

==>END MODEL<==


```

## Nominal version

### To execute

Add the requirement file as the first argument

Eg.

```
python main.py ../../PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt
```

Result:

```
-->Statistics<--
  status   : OPTIMAL
  conflicts: 1
  branches : 1
  wall time: 0.21484281000000002 s
-->FINISED<--

-->RESULTS<--
Optimal time usage : 2328.0
TASK0:SAT15_ANT7                    SAT15_ANT9                    SAT15_ANT5                    SAT15_ANT10                   SAT15_ANT1                    SAT15_ANT2                    SAT15_ANT3                    SAT15_ANT11                   SAT15_ANT6                    SAT15_ANT8                    SAT15_ANT4                    SAT15_ANT12                   
           [0,1851]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK4:SAT12_ANT7                    SAT12_ANT9                    SAT12_ANT5                    SAT12_ANT10                   SAT12_ANT1                    SAT12_ANT2                    SAT12_ANT3                    SAT12_ANT11                   SAT12_ANT6                    SAT12_ANT8                    SAT12_ANT4                    SAT12_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,1980]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK8:SAT21_ANT7                    SAT21_ANT9                    SAT21_ANT5                    SAT21_ANT10                   SAT21_ANT1                    SAT21_ANT2                    SAT21_ANT3                    SAT21_ANT11                   SAT21_ANT6                    SAT21_ANT8                    SAT21_ANT4                    SAT21_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,1810]                      [0,0]                         [0,0]                         [0,0]                         
TASK12:SAT17_ANT7                    SAT17_ANT9                    SAT17_ANT5                    SAT17_ANT10                   SAT17_ANT1                    SAT17_ANT2                    SAT17_ANT3                    SAT17_ANT11                   SAT17_ANT6                    SAT17_ANT8                    SAT17_ANT4                    SAT17_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,2227]                      
TASK16:SAT07_ANT7                    SAT07_ANT9                    SAT07_ANT5                    SAT07_ANT10                   SAT07_ANT1                    SAT07_ANT2                    SAT07_ANT3                    SAT07_ANT11                   SAT07_ANT6                    SAT07_ANT8                    SAT07_ANT4                    SAT07_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,1983]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK20:SAT09_ANT7                    SAT09_ANT9                    SAT09_ANT5                    SAT09_ANT10                   SAT09_ANT1                    SAT09_ANT2                    SAT09_ANT3                    SAT09_ANT11                   SAT09_ANT6                    SAT09_ANT8                    SAT09_ANT4                    SAT09_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,2185]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK24:SAT22_ANT7                    SAT22_ANT9                    SAT22_ANT5                    SAT22_ANT10                   SAT22_ANT1                    SAT22_ANT2                    SAT22_ANT3                    SAT22_ANT11                   SAT22_ANT6                    SAT22_ANT8                    SAT22_ANT4                    SAT22_ANT12                   
           [0,0]                         [0,2328]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK28:SAT11_ANT7                    SAT11_ANT9                    SAT11_ANT5                    SAT11_ANT10                   SAT11_ANT1                    SAT11_ANT2                    SAT11_ANT3                    SAT11_ANT11                   SAT11_ANT6                    SAT11_ANT8                    SAT11_ANT4                    SAT11_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,2275]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK32:SAT18_ANT7                    SAT18_ANT9                    SAT18_ANT5                    SAT18_ANT10                   SAT18_ANT1                    SAT18_ANT2                    SAT18_ANT3                    SAT18_ANT11                   SAT18_ANT6                    SAT18_ANT8                    SAT18_ANT4                    SAT18_ANT12                   
           [0,0]                         [0,0]                         [0,1934]                      [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         
TASK36:SAT03_ANT7                    SAT03_ANT9                    SAT03_ANT5                    SAT03_ANT10                   SAT03_ANT1                    SAT03_ANT2                    SAT03_ANT3                    SAT03_ANT11                   SAT03_ANT6                    SAT03_ANT8                    SAT03_ANT4                    SAT03_ANT12                   
           [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,0]                         [0,1999]                      [0,0]                         [0,0]                         

-->FINISHED<--

```
