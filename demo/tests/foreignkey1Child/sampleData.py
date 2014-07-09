from jelf.models import UserProfile, Individual, Address

arielsAddress=Address.objects.create(zipcode="02139")

ariel=Individual()
ariel.address=arielsAddress
ariel.save()
