from OpenmrsClasses import *

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

class BaseOpenmrsMetadata(BaseOpenmrsObject, OpenmrsMetadata):
    def __init__(self,name=None, description=None, creator=None, dateCreated=None, \
                 changedBy=None, retired=False, retiredBy = None):
        self.name = name
        self.description = description
        self.creator = creator
        self.dateCreated = dateCreated
        self.changedBy = changedBy
        self.dateChanged = dateChanged
        self.retired = retired
        self.dateRetired = dateRetired
        self.retiredBy = retiredBy
        self.retireReason = retireReason
