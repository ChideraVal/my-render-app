from django.shortcuts import render, redirect
from django.http import HttpResponse
from rave_python import Rave, RaveExceptions, Misc
from dotenv import load_dotenv
import os
import requests
from django.shortcuts import render
# from .models import Order

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

rave = Rave(os.getenv("FLW_PUBLIC_KEY"),
            os.getenv("SECRET_KEY"),
            # os.getenv("FLW_ENCRYPTION_KEY"),
            production=True)

# Payload with pin
payload = {
  "cardno": "4187451833403969",
  "cvv": "262",
  "expirymonth": "07",
  "expiryyear": "26",
  "currency": "NGN",
  "amount": "50",
  "email": "pyjamel224@gmail.com",
  "phonenumber": "07016793402",
  "firstname": "Joy",
  "lastname": "Ngozi",
  "redirect_url": "http://127.0.0.1:8000/verify/"
#   "IP": "355426087298442",
}


def pay(request):
    try:
        res = rave.Card.charge(payload)
        print(f'[INITIAL RESPONSE: {res}]')

        if res["suggestedAuth"]:
            arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])
            print(f'[ARG: {arg}]')


            if arg == "pin":
                Misc.updatePayload(res["suggestedAuth"], payload, pin="1010")
            if arg == "address":
                Misc.updatePayload(res["suggestedAuth"], payload, address= {"billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
            print(f'[NEW PAYLOAD: {payload}]')
            res = rave.Card.charge(payload)

        if res["validationRequired"]:
            print('vallidating...')
            print(f'[FINAL RESPONSE: {res}]')

            # print(res['authUrl'])
            # otp = input('OTP: ')
            request.session.__setitem__('txtref', res["txRef"])
            request.session.__setitem__('res', res)
            print(f'[SET TEXT REF TO {request.session.__getitem__("txtref")}]')
            return redirect(res['authUrl'])
            # rave.Card.validate(res["flwRef"], otp)
        

        print(f'[VERIFYING TRANSACTION...]')
        res = rave.Card.verify(res["txRef"])
        print(res["transactionComplete"])
        return HttpResponse("Transaction has been completed successfully, Hurray!!!")

    except RaveExceptions.CardChargeError as e:
        print('Card error')
        print(e.err)
        print(e.err["errMsg"])
        print(e.err["flwRef"])
        return HttpResponse(f"CARD ERROR: {e.err['errMsg']}")

    except RaveExceptions.TransactionValidationError as e:
        print('Validataion error')
        print(e.err)
        print(e.err["errMsg"])
        print(e.err["flwRef"])
        return HttpResponse(f"VALIDATION ERROR: {e.err['errMsg']}")

    except RaveExceptions.TransactionVerificationError as e:
        print('Verification error')
        print(e.err)
        print(e.err["errMsg"])
        print(e.err["txRef"])
        return HttpResponse(f"VERIFICATION ERROR: {e.err['errMsg']}")

def validate(request):
    txtRef = request.session.__getitem__('txtref')
    res = request.session.__getitem__('res')
    print(f'[GETTING TEXT REF AS: {txtRef}]')
    try:
        print(f'[VALIDATING TRANSACTION IN FUNC...]')
        res = rave.Card.validate(str(txtRef))
        # print(f'[CLOSE RESPONSE: {res}]')
        # print(res["transactionComplete"])
        return HttpResponse("Transaction has been completed successfully, Hurray!!!")
    except RaveExceptions.TransactionVerificationError as e:
        print('Verification error')
        print(e.err)
        print(e.err["errMsg"])
        print(e.err["txRef"])
        return HttpResponse(f"VERIFICATION ERROR: {e.err['errMsg']}")

def verify(request):
    txtRef = request.session.__getitem__('txtref')
    res = request.session.__getitem__('res')
    print(f'[GETTING TEXT REF AS: {txtRef}]')
    try:
        print(f'[VERIFYING TRANSACTION IN FUNC...]')
        res = rave.Card.verify(str(txtRef))
        print(f'[CLOSE RESPONSE: {res}]')
        # print(res["transactionComplete"])
        return HttpResponse("Transaction has been completed successfully, Hurray!!!")
    except RaveExceptions.TransactionVerificationError as e:
        print('Verification error')
        print(e.err)
        print(e.err["errMsg"])
        print(e.err["txRef"])
        return HttpResponse(f"VERIFICATION ERROR: {e.err['errMsg']}")
    



# Good code
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
    transaction_id = request.GET.get('transaction_id')
    
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



