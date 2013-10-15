'''
Authentication demo example for Jeeves with confidentiality policies.
'''
#from macropy.case_classes import macros, case
import JeevesLib

class User:
  def __init__(self, userId):
    self.userId = userId

class AuctionContext():
  def __init__(self, user, time, bids):
    self.user = user
    self.time = time
    self.bids = bids

class Bid:
  def __init__(self, value, owner, policy):
    lab = JeevesLib.mkLabel ()
    # TODO: Add policy that the output channel has to be either the owner or
    # satisfy the policy on it (policy(oc)).
    JeevesLib.restrict(lab
        , lambda oc: JeevesLib.jor(
            lambda: oc.user == owner, lambda: policy(oc)))
    self.value = JeevesLib.mkSensitive(lab, value, -1)
    self.owner = owner
