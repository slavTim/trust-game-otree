from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """
Игра в доверие (Trust Game) с перетасовкой ролей и асинхронным режимом
"""

class Constants(BaseConstants):
    name_in_url = 'trust'
    players_per_group = 2
    num_rounds = 5          # МЕНЯЙТЕ ЗДЕСЬ количество раундов
    endowment = c(100)
    multiplication_factor = 3
    instructions_template = 'trust/Instructions.html'


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.group_randomly()
        else:
            players = self.get_players()
            random.shuffle(players)
            groups = [players[i:i+2] for i in range(0, len(players), 2)]
            for group_id, group_players in enumerate(groups, start=1):
                group = self.get_group_by_id(group_id)
                group.set_players(group_players)


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="Сумма, отправленная игроком A",
    )
    sent_back_amount = models.CurrencyField(
        doc="Сумма, возвращенная игроком B",
        min=c(0),
    )

    def set_payoffs(self):
        p1 = self.get_player_by_id(1)
        p2 = self.get_player_by_id(2)
        p1.payoff = Constants.endowment - self.sent_amount + self.sent_back_amount
        p2.payoff = self.sent_amount * Constants.multiplication_factor - self.sent_back_amount


class Player(BasePlayer):
    pass