from macropy.case_classes import macros, enum

@enum
class RoleType:
  Patient, Doctor, Psychiatrist, Nurse, Pharmacist, Nurse, Pharmacist
  InsuranceProvider

class Action:
  class Read:
    def __init__(self, v):
      self.v = v
  class Write:
    def __init__(self, v):
      self.v = v
  class Annotate:
    def __init__(self, v):
      self.v = v
  class Delete:
    def __init__(self, v):
      self.v = v
  class Search:
    pass
  class ConsentTo:
    def __init__(self, p):
      self.p = p
  class Activate:
    def __init__(self, r):
      self.r = r

# This is a kind of permission.
class Permit:
  def __init__(self, prin, action):
    self.prin = prin
    self.action = action

class Attribute:
  class CanBeInRole:
    def __init__(self, prin, role):
      self.prin = prin
      self.role = role
    def __eq__(self, other):
      return self.prin == other.prin and self.role == other.role
  class ActiveRole:
    def __init__(self, prin, role):
      self.prin = prin
      self.role = role
    def __eq__(self, other):
      return self.prin == other.prin and self.role == other.role
  class IsTreating:
    def __init__(self, p1, p2):
      self.p1 = p1
      self.p2 = p2
      return self.p1 == other.p1 and self.p2 == other.p2

class AuthState:
  def __init__(self):
    self.attribs = []
  # Add attribute etc.
  def __contains__(self, item):
    item in self.attribs
  def addElt(self, elt):
    self.attribs.append(elt)

'''
n :: attribute => authstate => P
assume forall (a:attribute) (tl:authstate). In a (ACons a tl)
assume forall (a:attribute) (b:attribute) (tl:authstate). In a tl => In a (ACons b tl)
assume forall (a:attribute). (not (In a ANil))
assume forall (a:attribute) (b:attribute) (tl:authstate). ((not (In a tl)) && (not (a=b)))
  => (not (In a (ACons b tl)))
'''
class Sign:
  def __init__(self, authstate):
    self.authstate = authstate
  def __eq__(self, other):
    return self.authstate == other.authstate

'''
type GrantedIn :: permission => authstate => P
(* Some commonly used type abbreviations *)
type permit (p:prin) (a:action) = s:authstate { GrantedIn (Permit p a) s}
type authcontains (a:attribute) = x:authstate { In a x}

(* prenex and implies rewritten *)
type extendedstate (s:authstate) (a:attribute) =
    x:authstate { (forall (b:attribute). (In a x) && ((not (In b s)) || (In b x)))}

assume Skolemize_extendedstate:
  forall (s:authstate) (a:attribute) (x:authstate).
    ((not (forall (b:attribute).     ((In a x) && ((not (In b s)) || (In b x)))))
       => (exists (b:attribute). not ((In a x) && ((not (In b s)) || (In b x)))))
'''

'''
Checks if 
'''
def checkIn(a, authState):
  return a in authState
