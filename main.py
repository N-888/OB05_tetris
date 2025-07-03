from abc import ABC, abstractmethod
import random
import pygame
import time
from typing import List, Tuple, Dict, Optional, Type


# --------------------------------------------
# Исправленные классы
# --------------------------------------------

class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col


class Block:
    def __init__(self, color: Tuple[int, int, int]):
        self.color = color


class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def is_valid_position(self, position: Position) -> bool:
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_cell_empty(self, position: Position) -> bool:
        return self.is_valid_position(position) and self.grid[position.row][position.col] is None

    def place_block(self, position: Position, block: Block):
        if self.is_valid_position(position):
            self.grid[position.row][position.col] = block

    def clear_lines(self) -> int:
        lines_cleared = 0
        row = self.rows - 1
        while row >= 0:
            if all(self.grid[row]):
                lines_cleared += 1
                for r in range(row, 0, -1):
                    self.grid[r] = self.grid[r - 1][:]
                self.grid[0] = [None] * self.cols
            else:
                row -= 1
        return lines_cleared


class Tetromino(ABC):
    def __init__(self):
        self.blocks: List[Block] = []
        self.positions: List[Position] = []
        self.pivot = Position(0, 0)
        self.color: Tuple[int, int, int]

    @abstractmethod
    def initialize_positions(self):
        pass

    def rotate(self):
        new_positions = []
        for pos in self.positions:
            row_offset = pos.row - self.pivot.row
            col_offset = pos.col - self.pivot.col
            new_row = self.pivot.row - col_offset
            new_col = self.pivot.col + row_offset
            new_positions.append(Position(round(new_row), round(new_col)))
        self.positions = new_positions

    def move(self, row_offset: int, col_offset: int):
        self.pivot.row += row_offset
        self.pivot.col += col_offset
        for pos in self.positions:
            pos.row += row_offset
            pos.col += col_offset


class I_Tetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        super().__init__()
        self.color = (0, 255, 255)
        self.pivot = Position(start_row, start_col + 1.5)
        self.initialize_positions()

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, round(self.pivot.col - 1.5)),
            Position(self.pivot.row, round(self.pivot.col - 0.5)),
            Position(self.pivot.row, round(self.pivot.col + 0.5)),
            Position(self.pivot.row, round(self.pivot.col + 1.5))
        ]


class O_Tetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        super().__init__()
        self.color = (255, 255, 0)
        self.pivot = Position(start_row + 0.5, start_col + 0.5)
        self.initialize_positions()

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row - 0.5, self.pivot.col - 0.5),
            Position(self.pivot.row - 0.5, self.pivot.col + 0.5),
            Position(self.pivot.row + 0.5, self.pivot.col - 0.5),
            Position(self.pivot.row + 0.5, self.pivot.col + 0.5)
        ]

    def rotate(self):
        pass


class TetrominoFactory:
    @staticmethod
    def create_random(start_row: int, start_col: int) -> Tetromino:
        tetrominoes: List[Type[Tetromino]] = [I_Tetromino, O_Tetromino]
        return random.choice(tetrominoes)(start_row, start_col)


class Renderer(ABC):
    @abstractmethod
    def render(self, grid: Grid, current_piece: Tetromino):
        pass


class PyGameRenderer(Renderer):
    def __init__(self, grid_rows: int, grid_cols: int, block_size: int, colors: Dict[str, Tuple[int, int, int]]):
        self.block_size = block_size
        self.colors = colors
        pygame.init()
        self.screen = pygame.display.set_mode((
            grid_cols * block_size,
            grid_rows * block_size
        ))
        pygame.display.set_caption("Tetris")

    def render(self, grid: Grid, current_piece: Tetromino):
        self.screen.fill(self.colors['background'])

        # Отрисовка сетки
        for row in range(grid.rows):
            for col in range(grid.cols):
                rect = pygame.Rect(
                    col * self.block_size,
                    row * self.block_size,
                    self.block_size,
                    self.block_size
                )
                pygame.draw.rect(self.screen, self.colors['grid'], rect, 1)

                if grid.grid[row][col]:
                    pygame.draw.rect(
                        self.screen,
                        grid.grid[row][col].color,
                        pygame.Rect(
                            col * self.block_size + 1,
                            row * self.block_size + 1,
                            self.block_size - 2,
                            self.block_size - 2
                        )
                    )

        # Отрисовка текущей фигуры
        for pos in current_piece.positions:
            if 0 <= pos.row < grid.rows and 0 <= pos.col < grid.cols:
                pygame.draw.rect(
                    self.screen,
                    current_piece.color,
                    pygame.Rect(
                        pos.col * self.block_size + 1,
                        pos.row * self.block_size + 1,
                        self.block_size - 2,
                        self.block_size - 2
                    )
                )

        pygame.display.flip()


class Game:
    def __init__(
            self,
            grid: Grid,
            renderer: Renderer,
            piece_factory: TetrominoFactory
    ):
        self.grid = grid
        self.renderer = renderer
        self.piece_factory = piece_factory
        self.current_piece: Optional[Tetromino] = None
        self.game_over = False
        self.score = 0

    def start(self):
        self._spawn_new_piece()
        clock = pygame.time.Clock()
        last_move_down = time.time()

        while not self.game_over:
            current_time = time.time()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self._try_move_piece(0, -1)
                    elif event.key == pygame.K_RIGHT:
                        self._try_move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self._rotate_piece()
                    elif event.key == pygame.K_DOWN:
                        self._try_move_piece(1, 0)

            # Автоматическое движение вниз
            if current_time - last_move_down > 0.5:
                self._update()
                last_move_down = current_time

            self.renderer.render(self.grid, self.current_piece)
            clock.tick(60)

    def _spawn_new_piece(self):
        start_row = 0
        start_col = self.grid.cols // 2
        self.current_piece = self.piece_factory.create_random(start_row, start_col)

        # Проверка коллизий при появлении
        if self._has_collision():
            self.game_over = True

    def _rotate_piece(self):
        original_positions = self.current_piece.positions.copy()
        original_pivot = Position(self.current_piece.pivot.row, self.current_piece.pivot.col)

        self.current_piece.rotate()

        if self._has_collision():
            self.current_piece.positions = original_positions
            self.current_piece.pivot = original_pivot

    def _update(self):
        if not self._try_move_piece(1, 0):
            self._lock_piece()
            lines = self.grid.clear_lines()
            self._update_score(lines)
            self._spawn_new_piece()

    def _try_move_piece(self, row_delta: int, col_delta: int) -> bool:
        original_positions = [Position(pos.row, pos.col) for pos in self.current_piece.positions]
        original_pivot = Position(self.current_piece.pivot.row, self.current_piece.pivot.col)

        self.current_piece.move(row_delta, col_delta)

        if self._has_collision():
            self.current_piece.positions = original_positions
            self.current_piece.pivot = original_pivot
            return False
        return True

    def _has_collision(self) -> bool:
        for pos in self.current_piece.positions:
            if not self.grid.is_valid_position(pos) or not self.grid.is_cell_empty(pos):
                return True
        return False

    def _lock_piece(self):
        for pos in self.current_piece.positions:
            if self.grid.is_valid_position(pos):
                self.grid.place_block(pos, Block(self.current_piece.color))

    def _update_score(self, lines_cleared: int):
        self.score += {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}.get(lines_cleared, 0)


# --------------------------------------------
# Запуск игры
# --------------------------------------------

if __name__ == "__main__":
    # Конфигурация
    GRID_ROWS = 20
    GRID_COLS = 10
    BLOCK_SIZE = 30
    COLORS = {
        'background': (0, 0, 0),
        'grid': (50, 50, 50),
        'I': (0, 255, 255),
        'O': (255, 255, 0),
    }

    # Инициализация компонентов
    grid = Grid(GRID_ROWS, GRID_COLS)
    renderer = PyGameRenderer(GRID_ROWS, GRID_COLS, BLOCK_SIZE, COLORS)
    factory = TetrominoFactory()

    # Запуск игры
    game = Game(grid, renderer, factory)
    game.start()