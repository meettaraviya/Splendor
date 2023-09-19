from ui import TerminalIO

import numpy as np

import random

class Player:
    def __init__(self, id=0):
        self.bonuses = np.zeros(5, dtype=int)
        self.gems = np.zeros(5, dtype=int)
        self.prestige = 0
        self.gold = 0
        self.reserve = []
        self.id = id

    def show(self):
        print(f"Bonuses: {TerminalIO.print_piles(self.bonuses)}  " +
              f"Gems: {TerminalIO.print_piles(self.gems, self.gold)}  " +
              f"Total: {TerminalIO.print_piles(self.bonuses + self.gems, self.gold)}")
        print(f"Prestige : {self.prestige}")
        # print(self.reserve)
        print(f"Reserve  : {' '.join(TerminalIO.print_card(card) for card in self.reserve)}", end='\n\n')

    def can_afford(self, card):
        card_cost = card.loc[TerminalIO.GEM_COLORS].to_numpy().astype(int)
        return np.maximum(card_cost - (self.bonuses + self.gems), 0).sum() <= self.gold

    def get_payment(self, card):
        card_cost = card.loc[TerminalIO.GEM_COLORS].to_numpy().astype(int)
        gem_payment = np.maximum(card_cost - self.bonuses, 0)
        gold_payment = np.maximum(gem_payment - self.gems, 0).sum()
        gem_payment = np.minimum(gem_payment, self.gems)
        return gem_payment, gold_payment

    def choose_action(self, game):
        pick_actions, buy_actions, reserve_actions = game.get_actions()
        return random.choice(pick_actions + buy_actions + reserve_actions)


class HumanPlayer(Player):
    def choose_action(self, game):
        pick_actions, buy_actions, reserve_actions = game.get_actions()
        while True:
            print("Pick an action type -")
            valid_choices = []
            if pick_actions:
                print(f"0: Pick gems")
                valid_choices.append(0)
            if buy_actions:
                print(f"1: Buy a card")
                valid_choices.append(1)
            if reserve_actions:
                print(f"2: Reserve a card")
                valid_choices.append(2)
            choice = 3
            first_time = True
            while choice not in valid_choices:
                choice = input("Your choice: " if first_time else "Invalid choice, try again: ").strip()
                try:
                    choice = int(choice)
                except Exception:
                    choice = 3
                first_time = False
            print()
            action_set = [pick_actions, buy_actions, reserve_actions][choice]
            print("Pick an action -")
            valid_choices = list(range(len(action_set))) + ['b']
            for i, action in enumerate(action_set):
                print(f"{i}: {TerminalIO.print_action(action, self.id)}")
            print("b: Pick another action type")

            choice = -1
            first_time = True
            while choice not in valid_choices:
                choice = input("Your choice: " if first_time else "Invalid choice, try again: ").strip()
                try:
                    if choice != 'b':
                        choice = int(choice)
                except Exception:
                    choice = -1
                first_time = False
            print()
            if choice != 'b':
                return action_set[choice]

