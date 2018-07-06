from infrastructure.switchlang import switch
import program_hosts as hosts
from program_hosts import success_msg, error_msg
import infrastructure.state as state
import services.data_service as svc


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
    state.reload_account
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
    # TODO: Require an account
    # TODO: Verify they have a snake
    # TODO: Get dates and select snake
    # TODO: Find cages available across date range
    # TODO: Let user select cage to book.

    print(" -------- NOT IMPLEMENTED -------- ")


def view_bookings():
    print(' ****************** Your bookings **************** ')
    # TODO: Require an account
    # TODO: List booking info along with snake info

    print(" -------- NOT IMPLEMENTED -------- ")
