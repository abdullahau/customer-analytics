# Collections - implements specialized container datatypes providing alternatives to Python’s general purpose built-in containers, dict, list, set, and tuple.
# https://docs.python.org/3/library/collections.html

# namedtuple - assign meaning to each position in a tuple and allow for more readable, self-documenting code. 
# They can be used wherever regular tuples are used, and they add the ability to access fields by name instead of position index.
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

p = Point(x=11, y=22)   # instantiate with positional or keyword arguments
p[0] + p[1]             # indexable like the plain tuple (11, 22)

x, y = p                # unpack like a regular tuple
x, y

p.x + p.y               # fields also accessible by name

p                       # readable __repr__ with a name=value style

# In addition to the methods inherited from tuples, named tuples support three additional methods and two attributes.
# ._make(iterable)
# ._asdict()
# ._replace()
# ._fields
# ._field_defaults

# ._make(iterable) - makes a new instance from an existing sequence or iterable
t = [11, 22]
p_t = Point._make(t)
p_t

# ._asdict() - return a new dict which maps field names to their corresponding values
p = Point(x=11, y=22)
p._asdict()

# ._replace() - return a new instance of the named tuple replacing specified fields with new values
p = Point(x=11, y=22)
p._replace(x=33)

# _fields - Tuple of strings listing the field names
p._fields            # view the field names

Color = namedtuple('Color', 'red green blue')
Pixel = namedtuple('Pixel', Point._fields + Color._fields)
Pixel(11, 22, 128, 255, 0)

# ._field_defaults - Dictionary mapping field names to default values
Account = namedtuple('Account', ['type', 'balance'], defaults=[0]) # defaults are applied to the rightmost parameters
Account._field_defaults
Account('premium')

tab = namedtuple('Tab', ['x', 'y', 'z'], defaults=(1,2)) # x will be a required argument, y will default to 1, and z will default to 2.
tab._field_defaults


# To retrieve a field whose name is stored in a string, use the getattr() function:
getattr(p, 'x')

# To convert a dictionary to a named tuple, use the double-star-operator
d = {'x': 11, 'y': 22}
Point(**d)

# Since a named tuple is a regular Python class, it is easy to add or change functionality with a subclass. 
# Here is how to add a calculated field and a fixed-width print format:
class Point(namedtuple('Point', ['x', 'y'])):
    __slots__ = ()  #  sets __slots__ to an empty tuple. This helps keep memory requirements low by preventing the creation of instance dictionaries.
    @property
    def hypot(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    def __str__(self):
        return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)

for p in Point(3, 4), Point(14, 5/7):
    print(p)


# deque 