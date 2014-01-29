from OpenmrsClasses import *

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
