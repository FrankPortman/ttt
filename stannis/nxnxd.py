from __future__ import print_function

from itertools import product
import random
import shutil

import ai

'''
Generalized n x n x d tic tac toe. 
You need d in a row on an n x n grid to win.
'''

# Marks to strings
X = u' ❌'
O = u' ⭕'

class Board(object):
    '''
    Board and all that fun stuff.
    '''
    def __init__(self, n, d):
        self.n = n
        self.d = d
        self.board = [[None for _ in range(n)] for _ in range(n)]
        self.available_moves = set(product(range(n), range(n)))

    def print_board(self):
        # columns = shutil.get_terminal_size().columns
        # border = '----' * self.n + '-' * (self.n - 1)
        # print(border.center(columns))
        print('----' * self.n + '-' * (self.n - 1))
        for row in self.board:
            rep = '  |'.join(i if i is not None else '  ' for i in row)
            # print(rep.center(columns))
            # print(border.center(columns))
            print(*[i if i == X or i == O else '  ' for i in row], sep="  |")
            print('----' * self.n + '-' * (self.n - 1))

    def copy(self):
        return [x[:] for x in self.board]

    def serialize(self):
        return tuple(map(tuple, self.board))

    def _direction_checker(self, row_dir=0, col_dir=0):
        '''
        Returns a function that checks a certain row direction or column
        direction or both (diagonal). We use these to construct the broader
        victory checkers.

        col_dir / row_dir should be either 0 if they don't vary for a 
        specific check, +1 if you want an increasing checker or -1 if you want a
        decreasing checker.

        Returns number of matches equal to board(row, col) in a single direction,
        returning 0 if the first step in said direction is not equal to board(row, col).

        This whole thing is probably uglier than it needs to be, but the 
        optimizations it offers over a full brute force each time make the AI 
        work marginally better. *shrug*
        '''

        def checker(row, col):
            '''
            Try at most (d - 1) in a given direction and stop early if we hit 
            an edge. Only need (d - 1) in any given direction since we are only
            looking for matches on a given (row, col), adding 1 later.
            '''
            val = self.board[row][col]
            matches = 0

            for i in range(1, self.d):
                cr = row + row_dir * i
                cc = col + col_dir * i
                if cr < 0 or cc < 0:
                    break
                if cr >= self.n or cc >= self.n:
                    break
                if self.board[cr][cc] != val:
                    break
                matches += 1
            return matches
        return checker

    def check_victory(self, row, col):
        if self.board[row][col] is None:
            return False

        def make_scorer(row_dirs, col_dirs):
            def scorer():
                score = 1 
                for row_dir, col_dir in zip(row_dirs, col_dirs):
                    checker = self._direction_checker(row_dir=row_dir, 
                                                      col_dir=col_dir)
                    score += checker(row, col)
                    if score >= self.d:
                        return self.board[row][col]
                return False
            return scorer

        horizontal_scorer = make_scorer([0, 0], [-1, 1])
        vertical_scorer = make_scorer([-1, 1], [0, 0])
        diagonal_scorer = make_scorer([-1, 1], [-1, 1])
        antidiag_scorer = make_scorer([-1, 1], [1, -1])

        return (horizontal_scorer()
                or vertical_scorer()
                or diagonal_scorer()
                or antidiag_scorer())

    def move(self, player, row, col):
        self.board[row][col] = player
        # self.available_moves.remove((row, col))

    def _undo(self, row, col):
        self.board[row][col] = None
        # self.available_moves.add((row, col))

    def get_board_state(self):
        for r,c in product(range(self.n), range(self.n)):
            victory = self.check_victory(r, c)
            if victory:
                return victory
        return False

    def get_available_moves(self):
        '''
        Returns coordinates that aren't `None` so the bot can do its thang.
        '''
        return [
            (r, c) for r, c 
            in product(range(self.n), range(self.n)) 
            if self.board[r][c] is None
        ]


class Game(object):
    ''' 
    A single game of nxnxd Tic Tac Toe.
    '''
    modes = [
        'cc', # computer vs computer
        'hc', # human vs computer
        'ch', # computer vs human
        'hh', # human vs human
    ]

    def __init__(self, n, d, mode='cc'):
        self.board = Board(n, d)
        self.turn = 0
        self.players = [X, O] if random.random() < 0.5 else [O, X]

        if mode not in self.modes:
            Exception('Invalid mode selected.')
        self.mode = mode

        if mode == 'hc':
            self.human_turn = 0
        if mode == 'ch':
            self.human_turn = 1

    @property
    def current(self):
        return self.players[self.turn % 2]

    def move(self, row, col):
        self.board.move(self.current, row, col)
        self.turn += 1

    def _undo(self, row, col):
        self.board._undo(row, col)
        self.turn -= 1        

    def play(self):
        negamax = ai.Negamax()

        if self.mode != 'cc':
            idx = input('0 or 1 index?')
            idx = int(idx)

        def human_move():
            row = input('row?: ')
            col = input('col?: ')
            row = int(row) - idx
            col = int(col) - idx
            return row, col

        def computer_move():
            player = -1 if self.current == O else 1
            #score, (row, col) = ai.negamax2(self, player)
            score, (row, col) = negamax(self, player)
            print('score: {} \n\n'.format(score))
            return row, col

        def move_handler():
            if self.mode == 'hh':
                return human_move()
            elif self.mode == 'cc':
                return computer_move()
            else:
                if self.turn % 2 == self.human_turn:
                    return human_move()
                else:
                    return computer_move()

        while True:
            self.board.print_board()
            print('{} turn'.format(self.current))

            row, col = move_handler()
            if (row, col) not in self.board.get_available_moves():
                print('Invalid move... try again.')
                continue
            self.move(row, col)

            if self.board.check_victory(row, col):
                self.turn -= 1
                self.board.print_board()
                print('{} wins!'.format(self.current))
                break

            if self.board.get_available_moves() == []:
                self.board.print_board()
                print('Tie!')
                break
