from django.db import transaction
from django.shortcuts import redirect, render

from .forms import BookingForm
from .telegram_notify import notify_in_background


def index(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            transaction.on_commit(lambda: notify_in_background(booking.pk))
            return redirect('success')
    else:
        form = BookingForm()
    return render(request, 'salon/index.html', {
        'form': form,
    })


def success(request):
    return render(request, 'salon/success.html')
