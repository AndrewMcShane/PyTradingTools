from collections import deque
#==============================================#
#
#     In this file (in-order as they appear):
#         RollingQueue
#
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class RollingQueue:
    '''
    A fixed-size queue structure that automatically

    removes the first element from the queue when at capacity.

    Rolling Queues can be iterated and imlpement an __iter__ method.

    Properties
    ----------
    capacity:
        the max size of the queue

    size:
        the current size of the queue

    Methods
    -------
    isEmpty():
        returns if the queue is empty or not.

    atCapacity():
        returns if the queue is at capacity or not.

    peek():
        returns the element at the front of the queue, or None if empty.

    enqueue(value : object):
        adds an object into the queue. If at capacity, return the removed element, otherwise None.

    dequeue() raises ValueError:
        remove the first element from the rolling queue. Raises ValueError if empty.

    __iter__():
        returns an iterable of the rolling queue data

    Protected
    ---------
    _capacity : int
        maximum size of the rolling queue

    _size : int
        current size of the queue

    data: list
        underlying data  of the queue

    '''
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be greater than 0.")
        # Read only intention.
        self._capacity = capacity
        self._size = 0

        self.data = deque()

    def __iter__(self):
        return iter(self.data)

    def isEmpty(self):
        '''returns True if the rolling queue contains no elements'''
        return self._size == 0

    def atCapacity(self):
        '''returns True if the rolling queue is at capacity and will roll off old values'''
        return self.size == self._capacity

    def peek(self):
        '''Return the first element in the queue, otherwise None.'''
        if not self.isEmpty():
            return self.data[0]
        else:
            return None

    def enqueue(self, value):
        '''Enqueues an object to the list. If at capacity, returns the removed object, else None.'''
        removed = None
        if self._size == self._capacity:
            removed = self.data.popleft()
        else:
            self._size += 1

        self.data.append(value)

        return removed

    def dequeue(self):
        '''Remove the element in front of the queue and return it. Raises ValueError if empty.'''
        if self.isEmpty():
            raise ValueError("the queue is empty.")
        else:
            self._size -= 1
            return self.data.popleft()
    @property
    def capacity(self):
        '''The capacity of the rolling queue. Read-only'''
        return self._capacity

    @property
    def size(self):
        '''The current size of the rolling queue. Read-only'''
        return self._size
