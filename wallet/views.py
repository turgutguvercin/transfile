from django.db.models import ObjectDoesNotExist
from django.shortcuts import render
from .models import UserWallet

def get_credits(request):
    if request.user.is_authenticated:
        try:
            wallet = UserWallet.objects.get(user=request.user)
        
        except: 
            raise ObjectDoesNotExist("Could not found any wallet") 
        
        return render(request, "pigeon.html", {"credits":credits})