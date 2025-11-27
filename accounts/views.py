from django.shortcuts import redirect, render
from .forms import UserForm
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserForm()
    return render(request, "registration/register.html",{"form":form})