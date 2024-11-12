from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from .models import Product

# Create your views here.

def product_purchase(request, product_id):

   
    product = Product.objects.get(id=product_id)
    paypal_form = PayPalPaymentsForm(initial={
        'business': "testdjangopaypal@gmail.com",
        'amount': product.price,
        'item_name': product.name,
        'invoice': product_id ,
        'currency_code': 'USD',
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('successful')),
        'cancel_return': request.build_absolute_uri(reverse('cancelled')),
    })
    context = {
        'product': product,
        'paypal_form': paypal_form
    }

    return render(request, "purchase.html", context)

def successful(request):
    return render(request, 'successful.html')

def cancelled(request):
    return render(request, 'cancelled.html')

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):

    ipn_obj = sender

    if ipn_obj.payment_status == "Completed":
        print("Payment successful, reduce product quantity")
        product_id = ipn_obj.invoice
        product = Product.objects.get(id=product_id)
        product.quantity -= 1
        product.save()