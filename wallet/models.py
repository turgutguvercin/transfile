from django.db import models 
from django.contrib.auth.models import User

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)


    def add_credits(self, amount, description=""):
        Transaction.objects.create(user=self.user, amount=amount, description=description)
        self.credits += amount
        self.save()

    def spend_credits(self, amount, description=""):
        if self.credits < amount:
            raise ValueError("You poor you don't have enough credits")  
        Transaction.objects.create(user=self.user, amount=-amount, description=description)
        self.credits -= amount
        self.save()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)