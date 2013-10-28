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

class TestJeevesWrite(unittest.TestCase):
  class DummyUser:
    def __init__(self, userId):
      self.userId = userId
    def __eq__(self, other):
      self.userId == other.userId

  def setUp(self):
    # reset the Jeeves state
    JeevesLib.init()
    self.nobodyUser = DummyUser(-1)
    self.aliceUser = DummyUser(0)
    self.bobUser = DummyUser(1)
    self.carolUser = DummyUser(2)

  def allowUserWrite(self, user):
    lambda _this: lambda ictxt: ictxt == user

  '''
  def test_write_allowed_for_all_viewers(self):
    x = ProtectedRef(0, None, self.allowUserWrite(self.aliceUser), None)
    assert x.update(self.aliceUser, self.aliceUser, 42) == UpdateResult.Success
    self.assertEqual(JeevesLib.concretize(self.aliceUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.bobUser, x.v), 42)
    self.assertEqual(JeevesLib.concretize(self.carolUser, x.v), 42)
  
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
  '''

  '''
  test ("combining integrity policies in an operation") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(bob)), None)(this)
    x.update(bob, bobContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](2
      , None, None
      , Some(_this => ictxt => octxt =>
          ictxt === alice && octxt.viewer === bob))(this)
    y.update(alice, aliceContext(), 43)
    expectResult (44) {
      concretize(aliceContext(), x.getValue() + y.getValue()) }
    expectResult (85) { concretize(bobContext(), x.getValue() + y.getValue()) }
    expectResult (44) {
      concretize(carolContext(), x.getValue() + y.getValue()) }
  }
 
  /* Alice is allowed to write to x and only Bob is allowed to write to y.
     Our write policies disallow Bob from accidentally writing a value from
     Alice into y. (That is, without an explicit endorsement...) */
  test ("Prevent flow of untrusted writes") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(alice)), None, "x")(this)
    x.update(alice, aliceContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](
              1, None, Some(allowUserWrite(bob)), None, "y")(this)
    y.update(bob, bobContext(), x.getValue())
    expectResult (42) { concretize(aliceContext(), x.getValue()) }
    expectResult (42) { concretize(bobContext(), x.getValue()) }
    expectResult (0) { concretize(aliceContext(), y.getValue()) }
    expectResult (0) { concretize(bobContext(), y.getValue()) }
  }

  test ("Prevent flow of operations on untrusted writes") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(alice)), None)(this)
    x.update(alice, aliceContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](
              1, None, Some(allowUserWrite(bob)), None)(this)
    y.update(bob, aliceContext(), 43)
    val z = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(carol)), None)(this)
    z.update(carol, carolContext(), x.getValue() + y.getValue())
    expectResult (1) { concretize(aliceContext(), z.getValue()) }
    expectResult (1) { concretize(bobContext(), z.getValue()) }
    expectResult (1) { concretize(carolContext(), z.getValue()) }
  }

  /* Alice is allowed to write to x and only Bob is allowed to write to y.
     Our policy enforcement prevents Alice from influencing values that Bob
     writes. */
  test ("Prevent untrusted writes through implicit flows.") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(alice)), None)(this)
    x.update(alice, aliceContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](
              1, None, Some(allowUserWrite(bob)), None)(this)
    y.update(bob, bobContext(), jif (x.getValue() === 42, _ => 2, _ => 3))
    expectResult (3) { concretize(aliceContext(), y.getValue()) }
    expectResult (3) { concretize(bobContext(), y.getValue()) }
  }

  test ("Prevent implicit flows of confidential values") {
    val x = ProtectedIntRef[DummyUser, DummyContext](0, None, None
      , Some(_this => ictxt => octxt =>
          ictxt === alice && octxt.viewer === alice))(this)
    x.update(alice, aliceContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](1, None, None
      , Some(_this => ictxt => octxt => ictxt === bob || ictxt === alice))(this)
    y.update(bob, bobContext(), jif(x.getValue() === 42, _ => 2, _ => 3))
    expectResult (2) { concretize(aliceContext(), y.getValue()) }
    expectResult (3) { concretize(bobContext(), y.getValue()) }
  }

  /* If Alice and Bob are allowed to write to x and y respectively, then
     x + y should be allowed to be written to a value where they are both
     allowed to write. */
  test ("combining values into permissive write") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(bob)), None)(this)
    x.update(bob, bobContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](
              1, None, Some(allowUserWrite(alice)), None)(this)
    y.update(alice, aliceContext(), 43)
    val z =
      ProtectedIntRef[DummyUser, DummyContext](0, None, None
      , Some(_this => ictxt => octxt =>
          ictxt === alice || ictxt === bob || ictxt === carol))(this)
    z.update(carol, carolContext(), x.getValue() + y.getValue())
    expectResult (85) { concretize(aliceContext(), z.getValue()) }
    expectResult (85) { concretize(bobContext(), z.getValue()) }
    expectResult (85) { concretize(carolContext(), z.getValue()) }
  }

  // Only bob can see the special value alice wrote to him...
  test ("Combining confidentiality with operations") {
    val x = ProtectedIntRef[DummyUser, DummyContext](
              0, None, Some(allowUserWrite(bob)), None)(this)
    x.update(bob, bobContext(), 42)
    val y = ProtectedIntRef[DummyUser, DummyContext](2, None, None
      , Some(_this => ictxt => octxt =>
          ictxt === alice && octxt.viewer === bob))(this)
    y.update(alice, aliceContext(), 43)
    val z = ProtectedIntRef[DummyUser, DummyContext](0, None, None
      , Some(_this => ictxt => _octxt =>
          ictxt === alice || ictxt === bob || ictxt === carol))(this)
    z.update(carol, carolContext(),  x.getValue() + y.getValue())
    expectResult (44) { concretize(aliceContext(), z.getValue()) }
    expectResult (85) { concretize(bobContext(), z.getValue()) }
    expectResult (44) { concretize(carolContext(), z.getValue()) }
  }

  // Since only bob knows that he can write, only he can see his value...
  test ("Integrity policies that involve confidentiality policies") {
    val a = mkLabel ()
    restrict (a, (ctxt: ObjectExpr[DummyContext]) => ctxt.viewer === bob)
    val secretWriter: ObjectExpr[DummyUser] = mkSensitive(a, bob, nobody)
    val x = ProtectedIntRef[DummyUser, DummyContext](0, None, None
    , Some(_this => ictxt => octxt => ictxt === secretWriter))(this)
    x.update(bob, bobContext(), 42)
    expectResult (bob) { concretize(bobContext(), secretWriter) }
    expectResult (nobody) { concretize(aliceContext(), secretWriter) }
    expectResult (nobody) { concretize(carolContext(), secretWriter) }
    expectResult (0) { concretize(aliceContext(), x.getValue()) }
    expectResult (42) { concretize(bobContext(), x.getValue()) }
    expectResult (0) { concretize(carolContext(), x.getValue()) }
  }

  /* If Alice does something bad, then we will reject all of her influences.
   */
  test ("Determine whether a writer is trusted later") {
    val x = ProtectedIntRef[DummyUser, DummyContext](0, None, None
      , Some(_this => ictxt => octxt => (
          octxt.applyFunction((oc: DummyContext) =>
           !Atoms(oc.badUsers).has(ictxt)))))(this)
    x.update(alice, aliceContext(), 42)
    expectResult(0) { concretize(aliceContext(List(alice)), x.getValue()) }
    expectResult(42) { concretize(aliceContext(List()), x.getValue()) }
  }
 
  /* Make sure we can change the input channel type without things breaking. */
  test ("Different types for input channels") {
    val x = ProtectedIntRef[DummyContext, DummyContext](0, None, None
      , Some(_this => ictxt => _octxt => ictxt.viewer === alice))(this)
    x.update(aliceContext(List()), aliceContext(), 42)
    expectResult(42) { concretize(aliceContext(), x.getValue()) }
  }

  def id[T](x: T): T = x
  def inc(x: IntExpr): IntExpr = x + 1

  test ("Function facets--allowed to write.") {
    val x =
      ProtectedFunctionRef[IntExpr, IntExpr, DummyUser, DummyContext](
        FunctionVal(id[IntExpr]_)
        , None, Some(allowUserWrite(bob)), None)(this)
    expectResult (1) {
      concretize(aliceContext(), jfun[IntExpr, IntExpr](x.getValue(), 1)) }
    x.update(bob, bobContext(), FunctionVal(inc))
    expectResult (2) {
      concretize(aliceContext(), jfun[IntExpr, IntExpr](x.getValue(), 1)) }
  }

  test ("Function facets--not allowed to write.") {
    val x =
      ProtectedFunctionRef[IntExpr, IntExpr, DummyUser, DummyContext](
        FunctionVal(id[IntExpr]_)
        , None, Some(allowUserWrite(bob)), None)(this)
    expectResult (1) {
      concretize(aliceContext(), jfun[IntExpr, IntExpr](x.getValue(), 1)) }
    x.update(alice, aliceContext(), FunctionVal(inc))
    expectResult (1) {
      concretize(aliceContext(), jfun[IntExpr, IntExpr](x.getValue(), 1)) }
  }

  test ("Output write policies involving 'this'--cannot update") {
    val x =
      ProtectedIntRef[DummyUser, DummyContext](0, None, None
      , Some(v => ictxt => _ => !(v === 3) && ictxt === alice))(this)
    x.update(alice, aliceContext(), 1)
    expectResult(1) {
      concretize(aliceContext(), x.getValue())
    }
    x.update(alice, aliceContext(), 3)
    expectResult(3) {
      concretize(aliceContext(), x.getValue())
    }
    x.update(alice, aliceContext(), 5)
    // println(x.getValue())
    // DebugPrint.debugPrint(aliceContext(), x.getValue())(this)
    expectResult(3) {
      concretize(aliceContext(), x.getValue())
    }
  }

  test ("Output write policies involving 'this'--can update") {
    val x =
      ProtectedIntRef[DummyUser, DummyContext](0
      , None, None, Some(v => ictxt => _ => (v === 0) && ictxt === alice))(this)
    x.update(alice, aliceContext(), 1)
    expectResult(1) {
      concretize(aliceContext(), x.getValue())
    }
    x.update(alice, aliceContext(), 3)
    expectResult(1) {
      concretize(aliceContext(), x.getValue())
    }
  }
  '''

if __name__ == '__main__':
    unittest.main()
