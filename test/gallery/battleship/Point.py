class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def distance(self, other):
    return abs(self.x - other.x) + abs(self.y - other.y)

  def inLine(self, other):
    return self.x == other.x or self.y == other.y
