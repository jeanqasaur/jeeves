from django.db.models import Model, ManyToManyField, ForeignKey, OneToOneField, CharField, TextField, DateField, DateTimeField, IntegerField, FileField, BooleanField

from jeevesdb.JeevesModel import JeevesModel as Model
from jeevesdb.JeevesModel import JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

from settings import CONF_PHASE as phase

class Address(Model):
	Street=CharField(max_length=100, blank=True, null = True)
	City=CharField(max_length=30)
	State=CharField(max_length=20)
	ZipCode=CharField(max_length=5)
	def String(self):
		return self.Street+"\n"+self.ZipCode+" "+self.City+", "+self.State
	class Meta:
		db_table = 'Address'

class Individual(Model):
	FirstName = CharField(max_length=1024)
	Email = CharField(max_length=1024, blank=True, null = True)
	Address = ForeignKey(Address, blank=True, null = True)
	BirthDate = DateField(blank=True, null = True)
	Sex = CharField(max_length=6, blank=True, null = True)
	#Parent = ForeignKey("self",blank=True,null=True)
	LastName = CharField(max_length=1024)
	UID = IntegerField(primary_key=True)
	SSN = CharField(max_length=9, blank=True, null = True)
	TelephoneNumber = CharField(max_length=10, blank=True, null = True)
	DriversLicenseNumber = CharField(max_length=20, blank=True, null = True)
	Employer = CharField(max_length=50, blank=True, null = True)
	FaxNumber = CharField(max_length=10, blank=True, null = True)
	#PersonalRepresentative = ForeignKey("self",blank=True,null=True)
	ReligiousAffiliation = CharField(max_length=100, blank=True, null = True)
	class Meta:
		db_table = 'Individual'
	def Name(self):
		return self.FirstName +" "+self.LastName

class UserProfile(Model):
    username = CharField(max_length=1024)
    email = CharField(max_length=1024)

    name = CharField(max_length=1024)
    affiliation = CharField(max_length=1024)
    acm_number = CharField(max_length=1024)

    level = CharField(max_length=12,
                    choices=(('normal', 'normal'),
                        ('pc', 'pc'),
                        ('chair', 'chair')))

    @staticmethod
    def jeeves_get_private_email(user):
        return ""

    @staticmethod
    @label_for('email')
    @jeeves
    def jeeves_restrict_userprofilelabel(user, ctxt):
        return user == ctxt or (ctxt != None and ctxt.level == 'chair')

    class Meta:
        db_table = 'user_profiles'

class UserPCConflict(Model):
    user = ForeignKey(UserProfile, null=True, related_name='userpcconflict_user')
    pc = ForeignKey(UserProfile, null=True, related_name='userpcconflict_pc')

    @staticmethod
    def jeeves_get_private_user(uppc):
        return None
    @staticmethod
    def jeeves_get_private_pc(uppc):
        return None

    @staticmethod
    @label_for('user', 'pc')
    @jeeves
    def jeeves_restrict_userpcconflictlabel(uppc, ctxt):
        return True
        #return ctxt.level == 'chair' or uppc.user == ctxt


class BusinessAssociate(Model):
	
	'''
	Persons or corporations that perform services for covered entities. They may
	or may not be covered entities themselves.
	'''
	
	Name = CharField(max_length=1024)
	#CoveredIdentity = ForeignKey("CoveredEntity", null=True, blank=True)
	Covered = BooleanField() #Because the above line doesn't work yet in Jeeves (circular references)
	class Meta:
		db_table = 'BusinessAssociate'

class CoveredEntity(Model):
    
    '''
    Health plan, health clearinghouse,
    or health care provider making sensitive transactions. This includes hospitals.
    '''
    EIN = CharField(max_length=9, blank=False, null=False,unique=True) #Employer Identification Number
    Name = CharField(max_length=1024)
    Directory = ManyToManyField(Individual,through="HospitalVisit")
    Associates = ManyToManyField(BusinessAssociate,through="BusinessAssociateAgreement")
    class Meta:
        db_table = 'CoveredEntity'

class HospitalVisit(Model):
    Patient = ForeignKey(Individual)
    Hospital = ForeignKey(CoveredEntity, related_name="Patients")
    DateAdmitted = DateField()
    Location = TextField(blank=True, null = True)
    Condition = TextField(blank=True, null = True)
    DateReleased = DateField(blank=True, null=True) #Blank if the patient is still at the hospital.
    class Meta:
        db_table = 'HospitalVisit'

class Treatment(Model):
    '''
    Provided medical treatment, medication, or service.
    '''
    Service = CharField(max_length=100)
    DatePerformed = DateField()
    PrescribingEntity = ForeignKey(CoveredEntity, related_name="Prescriptions")
    PerformingEntity = ForeignKey(CoveredEntity)
    Patient = ForeignKey(Individual)
    class Meta:
        db_table = 'Treatment'

class Diagnosis(Model): 
    '''
    Recognition of health condition or situation by a medical professional.
    '''
    Manifestation = CharField(max_length=100)
    Diagnosis = CharField(max_length=255)
    DateRecognized = DateField()
    RecognizingEntity = ForeignKey(CoveredEntity)
    Patient = ForeignKey(Individual)
    class Meta:
        db_table = 'Diagnosis'

class InformationTransferSet(Model):
	'''
	Collection of private information that can be shared
	'''
	class Meta:
		db_table = 'InformationTransferSet'

class TreatmentTransfer(Model):
	Set = ForeignKey(InformationTransferSet, related_name="Treatments")
	Treatment = ForeignKey(Treatment)
	class Meta:
		db_table = 'TreatmentTransfer'
class DiagnosisTransfer(Model):
	Set = ForeignKey(InformationTransferSet, related_name="Diagnoses")
	Diagnosis = ForeignKey(Diagnosis)
	class Meta:
		db_table = 'DiagnosisTransfer'
class HospitalVisitTransfer(Model):
	Set = ForeignKey(InformationTransferSet, related_name="Visits")
	Visit = ForeignKey(HospitalVisit)
	class Meta:
		db_table = 'HospitalVisitTransfer'

class BusinessAssociateAgreement(Model):
	BusinessAssociate = ForeignKey(BusinessAssociate, related_name="Associations")
	CoveredEntity = ForeignKey(CoveredEntity, related_name="Associations")
	SharedInformation = OneToOneField(InformationTransferSet)
	Purpose = TextField(blank=True, null = True)
	class Meta:
		db_table = 'BusinessAssociateAgreement'

class Transaction(Model):

    '''
    A defined standard transaction between covered entitities.

    Attributes:
    Standard - Transaction Code: ICS-10-PCS, HCPCS, e.g.
    FirstParty, SecondParty - Covered entities performing the transaction
    SharedInformation - Information transferred between the parties to fulfill the transaction.
    '''

    Standard = CharField(max_length=100)
    FirstParty = ForeignKey(CoveredEntity, related_name = "SomeTransactions")
    SecondParty = ForeignKey(CoveredEntity, related_name = "MoreTransactions")
    SharedInformation = OneToOneField(InformationTransferSet)
    DateRequested = DateField()
    DateResponded = DateField()
    Purpose = TextField(blank=True, null = True)
    class Meta:
        db_table = 'Transaction'

class PersonalRepresentative(Model):
	Dependent = ForeignKey(Individual)
	Representative = ForeignKey(Individual, related_name='Dependents')
	Parent = BooleanField()
	class Meta:
		db_table = 'PersonalRepresentative'