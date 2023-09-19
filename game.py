from player import Player
from ui import TerminalIO

import numpy as np
import pandas as pd
from termcolor import colored

from itertools import product
from collections import defaultdict


class Game:
    def __init__(self, players=None):
        if players is None:
            self.players = [Player(id=i) for i in range(2)]
        else:
            self.players = players

        gem_pile_size = {2: 4, 3: 5, 4: 7}.get(len(self.players))
        self.gem_piles = np.ones(5, dtype=int) * gem_pile_size
        self.gold_pile = 5

        cards = pd.read_csv('cards_list.csv', dtype=str).fillna(0)
        for col in cards.columns:
            if col != 'color':
                cards[col] = pd.to_numeric(cards[col])

        self.shop_piles = [
            cards[cards.level == 1].sample(frac=1),
            cards[cards.level == 2].sample(frac=1),
            cards[cards.level == 3].sample(frac=1),
        ]

        nobles = pd.read_csv('nobles_list.csv', dtype=str).fillna(0)
        for col in nobles.columns:
            nobles[col] = pd.to_numeric(nobles[col])

        self.nobles = nobles.sample(len(self.players) + 1)
        self.turn_id = 0

        self.all_configs = defaultdict(list)
        for config in product(list(range(gem_pile_size + 1)), repeat=5):
            config = np.array(config, dtype=int)
            if config.max() <= gem_pile_size and config.sum() <= 10:
                self.all_configs[config.sum()].append(np.array(config))


    def get_actions(self):
        pick_actions = []
        player_gems = self.players[self.turn_id].gems
        player_gold = self.players[self.turn_id].gold
        player_gem_count = player_gems.sum()
        take_count = min((self.gem_piles > 0).sum(), 3)
        for config in self.all_configs[min(player_gem_count + take_count, 10 - player_gold)]:
            diff = config - player_gems
            if (diff <= self.gem_piles).all() and diff.max() == 1 and (diff > 0).sum() <= take_count:
                pick_actions.append(diff)

        for config in self.all_configs[min(player_gem_count + 2, 10 - player_gold)]:
            diff = config - player_gems
            if ((diff > 0) <= (self.gem_piles >= 4)).all() and diff.max() == 2 and (diff > 0).sum() == 1:
                pick_actions.append(diff)

        buy_actions = []
        for level in range(3):
            for _, card in self.shop_piles[level][:4].iterrows():
                if self.players[self.turn_id].can_afford(card):
                    buy_actions.append(card)

        for card in self.players[self.turn_id].reserve:
            if self.players[self.turn_id].can_afford(card):
                buy_actions.append(card)

        reserve_actions = []
        if len(self.players[self.turn_id].reserve) < 3:
            gold_available = min(self.gold_pile, 1)
            return_actions = []
            if gold_available == 1 and self.players[self.turn_id].gems.sum() == 10:
                for i in range(5):
                    if self.players[self.turn_id].gems[i] > 0:
                        return_action = np.zeros(5, dtype=int)
                        return_action[i] = 1
                        return_actions.append(return_action)
            else:
                return_actions.append(np.zeros(5, dtype=int))

            for level in range(3):
                if len(self.shop_piles[level]) > 0:
                    for return_action in return_actions:
                        reserve_actions.append((level + 1, gold_available, return_action))
                for _, card in self.shop_piles[level].iloc[:4].iterrows():
                    for return_action in return_actions:
                        reserve_actions.append((card, gold_available, return_action))

        return pick_actions, buy_actions, reserve_actions

    def remove_card(self, card):
        l = card.level - 1
        self.shop_piles[l] = self.shop_piles[l][(self.shop_piles[l] != card).any(axis=1)]

    def take_action(self, action):
        if isinstance(action, type(np.array([0]))):
            self.gem_piles -= action
            self.players[self.turn_id].gems += action
        elif isinstance(action, tuple):
            card, gold_available, return_action = action
            if isinstance(card, int):
                card = self.shop_piles[card - 1].iloc[4]
            self.gem_piles += return_action
            self.players[self.turn_id].gems -= return_action
            self.players[self.turn_id].gold += gold_available
            self.gold_pile -= gold_available
            self.players[self.turn_id].reserve.append(card)
            self.remove_card(card)
        elif isinstance(action, pd.Series):
            gem_payment, gold_payment = self.players[self.turn_id].get_payment(action)
            self.gem_piles += gem_payment
            self.players[self.turn_id].gems -= gem_payment
            self.players[self.turn_id].gold -= gold_payment
            self.gold_pile += gold_payment
            self.players[self.turn_id].prestige += action.prestige
            i = TerminalIO.GEM_COLORS.index(action.color)
            self.players[self.turn_id].bonuses[i] += 1
            eligible_nobles = (self.nobles[TerminalIO.GEM_COLORS] <= self.players[self.turn_id].bonuses).all(axis=1)
            if eligible_nobles.sum() == 1:
                self.players[self.turn_id].prestige += self.nobles[eligible_nobles].iloc[0].prestige
                self.nobles = self.nobles[~eligible_nobles]
            elif eligible_nobles.sum() > 1:
                min_deficiency = 10
                best_ni = None
                for ni, noble in self.nobles[eligible_nobles].iterrows():

                    for i in range(len(self.players)):
                        if i != self.turn_id:
                            deficiency = np.maximum(self.nobles[TerminalIO.GEM_COLORS].to_numpy().astype(int) - self.players[i].bonuses, 0).sum()
                            if deficiency < min_deficiency:
                                best_ni = ni
                                min_deficiency = deficiency

                self.players[self.turn_id].prestige += self.nobles.loc[best_ni].prestige
                self.nobles = self.nobles.drop(best_ni)

            try:
                j = [(card == action).all() for card in self.players[self.turn_id].reserve].index(True)
                del self.players[self.turn_id].reserve[j]
            except Exception:
                self.remove_card(action)

        self.turn_id = (self.turn_id + 1) % len(self.players)

        if self.turn_id == 0 and any(p.prestige >= 15 for p in self.players):
            return False
        else:
            return True



    def show(self):
        for i, player in enumerate(self.players):
            print(colored(f"Player {i + 1}", None, "on_magenta" if self.turn_id == i else None) + " -")
            player.show()

        print(f'Piles - {TerminalIO.print_piles(self.gem_piles, self.gold_pile)}\n')
        print('Shop -')
        print(f'Level 1 : {" ".join(TerminalIO.print_card(card) for _, card in self.shop_piles[0].iloc[:4].iterrows())}')
        print(f'Level 2 : {" ".join(TerminalIO.print_card(card) for _, card in self.shop_piles[1].iloc[:4].iterrows())}')
        print(f'Level 3 : {" ".join(TerminalIO.print_card(card) for _, card in self.shop_piles[2].iloc[:4].iterrows())}')
        print()
        # print(type(self.nobles))
        print(f"Nobles - {' '.join(TerminalIO.print_noble(noble) for _, noble in self.nobles.iterrows())}")
