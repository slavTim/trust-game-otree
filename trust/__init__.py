from otree.api import *
from otree.models import Participant
import random

class Constants(BaseConstants):
    name_in_url = 'trust'
    players_per_group = 2
    num_rounds = 5
    endowment = 100
    multiplication_factor = 3
    
    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    BOT_SENDER_TRUST_RATE = 0.45
    BOT_RECEIVER_BASE_RATE = 0.35
    BOT_MIN_RETURN = 5
    BOT_MAX_RETURN_RATE = 0.6
    BOT_LOW_SEND_THRESHOLD = 0.3 * endowment
    BOT_HIGH_SEND_THRESHOLD = 0.7 * endowment
    BOT_GENEROUS_BONUS = 0.15
    BOT_CONSERVATIVE_PENALTY = 0.05


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

    def apply_bot_strategy(self):
        bot = None
        human = None
        
        for player in self.get_players():
            if player.is_bot:
                bot = player
            else:
                human = player
        
        if not bot or not human:
            return
        
        if bot.role == Constants.SENDER_ROLE:
            self._apply_sender_bot_strategy()
        elif bot.role == Constants.RECEIVER_ROLE:
            self._apply_receiver_bot_strategy()
    
    def _apply_sender_bot_strategy(self):
        self.sent_amount = int(Constants.endowment * Constants.BOT_SENDER_TRUST_RATE)
        if self.field_maybe_none('sent_back_amount') is not None:
            self.set_payoffs()
    
    def _apply_receiver_bot_strategy(self):
        if self.sent_amount is None:
            return
        
        received = self.sent_amount * Constants.multiplication_factor
        
        if self.sent_amount < Constants.BOT_LOW_SEND_THRESHOLD:
            return_rate = min(Constants.BOT_RECEIVER_BASE_RATE + Constants.BOT_GENEROUS_BONUS, Constants.BOT_MAX_RETURN_RATE)
        elif self.sent_amount > Constants.BOT_HIGH_SEND_THRESHOLD:
            return_rate = max(Constants.BOT_RECEIVER_BASE_RATE - Constants.BOT_CONSERVATIVE_PENALTY, 0.30)
        else:
            return_rate = Constants.BOT_RECEIVER_BASE_RATE
        
        bot_return = int(received * return_rate)
        if self.sent_amount < Constants.BOT_HIGH_SEND_THRESHOLD:
            bot_return = max(bot_return, self.send_amount + 1)
        bot_return = max(bot_return, Constants.BOT_MIN_RETURN)
        bot_return = min(bot_return, received)
        
        self.sent_back_amount = bot_return
        self.set_payoffs()

class Player(BasePlayer):
    is_bot = models.BooleanField(initial=False)

def creating_session(subsession: Subsession):
    players = subsession.get_players()
    use_bot = subsession.session.config.get('use_bot', False)
    if use_bot and len(players) > 0:
        players[-1].is_bot = True
        players[-1].participant.is_bot = True
        players[-1].participant.vars['is_bot'] = True
    else:
        for player in players:
            player.is_bot = False
            player.participant.is_bot = False
            player.participant.vars['is_bot'] = False
    
    subsession.group_randomly()
    
    for group in subsession.get_groups():
        group_players = group.get_players()
        if len(group_players) != 2:
            continue
            
        if random.random() < 0.7:
            group.set_players([group_players[1], group_players[0]])
        
        final_players = group.get_players()
        final_players[0].participant.vars['my_role'] = Constants.SENDER_ROLE
        final_players[1].participant.vars['my_role'] = Constants.RECEIVER_ROLE
        
        for player in final_players:
            if player.is_bot:
                if player.get_others_in_group()[0].participant.vars['my_role'] == Constants.SENDER_ROLE:
                    player.participant.vars['my_role'] = Constants.RECEIVER_ROLE
                else:
                    player.participant.vars['my_role'] = Constants.SENDER_ROLE
                player.participant.vars['bot_role'] = player.participant.vars['my_role']
                player.participant.vars['is_bot'] = True


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Send(Page):
    form_model = Group
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player: Player):
        if player.is_bot: return False
        return player.role == Constants.SENDER_ROLE


    @staticmethod
    def vars_for_template(player: Player):
        return {
            'round_number': player.round_number,
            'num_rounds': Constants.num_rounds,
            'endowment': Constants.endowment,
        }
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        receiver = group.get_player_by_role(Constants.RECEIVER_ROLE)
        if receiver and receiver.is_bot:
            group.apply_bot_strategy()


class SendBackWaitPage(WaitPage):
    wait_for_all_groups = False


class SendBack(Page):
    form_model = Group
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        if player.is_bot: return False

        group = player.group
        for p in group.get_players():
            if p.is_bot and p.role == Constants.SENDER_ROLE:
                group.apply_bot_strategy()
                break
        
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

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        sender = group.get_player_by_role(Constants.SENDER_ROLE)
        if sender and sender.is_bot:
            group.apply_bot_strategy()

class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_bot

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
        if player.is_bot: return False
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
