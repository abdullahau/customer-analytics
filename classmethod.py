import math

class Circle(object):
    'An advanced circle analytics toolkit'
    version = '0.4'
    
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        p = self.__perimeter()
        r = p / math.pi / 2.0
        return math.pi * r ** 2.0
    
    def perimeter(self):
        return 2.0 * math.pi * self.radius
    
    # Alternative constructor
    @classmethod
    def from_bbd(cls, bbd): # use `cls` petermeter to support subclassing
        'Construct a circle from a bounding box diagonal'
        radius = bbd / 2.0 / math.sqrt(2.0)
        return cls(radius)  # return `cls(radius)` instead of `Circle(radius)`

    @staticmethod  # Attach functions to classes - works without instantiating the class
    def angle_to_grade(angle): 
        # A standard method would require creating a new instance just to call a function which needs no 'self' variables or any information about the instance of a `Circle`
        # Adding this function inside the Circle class improves searchability and ensures the function is used in the appropriate context
        'Convert angle in degree to a percentage grade'
        return math.tan(math.radians(angle)) * 100.0   # variables used here do not require information about the instance
    
    __perimeter = perimeter


class Tire(Circle):
    'Tires are circles with an odometer corrected perimeter'
    
    def perimeter(self):
        'Circumference corrected for the rubber'
        return Circle.perimeter(self) * 1.25


std = Circle(2)
print('Radius of the Circle:', std.radius)
print('Area of the Circle:', std.area())
print('Perimeter of the Circle:', std.perimeter())

print()
new = Circle.from_bbd(25)
print('Radius of the Circle:', new.radius)
print('Area of the Circle:', new.area())
print('Perimeter of the Circle:', new.perimeter())

print()
t = Tire.from_bbd(25)
print('Radius of the Circle:', t.radius)
print('Area of the Circle:', t.area())
print('Perimeter of the Circle:', t.perimeter()) # This does not work if `classmethod` returns the class instance rather than `cls`

print()
t = Tire(15)
print('Radius of the Circle:', t.radius)
print('Area of the Circle:', t.area())
print('Perimeter of the Circle:', t.perimeter())

print()
grade = Circle.angle_to_grade(30)
print('Angle:', 30)
print('Grade:', grade)
print('Type:', type(grade))


if __name__ == "__main__":
    print(2.0 * math.pi * 15 * 1.25)
    print(2.0 * math.pi * 15)
    print(math.pi * 15 ** 2.0)
    
    print(math.pi * 15 ** 2.0)