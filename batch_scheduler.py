from collections import deque  # double ended queue
import heapq  # We probably need priority heap
# I ended up not using either of these because I don't remember how to use them, but as discussed I think
# SRTF could be sped up significantly in the simulation via the use of a heap
#(faster searchhes)
#word debug is placed several places at points I think might be
#failure points, usually because I wasn't sure of the behavior of a python funciton

class Job:
    #The jobs class will be the meat and potatos of this dish
    #it provides us with arrival and burst, completion ended up not being used
    
    def __init__(self, job_id, arrival, burst):
        self.id = job_id
        
        self.arrival = arrival
        #time that job arrives
        self.burst = burst
        #starts with total completion time as specified in third column
        
        self.remaining = burst
        # remaining time needed for preemptive switch style schedules
        # starts as equivalent to burst but is reduced and used for srtf and rr schedulers
        
        self.completion = 0
#Note: Need to add protection for faulty files later
def read_data():
    #First col in data is job number and works as id
    #Second col is time job submitted, corresponds with some epoch
    #Third is time for job to complete
    #unit of time will be in seconds
    jobs = []
    with open("data.txt", "r") as file_handle:
        for line in file_handle:
            cols = line.strip().split()
            job_id = int(cols[0])
            arrival = int(cols[1])
            burst = int(cols[2])
            jobs.append(Job(job_id, arrival, burst))
##        for job in jobs:
##            print(id)
    return jobs

def fcfs(jobs):
    #Run jobs in order, context switches is equal to n, let n = job count
    #we could perhaps save cycles in scheduler simulation by setting equal to n
    
    time = 0
    #time to complete all jobs
    context_switches = 0
    prior_job = None
    # Originally this was designed to go by id
    # There is a possible pitfall there however
    # in which there might be a data.txt containing
    # programs which somehow have a low id and a late
    # arrive time, not sure how this could happen
    # but planning for it here
    for job in sorted(jobs, key=lambda x: x.arrival):
        #Debug break point, long time since lambdas
        if time < job.arrival:
            time = job.arrival

        if prior_job != job:
            context_switches += 1

        time += job.burst
        job.completion = time
        prior_job = job
        #check if sum is used right here
    avg_turnaround = sum(j.completion - j.arrival for j in jobs)/len(jobs)
    return avg_turnaround, context_switches
def sjf(jobs):
    #Shortest Job First Scheduling
    #The key to this is that all the jobs are going to be sorted
    #by the arrival time first I think
    #Still have to do this for the purpose of the simulation
    #Though simply sorting by burst time feels logical
    #and might be more practical in real life(receiving jobs actively rather than reading from scanned list)
    
    time = 0
    context_switches = 0
    prior_job = None
    #was going to sort by burst, logical error therein
    #need to sort by arrival first so that jobs which
    #do not yet exist do not get loaded into the queue
    arrival_sorted = sorted(jobs, key = lambda x: x.arrival)
    arrived_jobs = []
    finished_jobs = []
   ##### for job in sorted(jobs, key x = x.arrival.burst)
    i = 0
    while len(finished_jobs) < len(arrival_sorted):
        while i < len(arrival_sorted) and arrival_sorted[i].arrival <= time:
            arrived_jobs.append(arrival_sorted[i])
            i += 1
    #check for the shortest job in the list
    #would probably be faster to use a different
    #sorting alg
        #if not
# I think I can rewrite this with a lambda,
#look into how later maybe something to do with min keyword on burst

            
        if arrived_jobs:  #check None vs Null
            shortest_job = arrived_jobs[0]
            for job in arrived_jobs:
                if job.burst < shortest_job.burst:
                    shortest_job = job
            arrived_jobs.remove(shortest_job) #syntax failure point here too

            if prior_job != shortest_job:
                context_switches += 1

            time += shortest_job.burst
            shortest_job.completion = time
            finished_jobs.append(shortest_job)
        else:
            time += 1
    avg_turnaround = sum(j.completion - j.arrival for j in jobs)/len(jobs)
    return avg_turnaround, context_switches
def srtf(jobs):
    #This works by sorting the jobs list into arrival sorted so that the simulation
    #does not jump to jobs not yet arrived
    #But we jump jobs when a shorter job arrives in the queue
    #started_jobs ended up not being used as it was easier to
    #scan just the arrived jobs, and perhaps would actually
    #cause a bug in which new arrived jobs don't get started until
    #old jobs are finished (though in a real system this looks preferable, similar to
    # a concept called ageing that I read about which prevents starvation of longer processes)
    
    time = 0
    completed = 0  # counter of jobs completed
    context_switches = 0
    prior_job = None
    arrival_sorted = sorted(jobs, key = lambda x: x.arrival)
    arrived_jobs = []
    finished_jobs = []
    started_jobs = []  #ended up not needing this, was going to have separate lists but easier to just remove from arrived
    
    current_job = None
    
    i = 0 #index for while loop, important to reset I think
    while completed < len(arrival_sorted):
        while i < len(arrival_sorted) and arrival_sorted[i].arrival <= time:
            arrived_jobs.append(arrival_sorted[i])
            i += 1
            
        if arrived_jobs:
            shortest_job = arrived_jobs[0]
            #dummy shortest job
            for job in arrived_jobs:
                if job.remaining < shortest_job.remaining:
                    shortest_job = job
                #shortest selection
        
            if (current_job != shortest_job):
                context_switches += 1
        #had to switch jobs thus context switch
        #Now we step down the remaining burst time
        #of shortest job and we step up time since epoch
            shortest_job.remaining -= 1
            time += 1
            if (shortest_job.remaining == 0):
                shortest_job.completion = time
                finished_jobs.append(shortest_job)
                arrived_jobs.remove(shortest_job)
                completed += 1
            current_job = shortest_job
                #assign current job after first 
        else:
            time += 1  # Time must go on, I think this is right
    avg_turnaround = sum(j.completion - j.arrival for j in jobs) / len(jobs)
    return avg_turnaround, context_switches
def round_robin(jobs):
    quantum = 1
    time = 0
    completed = 0
    context_switches = 0
    current_job = None

    arrival_sorted = sorted(jobs, key = lambda x: x.arrival)
    round_robin_queue = []

    i = 0

    while completed < len(jobs):

        while i < len(arrival_sorted) and arrival_sorted[i].arrival <= time:
            round_robin_queue.append(arrival_sorted[i])
            i += 1

        if round_robin_queue:
            #Debug pointIf Iremeber right this should remove from front of queue
            job = round_robin_queue.pop(0)

            if (current_job is not None and current_job != job):
                context_switches += 1

            run_time = min(quantum, job.remaining)
            job.remaining -= run_time
            time += run_time
            #This while loop is important, things go rather poorly without it
            #it is necessary in order to append new procs to queue as they arrive
            
            while i < len(arrival_sorted) and arrival_sorted[i].arrival <= time:
                round_robin_queue.append(arrival_sorted[i])
                i += 1

            if job.remaining == 0:
                job.completion = time
                completed += 1
            else:
                round_robin_queue.append(job)

            current_job = job

        else:
            time += 1
            
    avg_turnaround = sum(j.completion - j.arrival for j in jobs) / len(jobs)
    return avg_turnaround, context_switches
def reset_jobs(original):
    jobs = read_data()
    return jobs
def main():
    #loads in data and displays our info
    jobs_from_data = read_data()
    avg, cs = fcfs(reset_jobs(jobs_from_data))
    print("FCFS:", avg)
    print("FCFS Context Switches:",cs)

    avg, cs = sjf(reset_jobs(jobs_from_data))
    print("SJF:",avg)
    print("SJF Context Switches:",cs)

    avg, cs = srtf(reset_jobs(jobs_from_data))
    print("SRTF",avg)
    print("SRTF Context Switchees:",cs)

    avg, cs = round_robin(reset_jobs(jobs_from_data))
    print("Round Robin:",avg)
    print("Round Robin Context Switches",cs)


main()
    

