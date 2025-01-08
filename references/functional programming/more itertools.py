# https://martinheinz.dev/blog/52
import more_itertools

# divide - divides iterable into number of sub-iterables
# the length of the sub-iterables might not be the same, as it depends on number of elements being divided and number of sub-iterables
data = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]

div_data = [list(l) for l in more_itertools.divide(3, data)] #  [['first', 'second', 'third'], ['fourth', 'fifth'], ['sixth', 'seventh']] 
print(div_data)

data = [5,6,7,8,9,10]

div_data = [list(l) for l in more_itertools.divide(3, data)] #  [['first', 'second', 'third'], ['fourth', 'fifth'], ['sixth', 'seventh']] 
print(div_data)

# There is one more similar function in more_itertools called `distribute`, it however doesn't maintain order. 
# If you don't care about order you should use distribute as it needs less memory.

# partition - divide iterable using a predicate

# Split based on age - splitting list of dates into recent ones and old ones
from datetime import datetime, timedelta

dates = [
    datetime(2015, 1, 15),
    datetime(2025, 1, 16),
    datetime(2025, 1, 17),
    datetime(2019, 2, 1),
    datetime(2025, 2, 2),
    datetime(2018, 2, 4)
]

is_old = lambda x: datetime.now() - x < timedelta(days=30)

old, recent = more_itertools.partition(is_old, dates) # pass function that performes the perdicate and data to be partitioned
print(list(old))
#  [datetime.datetime(2015, 1, 15, 0, 0), datetime.datetime(2019, 2, 1, 0, 0), datetime.datetime(2018, 2, 4, 0, 0)]
print(list(recent))
#  [datetime.datetime(2025, 1, 16, 0, 0), datetime.datetime(2025, 1, 17, 0, 0), datetime.datetime(2025, 2, 2, 0, 0)]

# Split based on file extension - partitioning files based on their extension. 
# Spliting file name into name and extension and checks whether the extension is in list of allowed ones
files = [
    "foo.jpg",
    "bar.exe",
    "baz.gif",
    "text.txt",
    "data.bin",
]

ALLOWED_EXTENSIONS = ('jpg','jpeg','gif','bmp','png')
is_allowed = lambda x: x.split(".")[1] in ALLOWED_EXTENSIONS

allowed, forbidden = more_itertools.partition(is_allowed, files)
print(list(allowed)) #  ['bar.exe', 'text.txt', 'data.bin']
print(list(forbidden)) #  ['foo.jpg', 'baz.gif']

# consecutive_groups - find runs of consecutive numbers, dates, letters, booleans or any other orderable objects
dates = [
    datetime(2020, 1, 15),
    datetime(2020, 1, 16),
    datetime(2020, 1, 17),
    datetime(2020, 2, 1),
    datetime(2020, 2, 2),
    datetime(2020, 2, 4)
]

ordinal_dates = []
for d in dates:
    ordinal_dates.append(d.toordinal()) # convert date to ordinal

groups = [list(map(datetime.fromordinal, group)) for group in more_itertools.consecutive_groups(ordinal_dates)]
print(groups)

# In this example, we have list of dates, where some of them are consecutive. 
# To be able to pass these dates to consecutive_groups function, we first have to convert them to ordinal numbers. 
# Then using list comprehension we iterate over groups of consecutive ordinal dates created by consecutive_groups and convert them back to `datetime` using `map` and `fromordinal` functions.

# side_effect - cause side-effect when iterating over list of items (writing logs, writing to file, counting number of events that occurred, etc)
num_events = 0

def _increment_num_events(_):
    nonlocal num_events
    num_events += 1

# Iterator that will be consumed
event_iterator = more_itertools.side_effect(_increment_num_events, events)

more_itertools.consume(event_iterator)

print(num_events)
