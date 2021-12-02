from dataclasses import dataclass, field
from operator import attrgetter

from battle import Battle
from positions import Knight_Item_Positions


class Drowned(Exception):
    pass


class Arena:
    """
    The Arena class handles movement of its knights and items.

    The `board` property is a matrix of Pos elements.
    """

    def __init__(self):
        board = []
        for y in range(0, 8):
            row = [Knight_Item_Positions(y, x) for x in range(0, 8)]
            board.append(tuple(row))

        self.board = tuple(board)

    def move_knight(self, knight, direction):
        # clear out the old position square
        knight.pos.knight = None

        try:
            _pos = self._direction_to_pos(direction, knight.pos)
        except Drowned:
            loot, last_pos = Battle.kill_knight(knight, status=2)
            print('knight Drowned', knight)

            if self.drop_loot(loot, last_pos):
                print('the Loot dropped:', loot)

        else:
            if self._is_square_with_knight(_pos):
                # Battle!
                winner, loser = Battle.attack(knight, _pos.knight)
                self._move_knight_pos(winner, _pos)
                loot, last_pos = Battle.kill_knight(loser)

                print('BATTLE ')
                print("\n")
                print('Winner: ', winner)
                print('Loser: ', loser)
                if self.drop_loot(loot, last_pos):
                    print('The Loot dropped: ', loot)
                return winner

            if self._is_empty_square(_pos):
                self._move_knight_pos(knight, _pos)
                print('knight Moved', knight)

            elif self._is_square_with_item(_pos):
                self._move_knight_pos(knight, _pos)
                _pos.items.sort(key=attrgetter('priority'))

                if not knight.equipped:
                    knight.equipped = _pos.items.pop()
                    print(' knight equipment Acquired ', knight.equipped)

            return knight

    def drop_loot(self, item, pos):
        """
        Drop item onto Pos, update item pos.
        """
        if item:
            item.pos = pos
            pos.items.append(item)
            pos.items.sort(key=attrgetter('priority'))
            return True

    def _move_knight_pos(self, knight, pos):
        """
        Assign Pos to Knight and vice-versa.
        """
        knight.pos = pos
        pos.knight = knight
        if knight.equipped:
            knight.equipped.pos = pos

    def render(self):
        print('')
        for row in self.board:
            for pos in row:
                if pos.knight:
                    print('KNIGHT ID ' + pos.knight.id, end='')

                elif len(pos.items):
                    print('SWORD -' + pos.items[0].name[0] if pos.items[0] else '', end='')

                else:
                    print('  ', end='')
            print('')
        print('')

    def _direction_to_pos(self, direction: str, old_pos: Knight_Item_Positions):
        """
        Translate direction to Pos instance.
        Out of bounds coordinates will raise a `Drowned` error.
        This is needed in order to deal with tuple index wrap-around.

        e.g. On the initial board, when going North, the Y knight's
             position will wrap around and end up battling the G knight!
        """
        dir_map = {
            'N': (old_pos.y - 1, old_pos.x),
            'S': (old_pos.y + 1, old_pos.x),
            'E': (old_pos.y, old_pos.x + 1),
            'W': (old_pos.y, old_pos.x - 1),
        }
        y, x = dir_map[direction]

        if x < 0 or x > 7 or y < 0 or y > 7:
            raise Drowned('Knight drowned')

        return self.board[y][x]

    def _is_empty_square(self, pos):
        return not pos.knight and len(pos.items) == 0

    def _is_square_with_item(self, pos):
        return len(pos.items) > 0

    def _is_square_with_knight(self, pos):
        return pos.knight is not None
