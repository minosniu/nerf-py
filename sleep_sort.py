import os
import time, thread

def ssort(data, *args):
    if data == []: return 0
    thread.start_new_thread(ssort, (data[1:], 1))
    time.sleep(0.001 * data[0])
    print data[0],
    return 0


if __name__ == '__main__':
    x = [100, 2, 3, 1, 4]
    ssort(x)
