import unittest
from BaseOpenmrsObject import *

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

        self.assertIs(self.order.serialVersionUID, 1)
        
if __name__ == "__main__":
    unittest.main()
