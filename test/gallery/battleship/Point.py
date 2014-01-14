class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def distance(self, other):
    return abs(self.x - other.x) + abs(self.y - other.y)

  # Whether to points are in the same line. We use this function to determine
  # whether endpoints are legitimate for placing a ship.
  def inLine(self, other):
    return self.x == other.x or self.y == other.y
