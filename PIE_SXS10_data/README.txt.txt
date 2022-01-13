This repertory contains input data for the PIE project SXS10.

We consider that the project is composed by the following assets:
	- 60 satellites called "SATx" with x in [1,60]
	- 12 antennes called "ANTx" with x in [7,12]

The file visibilities.txt contains the visibilities for all satellites and assets during 14 days. The column header are:
	- Sat : the name of the satellite in the visibility 
	- Ant : the antenna in the visibility
	- Start : the start time in seconds of the visibility during the 14 days period
	- End : the end time in seconds of the visibility during the 14 days period


Two repertories 'nominal' and 'intermediate' contains the input task to plan, sorted by the difficulty of the tasks.
In all files, we have the same structure. First, the second line lists the satellites involved in the scenario.
Then, the tasks to plan are listed with the following properties:
	- Task number : identification of the task
	- Satellite : satellite on which the task needs to be planned
	- Priority : priority of the task (the min number is 1 and the max number is 10).
	- Duration : duration of the task in seconds
	- Earliest : earliest start time of the task during the 14 days period
	- Latest : latest start time of the task during the 14 days period
	- Repetitive : indicates if the task is repetitive (=1), or unary (=0).
	- Number occ : number of times the task needs to be repeated. Don't take into account if num is 0 or -1.
If the number is 0, the task is unary. 
If the number is -1, it means we don't have this information for repetitive tasks. 
	- Min time lag : minimum time needed between the start time of two consecutive contacts of a task.
	- Max time lag : maximum time needed between the start time of two consecutive contacts of a task. 
If the max time lag is -1, it means that we don't have this information.



Note1 : If a task is unary (repetitive=0), don't take into account the properties :
	- 'Number occ'
	- 'Min time lag'
	- 'Max time lag'

Note2 : The tasks with priority 1 are the most important, while the ones with a priority 10 are the less important.

