from BaseClasses import *
import sets
import logging

class Node:
    def __init__(self, cargo, nextNode, previousNode):
        self.cargo = cargo
        self.next = nextNode
        self.previous = previousNode
    def __str__(self):
        print str(self.cargo)
    
class ordered_set(set):
    def __init__(self, *args, **kwargs):
        set.__init__(self, *args, **kwargs)
        self.elements = []
        for i in self:
            self.elements.append(i)
        self._order = self.elements #NOT SURE IF ORDERED IN ORDER ELTS WERE ADDED

    def add(self, elt):
        set.add(self, elt)
        if elt in self._order:
            self._order.remove(elt)
        self._order.append(elt)

    def remove(self, elt):
        set.remove(self, elt)
        self._order.remove(elt)

    def order(self):
        return self._order[:]

    def ordered_items(self):
        return [(elt) for elt in self._order]
    
o = ordered_set(set([3, 2, 5, 4, 10]))
print o

            
class Obs(BaseOpenmrsData): #needs to implement Serializable
    serialVersionUID = 112342333L
    #log = LogFactory.getLog(Obs) #haven't defined a LogFactory yet

    def __init__(self, obsId=None,question=None, obsDatetime=None, accessionNumber=None,\
                 obsGroup = None, groupMembers=set(), valueCoded=None, valueCodedName=None,\
                 valueDrug=None, valueGroupId=None,valueDatetime=None, valueNumeric=None,\
                 valueModifier=None, valueText=None, valueComplex=None,complexData = None,\
                 comment=None, personId=None,person=None, order=None, location=None,encounter=None,\
                 previousVersion=None):
        self.obsId = obsId
        self.concept = question
        self.obsDatetime = obsDatetime
        self.accessionNumber = accessionNumber
        self.obsGroup = obsGroup
        self.groupMembers = groupMembers #set
        self.valueCoded = valueCoded #Concept obj
        self.valueCodedName = valueCodedName #ConceptName obj
        self.valueDrug = valueDrug #Drug obj
        self.valueGroupId = valueGroupId
        self.valueDatetime = valueDatetime
        self.valueNumeric = valueNumeric
        self.valueModifier = valueModifier
        self.valueText = valueText
        self.valueComplex = valueComplex
        self.complexData = complexData #transient: can't be serialized
        self.comment = comment
        self.person = person
        if person != None:
            self.personId = person.getPersonId() #transient
        self.order = order
        self.location = location
        self.encounter = encounter
        self.previousVersion = previousVersion

    def newInstance(self, obsToCopy):
        newObs = Obs(obsToCopy.getPerson(), obsToCopy.getConcept(), obsToCopy.getObsDateTime(),\
                     obsToCopy.getLocation())
        newObs.setObsGroup(obsToCopy.getObsGroup())
        newObs.setAccessionNumber(obsToCopy.getAccessionNumber())
        newObs.setValueCoded(obsToCopy.getValueCoded())
        newObs.setValueDrug(obsToCopy.getValueDrug())
        newObs.setValueGroupId(obsToCopy.getValueGroupId())
        newObs.setValueDatetime(obsToCopy.getValueDatetime())
        newObs.setValueNumeric(obsToCopy.getValueNumeric())
        newObs.setValueModifier(obsToCopy.getValueModifier())
        newObs.setValueText(obsToCopy.getValueText())
        newObs.setComment(obsToCopy.getComment())
        newObs.setOrder(obsToCopy.getOrder())
        newObs.setEncounter(obsToCopy.getEncounter())
        newObs.setCreator(obsToCopy.getCreator())
        newObs.setDateCreated(obsToCopy.getDateCreated())
        newObs.setVoided(obsToCopy.getVoided())
        newObs.setVoidedBy(obsToCopy.getVoidedBy())
        newObs.setDateVoided(obsToCopy.getDateVoided())
        newObs.setVoidReason(obsToCopy.getVoidReason())
        
        newObs.setValueComplex(obsToCopy.getValueComplex())
        newObs.setComplexData(obsToCopy.getComplexData())

        if obsToCopy.hasGroupMembers(True):
            for member in obsToCopy.getGroupMembers(True):
                if member.getObsId() == None:
                    newObs.addGroupMember(member)
                else:
                    newObs.addGroupMember(Obs.newInstance(member))
        return newObs
    def getComment(self):
        return self.comment
    def setComment(self, comment):
        self.comment = comment
    def getConcept(self):
        return self.concept
    def setConcept(self, concept):
        self.concept = concept
    def getConceptDescription(self):
        if self.getConcept() == None:
            return None
        return self.concept.getDescription()
    def getEncounter(self):
        return self.encounter
    def setEncounter(self, encounter):
        self.encounter = encounter
    def getLocation(self):
        return self.location
    def setLocation(self, location):
        self.location = location
    def getObsDatetime(self):
        return self.obsDatetime
    def setObsDatetime(self, obsDatetime):
        self.obsDatetime = obsDatetime
    def getObsGroup(self):
        return self.obsGroup
    def setObsGroup(self,obsGroup):
        self.obsGroup = obsGroup

    
    def hasGroupMembers(self, includeVoided=False):
        #uses springFramework library
        pass
        
    def isObsGrouping(self):
        return self.hasGroupMembers(True)
    
    def getGroupMembers(self, includeVoided=False):
        if includeVoided:
            return self.groupMembers
        if self.groupMembers == None:
            return None
        nonVoided = ordered_set(self.groupMembers)
        i = iter(nonVoided)
        while next(i) != None:
            obs = next(i)
            if obs.isVoided():
                nonVoided.remove(i) #not sure if this is what's required
        return nonVoided
    def setGroupMembers(self, groupMembers):
        self.groupMembers = groupMembers
    def addGroupMember(self, member):
        if member == None:
            return None
        if self.getGroupMembers() == None:
            self.groupMembers = sets.ImmutableSet() #Same as HashSet?
        if member == self:
            raise APIException("An obsGroup cannot have itself as a mentor. obsGroup: " + self \
			        + " obsMember attempting to add: " + member)
            #I think APIException is defined in another JAVA class file; not sure if Python has this
        member.setObsGroup(self)
        self.groupMembers.add(member)
    def removeGroupMember(self, member):
        if (member == None) or self.getGroupMembers() == None:
            return None
        if self.groupMembers.remove(member):
            member.setObsGroup(None)
    def getRelatedObservations(self):
        ret = sets.Set() #Supposed to be ImmutableSet but we can't add elts to that; Set isnt hashed
        if self.isObsGrouping():
            for i in self.getGroupMembers():
                ret.add(i)
            parentObs = self
            while parentObs.getObsGroup() != None :
                for obsSibling in parentObs.getObsGroup().getGroupMembers():
                    if not(obsSibling.isObsGrouping()):
                        ret.add(obsSibling)
                parentObs = parentObs.getObsGroup()
        elif self.getObsGroup() != None:
            for obsSibling in self.getObsGroup().getGroupMembers():
                if not(obsSibling.isObsGrouping()):
                    ret.add(obsSibling)
        return ret
    def getObsId(self):
        return self.obsId
    def setObsId(self,obsId):
        self.obsId = obsId
    def getOrder(self):
        return self.order
    def setOrder(self, order):
        self.order = order
    def getPersonId(self):
        return self.personId
    def setPersonId(self, personId):
        self.personId = personId
    def getPerson(self):
        return self.person
    def setPerson(self, person):
        self.person = person
        if person != None:
            self.personId = person.getPersonId()
    def setValueBoolean(self, valueBoolean):
        if (valueBoolean != None) and (self.getConcept() != None) and self.getConcept().getDatatype().isBoolean():
            if valueBoolean.booleanValue():
                self.setValueCoded(Context().getConceptService().getTrueConcept())
            else:
                self.setValueCoded(Context().getConceptService().getFalseConcept())
        #Context is from api directory
        elif valueBoolean == None:
            self.setValueCoded(None)
    def getValueAsBoolean(self):
        if self.getValueCoded() != None:
            if self.getValueCoded() == Context().getConceptService().getTrueConcept():
                return True
            elif self.getValueCoded() == Context().getConceptService().getFalseConcept():
                return False
        elif self.getValueNumeric() != None:
            if self.getValueNumeric() == 1:
                return True
            elif self.getValueNumeric() == 0:
                return False
        return None
    def getValueBoolean(self):
        if (self.getConcept() != None) and (self.valueCoded != None) and (self.getConcept().getDatatype().isBoolean()):
            trueConcept = Context.getConceptService().getTrueConcept()
            return (trueConcept != None) and (self.valueCoded.getId() == trueConcept.getId())
        return None
    def getValueCoded(self):
        return self.valueCoded
    def setValueCoded(self, valueCoded):
        self.valueCoded = valueCoded
    def getValueCodedName(self):
        return self.valueCodedName
    def setValueCodedName(self, valueCodedName):
        self.valueCodedName = valueCodedName
    def getValueDrug(self):
        return self.valueDrug
    def setValueDrug(self, valueDrug):
        self.valueDrug = valueDrug
    def getValueDatetime(self):
        return self.valueDatetime
    def setValueDatetime(self, valueDatetime):
        self.valueDatetime = valueDatetime
    def getValueDate(self):
        return self.valueDatetime
    def setValueDate(self, valueDate):
        self.valueDatetime = valueDate
    def getValueTime(self):
        return self.valueDatetime
    def setValueTime(self, valueTime):
        self.valueDatetime = valueTime
    def getValueGroupId(self):
        return valueGroupId
    def setValueGroupId(self, valueGroupId):
        self.valueGroupId = valueGroupId
    def getValueModifier(self):
        return self.valueModifier
    def setValueModifier(self, valueModifier)):
        self.valueModifier = valueModifier
    def getValueNumeric(self):
        return self.valueNumeric
    def setValueNumeric(self, valueNumeric):
        self.valueNumeric = valueNumeric
    def getValueText(self):
        return self.valueText
    def setValueText(self, valueText):
        self.valueText = valueText
    def isComplex(self):
        if self.getConcept() != None:
            return self.getConcept().isComplex()
        return False
    def getValueComplex(self):
        return self.valueComplex
    def setValueComplex(self, valueComplex):
        self.valueComplex = valueComplex
    def setComplexData(self, complexData):
        self.complexData = complexData
    def getComplexData(self):
        return self.complexData
    def getAccessionNumber(self):
        return self.accessionNumber
    def setAccessionNumber(self, accessionNumber):
        self.accessionNumber = accessionNumber
    def getValueAsString(self, locale):
        #Needs NumberFormat and other built in functions
        pass
    def setValueAsString(self, s):
        logging.logger.debug("self.getConcept() == " + str(self.getConcept()))
        if (self.getConcept() != None) and (isBlank(s)): #isBlank(s) checks if s is whitespace, null, or empty. Need to find Python equivalent. 
            abbrev = self.getConcept().getDatatype().getHl7Abbreviation()
            if abbrev == "BIT":
                self.setValueBoolean(s) #s might be lowercase true, not True. Solve this.
            elif abbrev == "CWE":
                raise RuntimeException("Not Yet Implemented")
            elif (abbrev == "NM") or (abbrev == "SN"):
                self.setValueNumeric(s)
            elif abbrev == "DT":
                self.setValueDatetime(s) #dateFormat.parse(s) in JAVA. must be in da specific date format
            elif abbrev == "TM":
                self.setValueDatetime(s) #timeFormat.parse(s) in JAVA too
            elif abbrev == "TS":
                self.setValueDatetime(s) #datetimeFormat.parse(s)
            elif abbrev == "ST":
                self.setValueText(s)
            else:
                raise RuntimeException("Don't know how to handle " + str(abbrev))
        else:
            raise RuntimeException("concept is None for " + str(self))
    def __str__(self):
        if self.obsId == None:
            return "obs id is None"
        return "Obs #" + str(self.obsId)
    def getId(self):
        return self.getObsId
    def setId(self,Id):
        self.setObsId(Id)
    def getPreviousVersion(self):
        return self.previousVersion
    def setPreviousVersion(self, previousVersion):
        self.previousVersion = previousVersion
    def hasPreviousVersion(self):
        return self.getPreviousVersion() != None
