# http://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Segment:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def is_between(self, c):
        # Check if slope of a to c is the same as a to b ;
        # that is, when moving from a.x to c.x, c.y must be proportionally
        # increased than it takes to get from a.x to b.x .

        # Then, c.x must be between a.x and b.x, and c.y must be between a.y and b.y.
        # => c is after a and before b, or the opposite
        # that is, the absolute value of cmp(a, b) + cmp(b, c) is either 0 ( 1 + -1 )
        #    or 1 ( c == a or c == b)

        a, b = self.a, self.b             

        return ((b.x - a.x) * (c.y - a.y) == (c.x - a.x) * (b.y - a.y) and 
                abs(cmp(a.x, c.x) + cmp(b.x, c.x)) <= 1 and
                abs(cmp(a.y, c.y) + cmp(b.y, c.y)) <= 1)
				
a = Point(0,0)
b = Point(50,100)
c = Point(25,50)
d = Point(0,8)

print Segment(a,b).is_between(c)
print Segment(a,b).is_between(d)				