from neat_splendor_entities import Tier
from copy import deepcopy
from enums import Resource

options = (
    (Tier.FIRST, 0), (Tier.SECOND, 0), (Tier.THIRD, 0), (Tier.FIRST, 1), (Tier.SECOND, 1), (Tier.THIRD, 1),
    (Tier.FIRST, 2), (Tier.SECOND, 2), (Tier.THIRD, 2), (Tier.FIRST, 3), (Tier.SECOND, 3), (Tier.THIRD, 3)
)

number_tier_translator = {
    0: Tier.FIRST,
    1: Tier.SECOND,
    2: Tier.THIRD,
    3: Tier.RESERVE
}


def _is_purchase_possible(player_instance, card):
    if card is not None:
        copy = deepcopy(player_instance.resources)
        try:
            player_instance.pay(card.cost)
            player_instance.resources = copy
            return True
        except ValueError:
            player_instance.resources = copy
            return False


def _convert_option_to_order(all_options):
    indexes_and_values = dict()
    for index, value in enumerate(all_options):
        indexes_and_values[value] = index
    order = []
    for option in sorted(all_options, reverse=True):
        order.append(indexes_and_values[option])
    return order


def _lacks(player, costs):
    lack = dict()
    for resource in costs:
        cost = costs[resource] - player.resources.get(resource, 0) - player.get_production().get(resource, 0)
        if cost > 0:
            lack[resource] = cost
    return lack


def go_for_option(game, all_options):
    order = _convert_option_to_order(all_options)
    player = game.players[0]
    board = game.board
    if sum(player.resources.values()) == 10:
        for option in order:
            card = game.board.visible_cards[option]
            if _is_purchase_possible(player, card):
                player.pay(card.cost)
                player.get_card(board.take_card(number_tier_translator[option // 4], option % 4))
                return True
        else:
            raise ValueError
    card = game.board.visible_cards[options[order[0]][0].value * 4 + options[order[0]][1]]
    if _is_purchase_possible(player, card):
        player.pay(card.cost)
        player.get_card(board.take_card(options[order[0]][0], options[order[0]][1]))
        return True
    else:
        gotten = set()
        i = 0
        can_be_taken = 3
        while sum(player.resources.values()) < 10 and len(gotten) < 3 and can_be_taken > 0:
            if i >= len(options):
                break
            card = game.board.visible_cards[options[order[i]][0].value * 4 + options[order[i]][1] - 3]
            if card:
                lack = _lacks(player, card.cost)
                if not cart_can_be_taken(lack, player.resources, board.available_resources):
                    i += 1
                    continue
                lack = tuple(
                    sorted(_lacks(player, card.cost).items(), key=lambda elem: elem[1], reverse=True))
                if not len(lack):
                    if not len(gotten):
                        player.pay(card.cost)
                        player.get_card(board.take_card(options[order[i]][0], options[order[i]][1]))
                        return True
                    else:
                        i += 1
                        continue
                if len(lack) == 1 and sum(player.resources.values()) <= 8 and board.available_resources[
                    lack[0][0]] >= 4 and can_be_taken >= 2 and lack[0][0] not in gotten:
                    res = lack[0][0]
                    player.get_resource(res)
                    player.get_resource(res)
                    board.remove_resource(res)
                    board.remove_resource(res)
                    break
                else:
                    for resource, _ in lack:
                        if resource not in gotten and board.available_resources[resource] and len(
                                gotten) < 3 and can_be_taken > 0:
                            player.get_resource(resource)
                            gotten.add(resource)
                            board.remove_resource(resource)
                            if i:
                                can_be_taken -= 1
                    can_be_taken = 10 - sum(_lacks(player, card.cost).values()) - sum(player.resources.values())
                    if not can_be_taken and len(gotten):
                        return False
                    i += 1
            else:
                i += 1


def cart_can_be_taken(lack, possessions, stored):
    if sum(lack.values()) > 10 - sum(possessions.values()):
        return False
    for gem in lack:
        if lack[gem] > stored.get(gem, 0):
            return False
    return True


def can_cart_be_reserved(player, board, tier, index):
    return len(player.reserve) < 3 and board.show_card(tier, index)


def reserve_cart(player, board, tier, index):
    player.add_reserve(board.reserve_card(tier, index))
    if sum(player.resources.values()) < 10:
        player.resources[Resource.GOLD] = player.resources.get(Resource.GOLD, 0) + 1


def go_for_option_full(game, all_options):
    index = 0
    order = _convert_option_to_order(all_options)
    player = game.players[0]
    board = game.board
    while order[index] >= 15:
        if can_cart_be_reserved(player, board, Tier.FIRST if order[index] < 20 else Tier.SECOND if order[index] < 25 else Tier.THIRD, order[index] % 5):
            reserve_cart(player, board, Tier.FIRST if order[index] < 20 else Tier.SECOND if order[index] < 25 else Tier.THIRD, order[index] % 5)
            return
        index += 1
    order = list(filter(lambda element: element < 15, order))
    if sum(player.resources.values()) == 10:
        for option in order:
            if option < 3:
                if len(player.reserve) > option:
                    cart = player.reserve[option]
                else:
                    continue
            else:
                cart = game.board.visible_cards[option-3]
            if _is_purchase_possible(player, cart):
                player.pay(cart.cost)
                if option < 3:
                    player.get_card(player.reserve.pop(player.reserve.index(cart)))
                else:
                    player.get_card(board.take_card(number_tier_translator[(option-3) // 4], (option-3) % 4))
                return
        else:
            raise ValueError
    if order[0] >= 3:
        cart = game.board.show_card(options[order[0]-3][0], options[order[0]-3][1])
        if _is_purchase_possible(player, cart):
            player.pay(cart.cost)
            player.get_card(board.take_card(options[order[0]-3][0], options[order[0]-3][1]))
            return True
    else:
        if len(player.reserve) > order[0]:
            cart = player.reserve[order[0]]
            if _is_purchase_possible(player, cart):
                player.pay(cart.cost)
                player.get_card(player.reserve.pop(order[0]))
                return True
    gotten = set()
    i = 0
    can_be_taken = 3
    while sum(player.resources.values()) < 10 and len(gotten) < 3 and can_be_taken > 0:
        if i >= 15:
            break
        if order[i] >= 3:
            cart = game.board.visible_cards[options[order[i]-3][0].value * 4 + options[order[i]-3][1]]
        else:
            if len(player.reserve) > order[0]:
                cart = player.reserve[order[0]]
            else:
                i += 1
                continue
        if cart:
            lack = _lacks(player, cart.cost)
            if not cart_can_be_taken(lack, player.resources, board.available_resources):
                i += 1
                continue
            lack = tuple(
                sorted(_lacks(player, cart.cost).items(), key=lambda elem: elem[1], reverse=True))
            if not len(lack):
                if not len(gotten):
                    player.pay(cart.cost)
                    player.get_card(cart)
                    if order[i] < 3:
                        player.reserve.pop(order[i])
                    return
                else:
                    i += 1
                    continue
            if len(lack) == 1 and sum(player.resources.values()) <= 8 and board.available_resources[
                lack[0][0]] >= 4 and can_be_taken >= 2 and lack[0][0] not in gotten:
                res = lack[0][0]
                player.get_resource(res)
                player.get_resource(res)
                board.remove_resource(res)
                board.remove_resource(res)
                break
            else:
                for resource, _ in lack:
                    if resource not in gotten and board.available_resources[resource] and len(
                            gotten) < 3 and can_be_taken > 0:
                        player.get_resource(resource)
                        gotten.add(resource)
                        board.remove_resource(resource)
                        if i:
                            can_be_taken -= 1
                can_be_taken = 10 - sum(_lacks(player, cart.cost).values()) - sum(player.resources.values())
                if not can_be_taken and len(gotten):
                    return
                i += 1
        else:
            i += 1
