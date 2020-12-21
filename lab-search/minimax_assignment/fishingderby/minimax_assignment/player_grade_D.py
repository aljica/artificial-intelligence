#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

import time
import math
from operator import itemgetter


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3},
          'fish1': {'score': 2, 'type': 1},
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """

        return Minimax(initial_data)

    def search_best_next_move(self, model, initial_tree_node):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        return ACTION_TO_STR[model.find_best_move(initial_tree_node)]

class Minimax:

    def h(self, node):
        """Heuristic function."""
        return node.state.get_player_scores()[0] - node.state.get_player_scores()[1]

    def alphabeta(self, node, depth, alpha, beta, start_time):
        player = node.state.get_player()
        children = node.compute_and_get_children()

        if depth == 0 or time.time() - start_time > 0.04:
            v = self.h(node)

        elif player == 0:
            v = -math.inf
            for child in children:
                v = max(v, self.alphabeta(child, depth-1, alpha, beta, start_time))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

        else:
            v = math.inf
            for child in children:
                v = min(v, self.alphabeta(child, depth-1, alpha, beta, start_time))
                beta = min(beta, v)
                if beta <= alpha:
                    break

        return v

    def find_best_move(self, root):
        # KATTIS ID: 6227574
        max_depth = 2
        children = root.compute_and_get_children()

        bestChild = None
        bestV = -math.inf

        start_time = time.time()
        for child in children:
            v = self.alphabeta(child, max_depth, -math.inf, math.inf, start_time)
            if v > bestV:
                v = bestV
                bestChild = child

        return bestChild.move

    def __init__(self, initial_data):
        #self.explored_states = {} # Stores str(hooks+fish) as keys and corresponding heuristic value as values
        self.activeFish(initial_data)
        self.explored_states = {}

    def activeFish(self, initial_data):
        """Process the number of active fish in the game.
        Doesn't seem like we actually need this?"""
        pass
