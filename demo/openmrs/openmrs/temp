from abc import ABCMeta, abstractmethod
import uuid
import org.python.google.common.base.objects as objects #not sure if this is the same as com.google.common.base.Objects in JAVA code
import datetime
import pickle
from flufl.enum import Enum

#Interfaces
class OpenmrsObject(object):
    """This is the base interface for all OpenMRS-defined classes"""
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def getId(self):
    #return id - The unique Identifier for the object
        pass
    
    def setId(self, Id):
    #param id - The unique Identifier for the object
        pass
    
    def getUuid(self):
    #return the universally unique id for this object
        pass
    
    def setUuid(self, uuid):
    #param uuid a universally unique id for this object
        pass


class Auditable(OpenmrsObject):
    __metaclass__= ABCMeta
    
    def getCreator(self):
        pass
    def setCreator(self, creator):
        pass
    def getDateCreated(self):
        pass
    def setDateCreated(self, dateCreated):
        pass
    def getChangedBy(self):
        pass
    def setChangedBy(self, changedBy):
        pass
    def getDateChanged(self):
        pass
    def setDateChanged(self, dateChanged):
        pass
    
class Attributable:
    __metaclass__= ABCMeta

    def hydrate(self, s):
        pass
    def serialize(self):
        pass
    def getPossibleValues(self):
        pass
    def findPossibleValues(self, searchText):
        pass
    def getDisplayString(self):
        pass
    
class Order(BaseOpenmrsData): #serializable has to be implemented
    serialVersionUID = 1L
    OrderAction = Enum('OrderAction', 'ORDER DISCONTINUE') #is this equivalent of enum type in JAVA?
    Urgency = Enum('Urgency', 'ROUTINE STAT')
    orderAction = OrderAction.ORDER
    urgency = Urgency.ROUTINE
    
    def __init__(self, orderId=None, patient=None, concept=None, discontinued = False, \
                 autoExpireDate=None, discontinuedBy=None, discontinuedDate=None, discontinuedReason=None, \
                 encounter=None, instructions=None,accessionNumber=None, orderer=None, startDate=None):
        self.orderId = orderId
        self.patient = patient
        self.concept = concept
        self.discontinued = discontinued
        self.autoExpireDate = autoExpireDate
        self.discontinuedBy = discontinuedBy
        self.discontinuedDate = discontinuedDate
        self.discontinuedReason = discontinuedReason
        self.encounter = encounter
        self.instructions = instructions
        self.accessionNumber = accessionNumber
        self.orderer = orderer
        self.startDate = startDate
    def copy(self):
        return self.copyHelper(Order())
    
    def copyHelper(self, target):
        target.setPatient(getPatient())
        target.setConcept(getConcept())
        target.setInstructions(getInstructions())
        target.setStartDate(getStartDate())
        target.setAutoExpireDate(getAutoExpireDate())
        target.setEncounter(getEncounter())
        target.setOrderer(getOrderer())
        target.setCreator(getCreator())
        target.setDateCreated(getDateCreated())
        target.setDiscontinued(getDiscontinued())
        target.setDiscontinuedDate(getDiscontinuedDate())
        target.setDiscontinuedReason(getDiscontinuedReason())
        target.setDiscontinuedBy(getDiscontinuedBy())
        target.setAccessionNumber(getAccessionNumber())
        target.setVoided(isVoided())
        target.setVoidedBy(getVoidedBy())
        target.setDateVoided(getDateVoided())
        target.setVoidReason(getVoidReason())
        target.setOrderNumber(getOrderNumber())
        target.setPreviousOrderNumber(getPreviousOrderNumber())
        target.setOrderAction(getOrderAction())
        target.setUrgency(getUrgency())
        return target

    def equals(self, obj):
        if isinstance(obj, Order):
            o = obj
            if (self.getOrderId() != None) and (o.getOrderId != None):
                return self.getOrderId() == o.getOrderId()
        return False
    
    def hashCode(self):
        if self.getOrderId() == None:
            return hash(object) #same as super.hashCode()
        return hash(self.getOrderId())

    def isDrugOrder(self):
        return False
    def getAutoExpireDate(self):
        return self.autoExpireDate
    def setAutoExpireDate(self, autoExpireDate):
        self.autoExpireDate = autoExpireDate
    def getConcept(self):
        return self.concept
    def setConcept(self, concept):
        self.concept = concept
    def getDiscontinued(self):
        return self.discontinued
    def setDiscontinued(self, discontinued):
        self.discontinued = discontinued #should it be discontinued or self.discontinued?
    def getDiscontinuedBy(self):
        return self.discontinuedBy
    def setDiscontinuedBy(self, discontinuedBy):
        self.discontinuedBy=discontinuedBy
    def getDiscontinuedDate(self):
        return self.discontinuedDate
    def setDiscontinuedDate(self, discontinuedDate):
        self.discontinuedDate=discontinuedDate
    def getDiscontinuedReason(self):
        return self.discontinuedReason
    def setDiscontinuedReason(self, discontinuedReason):
        self.discontinuedReason = discontinuedReason
    def getEncounter(self):
        return self.encounter
    def setEncounter(self, encounter):
        self.encounter = encounter
    def getInstructions(self):
        return self.instructions
    def setInstructions(self, instructions):
        self.instructions = instructions
    def getAccessionNumber(self):
        return self.accessionNumber
    def setAccessionNumber(self, accessionNumber):
        self.accessionNumber = accessionNumber
    def getOrderer(self):
        return self.orderer
    def setOrderer(self, orderer):
        self.orderer = orderer
    def getOrderId(self):
        return self.orderId
    def setOrderId(self, orderId):
        self.orderId = orderId
    def getStartDate(self):
        return self.startDate
    def setStartDate(self, startDate):
        self.startDate = startDate
    def isCurrent(self, checkDate):
        if self.isVoided():
            return False
        if checkDate == None:
            checkDate = datetime.date #this returns the time but the JAVA code return a Data object
            
class Orderable(Order):
    __metaclass__ = ABCMeta

    def getUniqueIdentifier(self):
        pass
    def getConcept(self):
        pass
    def getName(self):
        pass
    def getDescription(self):
        pass
 
class Retireable(OpenmrsObject):
    __metaclass__ = ABCMeta
    
    def isRetired(self):
        pass
    def setRetired(self, retired):
        pass
    def getRetiredBy(self):
        pass
    def setRetiredBy(self, retiredBy):
        pass
    def getDateRetired(self):
        pass
    def setDateRetired(self, dateRetired):
        pass
    def getRetireReason(self):
        pass
    def setRetireReason(self, retireReason):
        pass

class Voidable(OpenmrsObject):
    __metaclass__ = ABCMeta

    def isVoided(self):
        pass
    def setVoided(self, voided):
        pass
    def getVoidedBy(self):
        pass
    def setVoidedBy(self, voidedBy):
        pass
    def getDateVoided(self):
        pass
    def setDateVoided(self, dateVoided):
        pass
    def getVoidReason(self):
        pass
    def setVoidReason(self, voidReason):
        pass
    
class BaseOpenmrsObject(OpenmrsObject):
    def __init__(self):
        self.uuid = str(uuid4()) #generates a random uuid

    def getUuid(self):
        return self.uuid

    def setUuid(self, uuid):
        self.uuid = uuid

    def hashCode(self):
        if self.getUuid() == None:
            return hash(object) #im not sure if this serves the same purpose as "return super.hashCode();" in the JAVA code
        return hash(self.getUuid())

    def equals(self, obj):
        if self is obj:
            return True
        if not(isinstance(obj, BaseOpenmrsObject)):
            return False
        other = obj
        if self.getUuid() == None:
            return False
        return self.getUuid() == (other.getUuid())

    def __str__(self):
        return "ClassName{hashCode= " + str(self.hashCode()) + "," + "uuid=" + str(self.uuid) + "}"
        
       
