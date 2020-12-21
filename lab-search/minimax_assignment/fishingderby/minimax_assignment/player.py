#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

import time
import math


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
        state = node.state
        player = state.get_player()
        caught = state.get_caught()
        fish_scores = state.get_fish_scores()

        # Add score of fish if player has fish on its hook
        player_score = state.get_player_scores()[player]
        opposing_player_score = state.get_player_scores()[1-player]
        if caught[player]:
            fish_index = caught[player]
            score = fish_scores[fish_index]
            player_score += score
        if caught[1-player]:
            fish_index = caught[1-player]
            score = fish_scores[fish_index]
            opposing_player_score += score

        v = player_score - opposing_player_score

        # Find out which fish has highest score
        fish_positions = state.get_fish_positions()
        fish_scores = state.get_fish_scores()

        best_fish_score = -math.inf
        best_fish_index = -1
        for fish_index in fish_positions:
            score = fish_scores[fish_index]
            if score > best_fish_score:
                best_fish_score = score
                best_fish_index = fish_index

        if best_fish_score < 0:
            return 10*v

        # Get hook position for player 0 & calculate distance to best fish
        hook_positions = state.get_hook_positions()
        distance = abs(hook_positions[0][0] - fish_positions[best_fish_index][0]) + abs(hook_positions[0][1] - fish_positions[best_fish_index][1])

        if player == 0:
            # Check distance from green boat to fish with max score and subtract from v
            return 10*v - distance
        else:
            return 10*v + distance
            # Check distance from green boat to fish with max score and add to v

    def alphabeta(self, node, depth, alpha, beta, start_time):
        player = node.state.get_player()

        if time.time() - start_time > self.timeout_time:
            self.timedout = True
            return 0
        if depth == 0:
            v = self.h(node)
            return v

        key = self.generate_key(node)
        try:
            children = self.all_children[key]
        except KeyError:
            children = node.compute_and_get_children()
            self.all_children[key] = children

        if player == 0:
            # Node reordering/Move ordering below (max to min)
            children.sort(key=lambda child: self.h(child), reverse=True)
            # Node reordering/Move ordering above
            v = -math.inf
            for child in children:
                v = max(v, self.alphabeta(child, depth-1, alpha, beta, start_time))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

        else:
            # Node reordering/Move ordering below (min to max)
            # https://stackoverflow.com/questions/9964496/alpha-beta-move-ordering
            children.sort(key=lambda child: self.h(child))
            # Node reordering/Move ordering above
            v = math.inf
            for child in children:
                v = min(v, self.alphabeta(child, depth-1, alpha, beta, start_time))
                beta = min(beta, v)
                if beta <= alpha:
                    break

        return v

    def find_best_move(self, root):
        max_depth = 4

        bestChild = None
        bestV = -math.inf

        # Save children so we don't have to compute them over and over again in alphabeta()
        key = self.generate_key(root)
        try:
            children = self.all_children[key]
        except KeyError:
            children = root.compute_and_get_children()
            self.all_children[key] = children

        # Node/move ordering below
        if root.state.get_player() == 0:
            children.sort(key=lambda child: self.h(child), reverse=True)
        else:
            children.sort(key=lambda child: self.h(child))
        # Node/move ordering above

        ids_start_time = time.time() # Timer for iterative deepening search
        for depth in range(1, max_depth):
            for child in children:
                v = self.alphabeta(child, depth, -math.inf, math.inf, ids_start_time)
                if self.timedout:
                    self.timedout = False
                    break
                if v > bestV:
                    v = bestV
                    bestChild = child
                if time.time() - ids_start_time > self.timeout_time:
                    #print("timer's up, alphabeta is thus useless, breaking")
                    break
            if time.time() - ids_start_time > self.timeout_time:
                break

        return bestChild.move

    def generate_key(self, node):
        """For use in dictionary."""
        player = str(node.state.get_player())
        player_scores = str(node.state.get_player_scores())
        player_caught = str(node.state.get_caught())
        hook_pos = str(node.state.get_hook_positions())
        fish_pos = str(node.state.get_fish_positions())
        return player+player_scores+player_caught+hook_pos+fish_pos

    def __init__(self, initial_data):
        #self.explored_states = {} # Stores str(hooks+fish) as keys and corresponding heuristic value as values
        self.activeFish(initial_data)
        self.explored_states = {}
        self.timedout = False
        self.timeout_time = 0.067
        self.all_children = {}

    def activeFish(self, initial_data):
        """Process the number of active fish in the game.
        Doesn't seem like we actually need this?"""
        pass
