from operator import mul
from functools import reduce, partial
from fractions import Fraction
from random import randint

# This example demonstrates some of Python features for functional
# programming. This means that functions are treated as data that
# can be stored to variables, passed to other functions, returned
# from functions as results, created on the fly as needed, etc.


def is_positive(n):
    return n > 0


def square(n):
    return n * n


# Functional programming basic commands map, filter and reduce.
# Note that these both return iterator objects instead of doing
# the computation right away, so we force the computation to
# take place with list().

print("The positive elements are: ", end='')
print(list(filter(is_positive, [-7, 8, 42, -1, 0])))

print("The squares of first five positive integers are: ", end='')
print(list(map(square, [1, 2, 3, 4, 5])))

# Reduce is a handy operation to repeatedly combine first two
# elements of given sequence into one, until only one remains.

print(reduce(mul, [1, 2, 3, 4, 5], 1))  # 120 = 5!


def falling_power(n, k):
    return reduce(mul, reversed(range(n-k+1, n+1)))


def rising_power(n, k):
    return reduce(mul, range(n, n+k))


print(f"Falling power of 10 to 3 equals {falling_power(10, 3)}.")
print(f"Ordinary power of 10 to 3 equals {10**3}.")
print(f"Rising power of 10 to 3 equals {rising_power(10, 3)}.")

# Determine whether the sequence x, f(x), f(f(f(x))), ... becomes
# periodic after some point. A computer science classic without
# needing more than constant amount of extra memory.


def is_eventually_periodic(f, x, giveup=1000):
    tortoise, hare = x, f(x)
    while tortoise != hare and giveup > 0:
        tortoise = f(tortoise)
        hare = f(f(hare))
        giveup -= 1
    return tortoise == hare

# Next, let's examine how functions can be given to other functions
# as parameters, and returned as results to the caller. To demo this,
# let's write a function negate that can be given any predicate, and
# it creates and returns a function that behaves as the negation of
# its parameter.


def negate(f):
    # Nothing says that we can't define a function inside a function.
    # Since we don't know what parameters f takes, we write this
    # function to accept any arguments and keyword arguments that
    # it simply passes down to the original f without further ado.

    def negated_f(*args, **kwargs):
        return not f(*args, **kwargs)

    # Return the function that was just defined.
    return negated_f

# Let's try this out by negating the following simple function.


def is_odd(x):
    return x % 2 != 0


is_even = negate(is_odd)           # I can't even...
print(is_even)                     # <function result at ....>
print(f"Is 2 even? {is_even(2)}")  # True
print(f"Is 3 even? {is_even(3)}")  # False


# Partial evaluation or "currying" means setting some of the
# arguments of a function to stone, to create a new function
# that takes fewer parameters but works otherwise the same as
# the original function.

def foo(a, b, c):
    return a + (b * c)


# Create a version of foo with parameter b fixed to -1.

foob = partial(foo, b=-1)
print(f"After partial, foob(2, 5)={foob(a=2, c=5)}.")

# Sometimes functions can take a long time to calculate, but we
# know that they will always return the same result for the same
# arguments. The function memoize takes an arbitrary function as
# an argument, and creates and returns a new function that gives
# the same results as the original. However, it remembers what
# it has already computed, and simply looks up those results that
# have previously been calculated.


def memoize(f):
    results = {}   # empty dictionary, as nothing has been computed yet

    def lookup_f(*args):
        res = results.get(args, None)
        if res is None:
            res = f(*args)       # calculate the result
            results[args] = res  # and store it in dictionary
        return res

    # Alias the local variable so it can be seen from outside.
    lookup_f.results = results
    # Result is a function that can be called same as original.
    return lookup_f

# The famous Fibonacci series. This naive implementation would take
# nearly forever if called for n in largish double digits.


def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)


# print(fib(200))    # way longer than the lifetime of universe
oldfib = fib         # keep a reference to the original slow function
fib = memoize(fib)   # however, memoization makes it all smooth
print(fib(200))      # 453973694165307953197296969697410619233826

print(f"fib is oldfib = {fib is oldfib}")  # False
print(f"The memoized fib contains {len(fib.results)} cached results.")

# Hofstadter's recursive Q-function, memoized for efficiency.
# http://paulbourke.net/fractals/qseries/


@memoize
def hof_q(n):
    if n < 3:
        return 1
    else:
        return hof_q(n - hof_q(n - 1)) + hof_q(n - hof_q(n - 2))


print(f"HofQ(100) = {hof_q(100)}.")

# We can also perform the memoization explicitly. Since the function
# arguments are nonnegative integers, the computed results can be
# stored in a list. Otherwise, some kind of dictionary would be used.

Q = [0, 1, 1]


def hof_qt(n):
    if n >= len(Q):
        for i in range(len(Q), n + 1):
            Q.append(Q[i - Q[i-1]] + Q[i - Q[i-2]])
    return Q[n]


print(f"HofQt(1000000) = {hof_qt(1000000)}.")
print(f"HofQt table contains {len(Q)} cached entries.")

# An interesting problem from "Concrete Mathematics". A row of aging
# barrels is filled with wine at year 0. After each year, a portion
# of the aged wine from each barrel is poured in the next barrel from
# end to beginning. The wine taken from last barrel is bottled for
# sale, and the first barrel is refilled with new wine. What is the
# composition of the given barrel after the number of years?


@memoize
def wine(barrel, age, year, pour=Fraction(1, 2)):
    # Imaginary "zero" barrel to represent incoming flow of new wine.
    if barrel == 0:
        return Fraction(1) if age == 0 else 0
    # In the initial state, all barrels consist of new wine.
    elif year == 0:
        return 1 if age == 0 else 0
    # Recursive formula for proportion of wine of age a.
    else:
        return (1 - pour) * wine(barrel, age - 1, year - 1) +\
               pour * wine(barrel - 1, age - 1, year - 1)


year = 10
print(f"After year {year}, the barrel compositions are:")
for b in range(1, 6):
    comp = [str(wine(b, a, year)) for a in range(1, year + 1)]
    print(f"Barrel {b}: {', '.join(comp)}.")


# Wouldn't it be "groovy" to memoize the memoize function itself, so
# that if some function has already been memoized, the same function
# won't be redundantly memoized again, but its previously memoized
# version is returned? Isn't duck typing just dandy?

memoize = memoize(memoize)


def divisible_by_3(x):
    return x % 3 == 0


f1 = memoize(divisible_by_3)
f2 = memoize(divisible_by_3)      # already did that one
print(f"f1 is f2 = {f1 is f2}.")  # True


# We can use the memoization technique to speed up checking whether
# the so-called Collatz sequence starting from the given number
# eventually reaches 1. The function collatz(n) tells how many
# steps this needs.

@memoize
def collatz(n):
    if n == 1:
        return 0
    elif n % 2 == 0:
        return 1 + collatz(n // 2)
    else:
        return 1 + collatz(3 * n + 1)


lc = max(((collatz(i), i) for i in range(1, 10**6)))
print(f"Collatz sequence from {lc[1]} contains {lc[0]} steps.")
print(f"Stored {len(collatz.results)} results. Some of them are:")

for _ in range(10):
    v = randint(1, 10**6 - 1)
    print(f"From {v}, sequence contains {collatz.results[(v,)]} steps.")

# Sometimes we use some simple function only in one place. With lambdas,
# such a function can be defined anonymously on the spot, provided that
# the function can written as a single expression. For example, use the
# previous negate to a lambda predicate that checks if its parameter is
# negative or zero, to give a function is_positive.

is_positive = negate(lambda x: x <= 0)
print(is_positive(2))   # True
print(is_positive(-2))  # False

# The famous Thue-Morse sequence for "fairly taking turns". To
# illustrate the power of memoization, let's use a global count
# of how many times the function has been called.

__tm_call_count = 0


@memoize
def thue_morse(n, sign):
    global __tm_call_count
    __tm_call_count += 1
    if n < 2:
        return f"{str(sign)}"
    else:
        return thue_morse(n - 1, sign) + thue_morse(n - 1, 1 - sign)


print("Thue-Morse sequences from 2 to 10 are:")
for i in range(2, 11):
    print(f"{i}: {thue_morse(i, 0)}")

# Memoization of recursions that have repeating subproblems is awesome.
print(f"Computing those required {__tm_call_count} recursive calls.")


# The next function can be given any number of functions as parameters,
# and it creates and returns a function whose value is the maximum of
# the results of any of these functions.

def max_func(*args):
    funcs = args

    def our_max_f(*args):
        return max((f(*args) for f in funcs))

    return our_max_f


# Try that one out with some polynomials created as lambdas, to be
# used as throwaway arguments of max_func.

f = max_func(lambda x: -(x*x) + 3*x - 7,   # -x^2+3x-7
             lambda x: 4*x*x - 10*x + 10,  # 4x^2-10x+10
             lambda x: 5*x*x*x - 20)       # 5x^3-20

print("Maximums given by the three functions for -5, ..., 5 are:")
print([f(x) for x in range(-5, 5)])

# Here is another function decorator that maintains a count attribute
# to keep track of how many times the function has been called. Since
# nested functions cannot reassign a variable in the outer function,
# but can change the contents of the object that the variable refers
# to, we define the variable count to be a one-element mutable list.
# Even though we can't reassign this variable, we can reassign the
# value of its one element, following the letter of the law if not
# the spirit.


def counter(f):
    count = [0]

    def cf(*args, **kwargs):
        nonlocal count
        count[0] += 1
        return f(*args, **kwargs)

    def get_count():
        return count[0]

    def reset_count():
        count[0] = 0

    # This is ugly, but necessary. As so many other things in life.
    cf.get_count = get_count
    cf.reset_count = reset_count
    return cf


# Demonstrate the previous decorator by counting how many times the
# sorting algorithm computes the given key...

def kf(x):
    return x


kf = counter(kf)
sorted(range(-100, 100), key=kf, reverse=True)
print(f"The key was computed {kf.get_count()} times.")

# The key is computed only once per element, cached and then used in
# element comparisons. Let's see if this changes for a wider range...

kf.reset_count()
sorted(range(-100000, 100000), key=kf, reverse=True)
print(f"The key was computed {kf.get_count()} times.")

# Another sometimes handy feature of Python is its ability to compile
# and execute new code dynamically on the fly, in any desired context.
# However, be careful using eval and exec to strings that originate
# from outside your program, as this opens a doorway for a malicious
# attacker to execute hostile code in your computer.

myglobals = {"x": 10, "y": 20}
code = "print (x+y)"   # a super simple example program to run
exec(code, myglobals)  # 30


def myfun():
    x = 40
    y = 50
    # The built-in functions globals and locals return dictionaries
    # of the current global and local variables, respectively.
    return locals()


eval(code, myfun())    # 90
