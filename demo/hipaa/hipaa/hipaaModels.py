from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField, BooleanField

from jeevesdb.JeevesModel import JeevesModel as Model
from jeevesdb.JeevesModel import JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

from settings import CONF_PHASE as phase

class Address(Model):
    Street=CharField(max_length=100)
    City=CharField(max_length=30)
    State=CharField(max_length=20)
    ZipCode=CharField(max_length=5)
    class Meta:
        db_table = 'Address'
        
class Individual(Model):
    FirstName = CharField(max_length=1024)
    Email = CharField(max_length=1024)
    Address = ForeignKey(Address)
    BirthDate = DateField()
    Sex = CharField(max_length=6)
    Parent = ForeignKey("self",blank=True,null=True)
    LastName = CharField(max_length=1024)
    UID=IntegerField(primary_key=True)
    SSN = CharField(max_length=9)
    TelephoneNumber = CharField(max_length=10)
    FaxNumber = CharField(max_length=10)
    PersonalRepresentative = ForeignKey("self",blank=True,null=True)
    ReligiousAffiliation = CharField(max_length=100)
    class Meta:
        db_table = 'Individual'

class CoveredEntity(Model):
    
    '''
    Health plan, health clearinghouse,
    or health care provider making sensitive transactions. This includes hospitals.
    '''
    
    Name = CharField(max_length=1024)
    Directory = ManyToManyField(Individual,through="HospitalVisit")
    Associates = ManyToManyField(BusinessAssociate,through="BusinessAssociateAgreement")
    class Meta:
        db_table = 'CoveredEntity'

class BusinessAssociate(Model):
    
    '''
    Persons or corporations that perform services for covered entities. They may
    or may not be covered entities themselves.
    '''
    
    Name = CharField(max_length=1024)
    CoveredIdentity = ForeignKey(CoveredEntity, null=True, blank=True)
    class Meta:
        db_table = 'BusinessAssociate'

class BusinessAssociateAgreement(Model):
    BusinessAssociate = ForeignKey(BusinessAssociate)
    CoveredEntity = ForeignKey(CoveredEntity)
    SharedInformation = OneToOneField(InformationTransferSet)
    class Meta:
        db_table = 'BusinessAssociateAgreement'

class Treatment(Model):
    '''
    Provided medical treatment, medication, or service.
    '''
    Service = CharField(max_length=100)
    DatePerformed = DateField()
    PrescribingEntity = ForeignKey(CoveredEntity)
    PerformingEntity = ForeignKey(CoveredEntity)
    Patient = ForeignKey(Individual)
    class Meta:
        db_table = 'Treatment'

class Diagnosis(Model): 
    '''
    Recognition of health condition or situation by a medical professional.
    '''
    Manifestation = CharField(max_length=100)
    DateRecognized = DateField()
    RecognizedEntity = ForeignKey(CoveredEntity)
    Patient = ForeignKey(Individual)
    class Meta:
        db_table = 'Diagnosis'

class HospitalVisit(Model):
    Patient = ForeignKey(Individual)
    Hospital = ForeignKey(CoveredEntity)
    DateAdmitted = DateField()
    Location = TextField()
    Condition = TextField()
    Active = BooleanField(default=True) #If the patient is still at the hospital.
    class Meta:
        db_table = 'HospitalVisit'
        
class Transaction(Model):
    
    '''
    A defined standard transaction between covered entitities.

    Attributes:
    Standard - Transaction Code: ICS-10-PCS, HCPCS, e.g.
    FirstParty, SecondParty - Covered entities performing the transaction
    SharedInformation - Information transferred between the parties to fulfill the transaction.
    '''

    Standard = CharField(max_length=100)
    FirstParty = ForeignKey(CoveredEntity)
    SecondParty = ForeignKey(CoveredEntity)
    SharedInformation = OneToOneField(InformationTransferSet)
    DateRequested = DateField()
    DateResponded = DateField()
    Purpose = TextField()
    class Meta:
        db_table = 'Transaction'
        
class InformationTransferSet(Model):
    
    '''
    Collection of private information that can be shared
    '''
    Treatments = ManyToManyField(Treatment)
    Diagnoses = ManyToManyField(Diagnosis)
    HospitalVisits = ManyToManyField(HospitalVisit)
    class Meta:
        db_table = 'InformationTransferSet'
