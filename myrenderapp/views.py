from django.shortcuts import render, redirect
from django.http import HttpResponse
from rave_python import Rave, RaveExceptions, Misc
from dotenv import load_dotenv
import os
import requests
from django.shortcuts import render
import ast
from django.contrib.auth.forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

load_dotenv()

secret_key = os.getenv('SECRET_KEY')    

# Good code
def user_login(request):
    if request.method == 'POST':
        form  = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/home/')
        print(form.errors)
        return render(request, 'login.html', {'form': form})
        
    form  = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form  = UserCreationForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            print(user_data)
            new_user = form.save()
            login(request, new_user)
            return redirect('/home/')
        print(form.errors)
        return render(request, 'signup.html', {'form': form})
        
    form  = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def user_edit(request):
    if request.method == 'POST':
        form  = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user_data = form.cleaned_data
            print(user_data)
            form.save()
            return redirect('/edit/')
        print(form.errors)
        return render(request, 'edit.html', {'form': form})
        
    form  = UserChangeForm(initial={
        'username': 'admin',
    })
    return render(request, 'edit.html', {'form': form})

# @login_required
def home(request):
    return render(request, 'home.html')

def check_transaction_status(request, transaction_id):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {secret_key}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def activate_order(request):
    # print(request.GET['response'][0][0:20])
    transaction_id = 'tx-28'
    
    if not transaction_id:
        return HttpResponse('Transaction ID missing!')

    transaction_data = check_transaction_status(request, transaction_id)
    status_message = f"Payment processing for {transaction_id}, please refresh to check."

    if transaction_data:
        if transaction_data['status'] == 'success' and transaction_data['data']['status'] == 'successful':
            status_message = f"Payment successful for {transaction_id}! Your order is now active."
        elif transaction_data['data']['status'] == 'failed':
            status_message = f"Payment failed for {transaction_id}, please try again."
        else:
            status_message = f"Payment processing for {transaction_id}, please refresh to check."

    return render(request, 'order_status.html', {'status_message': status_message})



