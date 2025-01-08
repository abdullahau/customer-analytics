# https://martinheinz.dev/blog/52
from more_itertools import divide

data = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]

[list(l) for l in divide(3, data)] #  [['first', 'second', 'third'], ['fourth', 'fifth'], ['sixth', 'seventh']] 