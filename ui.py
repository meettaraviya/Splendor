from termcolor import colored
import numpy as np
import pandas as pd


class TerminalIO:
    WHITE = 'white'
    BLUE = 'blue'
    GREEN = 'green'
    RED = 'red'
    CYAN = 'cyan'
    GOLD = 'yellow'
    GEM_COLORS = [WHITE, BLUE, GREEN, RED, CYAN]

    @staticmethod
    def print_pile(size, color, bg_color='magenta'):
        return colored(size, color, f'on_{bg_color}',
                       attrs=['bold', 'dark'] if size == 0 else ['bold'])

    @staticmethod
    def print_action(action, player_id):
        out = ''
        if isinstance(action, type(np.array([0]))):
            out += f"Player {player_id + 1} takes {TerminalIO.print_piles(np.maximum(action, 0))} " + \
                   f"and returns {TerminalIO.print_piles(np.maximum(-action, 0))}"
        elif isinstance(action, tuple):
            card, gold_available, return_action = action
            if isinstance(card, int):
                card = f"top card of level {card}"
            else:
                card = TerminalIO.print_card(card)
            out += f"Player {player_id + 1} reserves {card}, takes {TerminalIO.print_pile(gold_available, TerminalIO.GOLD)} " + \
                   f"and returns {TerminalIO.print_piles(-return_action)}"
        elif isinstance(action, pd.Series):
            out += f"Player {player_id + 1} buys {TerminalIO.print_card(action)}"
        return out

    @staticmethod
    def print_piles(gems, gold=None, bg_color='magenta'):
        out = ''
        for size, color in zip(gems, TerminalIO.GEM_COLORS):
            out += TerminalIO.print_pile(size, color, bg_color)
        if gold is not None:
            out += TerminalIO.print_pile(gold, 'yellow', bg_color)
        return out

    @staticmethod
    def print_card(card):
        out = ''
        for size, color in zip(card.loc[TerminalIO.GEM_COLORS], TerminalIO.GEM_COLORS):
            out += TerminalIO.print_pile(size, color, card.color)
        return out + f"|{card.prestige}"

    @staticmethod
    def print_noble(noble):
        out = ''
        for size, color in zip(noble.loc[TerminalIO.GEM_COLORS], TerminalIO.GEM_COLORS):
            out += TerminalIO.print_pile(size, color, 'magenta')
        return out
