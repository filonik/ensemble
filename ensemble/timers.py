import time

from glue import gl, wgl

DEFAULT_FRAMES_PER_SECOND = 60


class VirtualClock(object):
    def __init__(self):
        self._time = 0.0
    
    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self, value):
        self._time = value
    
    def tick(self):
        pass
    
    def __str__(self):
        return "{}({})".format(type(self).__name__, self.time)

class SystemClock(object):
    @property
    def time(self):
        return time.time()
    
    def tick(self):
        pass
    
    def __str__(self):
        return "{}({})".format(type(self).__name__, self.time)

class SynchronisedClock(object):
    def __init__(self, clock):
        self._clock = clock
        self._delta = 0.0
    
    @property
    def time(self):
        return self._clock.time + self._delta
    
    @time.setter
    def time(self, value):
        self._delta = value - self._clock.time
    
    def tick(self):
        self._clock.tick()
    
    def __str__(self):
        return "{}({})".format(type(self).__name__, self.time)

class FrameClock(object):
    def __init__(self, frames_per_second=DEFAULT_FRAMES_PER_SECOND):
        super().__init__()
        
        self._frames_per_second = frames_per_second
        self._seconds_per_frame = 1.0/frames_per_second
        
        self._frame = 0
    
    @property
    def time(self):
        return self._frame * self._seconds_per_frame
    
    @time.setter
    def time(self, value):
        self._frame = int(value * self._frames_per_second)
    
    def tick(self):
        self._frame += 1
    
    def __str__(self):
        return "{}({},{})".format(type(self).__name__, self._frame, self.time)

class SwapGroupClock(object):
    def __init__(self, frames_per_second=DEFAULT_FRAMES_PER_SECOND):
        super().__init__()
        
        self._frames_per_second = frames_per_second
        self._seconds_per_frame = 1.0/frames_per_second
        
        self._frame = 0
        
        self._hdc = wgl.get_current_dc()
    
    @property
    def time(self):
        return self._frame * self._seconds_per_frame
    
    def tick(self):
        self._frame = wgl.query_frame_count(self._hdc)
    
    def reset(self):
        try:
            # TODO: This only succeeds on master.
            wgl.reset_frame_count(self._hdc)
        except RuntimeError:
            pass
    
    def __str__(self):
        return "{}({},{})".format(type(self).__name__, self._frame, self.time)


class Timer(object):
    def __init__(self, clock=None):
        super().__init__()
        
        self._clock = clock
        
        self._start = None
        self._pause = None
    
    @property
    def started(self):
        return not self._start is None
    
    @property
    def paused(self):
        return not self._pause is None
    
    @property
    def current(self):
        #return self._clock.time % (24.0*60.0*60.0)
        return self._pause if self.paused else self._clock.time
    
    @property
    def elapsed(self):
        if self.started:
            return self.current - self._start
        return 0.0
    
    def start(self, time=None):
        value = (self._pause - self._start) if self.started and self.paused else 0
        time = self._clock.time if time is None else time
        self._start = time - value
        self._pause = None
    
    def pause(self, time=None):
        time = self._clock.time if time is None else time
        self._pause = time
    
    def stop(self, time=None):
        time = self._clock.time if time is None else time
        self._start = None
        self._pause = None
    
    def seek(self, value, time=None):
        time = self._clock.time if time is None else time
        if self.started:
            self._start = time - value
        if self.paused:
            self._pause = time
    
    def toggle(self, time=None):
        if not self.started or self.paused:
            self.start(time)
        else:
            self.pause(time)
    
    def update(self):
        self._clock.tick()
