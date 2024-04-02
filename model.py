from enum import IntEnum

BOARD_DIM = [20,10]
BOARD_SIZE = BOARD_DIM[0] * BOARD_DIM[1]

# grid to str repr
def grid_repr(grid: list[list[bool]] | None = None) -> str:
    # 0001101111 -> 3,2,1,4
    # alternate between length of 0 seq and length of 1 seq
    arr = [False] * BOARD_SIZE if grid is None else [x for row in grid for x in row]
    ret = [0]
    curr = False
    for x in arr:
        if x == curr: ret[-1] += 1
        else:
            ret.append(1)
            curr = not curr
    # to string
    return ';'.join([str(x) for x in ret])

# str repr to grid
def load_repr(repr: str | None = None) -> list[list[bool]]:
    flat = [0] * BOARD_SIZE
    curr = False
    if repr is not None:
        offset = 0
        for x in repr.split(';'):
            x = int(x)
            if curr: flat[offset:offset+x] = [True] * x
            curr = not curr
            offset += x
    ret = [None] * BOARD_DIM[0]
    for r in range(0, BOARD_DIM[0]):
        offset = r * BOARD_DIM[1]
        ret[r] = flat[offset:offset + BOARD_DIM[1]]
    return ret

# piece type enum
class PieceType(IntEnum):
    O = 0
    I = 1
    L = 2
    J = 3
    S = 4
    Z = 5
    T = 6

# represents a tetromino
class Piece:
    _tile_data: list[list[tuple[int,int]]] = [
        [[(1,1),(1,2),(2,1),(2,2)]] * 4, # O
        [[(2,0),(2,1),(2,2),(2,3)], [(0,2),(1,2),(2,2),(3,2)]] * 2, #I
        [[(1,0),(1,1),(1,2),(2,0)], [(0,0),(0,1),(1,1),(2,1)], [(0,2),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)]], # L
        [[(1,0),(1,1),(1,2),(2,2)], [(0,1),(1,1),(2,0),(2,1)], [(0,0),(1,0),(1,1),(1,2)], [(0,1),(0,2),(1,1),(2,1)]], # J
        [[(1,1),(1,2),(2,0),(2,1)], [(0,1),(1,1),(1,2),(2,2)]] * 2, #S
        [[(1,0),(1,1),(2,1),(2,2)], [(0,2),(1,1),(1,2),(2,1)]] * 2, #Z
        [[(1,0),(1,1),(1,2),(2,1)], [(0,1),(1,0),(1,1),(2,1)], [(0,1),(1,0),(1,1),(1,2)], [(0,1),(1,1),(1,2),(2,1)]] #T
    ]
    _starting_offset: list[tuple[int,int]] = [
        (-1,3), # O
        (-2,4), # I
        (-1,4), # L
        (-1,4), # J
        (-1,4), # S
        (-1,4), # Z
        (-1,4)  # T
    ]

    def __init__(self, type: PieceType, dir: int = 0, offset: tuple[int,int] | None = None):
        self.type = type
        self.dir = dir
        self.offset = Piece._starting_offset[int(type)] if offset is None else offset
        self._tiles = None # cached instance of this piece's tiles

    def translate(self, dr: int, dc: int):
        self._tiles = None
        self.offset = (self.offset[0] + dr, self.offset[1] + dc)

    def rotate(self, ccw: bool) -> None:
        self._tiles = None
        self.dir = (self.dir + 4 + (-1 if ccw else 1)) & 3
        
    def clone(self) -> 'Piece':
        return Piece(self.type, self.dir, self.offset[:])
    
    def get_tiles(self) -> list[tuple[int,int]]:
        if self._tiles is None:
            self._tiles = [(t[0] + self.offset[0], t[1] + self.offset[1]) for t in Piece._tile_data[int(self.type)][self.dir]]
        return self._tiles
        
    def __hash__(self) -> int:
        return hash((self.type, self.dir, self.offset))
    
    def __eq__(self, other) -> bool:
        return (self.type, self.dir, self.offset) == (other.type, other.dir, other.offset)

# represents current game state
class State:
    def __init__(self, grid: list[list[bool]] | None = None, active_piece: Piece = Piece(PieceType.O), next_piece: Piece = Piece(PieceType.O)):
        self.grid = load_repr() if grid is None else [row[:] for row in grid]
        self.row_count = [self.grid[r].count(True) for r in range(BOARD_DIM[0])]
        self.active_piece = active_piece
        self.next_piece = next_piece

    # places piece, returns number of cleared lines
    def place_piece(self, new_next_piece: Piece) -> int:
        # place
        assert(self.placeable())
        row_clears = 0
        for r,c in self.active_piece.get_tiles():
            self.grid[r][c] = True
            self.row_count[r] += 1
            row_clears += int(self.row_count[r] == BOARD_DIM[1])
        self.active_piece, self.next_piece = self.next_piece, new_next_piece

        # handle line clears
        if row_clears == 0:
            return 0
        nr = BOARD_DIM[0]-1
        for r in range(BOARD_DIM[0]-1,-1,-1):
            self.row_count[nr] = self.row_count[r]
            self.grid[nr] = self.grid[r]
            nr += int(self.row_count[nr] == BOARD_DIM[1]) - 1
        for r in range(nr+1):
            self.grid[r] = [False] * BOARD_DIM[1]
        return row_clears

    # validates that no collisions between board bounds or grid happens with active piece
    def valid(self) -> bool:
        return all(t[0] >= 0 and t[1] >= 0 and t[0] < BOARD_DIM[0] and t[1] < BOARD_DIM[1] and not self.grid[t[0]][t[1]] for t in self.active_piece.get_tiles())
    
    # checks if is placeable
    def placeable(self) -> bool:
        return self.valid() and any(t[0] == BOARD_DIM[0]-1 or self.grid[t[0]+1][t[1]] for t in self.active_piece.get_tiles())