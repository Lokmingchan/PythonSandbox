# Modified from https://github.com/engineer-man/youtube/tree/master/031

import random
import multiprocessing
import math
import time

# configuration options
simulations = 6000000
num_decks = 8
shuffle_perc = 25


def simulate(queue, batch_size):
    deck = []

    def new_deck():
        std_deck = [
          # 2  3  4  5  6  7  8  9  10  J   Q   K   A
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
        ]

        # add more decks
        std_deck = std_deck * num_decks

        random.shuffle(std_deck)

        return std_deck[:]

    def play_hand():
        dealer_cards = []
        player_hands = []
        hand1 = []

        # deal initial cards
        hand1.append(deck.pop(0))
        dealer_cards.append(deck.pop(0))
        hand1.append(deck.pop(0))
        dealer_cards.append(deck.pop(0))
        player_hands.append(hand1)

        dealer_show_card = dealer_cards[0]

        current_hand = 0

        while current_hand < len(player_hands):
            if len(player_hands[current_hand]) == 2:
                if player_hands[current_hand][0] == player_hands[current_hand][1]:
                    if player_hands[current_hand][0] == 10:
                        current_hand += 1
                        continue
                    if player_hands[current_hand][0] == 11 \
                            or player_hands[current_hand][0] == 8 \
                            or (player_hands[current_hand][0] == 9 and dealer_show_card not in [7, 10]) \
                            or (player_hands[current_hand][0] in [7, 3, 2] and dealer_show_card in [2, 3, 4, 5, 6, 7]) \
                            or (player_hands[current_hand][0] in [6] and dealer_show_card in [2, 3, 4, 5, 6]) \
                            or (player_hands[current_hand][0] in [4] and dealer_show_card in [5, 6]):
                        new_hand = [player_hands[current_hand].pop(0)]
                        player_hands[current_hand].append(deck.pop(0))
                        new_hand.append(deck.pop(0))
                        player_hands.append(new_hand)

                if player_hands[current_hand][0] == 11 or player_hands[current_hand][1] == 11:
                    if sum(player_hands[current_hand]) > 18 \
                            or (sum(player_hands[current_hand]) > 18 and dealer_show_card < 9):
                        current_hand += 1
                        continue
                    if (sum(player_hands[current_hand]) == 17 and dealer_show_card in [3, 4, 5, 6]) \
                            or (sum(player_hands[current_hand]) in [15, 16] and dealer_show_card in [4, 5, 6]) \
                            or (sum(player_hands[current_hand]) in [13, 14] and dealer_show_card in [5, 6]):
                        if player_hands[current_hand][0] == 11:
                            player_hands[current_hand][0] = 1
                        else:
                            player_hands[current_hand][1] = 1
                elif sum(player_hands[current_hand]) > 17 \
                        or sum(player_hands[current_hand]) in [13, 14, 15, 16] and dealer_show_card in [2, 3, 4, 5, 6] \
                        or sum(player_hands[current_hand]) in [12] and dealer_show_card in [4, 5, 6]:
                    current_hand += 1
                    continue

            while sum(player_hands[current_hand]) < 17:
                player_hands[current_hand].append(deck.pop(0))

                if sum(player_hands[current_hand]) > 21:
                    for i, card in enumerate(player_hands[current_hand]):
                        if card == 11:
                            player_hands[current_hand][i] = 1
                            break

            current_hand += 1

        # deal dealer on soft 17
        while sum(dealer_cards) < 18:
            exit = False
            # check for soft 17
            if sum(dealer_cards) == 17:
                exit = True
                # check for an ace and convert to 1 if found
                for i, card in enumerate(dealer_cards):
                    if card == 11:
                        exit = False
                        dealer_cards[i] = 1

            if exit:
                break

            dealer_cards.append(deck.pop(0))

        d_sum = sum(dealer_cards)

        player_total = 0
        for hand in player_hands:
            p_sum = sum(hand)

            # player bust
            if p_sum > 21:
                player_total += -1
            # dealer bust
            elif d_sum > 21:
                player_total += 1
            # dealer tie
            elif d_sum == p_sum:
                player_total += 0
            # dealer win
            elif d_sum > p_sum:
                player_total += -1
            # dealer lose
            elif d_sum < p_sum:
                player_total += 1

        return player_total


    # starting deck
    deck = new_deck()

    # play hands
    win = 0
    draw = 0
    lose = 0
    for i in range(0, batch_size):
        # reshuffle cards at shuffle_perc percentage
        if (float(len(deck)) / (52 * num_decks)) * 100 < shuffle_perc:
            deck = new_deck()

        # play hand
        result = play_hand()

        # tally results
        if result > 0:
            win += 1
        if result == 0:
            draw += 1
        if result < 0:
            lose += 1

        # add everything to the final results
    queue.put([win, draw, lose])


def main():
    start_time = time.time()

    # simulate
    cpus = multiprocessing.cpu_count()
    batch_size = int(math.ceil(simulations / float(cpus)))

    queue = multiprocessing.Queue()

    # create n processes
    processes = []

    for i in range(0, cpus):
        process = multiprocessing.Process(target=simulate, args=(queue, batch_size))
        processes.append(process)
        process.start()

    # wait for everything to finish
    for proc in processes:
        proc.join()

    finish_time = time.time() - start_time

    # get totals
    win = 0
    draw = 0
    lose = 0

    for i in range(0, cpus):
        results = queue.get()
        win += results[0]
        draw += results[1]
        lose += results[2]

    print
    print('  cores used: %d' % cpus)
    print('  total simulations: %d' % simulations)
    print('  simulations/s: %d' % (float(simulations) / finish_time))
    print('  execution time: %.2fs' % finish_time)
    print('  win percentage: %.2f%%' % ((win / float(simulations)) * 100))
    print('  draw percentage: %.2f%%' % ((draw / float(simulations)) * 100))
    print('  lose percentage: %.2f%%' % ((lose / float(simulations)) * 100))
    print


if __name__ == "__main__":
    main()
