from jelf.models import UserProfile, Individual, Address

arielsAddress=Address()
arielsAddress.zipcode="02139"
arielsAddress.save()

ariel=Individual()
ariel.address=arielsAddress
ariel.save()
