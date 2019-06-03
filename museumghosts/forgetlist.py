import time


class Forgetlist:
    class _Node:
        def __init__(self, payload, timestamp):
            self.payload = payload
            self.timestamp = timestamp

    def __init__(self, duration, clock=None, maxsize=2 ** 16):
        self._duration = duration
        self._idx = 0
        self._lst = []
        self.clock = time.time if clock is None else clock  # primarily for mocking
        self.start = self.clock()
        self.maxsize = maxsize

    def now(self):
        return round(self.clock() - self.start, 3)

    def _valid(self, idx=None):
        if idx is None:
            idx = self._idx
        now = self.now()
        diff = now - (self._lst[idx].timestamp + self._duration)
        return diff < 0

    @property
    def duration(self):
        return self._duration

    def __ffw(self):
        if self._idx > self.maxsize:
            self._lst = self._lst[self._idx :]
            self._idx = 0
        while self._idx < len(self._lst) and not self._valid():
            self._idx += 1

    def append(self, obj):
        self._lst.append(Forgetlist._Node(obj, timestamp=self.now()))

    def __iter__(self):
        self.__ffw()
        i = self._idx
        while i < len(self._lst):
            if self._valid(i):
                yield self._lst[i].payload
            i += 1

    def __len__(self):
        self.__ffw()
        return len(self._lst) - self._idx

    def __contains__(self, obj):
        self.__ffw()
        for elt in self:
            if elt.payload == obj:
                return True
        return False

    def __getitem__(self, idx):
        self.__ffw()
        return (
            self._lst[self._idx + idx].payload if idx >= 0 else self._lst[idx].payload
        )

    def __str__(self):
        elts = ",".join([str(x) for x in self])
        return "<{} ⏱ [{}]>".format(self.now(), elts)
