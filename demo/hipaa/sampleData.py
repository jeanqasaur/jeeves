from jelf.models import *
from datetime import date

joesHouse=Address.objects.create(
	City="Cambridge",
    State="MA",
    Street="41 Home St.",
    ZipCode="14830")

arielsHouse=Address.objects.create(
	City="Cambridge",
	State="MA",
	Street="5 Y St.",
	ZipCode="14830")

suesHouse=Address.objects.create(
	City="Boston",
	State="MA",
	Street="1840 Healer",
	ZipCode="14830")

house1=Address.objects.create(
	City="Boston",
	State="MA",
	Street="625 Frost Ln.",
	ZipCode="14830")

house2=Address.objects.create(
	City="Boston",
	State="MA",
	Street="9 Xing",
	ZipCode="14830")

house3=Address.objects.create(
	City="Boston",
	State="MA",
	Street="13 Healer",
	ZipCode="14830")

house4=Address.objects.create(
	City="Seattle",
	State="WA",
	Street="1747 Gray Rd.",
	ZipCode="14830")


house5=Address.objects.create(
	City="Cambridge",
	State="MA",
	Street="7 Backends",
	ZipCode="14830")

ariel = Individual.objects.create(
	FirstName="Ariel",
	LastName="Jacobs",
	Email="ariel@example.com",
	Sex="Male",
	BirthDate=date(1993,03,21),
	Address=arielsHouse)

joe = Individual.objects.create(FirstName="Joe",
    LastName="McGrand",
    BirthDate = date(1979,2,13),
    Address = joesHouse,
    FaxNumber = "205-429-1012",
    TelephoneNumber = "143-143-9883",
    ReligiousAffiliation = "None",
    SSN = "193-24-8873",
    Sex = "Male",
    Email = "joe@example.com",
    DriversLicenseNumber = "J5938532984",
    Employer = "Macro Creations, Inc.")

sue=Individual.objects.create(FirstName="Sue",
    LastName="Huff",
    Email="sue@example.com",
    Address=suesHouse,
    Sex="Female",
    SSN="582081439")

greg=Individual.objects.create(FirstName="Greg",
    LastName="Huff",
    Address=suesHouse,
    Sex="Male",
    Email="greg@mit.example.com",
    TelephoneNumber="2845030411",
    ReligiousAffiliation="Christian")

bob=Individual.objects.create(
	FirstName="Bob",
	LastName="Dreck",
	Email="bob@national.example.com",
	Sex="Male",
	Address=house1,
	TelephoneNumber="4543398401",
	Employer = "Installations and Repair")

justin = Individual.objects.create(FirstName="Justin",
    LastName="Foo",
    Address=house2,
    Email="justin@example.com",
    Sex="Female",
    TelephoneNumber="5240198310",
    ReligiousAffiliation="Catholic",
    Employer = "Foo Market")

vision= CoveredEntity.objects.create(EIN = "01GBS253DV",
                      Name = "Vision National")

health = CoveredEntity.objects.create(EIN = "0424D3294N", Name = "Covered Health")

visit1 = HospitalVisit.objects.create(Patient=joe,
    DateAdmitted=date(2003,4,1),
    DateReleased=date(2003,9,13),
    Condition="Good",
    Location="Third room on the left",
    Hospital=vision)


treat1 = Treatment.objects.create(Patient=ariel,
    DatePerformed=date(2014,1,1),
    PerformingEntity = health,
    PrescribingEntity = health,
    Service = "W4-491")


diag1 = Diagnosis.objects.create(
    DateRecognized=date(2012,9,2),
    RecognizingEntity = vision,
    Diagnosis = "Positive",
    Manifestation = "Obesity",
    Patient = ariel,
)


data = InformationTransferSet.objects.create()
data.save()

dataVisit = HospitalVisitTransfer.objects.create(Set=data, Visit=visit1)
dataVisit.save()

dataTreatment = TreatmentTransfer.objects.create(Set=data, Treatment=treat1)
dataTreatment.save()

dataDiagnosis = DiagnosisTransfer.objects.create(Set=data, Diagnosis=diag1)
dataDiagnosis.save()


trans1 = Transaction.objects.create(
	Standard = "H-78F2",
	SharedInformation = data,
	FirstParty = vision,
	SecondParty = health,
	DateRequested = date(2014,3,4),
	DateResponded = date(2014,4,1),
	Purpose = "Synthesis of records")

'''
assoc = BusinessAssociate()
assoc.Covered=False
assoc.Name="The Best Tax Filers"
assoc.save()

association = assoc.Associations.create(SharedInformation=data, CoveredEntity = vision, Purpose="Tax Filing")

visit2=HospitalVisit()
visit2.Patient=justin
visit2.DateAdmitted=date(2014,4,10)
visit2.Hospital=vision
visit2.Location="369A"
visit2.Condition="Good"
visit2.save()

visit3=HospitalVisit()
visit3.Patient=greg
visit3.DateAdmitted=date(2011,8,10)
visit3.Hospital=vision
visit3.Location="245B"
visit3.Condition = "Improving"
visit3.save()

visit4=HospitalVisit()
visit4.Patient=sue
visit4.DateAdmitted=date(2013,8,10)
visit4.Hospital=vision
visit4.Location="454A"
visit4.Condition = "Steady"
visit4.DateReleased=date(2013,9,2)
visit4.save()

dataVisit = data.Visits.create(Visit = visit2)
dataVisit = data.Visits.create(Visit = visit3)
dataVisit = data.Visits.create(Visit = visit4)

###USERS###


arielj=User()
arielj.username="arielj321"
arielj.first_name="Ariel"
arielj.last_name="Jacobs"
arielj.email="ariel@example.com"
arielj.set_password("hipaaRules")
arielj.save()

arielProfile=UserProfile()
arielProfile.type=1
arielProfile.user=arielj
arielProfile.individual=ariel
arielProfile.save()


mcJoe=User()
mcJoe.username="mcjoe"
mcJoe.first_name="Joe"
mcJoe.last_name="McGrand"
mcJoe.email="joe@example.com"
mcJoe.set_password("hipaaRules")
mcJoe.save()

joeProfile=UserProfile()
joeProfile.type=1
joeProfile.user=mcJoe
joeProfile.individual=joe
joeProfile.save()


vnational=User()
vnational.username="vnational"
vnational.set_password("hipaaRules")
vnational.save()

visionProfile=UserProfile()
visionProfile.type=2
visionProfile.user=vnational
visionProfile.entity=vision
visionProfile.save()

bestTax = User()
bestTax.username = "bestTax"
bestTax.set_password("hipaaRules")
bestTax.save()

bestTaxProfile = UserProfile()
bestTaxProfile.type = 3
bestTaxProfile.user = bestTax
bestTaxProfile.associate = assoc
bestTaxProfile.save()
'''
