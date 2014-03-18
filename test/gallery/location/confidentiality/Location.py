'''
Location example for Jeeves with confidentiality policies.
'''
from abc import ABCMeta, abstractmethod
from macropy.case_classes import macros, enum

import JeevesLib
from sourcetrans.macro_module import macros, jeeves


class InternalError(Exception):
  def __init__(self, message):
    self.message = message

# Definitions of locations.
@jeeves
class Location:
  __metaclass__ = ABCMeta
  @abstractmethod
  def isIn(self, loc):
    return False
class GPS(Location):
  def __init__(self, latitude, longitude, city=None):
    self.latitude = latitude
    self.longitude = longitude
    self.city = city
  def __eq__(self, other):
    return (isinstance(other, GPS) and (self.latitude == other.latitude)
      and (self.longitude == other.longitude))
  def isIn(self, loc):
    if isinstance(loc, GPS):
      return self == loc
    elif isinstance(loc, City):
      return self.city == loc
    elif isinstance(loc, Country):
      return self.city.country == loc
    else:
      raise InternalError("A location must be a GPS, City, or Country.")
class City(Location):
  def __init__(self, city, country):
    self.city = city
    self.country = country
  def __eq__(self, other):
    return (isinstance(other, City) and (self.city == other.city)
      and (self.country == other.country))
  def isIn(self, loc):
    if isinstance(loc, GPS):
      return False
    elif isinstance(loc, City):
      return self == loc
    elif isinstance(loc, Country):
      return self.country == loc
    else:
      raise InternalError("A location must be a GPS, City, or Country.")
class Country(Location):
  def __init__(self, name):
    self.name = name
  def __eq__(self, other):
    return isinstance(other, Country) and self.name == other.name
  def isIn(self, loc):
    if isinstance(loc, GPS):
      return False
    elif isinstance(loc, City):
      return False
    elif isinstance(loc, Country):
      return self == loc
    else:
      raise InternalError("A location must be a GPS, City, or Country.")

# Users have a user ID and a location.
@jeeves
class User:
  def __init__(self, userId, location, friends=[]):
    self.userId = userId
    self.location = location
    self.friends = list(friends)
  def addFriend(self, friend):
    self.friends.append(friend)
  def isFriends(self, other):
    return JeevesLib.jhas(self.friends, other)
  def prettyPrint(self):
    return str(self.userId)

class LocationNetwork:
  def __init__(self, users=[]):
    self.users = users

  @jeeves
  def countUsersInLocation(self, loc):
    sum = 0
    for user in self.users:
      if user.location.isIn(loc):
        sum += 1
    return sum
