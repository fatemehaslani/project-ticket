
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from tickets.forms import TicketForm
from tickets.models import *


# Create your views here.
def index(request):
    tickets = Ticket.objects.prefetch_related('tags').all()
    request.session["page_route_name"] = "tickets"

    if 'mode' not in request.session:
        request.session['mode'] = 'dark'
        mode = request.session['mode']
    else:
        mode = request.session['mode']

    return render(request, template_name='index.html', context={'tickets': tickets, 'mode': mode})

def ticket_create(request):
    request.session["page_route_name"] = "tickets-create"

    if 'mode' not in request.session:
        request.session['mode'] = 'dark'
        mode = request.session['mode']
    else:
        mode = request.session['mode']


    if request.method == "POST":
        form = TicketForm(request.POST)  # کاربر فرم پر کرده همش میشنه داخل field
        if form.is_valid():
            new_ticket = form.save(commit=False)
            new_ticket.created_by_id = 1
            new_ticket.save()
            messages.success(request, "Your ticket has been created successfully!")
            return redirect("tickets")
    else:
        form = TicketForm()
    return render(request, "create_ticket.html", {"form": form, 'mode': mode})

def ticket_edit(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.info(request, f"Ticket #{id} edited successfully.")
            return redirect("tickets-detail", id=ticket.id)
    else:
        form = TicketForm(instance=ticket)

    return render(request, "create_ticket.html", {
        "form": form,
        "ticket": ticket,
    })

def ticket_delete(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    ticket.delete()

    messages.success(request, 'Ticket Deleted successfully!')

    return redirect('tickets')  # میره یه path دیگه

def ticket_detail(request, id):
    return HttpResponse("ok")


def color_mode(request):
    if 'mode' in request.session:
        if request.session.get('mode') == 'dark':
            request.session['mode'] = 'light'
        else:
            request.session['mode'] = 'dark'
    else:
        request.session['mode'] = 'dark'

    page = request.session.get('page_route_name')
    return HttpResponseRedirect(reverse(page))

