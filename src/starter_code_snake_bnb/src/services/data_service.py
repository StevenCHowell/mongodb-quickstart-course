from typing import List
from data.owners import Owner
from data.cages import Cage
from data.snakes import Snake
from data.bookings import Booking
import datetime

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


def register_cage(account: Owner, name: str, price: float, meters: float,
                  carpeted: bool, has_toys: bool,
                  allow_dangerous: bool) -> Cage:
    cage = Cage()
    cage.name = name
    cage.price = price
    cage.square_meters = meters
    cage.carpeted = carpeted
    cage.has_toys = has_toys
    cage.allow_dangerous_snakes = allow_dangerous
    cage.save()

    account = find_account_by_email(account.email)  # get fresh copy
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:

    query = Cage.objects(id__in=account.cage_ids)  # find all cage ids in account.cage_ids
    cages = list(query)

    return cages

def add_available_date(selected_cage: Cage, start_date: datetime.datetime,
                       days: int) -> Cage:

    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=selected_cage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage

def add_snake(account: Owner, name: str, species: float, length: float,
              venomous: bool) -> Snake:
    snake = Snake()
    snake.name = name
    snake.species = species
    snake.length = length
    snake.venomous = venomous
    snake.save()

    account = find_account_by_email(account.email)  # get fresh copy
    account.snake_ids.append(snake.id)
    account.save()

    return snake


def find_snakes_for_user(account: Owner) -> List[Snake]:
    account = find_account_by_email(account.email)  # get fresh copy
    query = Snake.objects(id__in=account.snake_ids).all()  # find all snake ids in account.snake_ids
    snakes = list(query)

    return snakes


def find_available_cages(check_in_date: datetime.datetime,
                        check_out_date: datetime.datetime, snake: Snake) -> List[Cage]:
    # set the minimum cage size as .25 m x length of the snake
    min_size = snake.length * 0.25

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=check_in_date) \
        .filter(bookings__check_out_date__gte=check_out_date)

    if snake.venomous:
        query = query.filter(allow_dangerous_snakes=True)

    cages = query.order_by('price', '-square_meters')

    final_cages = []

    print(f'Looking for availability in {len(cages)} cages')
    for c in cages:
        for b in c.bookings:
            after_open = b.check_in_date <= check_in_date
            before_close = b.check_out_date >= check_out_date
            available = b.guest_snake_id is None
            if after_open and before_close and available:
                final_cages.append(c)

            # # code used for debugging
            # if b.check_in_date <= check_in_date:
            #     if b.check_out_date >= check_out_date:
            #         if b.guest_snake_id is None:
            #             final_cages.append(c)
            #         else:
            #             print(f"{c.name} is booked by {b.guest_snake_id} during your dates")
            #     else:
            #         print(f"{check_out_date} is after {c.name}'s availability of {b.check_out_date}")
            # else:
            #     print(f"{check_in_date} is before {c.name}'s availability of {b.check_in_date}")

    return final_cages


def book_cage(account: Owner, cage: Cage, snake: Snake,
              check_in_date: datetime.datetime,
              check_out_date: datetime.datetime) -> Cage:

    # find the booking
    for b in cage.bookings:
        if b.check_in_date <= check_in_date and \
           b.check_out_date >= check_out_date and \
           b.guest_snake_id is None:
            booking = b
            break

    # create separate bookings for before/after this booking
    if booking.check_in_date < check_in_date:
        days = (check_in_date - booking.check_in_date).days
        add_available_date(cage, booking.check_in_date, days)

    if booking.check_out_date > check_out_date:
        days = (booking.check_out_date - check_out_date).days
        add_available_date(cage, check_out_date, days)

    # update this booking with the reservation details
    booking.guest_owner_id = account.id
    booking.guest_snake_id = snake.id
    booking.booked_date = datetime.datetime.now()
    booking.check_in_date = check_in_date
    booking.check_out_date = check_out_date

    cage.save()

    return


def find_bookings_for_user(account: Owner) -> List[Booking]:
    account = find_account_by_email(account.email)  # get fresh copy
    booked_cages = Cage.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_cage_to_booking(booking, cage):
        booking.cage = cage
        return booking

    bookings = [
        map_cage_to_booking(booking, cage)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
