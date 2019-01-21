from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate


from rundezvous import forms


def home(request):
    user = request.user

    return render(request, 'home.html', {'user': user})


def signup(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('home')
    else:
        form = forms.SignupForm()

    return render(request, 'registration/signup.html', {'form': form})
