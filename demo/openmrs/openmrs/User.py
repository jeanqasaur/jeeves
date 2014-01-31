from BaseClasses import *
from Interfaces import *
from sets import *
import logging

class User(BaseOpenmrsMetadata, Attributable):

    serialVersionID = 2L
    #log = LogFactory.getLog(getClass()); needs LogFactory
    
    def __init__(self, userId=None, person=None, systemId=None, username=None, secretQuestion=None, \
                 roles=None, userProperties=None, ):
        self.userId = userId
        self.person = person
        self.systemId = systemId
        self.username = username
        self.secretQuestion = secretQuestion
        self.roles = roles
        self.userProperties = userProperties
        self.proficientLocales = None
        self.parsedProficientLocalesProperty = ""

    def isSuperUser(self):
        return self.containsRole(RoleConstants.SUPERUSER) #imported library in java code; find equivalent in pyhton
    def hasPrivilege(self, privilege):
        if (privilege == None) or (privilege == ""):
            return True
        if self.isSuperUser():
            return True
        tmproles = self.getAllRoles()
        for i in tmproles:
            if i.hasPrivilege(privilege):
                return True
        return False
    def hasRole(self, r, ignoreSuperUser=False):
        if ignoreSuperUser == False:
            if self.isSuperUser():
                return True
        if self.roles == None:
            return False
        tmproles = self.getAllRoles()

        logging.logger.debug("User #" + str(self.userId) + " has roles: " + str(tmproles))
        
        return self.containsRole(r)
    
    def containsRole(self, roleName):
        for role in self.getAllRoles():
            if role.getRole() == roleName:
                return True
        return False
    def getPrivileges(self):
        privileges = sets.Set() #not hashed; in JAVA it is
        tmproles = self.getAllRoles()
        for role in tmproles: #should it being frmo role.next or the first one?(JAVA code)
            privs = role.getPrivileges()
            if privs != None:
                for priv in privs:
                    privileges.add(priv)
        return privileges
    def getAllRoles(self):
        baseRoles = sets.Set()
        totalRoles = sets.Set()
        if self.getRoles() != None:
            for role in self.getRoles:
                baseRoles.add(role)
                totalRoles.add(role)
        logging.logger.debug("User's base roles: " + str(baseRoles))

        try:
            for r in baseRoles:
                for p in r.getAllParentoles():
                    totalRoles.add(p)
        except ClassCastException: #in JAVA, is there an exception like this in python.
                logging.logger.error("Error converting roles for user: " + str(self))
                logging.logger.error("baseRoles.class: " + str(baseRoles.getClass().getName()))
                logging.logger.error("baseRoles: " + str(baseRoles))
                i = iter(baseRoles)
                while next(i) != None:
                    logging.logger.error("baseRoles: '" + str(next(i)) + "'")
        return totalRoles
        
        #incomplete; there are more methods
