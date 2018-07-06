from infrastructure.switchlang import switch
import program_hosts as hosts
from program_hosts import success_msg, error_msg
import infrastructure.state as state
import services.data_service as svc
from dateutil import parser

def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', list_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')

    if not state.active_account:
        error_msg('You must login first to register a cage.')
        return

    name = input('What is the name of your snake? ')
    if not name:
        error_msg('Cancelled')
        return

    length = float(input('How long is your snake (in meters)? '))
    species = input('Species? ')
    venomous = input('Is your snake venomous [y, n]? ').lower().startswith('y')

    snake = svc.add_snake(state.active_account, name, species, length, venomous)
    state.reload_account()
    success_msg(f'Registered {snake.name} with id {snake.id}.')

def list_snakes(suppress_header=False):
    if not suppress_header:
        print(' ****************** Your snakes **************** ')

    if not state.active_account:
        error_msg('You must login first to list your snake/s.')
        return

    snakes = svc.find_snakes_for_user(state.active_account)
    print(f'You have {len(snakes)} snakes.')
    for idx, s in enumerate(snakes):
        print(
            f' {idx+1}. {s.name} is a {s.species} that is {s.length}m long '
            f'and is {"" if s.venomous else "not "}venomous.'
        )


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    # Require an account
    if not state.active_account:
        error_msg('You must [l]ogin first to book a cage.')
        return

    # Verify they have a snake
    snakes = svc.find_snakes_for_user(state.active_account)
    if len(snakes) < 1:
        error_msg('You must first [a]dd a snake before booking a cage.')
        return

    # Select snake
    list_snakes(suppress_header=True)
    snake_number = input('Enter snake number: ').strip()
    if not snake_number:
        error_msg('Cancelled')
        return
    snake_number = int(snake_number)

    snakes = svc.find_snakes_for_user(state.active_account)
    selected_snake = snakes[snake_number - 1]
    success_msg(f'Booking a cage for {selected_snake.name}.')

    # Get dates
    check_in_date = parser.parse(input('Check-in date [yyyy-mm-dd]: '))
    check_out_date = parser.parse(input('Check-out date [yyyy-mm-dd]: '))

    if check_in_date >= check_out_date:
        error_msg('Check in must be before check out.')
        return

    # Find cages available across date range
    cages = svc.find_available_cages(check_in_date, check_out_date, selected_snake)

    # Let user select cage to book
    print(f'There are {len(cages)} cages available for those dates.')
    for idx, c in enumerate(cages):
        print(f' {idx+1}. ${c.price} - {c.name},'
              f' {c.square_meters} square meters,'
              f' it does{"" if c.carpeted else " not"} have carpet,'
              f' it does{"" if c.has_toys else " not"} have toys.')
    if not cages:
        error_msg('Sorry, no cages are available for that date.')
        return

    cage_number = int(input('Which cage would you like to book? '))
    selected_cage = cages[cage_number - 1]
    svc.book_cage(state.active_account, selected_cage, selected_snake, check_in_date, check_out_date)
    success_msg(f'Booked {selected_cage.name} from {check_in_date} to {check_out_date}')


def view_bookings():
    print(' ****************** Your bookings **************** ')
    # Require an account
    if not state.active_account:
        error_msg('You must [l]ogin first to book a cage.')
        return

    # Get the bookings
    bookings = svc.find_bookings_for_user(state.active_account)

    # List booking info along with snake info
    snakes = {s.id: s for s in svc.find_snakes_for_user(state.active_account)}
    for idx, b in enumerate(bookings):
        print(
            f' {idx+1}. {snakes.get(b.guest_snake_id).name} is booked at '
            f'{b.cage.name} starting on {b.check_in_date.date()} for '
            f'{(b.check_out_date - b.check_in_date).days} days.'
        )
