'''
This tests write policies.
'''
import unittest
from sourcetrans.macro_module import macros, jeeves
from fast.ProtectedRef import ProtectedRef, UpdateResult
import JeevesLib

class DummyUser:
  def __init__(self, userId):
    self.userId = userId
  def __eq__(self, other):
    self.userId == other.userId
class DummyContext:
  def __init__(self, user, badUsers):
    self.user = user
    self.badUsers = badUsers

class TestJeevesWrite(unittest.TestCase):
  def setUp(self):
    # reset the Jeeves state
    JeevesLib.init()
    self.nobodyUser = DummyUser(-1)
    self.aliceUser = DummyUser(0)
    self.bobUser = DummyUser(1)
    self.carolUser = DummyUser(2)

  def allowUserWrite(self, user):
    lambda _this: lambda ictxt: lambda octxt: ictxt == user

  '''
  def test_write_allowed_for_all_viewers(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser))
    assert x.update(self.aliceUser, self.aliceUser, 42) == UpdateResult.Success
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 42)
  ''' 

  ''' 
  def test_write_disallowed_for_all_viewers(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser), None)
    assert x.update(self.bobUser, self.bobUser, 42) == UpdateResult.Failure
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 0)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 0)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 0)

  @jeeves
  def test_write_selectively_allowed(self):
    x = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.aliceUser and octxt == self.bobUser)
    assert x.update(self.aliceUser, self.aliceUser, 42) == UpdateResult.Unknown
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 0)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 0)

  def test_permitted_writer_overwrite(self):  
    x = ProtectedRef(0, None, self.allowUserWrite(self.bobUser), None)
    assert x.update(self.aliceUser, self.aliceUser, 42) == UpdateResult.Failure
    assert x.update(self.bobUser, self.bobUser, 43) == UpdateResult.Success
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 43)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 43)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 43)

  def test_restricted_writer_overwrite(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.bobUser), None)
    x.update(self.bobUser, self.bobUser, 43)
    x.update(self.aliceUser, self.aliceUser, 42)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 43)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 43)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 43)

  @jeeves
  def test_output_varies_depending_on_viewer(self):
    x = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.aliceUser and octxt == self.bobUser)
    x.update(self.aliceUser, self.aliceUser(), 42)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 0)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 0)

  @jeeves
  def test_combining_integrity_policies_in_operation(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.bobUser), None)
    x.update(self.bobUser, self.bobUser, 42)
    y = ProtectedRef(2, None, None
      , lambda _this: lambda ictxt: lambda octxt:
          ictxt == self.aliceUser or octxt == self.bobUser)
    y.update(self.aliceUser, self.aliceUser, 43)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v + y.v), 44)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v + y.v), 85)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v + y.v), 44)

  # Alice is allowed to write to x and only Bob is allowed to write to y.
  # Our write policies disallow Bob from accidentally writing a value from
  # Alice into y. (That is, without an explicit endorsement...)
  def test_prevent_flow_of_untrusted_writes(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser), None)
    x.update(self.aliceUser, self.aliceUser, 42)
    y = ProtectedRef(1, None, self.allowUserWrite(self.bobUser), None)
    y.update(self.bobUser, self.bobUser, x.v)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, y.v), 0)
    self.assertEqual(JeevesLib.concretize(self.bobUser, y.v), 0)   

  def test_prevent_flow_of_operations_on_untrusted_writes(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser), None)
    x.update(self.aliceUser, self.aliceUser, 42)
    y = ProtectedRef(1, None, self.allowUserWrite(self.bobUser), None)
    y.update(self.bobUser, self.bobUser, 43)
    z = ProtectedRef(0, None, self.allowUserWrite(self.carolUser), None)
    z.update(self.carolUser, self.carolUser, x.v + y.v)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, z.v), 1)
    self.assertEqual(JeevesLib.concretize(self.bobUser, z.v), 1)
    self.assertEqual(JeevesLib.concretize(self.carolUser, z.v), 1)

  # Alice is allowed to write to x and only Bob is allowed to write to y.
  # Our policy enforcement prevents Alice from influencing values that Bob
  # writes.
  @jeeves
  def test_prevent_untrusted_writes_through_implicit_flows(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser), None)
    x.update(self.aliceUser, self.aliceUser, 42)
    y = ProtectedRef(1, None, self.allowUserWrite(self.bobUser), None)
    y.update(self.bobUser, self.bobUser, 2 if x.v == 42 else 3)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, y.v), 3)
    self.assertEqual(JeevesLib.concretize(self.bobUser, y.v), 3)

  @jeeves
  def test_prevent_implicit_flows_of_confidential_values(self):
    x = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.aliceUser and octxt == self.aliceUser)
    x.update(self.aliceUser, self.aliceUser, 42)
    y = ProtectedRef(1, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.bobUser or ctxt == self.aliceUser)
    y.update(self.bobUser, self.bobUser, 2 if x.v == 42 else 3)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, y.v), 2)
    self.assertEqual(JeevesLib.concretize(self.bobUser, y.v), 3)

  # If Alice and Bob are allowed to write to x and y respectively, then
  # x + y should be allowed to be written to a value where they are both
  # allowed to write.
  def test_combining_values_into_permissive_write(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.bobUser), None)
    x.update(self.bobUser, self.bobUser, 42)
    y = ProtectedRef(1, None, self.allowUserWrite(self.aliceUser), None)
    y.update(self.aliceUser, self.aliceUser, 43)
    z = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda otxt:
              ictxt == self.aliceUser or ictxt == self.bobUser
                or ictxt == self.carolUser)
    z.update(self.carolUser, self.carolUser, x.v + y.v)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, z.v), 85)
    self.assertEqual(JeevesLib.concretize(self.bobUser, z.v), 85)
    self.assertEqual(JeevesLib.concretize(self.carolUser, z.v), 85)

  # Only bob can see the special value alice wrote to him...
  @jeeves
  def test_combining_confidentiality_with_operations(self):  
    x = ProtectedRef(0, None, self.allowUserWrite(self.bobUser), self.bobUser)
    x.update(self.bobUser, self.bobUser, 42)
    y = ProtectedRef(2, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.aliceUser and octxt == self.bobUser)
    y.update(self.aliceUser, self.aliceUser, 43)
    z = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              ictxt == self.aliceUser or ictxt == self.bobUser
                or ictxt == self.carolUser)
    z.update(self.carolUser, self.carolUser,  x.v + y.v)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, z.v), 44)
    self.assertEqual(JeevesLib.concretize(self.bobUser, z.v), 85)
    self.assertEqual(JeevesLib.concretize(self.carolUser, z.v), 44)

  # TODO: This has a Z3 error... Look into this once more stuff is implemented.
  def test_integrity_policies_with_confidentiality(self):  
    a = JeevesLib.mkLabel ()
    JeevesLib.restrict(a, lambda ctxt: ctxt == self.bobUser)
    secretWriter = JeevesLib.mkSensitive(a, self.bobUser, self.nobodyUser)
    x = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt: ictxt == secretWriter)
    x.update(self.bobUser, self.bobUser, 42)
    self.assertEqual(JeevesLib.concretize(self.bobUser, secretWriter)
      , self.bobUser)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, secretWriter)
      , self.nobodyUser)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, secretWriter)
      , self.nobodyUser)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 0)   
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 0)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 0)

  # If Alice does something bad, then we will reject all of her influences.
  def test_determine_writer_trust_later(self):
    x = ProtectedRef(0, None, None
          , lambda _this: lambda ictxt: lambda octxt:
              JeevesLib.jhas(octxt.badUsers, ictxt))
    x.update(self.aliceUser, self.aliceUser, 42)
    self.assertEqual(
        JeevesLib.concretize(DummyContext(self.aliceUser
          , [self.aliceUser]), x.v)
      , 0)
    self.assertEqual(JeevesLib.concretize(DummyContext(self.aliceUser, []), x.v)
      , 42)

  def test_function_facets_allowed_to_write(self):
    def id(x):
      return x
    def inc(x):
      return x+1
    x = ProtectedRef(id, None, self.allowUserWrite(self.bobUser), None)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v)(1), 1)
    x.update(self.bobUser, self.bobUser, inc)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v)(1), 2)
    
  def test_function_facets_cannot_write(self):
    def id(x):
      return x
    def inc(x):
      return x+1
    x = ProtectedRef(id, None, self.allowUserWrite(self.bobUser), None)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v)(1), 1)
    x.update(self.aliceUser, self.aliceUser, inc)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v)(1), 1)

  def test_output_write_policy_with_this_cannot_update(self):  
    x = ProtectedRef(0, None, None
          , lambda v: lambda ictxt: lambda _octxt:
              (not (v == 3)) and ictxt == self.aliceUser)    
    x.update(self.aliceUser, self.aliceUser, 1)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 1)
    x.update(self.aliceUser, self.aliceUser, 3)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 3)  
    x.update(self.aliceUser, self.aliceUser, 5)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 3)    

  @jeeves
  def test_output_write_policies_involving_this_can_update(self):
    x = ProtectedRef(0, None, None
          , lambda v: lambda ictxt: lambda _: v == 0 and ictxt == alice)
    x.update(self.aliceUser, self.aliceUser, 1)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 1)
    x.update(self.aliceUser, self.aliceUser, 3)
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 1)
  '''

if __name__ == '__main__':
    unittest.main()
