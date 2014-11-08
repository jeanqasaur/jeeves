from django.conf import settings
from django.db import connection, models
from django.template import Template, Context
from django.utils import unittest
from django.test import TestCase

import JeevesLib
import sys

from jeevesdb import JeevesModel
from testdb.models import Animal, Zoo

import nose.tools as nt

def parse_vars_row(vs):
    d = {}
    for entry in vs.split(';')[1:-1]:
        name, val = entry.split('=')
        d[name] = bool(int(val))
    return d

def areRowsEqual(rows, expected):
    """expected is a list
    [({name:'lion',...}, {var_name:True,...})]
    """
    rows = list(rows)
    if len(rows) != len(expected):
        print 'got len %d, expected %d' % (len(rows), len(expected))
        return False
    for attrs_dict, vars_dict in expected:
        for r in rows:
            vars_dict1 = parse_vars_row(r.jeeves_vars)
            if (vars_dict == vars_dict1 and
                all(getattr(r, name) == val
                    for name, val in attrs_dict.iteritems())):
                break
        else:
            print 'could not find', attrs_dict, vars_dict
            return False
    return True

'''
This tests Django monkey-patching to support Jeeves.
'''
class TestJeevesModel(TestCase):
    def setUp(self):
        JeevesLib.init()
        self.f = open('log.txt', 'w')
        JeevesLib.set_log_policies(self.f)

        Animal.objects.create(name='lion', sound='roar')
        # Animal.objects.create(name='cat', sound='meow')

        '''
        self.x = JeevesLib.mkLabel()
        self.y = JeevesLib.mkLabel()
        JeevesLib.restrict(self.x, lambda (a,_) : a)
        JeevesLib.restrict(self.y, lambda (_,a) : a)

        # Add elements to the database.
        print >> sys.stderr, "adding fox"
        Animal.objects.create(name='fox',
            sound=JeevesLib.mkSensitive(self.x, 'Hatee-hatee-hatee-ho!',
                'Joff-tchoff-tchoff-tchoffo-tchoffo-tchoff!'))

        print >> sys.stderr, "adding a"
        Animal.objects.create(name='a',
            sound=JeevesLib.mkSensitive(self.x,
                JeevesLib.mkSensitive(self.y, 'b', 'c'),
                JeevesLib.mkSensitive(self.y, 'd', 'e')))

        self.assertEquals(JeevesLib.get_num_concretize(), 0)
        self.assertEquals(JeevesLib.get_num_concretize_labels(), 0)
        '''

    def tearDown(self):
        self.f.close()

    @staticmethod
    def setUpClass():
        # The test runner sets DEBUG to False. Set to True to enable SQL logging.
        settings.DEBUG = True

    @staticmethod
    def tearDownClass():
        time = sum([float(q['time']) for q in connection.queries])
        t = Template("{{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds:\n\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
        print >> sys.stderr, t.render(Context({'sqllog': connection.queries, 'count': len(connection.queries), 'time': time}))

        # Empty the query list between TestCase.
        connection.queries = []

    # Tests that writes create the appropriate rows with associated Jeeves
    # bookkeeping.
    def testWrite(self):
        lion = Animal.objects.get(name='lion')
        # self.assertEquals(JeevesLib.concretize(lion, lion.name), 'lion')
        # self.assertEquals(JeevesLib.concretize(lion, lion.sound), 'roar')

        '''
        fox = Animal._objects_ordinary.filter(name='fox').filter(
                jeeves_vars=';%s=1;'%self.x.name).all()[0]
        self.assertEquals(fox.sound, 'Hatee-hatee-hatee-ho!')

        fox = Animal._objects_ordinary.filter(name='fox').filter(
                jeeves_vars=';%s=0;'%self.x.name).all()[0]
        self.assertEquals(fox.sound
            , 'Joff-tchoff-tchoff-tchoffo-tchoffo-tchoff!')

        a = list(Animal._objects_ordinary.filter(name='a').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'a', 'sound':'b'}, {self.x.name:True, self.y.name:True}),
            ({'name':'a', 'sound':'c'}, {self.x.name:True, self.y.name:False}),
            ({'name':'a', 'sound':'d'}, {self.x.name:False, self.y.name:True}),
            ({'name':'a', 'sound':'e'}, {self.x.name:False, self.y.name:False}),
        ]))
        '''

    '''
    def testQueryDelete(self):
        """Test that delete removes all rows.
        """
        Animal.objects.create(name='delete_test1',
            sound=JeevesLib.mkSensitive(self.x,
                JeevesLib.mkSensitive(self.y, 'b', 'c'),
                JeevesLib.mkSensitive(self.y, 'd', 'e')))
        Animal.objects.filter(name='delete_test1').filter(sound='b').delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test1').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test1', 'sound':'c'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'delete_test1', 'sound':'d'}
            , {self.x.name:False, self.y.name:True}),
            ({'name':'delete_test1', 'sound':'e'}
            , {self.x.name:False, self.y.name:False})]))

        an = Animal.objects.create(name='delete_test2',
            sound=JeevesLib.mkSensitive(self.x,
                JeevesLib.mkSensitive(self.y, 'b', 'c'),
                JeevesLib.mkSensitive(self.y, 'd', 'e')))
        with JeevesLib.PositiveVariable(self.x):
            an.delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test2').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test2', 'sound':'d'}
            , {self.x.name:False, self.y.name:True}),
            ({'name':'delete_test2', 'sound':'e'}
            , {self.x.name:False, self.y.name:False}),
        ]))

        an = Animal.objects.create(name='delete_test3', sound='b')
        with JeevesLib.PositiveVariable(self.x):
            an.delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test3').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test3', 'sound':'b'}, {self.x.name:False})
        ]))

        an = Animal.objects.create(name='delete_test4', sound='b')
        with JeevesLib.PositiveVariable(self.x):
            with JeevesLib.NegativeVariable(self.y):
                an.delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test4').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test4', 'sound':'b'}
            , {self.x.name:False}),
            ({'name':'delete_test4', 'sound':'b'}
            , {self.x.name:True, self.y.name:True}),
        ]) or areRowsEqual(a, [
            ({'name':'delete_test4', 'sound':'b'}, {self.y.name:True}),
            ({'name':'delete_test4', 'sound':'b'}
            , {self.y.name:False, self.x.name:False}),
        ]))

        an = Animal.objects.create(name='delete_test5',
                sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        with JeevesLib.PositiveVariable(self.x):
            an.delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test5').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test5', 'sound':'c'}, {self.x.name:False})
        ]))

        an = Animal.objects.create(name='delete_test6',
                sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        with JeevesLib.PositiveVariable(self.y):
            an.delete()
        a = list(Animal._objects_ordinary.filter(name='delete_test6').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'delete_test6', 'sound':'b'}
            , {self.x.name:True,self.y.name:False}),
            ({'name':'delete_test6', 'sound':'c'}
            , {self.x.name:False,self.y.name:False}),
        ]))

    def testSave(self):
        """Test that saving does the correct bookkeeping.
        """
        an = Animal.objects.create(name='save_test1', sound='b')
        an.sound = 'c'
        with JeevesLib.PositiveVariable(self.x):
            an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test1').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test1', 'sound':'b'}, {self.x.name:False}),
            ({'name':'save_test1', 'sound':'c'}, {self.x.name:True}),
        ]))

        an = Animal.objects.create(name='save_test2', sound='b')
        an.sound = 'c'
        with JeevesLib.PositiveVariable(self.x):
            with JeevesLib.NegativeVariable(self.y):
                an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test2').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test2', 'sound':'c'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'save_test2', 'sound':'b'}
            , {self.x.name:True, self.y.name:True}),
            ({'name':'save_test2', 'sound':'b'}, {self.x.name:False}),
        ]) or areRowsEqual(a, [
            ({'name':'save_test2', 'sound':'c'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'save_test2', 'sound':'b'}
            , {self.x.name:False, self.y.name:False}),
            ({'name':'save_test2', 'sound':'b'}, {self.y.name:True}),
        ]))

        an = Animal.objects.create(name='save_test3',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        an.sound = JeevesLib.mkSensitive(self.x, 'd', 'e')
        an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test3').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test3', 'sound':'d'}, {self.x.name:True}),
            ({'name':'save_test3', 'sound':'e'}, {self.x.name:False}),
        ]))

        an = Animal.objects.create(name='save_test4',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        an.sound = JeevesLib.mkSensitive(self.y, 'd', 'e')
        an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test4').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test4', 'sound':'d'}, {self.y.name:True}),
            ({'name':'save_test4', 'sound':'e'}, {self.y.name:False}),
        ]) or areRowsEqual(a, [
            ({'name':'save_test4', 'sound':'d'}
            , {self.y.name:True, self.x.name:True}),
            ({'name':'save_test4', 'sound':'d'}
            , {self.y.name:True, self.x.name:False}),
            ({'name':'save_test4', 'sound':'e'}
            , {self.y.name:False, self.x.name:True}),
            ({'name':'save_test4', 'sound':'e'}
            , {self.y.name:False, self.x.name:False}),
        ]))

        an = Animal.objects.create(name='save_test5',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        an.sound = JeevesLib.mkSensitive(self.y, 'd', 'e')
        with JeevesLib.PositiveVariable(self.x):
            an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test5').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test5', 'sound':'c'}, {self.x.name:False}),
            ({'name':'save_test5', 'sound':'d'}
            , {self.x.name:True, self.y.name:True}),
            ({'name':'save_test5', 'sound':'e'}
            , {self.x.name:True, self.y.name:False}),
        ]))

        an = Animal.objects.create(name='save_test6',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        an.sound = JeevesLib.mkSensitive(self.y, 'd', 'e')
        with JeevesLib.PositiveVariable(self.y):
            an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test6').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test6', 'sound':'b'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'save_test6', 'sound':'d'}
            , {self.x.name:True, self.y.name:True}),
            ({'name':'save_test6', 'sound':'c'}
            , {self.x.name:False, self.y.name:False}),
            ({'name':'save_test6', 'sound':'d'}
            , {self.x.name:False, self.y.name:True}),
        ]) or areRowsEqual(a, [
            ({'name':'save_test6', 'sound':'b'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'save_test6', 'sound':'d'}, {self.y.name:True}),
            ({'name':'save_test6', 'sound':'c'}
            , {self.x.name:False, self.y.name:False}),
        ]))

        an = Animal.objects.create(name='save_test7',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
        an.sound = JeevesLib.mkSensitive(self.y, 'd', 'e')
        with JeevesLib.PositiveVariable(self.x):
            with JeevesLib.PositiveVariable(self.y):
                an.save()
        a = list(Animal._objects_ordinary.filter(name='save_test7').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_test7', 'sound':'d'}
            , {self.x.name:True, self.y.name:True}),
            ({'name':'save_test7', 'sound':'b'}
            , {self.x.name:True, self.y.name:False}),
            ({'name':'save_test7', 'sound':'c'}, {self.x.name:False}),
        ]))

    def testSaveCollapse(self):
        an = Animal.objects.create(name='savec_test', sound='b')
        an.sound = 'c'
        with JeevesLib.PositiveVariable(self.x):
            an.save()
        with JeevesLib.NegativeVariable(self.x):
            an.save()

        a = list(Animal._objects_ordinary.filter(name='savec_test').all())
        self.assertTrue(areRowsEqual(a
            , [({'name':'savec_test', 'sound':'c'}, {}),]))

    def testEnvWrite(self):
        an = Animal.objects.create(name='save_ew_test', sound='b')
        with JeevesLib.PositiveVariable(self.x):
            an.sound = 'c'
        an.save()

        a = list(Animal._objects_ordinary.filter(name='save_ew_test').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'save_ew_test', 'sound':'b'}, {self.x.name:False}),
            ({'name':'save_ew_test', 'sound':'c'}, {self.x.name:True}),
        ]))
    
    def testGet1(self):
        an = Animal.objects.create(name='get_test1'
                , sound='get_test1_sound_xyz')

        bn = Animal.objects.get(name='get_test1')
        self.assertEqual(an.name, 'get_test1')
        self.assertEqual(an.sound, 'get_test1_sound_xyz')

        cn = Animal.objects.get(sound='get_test1_sound_xyz')
        self.assertEqual(cn.name, 'get_test1')
        self.assertEqual(cn.sound, 'get_test1_sound_xyz')

        self.assertTrue(JeevesLib.concretize((True, True), an == bn))
        self.assertEquals(JeevesLib.get_num_concretize(), 1)
        self.assertEquals(JeevesLib.get_num_concretize_labels(), 0)

        self.assertTrue(JeevesLib.concretize((True, True), an == cn))
        self.assertTrue(JeevesLib.concretize((True, True), bn == cn))

        self.assertTrue(JeevesLib.concretize((False, True), an == bn))
        self.assertTrue(JeevesLib.concretize((False, True), an == cn))
        self.assertTrue(JeevesLib.concretize((False, True), bn == cn))

    def testGet2(self):
        an = Animal.objects.create(name='get_test2'
            , sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))

        bn = Animal.objects.get(name='get_test2')

        self.assertEqual(JeevesLib.concretize((True, True), an == bn), True)
        self.assertEqual(JeevesLib.concretize((False, True), an == bn), True)
        self.assertEqual(an.name, 'get_test2')
        self.assertEqual(an.sound.cond.name, self.x.name)
        self.assertEqual(an.sound.thn.v, 'b')
        self.assertEqual(an.sound.els.v, 'c')

    def testGet3(self):
        an = Animal.objects.create(name='get_test3'
            , sound=JeevesLib.mkSensitive(self.x
                , JeevesLib.mkSensitive(self.y, 'b', 'c')
                , JeevesLib.mkSensitive(self.y, 'd', 'e')))

        bn = Animal.objects.get(name='get_test3')

        self.assertEqual(JeevesLib.concretize((True, True), an == bn), True)
        self.assertEqual(JeevesLib.concretize((False, True), an == bn), True)
        self.assertEqual(JeevesLib.concretize((True,True), bn.sound), 'b')
        self.assertEqual(JeevesLib.concretize((True,False), bn.sound), 'c')
        self.assertEqual(JeevesLib.concretize((False,True), bn.sound), 'd')
        self.assertEqual(JeevesLib.concretize((False,False), bn.sound), 'e')

    def testGet4(self):
        with JeevesLib.PositiveVariable(self.x):
            an = Animal.objects.create(name='get_test4', sound='a')
        with JeevesLib.NegativeVariable(self.y):
            bn = Animal.objects.create(name='get_test4', sound='b')
    
        got_exc = False
        try:
            cn = Animal.objects.get(name='get_test4')
        except Exception:
            got_exc = True

        self.assertTrue(got_exc)
        #self.assertEqual(cn.cond.name, self.x.name)
        #self.assertEqual(cn.thn.v.name, 'get_test4')
        #self.assertEqual(cn.thn.v.sound, 'a')
        #self.assertEqual(cn.els.v.name, 'get_test4')
        #self.assertEqual(cn.els.v.sound, 'b')

        #an1 = cn.thn
        #bn1 = cn.els
        #self.assertTrue(an == an1)
        #self.assertTrue(bn == bn1)
        #self.assertTrue(an != bn)
        #self.assertTrue(an != bn1)
        #self.assertTrue(bn != an)
        #self.assertTrue(bn != an1)

    def testFilter1(self):
        an = Animal.objects.create(name='filter_test1', sound='a')
        bl = Animal.objects.filter(name='filter_test1').get_jiter()
        self.assertEquals(bl, [(an, {})])

    def testFilter2(self):
        with JeevesLib.PositiveVariable(self.x):
            an = Animal.objects.create(name='filter_test2', sound='a')

        bl = Animal.objects.filter(name='filter_test2').get_jiter()
        self.assertEquals(bl, [(an, {self.x.name:True})])

    def testFilter3(self):
        with JeevesLib.PositiveVariable(self.x):
            an = Animal.objects.create(name='filter_test3', sound='a')
        with JeevesLib.NegativeVariable(self.y):
            bn = Animal.objects.create(name='filter_test3', sound='b')

        bl = Animal.objects.filter(
                name='filter_test3').order_by('sound').get_jiter()
        self.assertEquals(bl
            , [(an, {self.x.name:True}), (bn, {self.y.name:False})])

    def testFilter4(self):
        an = Animal.objects.create(name='filter_test4', sound='b')
        bn = Animal.objects.create(name='filter_test4'
            , sound=JeevesLib.mkSensitive(self.x, 'a', 'c'))

        bl = Animal.objects.filter(
                name='filter_test4').order_by('sound').get_jiter()
        self.assertEquals(bl
            , [(bn, {self.x.name:True}), (an, {}), (bn, {self.x.name:False})])

    def testJeevesForeignKey(self):
        an = Animal.objects.create(name='fkey_test1_an', sound='a')
        bn = Animal.objects.create(name='fkey_test1_bn', sound='b')
        zoo = Zoo.objects.create(name='fkey_test1_zoo',
            inhabitant=JeevesLib.mkSensitive(self.x, an, bn))
        a = list(Animal._objects_ordinary.filter(name='fkey_test1_an').all())
        b = list(Animal._objects_ordinary.filter(name='fkey_test1_bn').all())
        z = list(Zoo._objects_ordinary.filter(name='fkey_test1_zoo').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'fkey_test1_an', 'sound':'a'}, {})
        ]))
        self.assertTrue(areRowsEqual(b, [
            ({'name':'fkey_test1_bn', 'sound':'b'}, {})
        ]))
        self.assertTrue(areRowsEqual(z, [
            ({'name':'fkey_test1_zoo', 'inhabitant_id':an.jeeves_id}
            , {self.x.name:True}),
            ({'name':'fkey_test1_zoo', 'inhabitant_id':bn.jeeves_id}
            , {self.x.name:False}),
        ]))
        z = Zoo.objects.get(name='fkey_test1_zoo')
        self.assertEqual(JeevesLib.concretize((True, True), z.inhabitant), an)
        self.assertEqual(JeevesLib.concretize((False, True), z.inhabitant), bn)

        z.inhabitant.sound = 'd'
        z.inhabitant.save()

        a = list(Animal._objects_ordinary.filter(name='fkey_test1_an').all())
        b = list(Animal._objects_ordinary.filter(name='fkey_test1_bn').all())
        z = list(Zoo._objects_ordinary.filter(name='fkey_test1_zoo').all())
        self.assertTrue(areRowsEqual(a, [
            ({'name':'fkey_test1_an', 'sound':'a'}, {self.x.name:False}),
            ({'name':'fkey_test1_an', 'sound':'d'}, {self.x.name:True}),
        ]))
        self.assertTrue(areRowsEqual(b, [
            ({'name':'fkey_test1_bn', 'sound':'b'}, {self.x.name:True}),
            ({'name':'fkey_test1_bn', 'sound':'d'}, {self.x.name:False}),
        ]))
        self.assertTrue(areRowsEqual(z, [
            ({'name':'fkey_test1_zoo', 'inhabitant_id':an.jeeves_id}
            , {self.x.name:True}),
            ({'name':'fkey_test1_zoo', 'inhabitant_id':bn.jeeves_id}
            , {self.x.name:False}),
        ]))

    def testFKeyUpdate(self):
        an = Animal.objects.create(name='fkeyup_test_an', sound='a')
        zoo = Zoo.objects.create(name='fkeyup_test_zoo', inhabitant=an)

        an.sound = 'b'
        an.save()

        z = Zoo.objects.get(name='fkeyup_test_zoo')
        self.assertTrue(z != None)
        self.assertEqual(z.inhabitant, an)

    def testFilterForeignKeys1(self):
        an = Animal.objects.create(name='filterfkey_test1_an', sound='a')
        bn = Animal.objects.create(name='filterfkey_test1_bn', sound='b')
        zoo = Zoo.objects.create(name='filterfkey_test1_zoo',
            inhabitant=JeevesLib.mkSensitive(self.x, an, bn))

        zool = Zoo.objects.filter(
                inhabitant__name='filterfkey_test1_an').get_jiter()
        self.assertEquals(zool, [(zoo, {self.x.name:True})])

    def testFilterForeignKeys2(self):
        an = Animal.objects.create(name='filterfkey_test2_an',
                    sound=JeevesLib.mkSensitive(self.x, 'a', 'b'))
        zoo = Zoo.objects.create(name='filterfkey_zoo', inhabitant=an)

        zool = Zoo.objects.filter(
                inhabitant__name='filterfkey_test2_an').filter(
                    inhabitant__sound='a').get_jiter()
        self.assertEquals(zool, [(zoo, {self.x.name:True})])
    '''

    '''
    def testPolicy(self):
        awp = AnimalWithPolicy.objects.create(name='testpolicy1', sound='meow')
        a = list(AnimalWithPolicy._objects_ordinary.filter(
                name='testpolicy1').all())
        name = 'AnimalWithPolicy__sound__' + awp.jeeves_id
        self.assertTrue(areRowsEqual(a, [
            ({'name':'testpolicy1', 'sound':'meow'}, {name:True}),
            ({'name':'testpolicy1', 'sound':''}, {name:False}),
        ]))

        self.assertEquals(JeevesLib.get_num_concretize(), 0)
        self.assertEquals(JeevesLib.get_num_concretize_labels(), 0)

    def testPolicy2(self):
        awp = AnimalWithPolicy2.objects.create(name='testpolicy2', sound='meow')
        a = list(AnimalWithPolicy2._objects_ordinary.filter(
                name='testpolicy2').all())
        name = 'AnimalWithPolicy2__awplabel__' + awp.jeeves_id
        self.assertTrue(areRowsEqual(a, [
            ({'name':'testpolicy2', 'sound':'meow'}, {name:True}),
            ({'name':'testpolicy2', 'sound':''}, {name:False}),
        ]))

        self.assertEquals(JeevesLib.get_num_concretize(), 0)
        self.assertEquals(JeevesLib.get_num_concretize_labels(), 0)

    def testObjectModel(self):
        dogWithPolicy = AnimalWithPolicy()
        dogWithPolicy.name="dog"
        dogWithPolicy.sound="bark"
        AnimalWithPolicy.objects.create(name="dog",sound="bark")
        AnimalWithPolicy.objects.create(name="cat",sound="meow")
        AnimalWithPolicy.objects.create(name="gorilla",sound="aaaaah")
        cat=AnimalWithPolicy.objects.get(name="cat")
        dog=AnimalWithPolicy.objects.get(name="dog")
        
        # dataset={"sound":animal.sound}
        # self.assertIn(dataset['sound'],["meow",""])
        # self.assertTrue(False) # TODO: This should fail!
        # self.assertEquals(dogWithPolicy,dog)
        # allAnimals=AnimalWithPolicy.objects.filter
        # self.assertIn(dataset.sound,["meow",""])
    '''
    # TODO: Test how things change as we get more fake data.
    # Use this: http://www.makeuseof.com/tag/generate-dummy-data-python-ruby-perl/
