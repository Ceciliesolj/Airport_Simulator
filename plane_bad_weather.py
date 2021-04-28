import random
import simpy
import numpy as np
import matplotlib.pyplot as plt
from time import gmtime
from time import strftime


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


def edit_snow_lists(list):
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    for i in list:
        if i < 60*60:
            one += 1
        elif 60*60 <= i < 60*60*2:
            two += 1
        elif 60*60*2 <= i < 60*60*3:
            three += 1
        elif 60*60*3 <= i < 60*60*4:
            four += 1
        else:
            five += 1
    new_list = [one, two, three, four, five]
    return new_list

bars_snow = ["0-1h", "1-2h", "2-3h", "3-4h", "4+h"]

def edit_plow_lists(list):
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    for i in list:
        if i < 600.0:
            one += 1
        elif 600.0 <= i < 1200.0:
            two += 1
        elif 1200.0 <= i < 1800.0:
            three += 1
        elif 1800.0 <= i < 2400.0:
            four += 1
        else:
            five += 1
    new_list = [one, two, three, four, five]
    return new_list

bars_plow = ["< 10min", "10-20min", "20-30min", "30-40min", "40+min"]

def edit_deice_lists(list):
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    for i in list:
        if i < 600.0:
            one += 1
        elif 600.0 <= i < 1200.0:
            two += 1
        elif 1200.0 <= i < 1800.0:
            three += 1
        elif 1800.0 <= i < 2400.0:
            four += 1
        else:
            five += 1
    new_list = [one, two, three, four, five]
    return new_list

bars_deice = ["< 10min", "10-20min", "20-30min", "30-40min", "40+min"]

def edit_ta_lists(list):
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    for i in list:
        if i < 1800.0:
            one += 1
        elif 1800.0 <= i < 3600.0:
            two += 1
        elif 3600.0 <= i < 3600.0*2:
            three += 1
        elif 3600.0*2 <= i < 3600.0*3:
            four += 1
        else:
            five += 1
    new_list = [one, two, three, four, five]
    return new_list

bars_ta = ["< 30min", "30min- 1h", "1-2h", "2-3h", "3+h"]



def convert_time_to_str(time):
    """Output time in a readable manner"""
    return strftime("%H:%M:%S", gmtime(time))

def det_delay():
    """Determine if a plane is to be delayed or not with a probability of 0.5"""
    p = random.random()
    if p < 0.5:
        return True
    else:
        return False

def Erlang(x, u_delay):
    """Make an erlang distribution"""
    return np.random.gamma(x,u_delay)


RANDOM_SEED = 678
NUM_RUNWAYS = 4
T_GUARD = 60
T_LANDING = 60      # seconds it takes to land
T_TAKEOFF = 60
#T_TURNAROUND = 60*45 #Erlang(7, 2700)
SIM_TIME = 60*60*24    # Simulation time in seconds
QUEUE = Queue() #queue for landing
TQUEUE = Queue() #queue for take-off, make it less prioritized than landing queue.
planes = []
NUM_PLOWTRUCKS = 4
NUM_DEICING = 8
TIME_PLOW = 600 #How long it takes for a truck to plow the runway
TIME_DEICE = 600
inter_arr_times = []
landing_times = []
takeoff_times = []
time_snowing = []
time_between_snow = []
time_deice = []
time_plowig = []
last = 0
plane_exist = []
times_ta = []
planes_per_hour = [0]*24


class Runway(object):
    """An airport has a limited number of runways to land and take-off planes.Planes have to request one of the runways."""
    def __init__(self, env, num_runways):
        self.env = env
        self.runway = simpy.PriorityResource(env, num_runways)
        #self.t = t
        self.planes_generated = 0
        self.closed = False
        self.isFree = True

    def landing(self, plane):
        print("%s begins landing at time %s" %
              (plane, convert_time_to_str(env.now)))
        yield self.env.timeout(T_LANDING)
        print("%s is finished landing at time %s and the runway is free" %
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

    def plow(self, plowtruck):
        yield self.env.timeout(TIME_PLOW)


def snowing_controller(env, pt, rw):
    while True:
        INTER_SNOW = np.random.exponential(9000) #set expected value in seconds for time between snowing
        IS_SNOWING = np.random.exponential(3600) # set expected value in seconds for time snowing
        UNTIL_FILLED = np.random.exponential(60 * 45) #expected value in seconds it takes for a runway to fill with snow.
        yield env.timeout(INTER_SNOW)
        start_snow = env.now
        print("Starts snowing at " + convert_time_to_str(env.now))
        yield env.timeout(UNTIL_FILLED)
        print("Runways filled with snow, must close them until plowed")
        for i in range(NUM_RUNWAYS):
            env.process(close_rw(env, rw, pt))
        if IS_SNOWING > UNTIL_FILLED:
            left = (IS_SNOWING - UNTIL_FILLED)
            while left > UNTIL_FILLED:
                yield env.timeout(UNTIL_FILLED)
                print("Runways filled with snow, must close them until plowed")
                left -= UNTIL_FILLED
                for i in range(NUM_RUNWAYS):
                    env.process(close_rw(env, rw, pt))
            yield env.timeout(left)
        stopped_snow = env.now
        time_snowing.append(stopped_snow-start_snow)
        print("stopped snowing at " + convert_time_to_str(env.now))


def close_rw(env, rw, pt):
    plow_start = env.now
    with rw.runway.request(priority=1) as req:
        yield req
        with pt.plow_truck.request() as request:
            yield request
            yield env.process(pt.plow(env))
        plow_end = env.now
        time_plowig.append(plow_end - plow_start)


def plane(env, name, rw, delay, dt):

    """The plane process, each plane has a ``name``, arrives at the airspace and requests a runway. It then starts the landing process, waits for it to finish and
    leaves to turn around
    """
    global last
    start_exist = env.now
    yield env.timeout(delay)
    if last != 0:
        inter_arr_times.append(env.now - last)
    last = env.now
    begin_landing = env.now
    print('%s is generated and enters the airspace at %s' % (name, convert_time_to_str(env.now)))
    hour = int(convert_time_to_str(env.now)[0:2])
    planes_per_hour[hour] += 1

    QUEUE.push(name)
    print("Length of landing queue: " + str(QUEUE.len()))
    #make queue time list for both queues with how long they are in the queue
    print('%s is now in the landing queue' % (name))
    print('%s requests the runway for landing.' % (name))
    #bruke Runway.isFree istedenfor??
    with rw.runway.request(priority = 2) as request:
        yield request
        yield env.process(rw.landing(name))
    QUEUE.pop()
    end_landing = env.now
    landing_times.append(end_landing-begin_landing)
    print("Length of landing queue: " + str(QUEUE.len()))
    ta_start = env.now
    yield env.timeout(Erlang(7, (45*60)/7))  #expected turn-around time, must devide by seven in order to get correct value
    deice_start = env.now
    times_ta.append(deice_start-ta_start)
    with dt.deice_truck.request() as request:
        yield request
        yield env.process(dt.deice(name))
    takeoff_begin = env.now
    time_deice.append(takeoff_begin-deice_start)
    print("%s has turned around and is ready to request take-off" % (name))
    TQUEUE.push(name)
    with rw.runway.request(priority = 3) as request:
        yield request
        yield env.process(rw.take_off(name))
        TQUEUE.pop()
    takeoff_end = env.now
    takeoff_times.append(takeoff_end - takeoff_begin)
    end_exist = env.now
    plane_exist.append(end_exist - start_exist)


class Plow_truck(object):
    def __init__(self, env, num_plowtrucks):
        self.env = env
        self.plow_truck = simpy.Resource(env, num_plowtrucks)
        self.isFree = True

    def plow(self, env):
        yield env.timeout(TIME_PLOW)
        print("Runway plowed")

class Deice_truck(object):
    def __init__(self, env, num_deicetrucks):
        self.env = env
        self.deice_truck = simpy.Resource(env, num_deicetrucks)
        self.isFree = True

    def deice(self, plane):
        yield env.timeout(TIME_DEICE)
        print(str(plane) + " deiced at time " + convert_time_to_str(env.now))

def plow_truck(env, name, rw, weather):
    with rw.runway.request() as request:
        yield request
        yield env.process(rw.plow(name))
        print("Runway " + str(rw) + "was plowed")


def setup(env, num_runways, num_plowtrucks, num_deicetrucks):
    """Create a runway and planes"""
    # Create the runway
    runway = Runway(env, num_runways)
    plow_truck = Plow_truck(env, num_plowtrucks)
    deice_truck = Deice_truck(env, num_deicetrucks)
    planes_generated = 0
    delayed_planes = 0
    i = 0

    #Create the weather
    env.process(snowing_controller(env, plow_truck, runway))

    # Create more planes while the simulation is running
    yield env.timeout(60 * 60 * 5)
    while True:
        if not det_delay():
            delay = 0
        else:
            delay = Erlang(3,0/3) #input expected delay time, must devide by three in order to get correct value
            delayed_planes += 1
        yield env.timeout(max(T_GUARD, np.random.exponential(get_intensity(env.now))))
        i += 1
        env.process(plane(env, 'Plane %d' % i, runway, delay, deice_truck))
        planes_generated += 1
        print("generated planes: " + str(planes_generated))
        print("delayed planes: " + str(delayed_planes))




"Setup and start the simulation"
print('Plane Generator')
print ("")


random.seed(RANDOM_SEED)

"Create an environment and start the setup process"
env = simpy.Environment()
env.process(setup(env, NUM_RUNWAYS, NUM_PLOWTRUCKS, NUM_DEICING))

"Execute!"
env.run(until=SIM_TIME)



hours = ["00-01", "01-02" ,"02-03" ,"03-04","04-05","05-06","06-07","07-08", "08-09","09-10","10-11","11-12","12-13","13-14","14-15","15-16","16-17","17-18","18-19","19-20","20-21","21-22","22-23","23-00"]
#plt.hist(QUEUE.len())


print(planes_per_hour)
inter = edit_inter_arr_list(inter_arr_times)
cat = ["<60", "60", "60-160", "160-260", "260-360", "360+"]
print(inter)
plt.subplots(1)
plt.bar(cat, inter)
plt.xlabel("inter-arrival time (s) \n Average inter-arrival time:" + convert_time_to_str(sum(inter_arr_times)/len(inter_arr_times)))
plt.ylabel("# planes")
plt.subplots(1)
plt.bar(hours[5:], planes_per_hour[5:])
plt.xlabel("time of day")
plt.ylabel("# planes")
plt.subplots(1)
plt.bar(bars_land_tko, edit_lt_lists(landing_times))
plt.xlabel("landing time (s) \n Average landing time:" + convert_time_to_str(sum(landing_times)/len(landing_times)))
plt.ylabel("# planes")
plt.subplots(1)
plt.bar(bars_land_tko, edit_lt_lists(takeoff_times))
plt.xlabel("take-off time (s) \n Average take-off time:" + convert_time_to_str(sum(takeoff_times)/len(takeoff_times)))
plt.ylabel("# planes")

plt.subplots(1)
plt.bar(bars_deice, edit_deice_lists(time_deice))
plt.xlabel("deicing times (s) \n Average deicing time:" + convert_time_to_str(sum(time_deice)/len(time_deice)))
plt.ylabel("# planes")

plt.subplots(1)
plt.bar(bars_ta, edit_ta_lists(times_ta))
plt.xlabel("turn-around time (s) \n Average turn-around time:" + convert_time_to_str(sum(times_ta)/len(times_ta)))
plt.ylabel("# planes")

plt.subplots(1)
plt.bar(bars_plow, edit_plow_lists(time_plowig))
plt.xlabel("plowing time time (runway closed) (s) \n Average plowing time:" + convert_time_to_str(sum(time_plowig)/len(time_plowig)))
plt.ylabel("# planes")

plt.subplots(1)
plt.bar(bars_snow, edit_snow_lists(time_snowing))
plt.xlabel("snownig time (s) \n Average snowing time:" + convert_time_to_str(sum(time_snowing)/len(time_snowing)))
plt.ylabel("# planes")

plt.subplots(1)
plt.hist(plane_exist)
plt.xlabel("existing time (s) \n Average existence time:" + convert_time_to_str(sum(plane_exist)/len(plane_exist)))
plt.ylabel("# planes")
plt.show()




print("inter-arrivals")
print((inter_arr_times))
print("landing times")
print(landing_times)
print("snow times")
print(time_snowing)
print("deice times")
print(time_deice)
print("take-off times")
print(takeoff_times)
print("plane exists")
print(plane_exist)
print("plow times")
print(time_plowig)


print(len(landing_times))
print(len(landing_times) - len(takeoff_times))



