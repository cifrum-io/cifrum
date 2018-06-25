import pandas as pd
import numpy as np


class TimeValue:
    def __init__(self, value, start_period: pd.Period, end_period: pd.Period, derivative):
        self.value = value
        self.start_period = start_period
        self.end_period = end_period
        self.derivative = derivative

    def __validate(self, time_value):
        if self.start_period != time_value.start_period:
            raise ValueError('start periods are incompatible')
        if self.end_period != time_value.end_period:
            raise ValueError('end periods are incompatible')
        if self.derivative != time_value.derivative:
            raise ValueError('derivatives are incompatible')

    def apply(self, fun, *args):
        args_raw = [self.value]
        for arg in args:
            if isinstance(arg, TimeValue):
                self.__validate(arg)
                args_raw.append(arg.value)
            elif isinstance(arg, (int, float, complex)):
                args_raw.append(arg)
            else:
                raise ValueError('argument is of incompatible type')
        ts = TimeValue(value=fun(*args_raw),
                       start_period=self.start_period, end_period=self.end_period,
                       derivative=self.derivative)
        return ts

    def __mul__(self, other):
        return self.apply(lambda x, y: x * y, other)

    def __add__(self, other):
        return self.apply(lambda x, y: x + y, other)

    def __sub__(self, other):
        return self.apply(lambda x, y: x - y, other)

    def __pow__(self, power):
        return self.apply(lambda x, p: x ** p, power)

    def __truediv__(self, other):
        return self.apply(lambda x, y: x / y, other)

    def sqrt(self):
        return self.apply(lambda x: np.sqrt(x))

    def __repr__(self):
        return 'TimeSeries(start_period={}, end_period={}, derivative={}, values={}'.format(
            self.start_period, self.end_period, self.derivative, self.value
        )


class TimeSeries:
    def __init__(self, values, start_period: pd.Period, end_period: pd.Period, derivative):
        if not isinstance(values, np.ndarray):
            raise ValueError('values should be numpy array')
        if len(values) != end_period - start_period + 1:
            raise ValueError('values and period range are of different length')
        self.values = values
        self.start_period = start_period
        self.end_period = end_period
        self.derivative = derivative

    def __validate(self, time_series):
        if self.start_period != time_series.start_period:
            raise ValueError('start periods are incompatible')
        if self.end_period != time_series.end_period:
            raise ValueError('end periods are incompatible')
        if self.derivative != time_series.derivative:
            raise ValueError('derivatives are incompatible')

    def pct_change(self):
        if len(self.values) < 2:
            raise ValueError("Can't compute because of `value` length")
        vals = np.diff(self.values) / self.values[:-1]
        return TimeSeries(values=vals,
                          start_period=self.start_period + 1, end_period=self.end_period,
                          derivative=self.derivative + 1)

    def apply(self, fun, *args):
        if len(args) == 0:
            ts = TimeSeries(values=fun(self.values),
                            start_period=self.start_period, end_period=self.end_period,
                            derivative=self.derivative)
            return ts
        else:
            other = args[0]
            if isinstance(other, TimeSeries):
                self.__validate(other)
                ts = TimeSeries(values=fun(self.values, other.values),
                                start_period=self.start_period, end_period=self.end_period,
                                derivative=self.derivative)
                return ts
            elif isinstance(other, (int, float, complex)):
                ts = TimeSeries(fun(self.values, other),
                                start_period=self.start_period, end_period=self.end_period,
                                derivative=self.derivative)
                return ts
            else:
                raise ValueError('argument is of incompatible type')

    def reduce(self, fun):
        return TimeValue(value=fun(self.values),
                         start_period=self.start_period, end_period=self.end_period,
                         derivative=self.derivative)

    def __mul__(self, other):
        return self.apply(lambda x, y: x * y, other)

    def __add__(self, other):
        return self.apply(lambda x, y: x + y, other)

    def __radd__(self, other):
        return self.apply(lambda x, y: y + x, other)

    def __rsub__(self, other):
        return self.apply(lambda x, y: y - x, other)

    def __sub__(self, other):
        return self.apply(lambda x, y: x - y, other)

    def __truediv__(self, other):
        return self.apply(lambda x, y: x / y, other)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if not (key.step is None or key.step == 1):
                raise ValueError('step value is not supported: {}'.format(key.step))
            pr = pd.period_range(start=self.start_period, end=self.end_period, freq='M')
            pr = pr[key.start:key.stop]
            ts = TimeSeries(values=self.values[key.start:key.stop],
                            start_period=pr.min(), end_period=pr.max(),
                            derivative=self.derivative)
            return ts
        return self.values[key]

    def sqrt(self):
        return self.apply(lambda x: x.sqrt())

    def std(self):
        return self.reduce(lambda x: x.std())

    def mean(self):
        return self.reduce(lambda x: x.mean())

    def sum(self):
        return self.reduce(lambda x: x.sum())

    def prod(self):
        return self.reduce(lambda x: x.prod())

    def cumprod(self):
        return self.apply(lambda x: x.cumprod())

    def __repr__(self):
        return 'TimeSeries(start_period={}, end_period={}, derivative={}, values={}'.format(
            self.start_period, self.end_period, self.derivative, self.values
        )
