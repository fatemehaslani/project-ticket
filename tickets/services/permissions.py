from django.contrib.auth.models import User

ROLE_ORDER = {
    "SuperAdmin": 1,
    "Admin": 2,
    "Employee": 3,
}

def get_role_level(user):
    if get_role(user):
        return ROLE_ORDER[get_role(user)]
    return None



def get_role(user):
    return user.groups.first().name if user.groups.exists() else None

def can_assign_ticket(assigner, assignee):
    role_from = get_role(assigner)
    role_to = get_role(assignee)
    if not role_from or not role_to:
        return False

    return ROLE_ORDER[role_from] <= ROLE_ORDER[role_to]


def get_assignees(assigner):
    all_users = User.objects.all()
    filtered_users = []

    for user in all_users:
        if can_assign_ticket(assigner, user):
            filtered_users.append(user)

    return filtered_users