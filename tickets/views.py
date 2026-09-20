from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.template.context_processors import request
from django.urls import reverse
from django.utils import timezone
from unicodedata import category
from django.db.models import Count

from tickets.forms import TicketForm, RegisterForm
from tickets.models import *
from tickets.validators import validate
from django.core.paginator import Paginator
from .services.permissions import *


@login_required
def dashboard(request):
    global high_priority_unclosed
    user_id = request.user.id
    user_role = UserRole.objects.filter(user=user_id).first()
    role_title = Role.objects.filter(id=user_role.role_id).first().title
    request.session['role'] = role_title

    week_ago = timezone.now() - timedelta(days=7)
    weekly_tickets = Ticket.objects.filter(created_at__gte=week_ago).count()
    # آخرین تیکت‌ها
    recent_tickets = Ticket.objects.select_related('category').order_by('-created_at')[:5]

    # آمار بر اساس وضعیت (با استفاده از closed_at)
    total_tickets = Ticket.objects.all().count()
    closed_tickets = Ticket.objects.filter(closed_at__isnull=False).count()  # تیکت‌های بسته
    open_tickets = Ticket.objects.filter(closed_at__isnull=True).count()  # تیکت‌های باز

    category_stats = Ticket.objects.values(
        'category__id',
        'category__name',
        #'category__color',  # اگر فیلد رنگ دارید
        'category__slug'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    # محاسبه درصد برای هر دسته
    for stat in category_stats:
        if total_tickets > 0:
            stat['percentage'] = (stat['count'] / total_tickets) * 100
        else:
            stat['percentage'] = 0

        # محاسبه میانگین تیکت در هر دسته
    categories_count = Category.objects.count()
    if categories_count > 0:
        avg_tickets_per_category = total_tickets / categories_count
    else:
        avg_tickets_per_category = 0

    if category_stats:
        max_category = category_stats[0]['category__name'] or 'بدون دسته'
    else:
        max_category = 'بدون تیکت'

        # نرخ بسته شدن
    if total_tickets > 0:
        closure_rate = (closed_tickets / total_tickets) * 100
    else:
        closure_rate = 0

        # تیکت‌های با اولویت بالا که هنوز بسته نشده‌اند
    high_priority_unclosed = Ticket.objects.filter(
        priority='high',
        closed_at__isnull=True  # بسته نشده‌اند
    ).count()

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
        #    'category__id',
        #    'category__name',
        #    'category__slug'
        #).annotate(
        #    count=Count('id')
        #).order_by('-count'),
        'categories_count': Category.objects.count(),
        'avg_tickets_per_category': avg_tickets_per_category,
        'max_category': max_category,
        'closure_rate': closure_rate,
        'high_priority_unclosed': high_priority_unclosed,
        'now': timezone.now(),
    }

    return render(request, 'dashboard.html', context)


# Create your views here.
@login_required(login_url='login')
def index(request):
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    priority = request.GET.get("priority", "").strip()
    operator = request.GET.get("operator", "OR")
    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("dir", "desc")
    with_close = request.GET.get("with_close", None)
    ticket = Ticket.objects.all().order_by('-id')

    paginator = Paginator(ticket, 5)  # 10 آیتم در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    view_mode = request.GET.get("view", request.COOKIES.get('ticket_view_mode', 'table'))

    is_user_search = False
    new_log = None

    if search_query or category_id or priority:
        is_user_search = True
        new_log = SearchLog()

    tickets = Ticket.objects

    user_role = get_role(request.user)
    if user_role in ["Admin", "Emplod"]:
        tickets = Ticket.objects.filter(created_by=request.user)

    if not with_close == "on":
        tickets = tickets.is_open()

    #tickets = Ticket.objects if with_close == "on" else Ticket.objects.is_open()

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
    priorities = Ticket._meta.get_field(
        "priority").choices  #چون priority مدل نداره باید اینجوری بنویسیم مدل Ticket فیلد priority پیدا میکنیم

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
               "view_mode": view_mode,
               'page_obj': page_obj,
               }

    if is_user_search and new_log:
        if request.user.is_authenticated:
            new_log.user = request.user
        new_log.save()

    response = render(request, template_name='index.html', context=context)

    # ذخیره view mode در کوکی
    if 'view' in request.GET:
        response.set_cookie('ticket_view_mode', view_mode, max_age=30 * 24 * 60 * 60)

    return response


def ticket_create(request):
    #request.session["page_route_name"] = "tickets-create"

    #if 'mode' not in request.session:
    #   request.session['mode'] = 'dark'
    #  mode = request.session['mode']
    #else:
    #   mode = request.session['mode']

    #user_role = request.session.get("role")
    #if user_role == "Employee":
    #    raise PermissionDenied

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, request=request)  # کاربر فرم پر کرده همش میشنه داخل field

        rules = {
            "category": ["required"],
            "priority": ["required", "in:low,middle,high"],
            "subject": ["required", "min:5", "max:200"],
            #"age": ["required", "between:12,100"],
            #"email": ["required", "email"],
            "description": ["required"],
            "max_reply_date": ["required", "future_date"],
        }

        errors = validate(request.POST, rules)

        if errors:
            for field, error in errors.items():
                form.add_error(field, error)
        elif form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by_id = request.user.id
            ticket.save()

            # Handle Assignment
            selected_users = form.cleaned_data["users"]

            assignments = []
            for user in selected_users:
                assignments.append(
                    Assignment(
                        assigned_ticket=ticket,
                        assignee=user,
                        status="new",
                    )
                )

            Assignment.objects.bulk_create(assignments)

            files = request.FILES.getlist('attachments')
            for f in files:
                Attachment.objects.create(ticket=ticket, file=f)

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
        form = TicketForm(request=request)
    return render(request, "create_ticket.html", {"form": form})


def ticket_edit(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket, request=request)
        if form.is_valid():
            form.save()

            #Handle Assignment
            selected_users = set(form.cleaned_data["users"])
            current_users = set(
                ticket.assignments.values_list("assignee_id", flat=True)
            )

            #Remove unassigned users
            Assignment.objects.filter(
                assigned_ticket=ticket,
                assignee_id__in=(current_users - set(u.id for u in selected_users))
            ).delete()

            #Add new assignments
            new_assignments = [
                Assignment(assigned_ticket=ticket, assignee=user)
                for user in selected_users
                if user.id not in current_users
            ]
            Assignment.objects.bulk_create(new_assignments)

            files = request.FILES.getlist('attachments')
            for f in files:
                Attachment.objects.create(ticket=ticket, file=f)

            messages.info(request, f"Ticket #{id} edited successfully.")
            return redirect("tickets-detail", id=ticket.id)
    else:
        form = TicketForm(instance=ticket)

    return render(request, "create_ticket.html", {
        "form": form,
        "ticket": ticket,
        "attachments": ticket.attachments.all(),
    })


def ticket_delete(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    ticket.delete()

    messages.success(request, 'Ticket Deleted successfully!')

    return redirect('tickets')  # میره یه path دیگه


@login_required
def ticket_detail(request, id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("category", "created_by").prefetch_related("tags"),
        pk=id
    )
    attachments = ticket.attachments.all()

    if not ActivityLog.objects.filter(ticket=ticket).filter(user=request.user).exists():
        ActivityLog.objects.create(
            ticket=ticket,
            user=request.user,
            action="view",
            ip_address=request.META.get("REM"),
        )

    return render(request, "ticket-detail.html", {"ticket": ticket, "attachments": attachments})


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


def attachment_delete(request, id):
    attachment = get_object_or_404(Attachment, id=id)
    ticket = attachment.ticket

    attachment.file.delete(save=False)
    attachment.delete()

    messages.success(request, "Attachment removed successfully.")
    return redirect("tickets-update", id=ticket.id)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account was created successfuly. Please log in.")
            return redirect('tickets')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def assignee_ticket_list(request):
    assignments = (
        Assignment.objects
        .for_user(request.user)
        .select_related("assigned_ticket", "assigned_ticket__category")
        .order_by("-created_at")
    )

    paginator = Paginator(assignments, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "assignee/ticket_list.html", {
        "page_obj": page_obj,
    })


@login_required
def assignee_ticket_detail(request, pk):
    assignment = get_object_or_404(
        Assignment,
        pk=pk,
        assignee=request.user
    )

    if request.method == "POST":
        assignment.status = request.POST.get("status")
        assignment.description = request.POST.get("description")
        assignment.save()
        return redirect('assignee_list')

    return render(request, "assignee/tickets_detail.html", {
        "status_choices": STATUS_CHOICES,
        "assignment": assignment,
        "ticket": assignment.assigned_ticket,
    })
