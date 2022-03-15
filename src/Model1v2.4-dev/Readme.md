# Readme

## Sampler

A sampler that can generate one or several samples of scenarios with number of satellites wanted.

The samples are stored in `./PIE_SXS10_data/nominal/random_sample/`


* Generate one sample with 5 satellites
```
$ python Sampler.py 5
```

* Generate 5 samples with 10 satellites
```
$ python Sampler.py 10 5
```

## Main Model

### help

```
$ python main.py -h
```

```
usage: main.py [-h] [-g] [-no] [-n [SETOCCURRENCE]] [--p [P]] [--r [R]] [--v [V]]

Modèle Matriciel

optional arguments:
  -h, --help            show this help message and exit
  -g, --TestForGroupScenario
                        If you want to run the model for a group of scenarios
  -no, --NoOccurrence   If you want to run the model without considering the repetition
  -n [SETOCCURRENCE], --SetOccurrence [SETOCCURRENCE]
                        (optional) Set the max time of repetion manully
  --p [P]               Test files path
  --r [R]               Requirements file
  --v [V]               Visibility file

```

## Examples

### Simple version

We assume that, each task is related to a unique satelite, which means that the index of task
and the index of satelite is corresponding.

### To execute the simple version

```
python main.py -n 3
```

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
```


### Nominal version

### To execute Nominal version

* Modify the total période

Go to file ModelCP.py

* Limite the occurrence of repetitive task

```
python main.py --r ./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt -n 5
```

* No Occurrence

```
python main.py --no --r ./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt 
```

* Test for a group of scenarios

```
python main.py -g --p ./PIE_SXS10_data/nominal/random_sample/10/ -n 5
```
