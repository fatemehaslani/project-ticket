from datetime import timedelta

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.context_processors import request
from django.urls import reverse
from django.utils import timezone
from unicodedata import category
from django.db.models import Count

from tickets.forms import TicketForm
from tickets.models import *
from tickets.validators import validate


def dashboard(request):
    week_ago = timezone.now() - timedelta(days=7)
    weekly_tickets = Ticket.objects.filter(created_at__gte=week_ago).count()
    # آخرین تیکت‌ها
    recent_tickets = Ticket.objects.select_related('category').order_by('-created_at')[:5]

    context = {
        'total_tickets': Ticket.objects.all().count(),
        'low_tickets': Ticket.objects.with_priority('low').count(),
        'middle_tickets': Ticket.objects.with_priority('middle').count(),
        'high_tickets': Ticket.objects.with_priority('high').count(),
        'closed_tickets': Ticket.objects.is_close().count(),
        'open_tickets': Ticket.objects.is_open().count(),
        #'assigned_by_auth_user': Ticket.objects.assigned_by(request.user).count(),

        'weekly_tickets': weekly_tickets,
        'recent_tickets': recent_tickets,

        #'category_stats': Ticket.objects.values(
         #   'category__name'  # اگر رابطه ForeignKey به مدل Category دارید
        #).annotate(
         #   count=Count('id')
        #).order_by('-count')
        'category_stats': Ticket.objects.values(
            'category__id',
            'category__name',
            'category__slug'
        ).annotate(
            count=Count('id')
        ).order_by('-count'),

        'categories_count': Category.objects.count(),
    }

    return render(request, 'dashboard.html', context)


# Create your views here.
def index(request):
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    priority = request.GET.get("priority", "").strip()
    operator = request.GET.get("operator", "OR")
    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("dir", "desc")
    with_close = request.GET.get("with_close", None)

    is_user_search = False
    new_log = None

    if search_query or category_id or priority:
        is_user_search = True
        new_log = SearchLog()

    #if with_close == "on":
      #  tickets = Ticket.objects
    #else:
        #tickets = Ticket.objects.is_open()

    tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()

    tickets = tickets.prefetch_related('tags')


    #Apply filters
    if search_query:
        if new_log:
            new_log.search_subject = search_query
        tickets = tickets.filter(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tracking_code__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    #if search_query:
     #   search_terms = search_query.split()
      #  query = Q()

       # for term in search_terms:
        #    term_condition = (
         #           Q(subject__icontains=term) |
          #          Q(description__icontains=term) |
           #         Q(tracking_code__icontains=term) |
            #        Q(category__name__icontains=term)
            #)

            # استفاده از متد add برای ترکیب شرط‌ها
            #if operator == "AND":
             #   query.add(term_condition, Q.AND)
            #else:
             #   query.add(term_condition, Q.OR)

        #tickets = tickets.filter(query)

    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            if new_log:
                new_log.search_category = category.name
            request.session['search_category'] = category_id
            tickets = tickets.filter(category_id=category_id)
        except Category.DoesNotExist:
            pass
    elif request.session.get("search_category"):
        session_category = request.session.get("search_category")
        if session_category:
            tickets = tickets.filter(category_id=session_category)

    if priority:
        if new_log:
            new_log.search_priority = priority
        tickets = tickets.with_priority(priority)

    #request.session["page_route_name"] = "tickets"

    #if 'mode' not in request.session:
     #   request.session['mode'] = 'dark'
      #  mode = request.session['mode']
    #else:
     #   mode = request.session['mode']

    categories = Category.objects.active()
    priorities = Ticket._meta.get_field("priority").choices    #چون priority مدل نداره باید اینجوری بنویسیم مدل Ticket فیلد priority پیدا میکنیم

    if sort:
        if direction == "desc":
            sort_field = f"-{sort}"
        else:
            sort_field = sort
        tickets = tickets.order_by(sort_field)

    columns = [
        ("subject", "Subject"),
        ("tracking_code", "Tracking Code"),
        ("category__name", "Category"),
        ("tags", "Tags"),
        ("created_at", "Created At"),
        ("priority", "Priority"),
        ("created_by", "Created By"),
        ("max_reply_date", "Max Reply date"),
        ("actions", "Actions"),
    ]

    selected_category = category_id if category_id else request.session.get("search_category", "")


    context = {'tickets': tickets,
               'search_query': search_query,
               'selected_category': selected_category,
               'selected_priority': priority if priority not in ["", "None"] else "",
               'categories': categories,
               'priorities': priorities,
               'with_close': with_close,
               'sort_by': sort,
               "direction": direction,
               "columns": columns,
               }

    if is_user_search and new_log:
        if request.user.is_authenticated:
            new_log.user = request.user
        new_log.save()

    return render(request, template_name='index.html', context=context)

def ticket_create(request):
    #request.session["page_route_name"] = "tickets-create"

    #if 'mode' not in request.session:
     #   request.session['mode'] = 'dark'
      #  mode = request.session['mode']
    #else:
     #   mode = request.session['mode']


    if request.method == "POST":
        form = TicketForm(request.POST)  # کاربر فرم پر کرده همش میشنه داخل field


        rules = {
            "category": ["required"],
            "priority": ["required", "in:Low,Medium,High"],
            "subject": ["required", "min:5", "max:200"],
            "age": ["required", "between:12,100"],
            "email": ["required", "email"],
            "description": ["required"],
            "max_reply_data": ["required", "future_date"],
        }

        errors = validate(request.POST, rules)

        if errors:
            for field, error in errors.items():
                form.add_error(field, error)
        elif form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by_id = 1
            ticket.save()
            form.save_m2m()
            messages.success(request, "Your ticket has been created successfully!")
            return redirect("tickets")

        #if form.is_valid():
            #new_ticket = form.save(commit=False)
            #new_ticket.created_by_id = 1
           # new_ticket.save()
            #messages.success(request, "Your ticket has been created successfully!")
           # return redirect("tickets")
    else:
        form = TicketForm()
    return render(request, "create_ticket.html", {"form": form})

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


#def color_mode(request):
 #   if 'mode' in request.session:
  #      if request.session.get('mode') == 'dark':
   #         request.session['mode'] = 'light'
    #    else:
     #       request.session['mode'] = 'dark'
    #else:
     #   request.session['mode'] = 'dark'

    #page = request.session.get('page_route_name')
   # return HttpResponseRedirect(reverse(page))

def tickets_clear(request):
    request.session['search_category'] = None
    return redirect("tickets")