
class Task:
    def __init__(self, i, sat_id, priority, earliest, lastest, interval, sat, ant_id):
        self.i = i # id de tash
        # self.sid = sat_id # id de sat
        self.priority = priority
        self.earliest = earliest
        self.lastest = lastest
        self.interval = interval # model.NewIntervalVar(0,0,0,'task'+i.tostring) # without repetation
        self.sat = sat
        self.ant_id = ant_id