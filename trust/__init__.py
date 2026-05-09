from otree.api import *
import random

class Constants(BaseConstants):
    name_in_url = 'trust'
    players_per_group = 2
    num_rounds = 5
    endowment = 100
    multiplication_factor = 3
    
    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    sent_amount = models.CurrencyField(min=0, max=Constants.endowment)
    sent_back_amount = models.CurrencyField(min=0)

    def set_payoffs(self):
        sender = self.get_player_by_role(Constants.SENDER_ROLE)
        receiver = self.get_player_by_role(Constants.RECEIVER_ROLE)
        
        sender.payoff = Constants.endowment - self.sent_amount + self.sent_back_amount
        receiver.payoff = self.sent_amount * Constants.multiplication_factor - self.sent_back_amount


class Player(BasePlayer):
    pass

def creating_session(subsession: Subsession):
    subsession.group_randomly()
    
    for group in subsession.get_groups():
        players = group.get_players()
        if random.random() < 0.7:
            group.set_players([players[1], players[0]])


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Send(Page):
    form_model = Group
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.SENDER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'round_number': player.round_number,
            'num_rounds': Constants.num_rounds,
            'endowment': Constants.endowment,
        }


class SendBackWaitPage(WaitPage):
    wait_for_all_groups = False


class SendBack(Page):
    form_model = Group
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.RECEIVER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        sent_amount = group.field_maybe_none('sent_amount') or 0
        return {
            'tripled_amount': sent_amount * Constants.multiplication_factor,
            'sent_amount': sent_amount,
            'round_number': player.round_number,
            'num_rounds': Constants.num_rounds,
        }
    @staticmethod
    def error_message(player: Player, values):
        sent_amount = player.group.field_maybe_none('sent_amount') or 0
        max_return = sent_amount * Constants.multiplication_factor
        
        if values['sent_back_amount'] > max_return:
            return f'Вы можете вернуть не более {max_return} .'
        return None


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        sent_amount = group.field_maybe_none('sent_amount') or 0
        sent_back_amount = group.field_maybe_none('sent_back_amount') or 0
        
        return {
            'current_round_payoff': player.payoff or 0,
            'total_payoff': player.participant.payoff or 0,
            'round_number': player.round_number,
            'num_rounds': Constants.num_rounds,
            'tripled_amount': sent_amount * Constants.multiplication_factor,
            'sent_amount': sent_amount,
            'sent_back_amount': sent_back_amount,
            'is_sender': player.role == Constants.SENDER_ROLE,
        }


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'total_payoff': player.participant.payoff or 0,
            'num_rounds': Constants.num_rounds,
        }


page_sequence = [
    Introduction,
    Send,
    SendBackWaitPage,
    SendBack,
    ResultsWaitPage,
    Results,
    FinalResults,
]
