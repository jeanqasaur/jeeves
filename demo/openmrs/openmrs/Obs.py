from BaseOpenmrsObject import *

class ordered_dict(set):
    def __init__(self, *args, **kwargs):
        set.__init__(self, *args, **kwargs)
        self._order = self.keys() #change to elements, not keys

    def __setitem__(self, key):
        set.__setitem__(self, key)
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def __delitem__(self, key):
        set.__delitem__(self, key)
        self._order.remove(key)

    def order(self):
        return self._order[:]

    def ordered_items(self):
        return [(key,self[key]) for key in self._order]
    
class Obs(BaseOpenmrsData): #needs to implement Serializable
    serialVersionUID = 112342333L
    log = LogFactory.getLog(Obs) #haven't defined a LogFactory yet

    def __init__(self, obsId=None,question=None, obsDatetime=None, accessionNumber=None,\
                 obsGroup = None, groupMembers=set(), valueCoded=None, valueCodedName=None,\
                 valueDrug=None, valueGroupId=None,valueDatetime=None, valueNumeric=None,\
                 valueModifier=None, valueText=None, valueComplex=None,complexData = None,\
                 comment=None, personId=None,person=None, order=None, location=None,encounter=None,\
                 previousVersion=None, ):
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

        
    def isObsGrouping(self):
        return self.hasGroupMembers(True)
