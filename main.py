from timeit import timeit
import functools
import math

import params


def riemann_sum(start, stop, the_func, _, width):
    if width == 0:
        width = stop - start
    total = 0
    while start < stop:
        if start + width > stop:
            width = stop - start
        total += the_func(start) * width
        start += width
    return total


def trapezoid(start, stop, the_func, _, width):
    if width == 0:
        width = stop - start
    total = 0
    last = the_func(start)
    start += width
    if start > stop:
        return (last + the_func(stop)) * width / 2
    while start < stop:
        if start + width > stop:
            width = stop - start
        total += (last + (last := the_func(start))) * width / 2
        start += width
    return total


def wikipedia_adaptive(start, stop, f, _, initial_step_size, error_size):
    x = start
    width = initial_step_size
    total = 0
    while x < stop:
        # print(width, abs(f(x) - f(x + width)), error_size, x, stop)
        if x + width > stop:
            width = stop - x  # At end of unit interval, adjust last step to end stop
            total += f(x) * width
            break
        if abs(f(x) - (new := f(x + width))) > error_size:
            width *= 0.5
        else:
            total += f(x) * width
            x += width
            if abs(new - f(x + width)) < error_size:
                width *= 1.1  # Avoid wasting time on tiny steps.
    return total


def new_adaptive_linear(start, stop, f, df, error_size):
    x = start
    total = 0
    while x < stop:
        width = abs(error_size / df(x))
        if x + width > stop:
            width = stop - x
        total += f(x) * width
        x += width
    return total


def new_adaptive_exponential(start, stop, f, df, error_size):
    x = start
    total = 0
    while x < stop:
        width = error_size / (abs(df(x)) + 1)
        if x + width > stop:
            width = stop - x
        total += f(x) * width
        x += width
    return total


class ParamVariation:
    def __init__(self, function, initial_params, index_to_insert, start, stop):
        self.func = function
        self.params = initial_params
        self.index = index_to_insert
        self.max = start
        self.min = stop
        self.start = start
        self.stop = stop

    def iterate_params(self):
        step = (self.stop - self.start) / 1000
        start = self.start - step
        return (self.params[:self.index] + (i,) + self.params[self.index:] for i in
                (start := (start+step) for j in range(1000)))

    def calc_endpoints(self, test_func):
        self.start = params.get_param(self.func, test_func, self.params, self.index, 0.1, self.max)
        self.stop = params.get_param(self.func, test_func, self.params, self.index, 0.1, self.min)


class FuncIntDiff:
    def __init__(self, function, integral, derivative, start, stop, func_name):
        self.func = function
        self.int = integral
        self.diff = derivative
        self.start = start
        self.stop = stop
        self.name = func_name

    def check_approx(self, check_func, check_param):
        check_param = (self.start, self.stop, self.func, self.diff, *check_param)
        return (1 / abs(check_func(*check_param) - self.int(self.stop) + self.int(self.start)),
                timeit(functools.partial(check_func, *check_param), number=100))


functions_to_test = (
    FuncIntDiff(lambda x: (x + 1) ** 2, lambda x: (x ** 3) / 3 + x ** 2 + x, lambda x: 2 * (x + 1), 0, 10, "x+1 square"),
    FuncIntDiff(lambda x: math.sqrt(x), lambda x: (2/3)*(x**(3/2)), lambda x: 1/(2*math.sqrt(x)), 1, 5, "sqrt x"),
    FuncIntDiff(lambda x: math.exp(-x), lambda x: -math.exp(-x), lambda x: -math.exp(-x), 0, 2, "exp -x"),
)

variations = (
    ParamVariation(riemann_sum, tuple(), 0, 15, 1000),
    ParamVariation(trapezoid, tuple(), 0, 15, 1000),
    ParamVariation(wikipedia_adaptive, (0.1,), 1, 15, 1000),
    ParamVariation(new_adaptive_linear, tuple(), 0, 15, 1000),
    ParamVariation(new_adaptive_exponential, tuple(), 0, 15, 1000),
)

if __name__ == "__main__":
    for func in functions_to_test:
        with open(func.name + ".csv", "w") as file:
            print(",score," + ",".join(str(i.func).split()[1] for i in variations), file=file)
            for i, var in enumerate(variations):
                var.calc_endpoints(func)
                name = str(var.func).split()[1]
                print(func.name + ": " + name)
                for param in var.iterate_params():
                    # print(param)
                    time = func.check_approx(var.func, param)
                    print(name + "," + str(time[0]) + "," * (i + 1) + str(time[1]) + "," * (len(variations) - i - 1),
                          file=file)
                    # prints error then time taken
