"""
1. Parse CSV into a data structure we can work with. 
2a. Naive and easy : [], we do all poperations on the array
2b. Keep only the necessary rows in memory. 
"""
from datetime import datetime
from math import ceil

class Data:
    def __init__(self, port_name, state, port_code, border, date, measure, value):
        self.port_name = port_name
        self.state = state
        self.port_code = port_code
        self.border = border 
        self.date = date
        self.measure = measure
        self.value = value

    @classmethod
    def from_line(self, line):
        arr = line.strip().split(",")
        return Data(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], int(arr[6]))

    def get_date(self):
        date = self.date.split()[0] 
        #time = rows[0].date.split()[1]
        return datetime.strptime(date, "%m/%d/%Y").date()

    def get_key(self):
        date = self.get_date()
        return Key(date.month, date.year, self.border, self.measure)

class Key:
    def __init__(self, month, year, border, measure):
        self.month = month
        self.year = year
        self.border = border
        self.measure = measure

    def get_date_string(self):
        return "%02d/01/%d 12:00:00 AM" % (self.month, self.year)

    def prev_month_key(self, prev_month):
        return  Key(prev_month, self.year, self.border, self.measure)

    def __eq__(self, o):
        return self.month == o.month and self.year == o.year and self.border == o.border and self.measure == o.measure
        
    def __hash__(self): # lets your class be used as a key
        return hash((self.month, self.year, self.border, self.measure))

class Result:
    def __init__(self, key, value, running_avg):
        self.key = key
        self.value = value
        self.avg = running_avg
    
    def __lt__(self, o):
        """
        x < y
        Date
        Value (or number of crossings)
        Measure
        Border
        """
        if (self.key.year != o.key.year):
            return self.key.year < o.key.year
        elif (self.key.month != o.key.month):
            return self.key.month < o.key.month
        elif (self.value != o.value):
            return self.value < o.value
        elif (self.key.measure != o.key.measure):
            return self.key.measure < o.key.measure
        else:
            return self.key.border < o.key.border
    
    def get_line(self):
        return ",".join([
            self.key.border,
            self.key.get_date_string(), 
            self.key.measure, 
            str(self.value), 
            str(self.avg)
        ])

# sums and totals 

def compute_sums(file_name):
    """
    Compute totals as the file is read for efficiency. 
    """
    sums = dict() 
    with open(file_name, "r") as f:
        f.readline() # advance in file and ignore the first line
        for line in f:
            data_obj = Data.from_line(line)
            key = data_obj.get_key()
            # just initializes the sums dict
            if key not in sums:
                sums[key] = 0
            # cumulatively add to the appropriate counter for each row
            sums[key] = sums[key] + data_obj.value

    return sums

def list_avg(l):
    if not l:
        return 0
    else:
        return sum(l)/len(l)

def compute_averages(totals):
    avgs = dict()

    for key in totals:
        month = key.month

        data_prev_months = [ 
            totals[key.prev_month_key(prev_month)] 
            for prev_month in range(1, month) # from 1 (january) to just before the current month
            if key.prev_month_key(prev_month) in totals
        ]

        avgs[key] = ceil(list_avg(data_prev_months))
    return avgs

def write_rows(file_name, totals, avgs):
    results = [Result(key, totals[key], avgs[key]) for key in totals]
    with open(file_name, "w") as f:
        f.write("Border,Date,Measure,Value,Average\n") # Write header 
        for result in sorted(results, reverse=True): # __lt__ function is used for comparision which is implemnetd in the Result class
            f.write(result.get_line())
            f.write("\n") # \n as the newline separator windows vs mac + linux

# date -> date_object -> get month
test_file_name = "input/Border_Crossing_Entry_Data.csv"

totals = compute_sums(test_file_name)
avgs = compute_averages(totals)

write_rows("output/report.csv", totals, avgs)