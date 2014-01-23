from abc import ABCMeta, abstractmethod
import uuid
import org.python.google.common.base.objects as objects #not sure if this is the same as com.google.common.base.Objects in JAVA code
from datetime import datetime, date 
import pickle
from flufl.enum import Enum

#Interfaces
class OpenmrsObject:
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
    
class OpenmrsData(OpenmrsObject, Auditable, Voidable):

    __metaclass__ = ABCMeta
    

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
    #is it right that these are class attributes?
    
    def __init__(self, orderId=None, patient=None, concept=None, discontinued = False, \
                 autoExpireDate=None, discontinuedBy=None, discontinuedDate=None, discontinuedReason=None, \
                 encounter=None, instructions=None,accessionNumber=None, orderer=None, startDate=None,\
                 orderNumber=None, previousOrderNumber=None):
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
        self.orderNumber = orderNumber
        self.previousOrderNumber = previousOrderNumber
        self.orderAction = OrderAction.ORDER
        self.urgency = Urgency.ROUTINE
        #is it right that these are instance attributes
    def copy(self):
        return self.copyHelper(Order())
    
    def copyHelper(self, target):
        target.setPatient(self.getPatient())
        target.setConcept(self.getConcept())
        target.setInstructions(self.getInstructions())
        target.setStartDate(self.getStartDate())
        target.setAutoExpireDate(self.getAutoExpireDate())
        target.setEncounter(self.getEncounter())
        target.setOrderer(self.getOrderer())
        target.setCreator(self.getCreator())
        target.setDateCreated(self.getDateCreated())
        target.setDiscontinued(self.getDiscontinued())
        target.setDiscontinuedDate(self.getDiscontinuedDate())
        target.setDiscontinuedReason(self.getDiscontinuedReason())
        target.setDiscontinuedBy(self.getDiscontinuedBy())
        target.setAccessionNumber(self.getAccessionNumber())
        target.setVoided(self.isVoided())
        target.setVoidedBy(self.getVoidedBy())
        target.setDateVoided(self.getDateVoided())
        target.setVoidReason(self.getVoidReason())
        target.setOrderNumber(self.getOrderNumber())
        target.setPreviousOrderNumber(self.getPreviousOrderNumber())
        target.setOrderAction(self.getOrderAction())
        target.setUrgency(self.getUrgency())
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
        self.autoExpireDate = autoExpireDate #datetime object
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
        return self.startDate #datetime object
    def setStartDate(self, startDate):
        self.startDate = startDate
    def isCurrent(self, checkDate=None):
        #checkDate is an optional argument so it's equivalent of the two methods
        #isCurrent() and isCurrent(Date checkDate) in JAVA code. If checkDate is None,
        #a datetime object representing today is initialized, which is same as isCurrent(new Date()) 
        if self.isVoided():
            return False
        if checkDate == None:
            checkDate = datetime.now() #this returns the datetime object with microsecond, the JAVA code returns a Date object of when the obj was created
        if (self.startDate != None) and (checkDate < self.startDate):
            return False
        if (self.discontinued != None) and self.discontinued:
            if self.discontinuedDate == None:
                return checkDate == self.startDate
            else:
                return checkDate < self.discontinuedDate
        else:
            if self.autoExpireDate == None:
                return True
            else:
                return checkDate < self.autoExpireDate
            
    def isFuture(self, checkDate=None):
        if self.isVoided():
            return False
        if checkDate == None:
            checkDate = datetime.now()
        return (self.startDate != None) and checkDate < self.startDate
    
    def isDiscontinued(self, checkDate):
        if self.isVoided():
            return False
        if (checkDate == None):
            checkDate = datetime.now()
        if (self.discontinued == None) or not(self.discontinued):
            return False
        if (self.startDate == None) or (checkDate < self.startDate):
            return False
        if (self.discontinuedDate != None) and (self.discontinuedDate > checkDate):
            return False
        return True
    
    def isDiscontinuedRightNow(self):
        return self.isDiscontinued(datetime.now())
    
    def getPatient(self):
        return self.patient
    def setPatient(self, patient):
        self.patient = patient
    def getOrderNumber(self):
        return self.orderNumber
    def setOrderNumber(self, orderNumber):
        self.orderNumber = orderNumber
    def getPreviousOrderNumber(self):
        return self.previousOrderNumber
    def setPreviousOrderNumber(self, previousOrderNumber):
        self.previousOrderNumber = previousOrderNumber
    def getOrderAction(self):
        return self.orderAction
    def setOrderAction(self, orderAction):
        self.orderAction=orderAction
    def getId(self):
        return self.getOrderId()
    def __str__(self):
        #type(self) same as getClass()? 
        return "Order. orderId: " + str(self.orderId) + " patient: " + str(self.patient) + " orderType: " + type(self) + " concept: " + str(self.concept)
    def setId(self, Id):
        self.setOrderId(Id)
    def getUrgency(self):
        return self.urgency
    def setUrgency(self, urgency):
        self.urgency = urgency
        
    def copyForModification(self):
        #I'm not sure if this makes a copy
        copy = self.copyHelper(self)
        copy.orderNumber = None
        copy.previousOrderNumber = self.orderNumber
        #would self.orderNumber be None since copy.orderNumber = None and copy = self?
        return copy

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
        
class BaseOpenmrsData(BaseOpenmrsObject, OpenmrsData):
    def __init(self,creator=None,dateCreated=None, changedBy=None, dateChanged=None, \
               voided=False,dateVoided=None, voidedBy=None, voidReason=None):
        self.creator = creator
        self.dateCreated = dateCreated
        self.changedBy = changedBy
        self.dateChanged = dateChanged
        self.voided = voided
        self.dateVoided = dateVoided
        self.voidedBy = voidedBy
        self.voidReason = voidReason

    def getCreator(self):
        return self.creator
    def setCreator(self, creator):
        self.creator = creator
    def getDateCreated(self):
        return self.dateCreated
    def setDateCreated(self, dateCreated):
        self.dateCreated = dateCreated
    def getChangedBy(self):
        return self.changedBy
    def setChangedBy(self, changedBy):
        self.changedBy = changedBy
    def getDateChanged(self):
        return self.dateChanged
    def setDateChanged(self, dateChanged):
        self.dateChanged = dateChanged
    def isVoided(self):
        return self.voided
    def getVoided(self):
        return self.isVoided()
    def setVoided(self, voided):
        self.voided = voided
    def getDateVoided(self):
        return self.dateVoided
    def setDateVoided(self, dateVoided):
        self.dateVoided = dateVoided
    def getVoidedBy(self):
        return self.voidedBy
    def setVoidedBy(self, voidedBy):
        self.voidedBy = voidedBy
    def getVoidReason(self):
        return self.voidReason
    def setVoidReason(self, voidReason):
        self.voidReason = voidReason
