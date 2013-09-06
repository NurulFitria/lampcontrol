import sched
import threading
import time

scheduler = sched.scheduler(time.time, time.sleep)

# Set up a global to be modified by the threads
counter = 0

def increment_counter(name):
    global counter
    print 'EVENT:', time.time(), name
    counter += 1
    print 'NOW:', counter
    time.sleep(10)


print 'START:', time.time()
e1 = scheduler.enter(0, 1, increment_counter, ('E1',))
e2 = scheduler.enter(0, 1, increment_counter, ('E2',))

# Start a thread to run the events
t = threading.Thread(target=scheduler.run)
t.start()

# Back in the main thread, cancel the first scheduled event.
#scheduler.cancel(e1)

# Wait for the scheduler to finish running in the thread
t.join()

print 'FINAL:', counter