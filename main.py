from ui import TerminalIO
from game import Game
from player import Player, HumanPlayer


if __name__ == '__main__':

    game = Game(players=[HumanPlayer(id=0), Player(id=1)])

    while True:
        game.show()
        print()

        action = game.players[game.turn_id].choose_action(game)
        print(TerminalIO.print_action(action, game.turn_id))
        print('\n')
        outcome = game.take_action(action)
        if not outcome:
            break

    game.show()