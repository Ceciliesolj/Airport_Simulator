import random
import simpy
import numpy as np
import matplotlib.pyplot as plt
import heapq
from time import gmtime
from time import strftime
import scipy as sc
from scipy.stats import erlang


class Queue:
    "Making a first-in-first-out (FIFO) queuing method"
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the first enqueued item in the queue. The pop
          operation removes the item from the queue.
        """
        return self.list.pop()

    def get_next(self):
        """Gets the element first in line without removing it from the queue"""
        c = self.list.copy()
        return c.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

    def len(self):
        "Returns the length of the queue"
        return len(self.list)



def get_intensity(time):
    """Determine the intensity for the arrivals given time of day"""
    if (5*60*60 <= time < 8*60*60) or (20*60*60 <= time < 24*60*60):
        return 90
    elif (8*60*60 <= time < 11*60*60) or (15*60*60 <= time < 20*60*60):
        return 150
    else:
        return 60



def convert_time_to_str(time):
    """Output time in a readable manner"""
    return strftime("%H:%M:%S", gmtime(time))

def det_delay():
    """Determine if a plane is to be delayed or not with a probability of 0.5"""
    p = random.random()
    if p <= 0.5:
        return True
    else:
        return False

def Erlang(x, u_delay):
    """Make an erland distribution"""
    return np.random.gamma(x,u_delay)


RANDOM_SEED = 678
NUM_RUNWAYS = 2
T_GUARD = 60
T_LANDING = 60      # seconds it takes to land
T_TAKEOFF = 60
#T_TURNAROUND = Erlang(7, 76) #40*60
SIM_TIME = 60*60*24    # Simulation time in seconds
QUEUE = Queue() #queue for landing
TQUEUE = Queue() #queue for take-off, make it less prioritized than landing queue.
inter_arr_times = []
landing_times = []
takeoff_times = []

class Runway(object):
    """An airport has a limited number of runways to land and take-off planes.Planes have to request one of the runways."""
    def __init__(self, env, num_runways):
        self.env = env
        self.runway = simpy.PriorityResource(env, num_runways)
        self.planes_generated = 0

    def landing(self, plane):
        print("Plane %s begins landing at time %s" %
              (plane, convert_time_to_str(env.now)))
        yield self.env.timeout(T_LANDING)
        print("Plane %s is finished landing at time %s and the runway is free" %
              (plane, convert_time_to_str(env.now)))
        print("")


        print(str(QUEUE.len()))

    def take_off(self, plane):
        print(" %s begins take-off at time %s" %
              (plane, convert_time_to_str(env.now)))
        yield self.env.timeout(T_TAKEOFF)
        print(" %s is finished take-off at time %s and the runway is free" %
              (plane, convert_time_to_str(env.now)))
        print("Take off queue: " + str(TQUEUE.len()))
        print("")


plane_exist = []
last = 0
def plane(env, name, rw, delay):
    """The plane process, each plane has a ``name``, arrives at the airspace  and requests a runway. It then starts the landing process, waits for it to finish and
    leaves to turn around
    """
    global last
    start_exist = env.now
    #d = delay
    yield env.timeout(delay) #Koden oppfattet ikke delay så måtte caste datatype for å få den til å holde
    if last != 0:
        inter_arr_times.append(env.now - last)
    last = env.now
    begin_landing = env.now
    print('%s is generated and enters the airspace at %s' % (name, convert_time_to_str(env.now)))
    hour = int(convert_time_to_str(env.now)[0:2])
    planes_per_hour[hour] += 1

    QUEUE.push(name)
    print('%s is now in the landing queue' % (name))
    print('%s requests a runway for landing.' % (name))
    with rw.runway.request(priority = 1) as request:
        yield request
        yield env.process(rw.landing(name))
    QUEUE.pop()
    end_landing = env.now
    landing_times.append(end_landing-begin_landing)
    yield env.timeout(Erlang(7, (45*60)/7))
    takeoff_begin = env.now
    print("%s has turned around and is ready to request take-off" % (name))
    TQUEUE.push(name)
    with rw.runway.request(priority = 2) as request:
        #burde nok ikke være if her ?
        #if QUEUE.isEmpty() == True:
        yield request
        yield env.process(rw.take_off(name))
        TQUEUE.pop()
    takeoff_end = env.now
    takeoff_times.append(takeoff_end-takeoff_begin)
    end_exist = env.now
    plane_exist.append(end_exist-start_exist)



        #print('%s enters the airspace at %s' % (name, convert_time_to_str(env.now)))
        #yield env.process(rw.process_in_air(name))

        #print('%s is landed at %.2f.' % (name, env.now))
        #print('%s is landed at %s' % (name, convert_time_to_str(env.now)))


planes_per_hour = [0]*24
def setup(env, num_runways):
    """Create a runway and planes"""
    # Create the runway
    runway = Runway(env, num_runways)
    planes_generated = 0
    delayed_planes = 0
    i = 0

    # Create more planes while the simulation is running
    yield env.timeout(60 * 60 * 5) #No planes arriving the five first hours
    while True:
        if not det_delay():
            delay = 0
        else:
            delay = (Erlang(3, 10800/3)) #input expected delay time, must devide by three in order to get correct value
            print(delay)

            delayed_planes += 1
        yield env.timeout(max(T_GUARD, np.random.exponential(get_intensity(env.now))))
        #yield env.timeout(delay)
        i += 1
        env.process(plane(env, 'Plane %d' % i, runway, delay))
        planes_generated += 1
        #print("generated planes: "+ str(planes_generated))
        print("delayed planes: " + str(delayed_planes))




# Setup and start the simulation
print('Plane Generator')
print ("")


random.seed(RANDOM_SEED)

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env, NUM_RUNWAYS))

# Execute!
env.run(until=SIM_TIME)

def edit_inter_arr_list(list):
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    six = 0
    for i in list:
        if i < 60:
            six += 1
        elif i == 60:
            one += 1
        elif 60 < i <= 160:
            two += 1
        elif 160 < i <= 260:
            three += 1
        elif 260 < i <= 360:
            four += 1
        else:
            five += 1
    new_list = [six, one, two, three, four, five]
    return new_list

def edit_lt_lists(list):
    one = 0
    two = 0
    three = 0
    four = 0
    zero = 0
    for i in list:
        if i == 60:
            one += 1
        elif 60 < i <= 160:
            two += 1
        elif 160 < i <= 260:
            three += 1
        elif i < 60:
            zero += 1
        else:
            four += 1
    new_list = [zero, one, two, three, four]
    return new_list

bars_land_tko = ["<60", "60", "60-160", "160-260", "260+"]
"""
print(edit_lt_lists(landing_times))
print(edit_lt_lists(takeoff_times))

print(inter_arr_times)
print(len(inter_arr_times))
"""


#Oppgave a)
hours = ["00-01", "01-02" ,"02-03" ,"03-04","04-05","05-06","06-07","07-08", "08-09","09-10","10-11","11-12","12-13","13-14","14-15","15-16","16-17","17-18","18-19","19-20","20-21","21-22","22-23","23-00"]
"""
print(planes_per_hour)
inter = edit_inter_arr_list(inter_arr_times)
cat = ["<60", "60", "60-160", "160-260", "260-360", "360+"]
print(inter)
plt.subplot(311)
plt.bar(cat, inter)
plt.xlabel("inter-arrival time (s)")
plt.ylabel("# planes")
plt.subplot(312)
"""
plt.bar(hours[5:], planes_per_hour[5:])
plt.xlabel("Time of day")
plt.ylabel("# planes")

plt.show()


print(plane_exist)
print((sum(plane_exist)/len(plane_exist)))


#Oppgave b)
"""
plt.subplots(1)
plt.bar(bars_land_tko, edit_lt_lists(landing_times))
plt.xlabel("landing time (s)")
plt.ylabel("# planes")
plt.subplots(1)
plt.bar(bars_land_tko, edit_lt_lists(takeoff_times))
plt.xlabel("take-off time (s)")
plt.ylabel("# planes")
plt.subplots(1)
plt.hist(plane_exist)
plt.xlabel("existing time (s) \n Average existence time:" + str(sum(plane_exist)/len(plane_exist)))
plt.ylabel("# planes")
plt.show()
"""



"""
For oppgave a) 
fjern kommentar på det som står under #Oppgave a) og endre på forventet forsinkelse i Erlang-fordelingen i set-up. 

"""