import unittest
from Order import *
from Obs import *
from Interfaces import *
from HeadersForClasses import *

class TestOrderFunctions(unittest.TestCase):

    def setUp(self):
        self.order = Order()
        self.order.setOrderId(9112)
        self.order.setOrderNumber('911')
        
    def test_copy_methods(self):
        copy1 = self.order.copy()
        copy2 = self.order.copyForModification()
        self.assertEqual(self.order.OrderAction.ORDER, 'ORDER')
        self.assertEqual(self.order.Urgency.ROUTINE, 'ROUTINE')
        self.assertIs(copy2, self.order)
        self.assertIsNot(copy1, self.order)
        self.assertIsNot(copy1, copy2)
        self.assertEqual(self.order.hashCode(), self.order.getOrderId())

    def test_date_methods(self):
        self.assertTrue(self.order.isCurrent())
        checkDate = datetime(2013, 12, 25)

        autoExpireDate = datetime(2017, 12, 25)
        self.order.setAutoExpireDate(autoExpireDate)
        self.assertTrue(self.order.isCurrent(checkDate))
        
        discontinuedDate = datetime(2015, 12, 25)
        self.order.setDiscontinuedDate(discontinuedDate)
        self.assertTrue(self.order.isCurrent(checkDate))
        self.assertFalse(self.order.isDiscontinued(checkDate))
        
        startDate = datetime(2014, 12, 25)
        self.order.setStartDate(startDate)
        self.assertFalse(self.order.isCurrent(checkDate))
        self.order.setDiscontinued(True)
        self.assertFalse(self.order.isDiscontinued(checkDate))
        
        checkDate2 = datetime(2016, 12, 25)
        self.assertTrue(self.order.isDiscontinued(checkDate2))

        self.assertTrue(self.order.isFuture(checkDate))
        self.assertFalse(self.order.isDrugOrder())

        obj = Order(orderId = 9112)
        self.assertTrue(self.order.equals(obj))

        
        
class TestObsFunctions(unittest.TestCase):

    def setUp(self):
        self.obs = Obs(913)
        
    def test_newInstance_method(self):
        concept = Concept()
        concept.setDatatype(True)
        
        self.obsToCopy = Obs(Person(), concept, datetime.now(), Location())
        self.newObs = self.obs.newInstance(self.obsToCopy)
        self.assertFalse(self.newObs == self.obsToCopy)#both have None obsId
        self.assertIsNot(self.newObs, self.obsToCopy) 
        
        self.obsToCopy = Obs(9118)
        self.newObs = self.obs.newInstance(self.obsToCopy)
        self.assertFalse(self.newObs == self.obsToCopy)#newObs has None obsId but obsToCopy has an obsId

    def test_obs_group_methods(self):
        self.obs.setObsGroup(None)
        self.assertFalse(self.obs.hasGroupMembers())

        self.obs1 = Obs(127)
        self.obs2 = Obs(9827)
        concept = Concept()
        concept.setSet(True)
        self.obs.setConcept(concept)
        self.obs.setGroupMembers(set([self.obs1, self.obs2]))
        self.assertTrue(self.obs.getGroupMembers(True) != None)
        self.assertTrue(self.obs.getGroupMembers(False) != None)

        self.obs.addGroupMember(Obs(7543))
        self.obs.addGroupMember(self.obs)
        #self.assertRaises(APIException) #the line before should raise this exception

        self.obs.removeGroupMember(self.obs1)
        self.assertIsNone(self.obs1.getObsGroup())

        #self.obsToCopy should be parent group of obs members.  
        ret = self.obs.getRelatedObservations()
        for i in ret:
            self.assertFalse(i.isObsGrouping())
            
    def test_value_methods(self):
        self.obs.setValueBoolean(True)
        #self.assertIsNotNone(self.obs.getValueCoded())

        self.obs.setValueNumeric(1)
        self.assertTrue(self.obs.getValueAsBoolean())

        self.obs.setValueNumeric(0)
        self.assertFalse(self.obs.getValueAsBoolean())

        self.assertFalse(self.obs.isComplex())
        
        self.obs.setValueAsString("True")
        #self.assertTrue(self.obs.getValueAsString())

        concept1 = Concept()
        concept1.setDatatype(ConceptDatatype(13))
        self.obs.setConcept(concept1)
        self.obs.getConcept().getDatatype().setHl7Abbreviation("NM")
        self.obs.setValueAsString("13")
        #self.assertTrue(self.obs.getValueAsString(locale) == "13")

        
if __name__ == "__main__":
    unittest.main()
