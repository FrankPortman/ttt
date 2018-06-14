from __future__ import print_function

from itertools import product
import random

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
    def __init__(self, n, d, board=None):
        self.n = n
        self.d = d
        self.board = board or [[None for _ in range(n)] for _ in range(n)]

    def print_board(self):
        print('----' * self.n + '-' * (self.n - 1))
        for row in self.board:
            print(*[i if i == X or i == O else '  ' for i in row], sep="  |")
            print('----' * self.n + '-' * (self.n - 1))

    def copy(self):
        return [x[:] for x in self.board]

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

        return horizontal_scorer() or \
               vertical_scorer()   or \
               diagonal_scorer()   or \
               antidiag_scorer()

    def move(self, player, row, col):
        if self.board[row][col] is None:
            self.board[row][col] = player
            return True
        else:
            print('That position is already marked!  Please pick again.')
            return False

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


class GameVictory(Exception):
    pass


class GameTie(Exception):
    pass


class Game(object):
    ''' 
    A single game of nxnxd Tic Tac Toe.
    '''

    def __init__(self, n, d, players=None, mode='computer', turn=None, board=None):
        self.board = Board(n, d, board)
        self.turn = turn or 0
        self.players = players or ([X, O] if random.random() < 0.5 else [O, X])
        self.mode = mode

    @property
    def current(self):
        return self.players[self.turn % 2]

    def move(self, row, col):
        result = self.board.move(self.current, row, col)
        if result: # only change turn if marker placement successful
            self.turn += 1

    def _undo(self, row, col):
        self.board.board[row][col] = None
        self.turn -= 1

    def play(self):
        idx = input('0 or 1 index?')
        idx = int(idx)
        while True:
            self.board.print_board()
            print('{} turn'.format(self.current))
            if self.mode != 'computer':
                row = input('row?')
                col = input('col?')
                row = int(row) - idx
                col = int(col) - idx
                self.move(row, col)
            elif self.mode == 'computer' and self.current == X:
                score, (row, col) = ai.negamax2(self, 1)
                print('score: {}'.format(score))
                self.move(row, col)
            elif self.mode == 'computer' and self.current == O:
                score, (row, col) = ai.negamax2(self, -1)
                print('score: {}'.format(score))
                self.move(row, col)
                # row = input('row?')
                # col = input('col?')
                # row = int(row) - idx
                # col = int(col) - idx
                # self.move(row, col)
            if self.board.check_victory(row, col):
                self.turn -= 1
                self.board.print_board()
                print('{} wins!'.format(self.current))
                break
            if self.board.get_available_moves() == []:
                self.board.print_board()
                print('Tie!')
                break
