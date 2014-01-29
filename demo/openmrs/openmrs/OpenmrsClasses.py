from abc import ABCMeta, abstractmethod
import uuid
#import org.python.google.common.base.objects as objects #not sure if this is the same as com.google.common.base.Objects in JAVA code
from datetime import datetime, date 
import pickle


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


    
class OpenmrsData(Auditable, Voidable):

    __metaclass__ = ABCMeta
    
class OpenmrsMetadata(Auditable, Retireable):

    __metaclass__ = ABCMeta

    def getName(self):
        pass
    def setName(self, name):
        pass
    def getDescription(self):
        pass
    def setDescription(self, description):
        pass       
        

    




 

        

