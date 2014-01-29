from BaseClasses import *

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
    
class Order(BaseOpenmrsData): #serializable has to be implemented
    serialVersionUID = 1L
    OrderAction = Enum(['ORDER', 'DISCONTINUE']) #is this equivalent of enum type in JAVA?
    Urgency = Enum(['ROUTINE', 'STAT'])
    #is it right that these are class attributes?
    
    def __init__(self, creator = None, dateCreated = None, orderId=None, patient=None, concept=None, discontinued = False, \
                 autoExpireDate=None, discontinuedBy=None, discontinuedDate=None, discontinuedReason=None, \
                 encounter=None, instructions=None,accessionNumber=None, orderer=None, startDate=None,\
                 orderNumber=None, previousOrderNumber=None, voided = False, voidedBy = None, dateVoided=None, voidReason=None):
        self.creator = creator
        self.dateCreated = dateCreated
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
        self.orderAction = Order.OrderAction.ORDER
        self.urgency = Order.Urgency.ROUTINE
        self.voided = voided
        self.voidedBy = voidedBy
        self.dateVoided = dateVoided
        self.voidReason = voidReason
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
            return hash(object) #same as super.hashCode()? super.hashCode() returns diff codes everytime its run
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
        return "Order. orderId: " + str(self.orderId) + " patient: " + str(self.patient) + " concept: " + str(self.concept)
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
