from typing import List
from data.owners import Owner
from data.cages import Cage


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    # owner = Owner.objects().filter(email=email).first()
    owner = Owner.objects(email=email).first()  # only one filter, remove `).filter(`
    return owner


def register_cage(active_account: Owner, name: str, price: float, meters: float,
                  carpeted: bool, has_toys: bool,
                  allow_dangerous: bool) -> Cage:
    cage = Cage()
    cage.name = name
    cage.price = price
    cage.square_meters = meters
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.allow_dangerous_snakes = allow_dangerous

    cage.save()

    account = find_account_by_email(active_account.email)  # get fresh copy
    active_account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:

    query = Cage.objects(id__in=account.cage_ids)  # find all cage ids in account.cage_ids
    cages = list(query)

    return cages
