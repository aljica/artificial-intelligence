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
        state = node.state
        v = 10*(state.get_player_scores()[0] - state.get_player_scores()[1])

        fish_pos = state.get_fish_positions()
        fish_scores = state.get_fish_scores()
        hook_pos = state.get_hook_positions()

        idx_of_best_fish = -1
        val_of_best_fish = -1
        for i in range(len(fish_pos)):
            if fish_pos[i] > val_of_best_fish:
                idx_of_best_fish = i
                val_of_best_fish = fish_pos[i]

        try:
            fish_position = fish_pos[idx_of_best_fish]
        except KeyError:
            return v

        player = state.get_player()
        player_position = hook_pos[player]
        fish_distance = abs(fish_position[0] - player_position[0]) + abs(fish_position[1] - player_position[1])
        if fish_distance != 0:
            fish_distance = 1/fish_distance # Invert it so A wants to maximize, B minimize.
        else:
            fish_distance = 0

        return v-fish_distance
        #return node.state.get_player_scores()[0] - node.state.get_player_scores()[1]
        # addera med typ (total points of fish / distance of my hook to the fish)
        # add some weight to the first part (player_scores), like multiply it by 10 or so
        # då vill jag maximera detta och motståndaren minimera

    def alpha_beta_moves(node, depth, alpha, beta, t):
        player = node.state.get_player()

        if depth == 0 or (time.time() - t > 0.046):
            v = Minimax.h(node)

        elif player == 0:
            v = -math.inf
            for child in node.compute_and_get_children():
                hooks = child.state.get_hook_positions()
                fish = child.state.get_fish_positions()
                key = str(hooks)+str(fish)
                try:
                    v = max(v, explored_states[key])
                except KeyError:
                    v = max(v, Minimax.alpha_beta_moves(child, depth, -math.inf, math.inf, t))
                    explored_states[key] = v

                #v = max(v, Minimax.alpha_beta_move(child, depth-1, alpha, beta, t))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

        else:
            v = math.inf
            for child in node.compute_and_get_children():
                hooks = child.state.get_hook_positions()
                fish = child.state.get_fish_positions()
                key = str(hooks)+str(fish)
                try:
                    v = min(v, explored_states[key])
                except KeyError:
                    v = min(v, Minimax.alpha_beta_moves(child, depth, -math.inf, math.inf, t))
                    explored_states[key] = v

                #v = min(v, Minimax.alpha_beta_move(child, depth-1, alpha, beta, t))
                beta = min(beta, v)
                if beta <= alpha:
                    break

        return v

    def find_best_moves(self, root):
        max_depth = 9
        children = root.compute_and_get_children()
        # Add to explored states (do not! because then the first stay move will always be bad to perform)
        #hooks = root.state.get_hook_positions()
        #fish = root.state.get_fish_positions()

        bestChild = None
        bestV = -math.inf

        t = time.time()
        for depth in range(1, max_depth):
            for child in children:
                hooks = child.state.get_hook_positions()
                fish = child.state.get_fish_positions()
                key = str(hooks)+str(fish)
                try:
                    v = explored_states[key]
                    #print(explored_states)
                except KeyError:
                    print(depth)
                    print("keyerror")
                    v = Minimax.alpha_beta_moves(child, depth, -math.inf, math.inf, t)
                    explored_states[key] = v

                if v > bestV:
                    v = bestV
                    bestChild = child

            if (time.time() - t > 0.046):
                break

        return bestChild.move

    def alpha_beta_move(self, node, depth, alpha, beta, start_time):
        player = node.state.get_player()
        children = node.compute_and_get_children()

        if depth == 0 or (time.time() - start_time > 0.04):
            v = self.h(node)

        elif player == 0:
            # Node reordering/Move ordering below (max to min)
            children.sort(key=lambda child: self.h(child), reverse=True)
            # Node reordering/Move ordering above
            v = -math.inf
            for child in children:
                try:
                    v = self.explored_states[self.generate_key(child, depth)]
                except KeyError:
                    v = max(v, self.alpha_beta_move(child, depth-1, alpha, beta, start_time))
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
                # See if state is in our dict
                try:
                    v = self.explored_states[self.generate_key(child, depth)]
                except KeyError:
                    v = min(v, self.alpha_beta_move(child, depth-1, alpha, beta, start_time))
                beta = min(beta, v)
                if beta <= alpha:
                    break

        return v

    def find_best_move(self, root):
        fish_pos = root.state.get_fish_positions()
        fish_scores = root.state.get_fish_scores()
        hook_pos = root.state.get_hook_positions()

        max_depth = 6
        children = root.compute_and_get_children()
        #print("fish scores root", root.state.get_fish_scores())

        bestChild = None
        bestV = -math.inf

        #children.sort(key=lambda child: Minimax.h(child), reverse=True)
        start_time = time.time()
        for depth in range(1, max_depth):
            for child in children:
                v = self.alpha_beta_move(child, depth, -math.inf, math.inf, start_time)
                self.explored_states[self.generate_key(child, depth)] = v # Store the explored state in our dict
                if v > bestV:
                    v = bestV
                    bestChild = child

        #    print("reached depth", depth)
        # GETS STUCK AT RIGHT (COLLISION) AS OPPOSED TO CATCHING FISH TO THE LEFT???
        #print("fish scores", bestChild.state.get_fish_scores())

        return bestChild.move


    def find_best_movePAUSED(self, root):
        """For grade C (although Kattis only gives 12/25 points).
        With iterative deepening search."""
        max_depth = 8
        children = root.compute_and_get_children()

        bestChild = None
        bestV = -math.inf

        start = time.time()
        for depth in range(1, max_depth):
            for child in children:
                v = Minimax.alpha_beta_move(child, depth, -math.inf, math.inf, time.time())
                if v > bestV:
                    v = bestV
                    bestChild = child

            if time.time() - start > 0.025:
                break

        return bestChild.move

    def generate_key(self, node, depth):
        """For use in dictionary."""
        player = str(node.state.get_player())
        player_scores = str(node.state.get_player_scores())
        player_caught = str(node.state.get_caught())
        hook_pos = str(node.state.get_hook_positions())
        fish_pos = str(node.state.get_fish_positions())
        depth=str(depth)
        return player+player_scores+player_caught+hook_pos+fish_pos+depth

    def __init__(self, initial_data):
        #self.explored_states = {} # Stores str(hooks+fish) as keys and corresponding heuristic value as values
        self.activeFish(initial_data)
        self.explored_states = {}

    def activeFish(self, initial_data):
        """Process the number of active fish in the game.
        Doesn't seem like we actually need this?"""
        pass
