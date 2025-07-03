from abc import ABC, abstractmethod
import random
import pygame
import time
from typing import List, Tuple, Dict, Optional, Type


class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col


class Block:
    def __init__(self, color: Tuple[int, int, int]):
        self.color = color


class GameGrid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.cells = [[None for _ in range(cols)] for _ in range(rows)]

    def is_valid_position(self, position: Position) -> bool:
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_cell_empty(self, position: Position) -> bool:
        return self.is_valid_position(position) and self.cells[position.row][position.col] is None

    def place_block(self, position: Position, block: Block):
        if self.is_valid_position(position):
            self.cells[position.row][position.col] = block

    def clear_lines(self) -> int:
        lines_cleared = 0
        row = self.rows - 1
        while row >= 0:
            if all(self.cells[row]):
                lines_cleared += 1
                for r in range(row, 0, -1):
                    self.cells[r] = self.cells[r - 1][:]
                self.cells[0] = [None] * self.cols
            else:
                row -= 1
        return lines_cleared


class Tetromino(ABC):
    def __init__(self, start_row: int, start_col: int):
        self.positions: List[Position] = []
        self.pivot = Position(start_row, start_col)
        self._color: Tuple[int, int, int] = (0, 0, 0)
        self.initialize_positions()

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color

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
            new_positions.append(Position(int(new_row), int(new_col)))
        self.positions = new_positions

    def move(self, row_offset: int, col_offset: int):
        self.pivot.row += row_offset
        self.pivot.col += col_offset
        for pos in self.positions:
            pos.row += row_offset
            pos.col += col_offset


class ITetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 255, 255)  # Cyan
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 2),
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1)
        ]


class OTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 255, 0)  # Yellow
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col + 1)
        ]

    def rotate(self):
        pass  # Квадрат не вращается


class TTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (128, 0, 128)  # Purple
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col)
        ]


class STetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 255, 0)  # Green
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col - 1),
            Position(self.pivot.row + 1, self.pivot.col)
        ]


class ZTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 0, 0)  # Red
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col + 1)
        ]


class JTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 0, 255)  # Blue
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col + 1)
        ]


class LTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 165, 0)  # Orange
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col - 1)
        ]


class TetrominoFactory:
    @staticmethod
    def create_random(start_row: int, start_col: int) -> Tetromino:
        tetrominoes: List[Type[Tetromino]] = [
            ITetromino, OTetromino, TTetromino,
            STetromino, ZTetromino, JTetromino, LTetromino
        ]
        return random.choice(tetrominoes)(start_row, start_col)


class Renderer(ABC):
    @abstractmethod
    def render(self, grid: GameGrid, current_piece: Tetromino):
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

    def render(self, grid: GameGrid, current_piece: Tetromino):
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

                cell = grid.cells[row][col]
                if cell is not None:
                    pygame.draw.rect(
                        self.screen,
                        cell.color,
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


class TetrisGame:
    def __init__(
            self,
            grid: GameGrid,
            renderer: Renderer,
            piece_factory: TetrominoFactory
    ):
        self.grid = grid
        self.renderer = renderer
        self.piece_factory = piece_factory
        self.current_piece: Optional[Tetromino] = None
        self.game_over = False
        self.score = 0
        self.fall_speed = 0.5  # seconds per row
        self.last_move_down = time.time()

    def start(self):
        self._spawn_new_piece()
        clock = pygame.time.Clock()

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
                    elif event.key == pygame.K_SPACE:
                        self._hard_drop()

            # Автоматическое движение вниз
            if current_time - self.last_move_down > self.fall_speed:
                self._update()
                self.last_move_down = current_time

            self.renderer.render(self.grid, self.current_piece)
            clock.tick(60)

        pygame.quit()

    def _spawn_new_piece(self):
        start_row = 0
        start_col = self.grid.cols // 2 - 1
        self.current_piece = self.piece_factory.create_random(start_row, start_col)

        # Проверка коллизий при появлении
        if self._has_collision():
            self.game_over = True

    def _rotate_piece(self):
        original_positions = [Position(pos.row, pos.col) for pos in self.current_piece.positions]
        original_pivot = Position(self.current_piece.pivot.row, self.current_piece.pivot.col)

        self.current_piece.rotate()

        if self._has_collision():
            self.current_piece.positions = original_positions
            self.current_piece.pivot = original_pivot

    def _hard_drop(self):
        while self._try_move_piece(1, 0):
            pass

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
        # Увеличиваем скорость с ростом счета
        self.fall_speed = max(0.05, 0.5 - self.score * 0.0001)


if __name__ == "__main__":
    # Конфигурация
    GRID_ROWS = 20
    GRID_COLS = 10
    BLOCK_SIZE = 30
    COLOR_SCHEME = {
        'background': (0, 0, 0),
        'grid': (50, 50, 50),
        'I': (0, 255, 255),  # Cyan
        'O': (255, 255, 0),  # Yellow
        'T': (128, 0, 128),  # Purple
        'S': (0, 255, 0),  # Green
        'Z': (255, 0, 0),  # Red
        'J': (0, 0, 255),  # Blue
        'L': (255, 165, 0),  # Orange
    }

    # Инициализация компонентов
    game_grid = GameGrid(GRID_ROWS, GRID_COLS)
    game_renderer = PyGameRenderer(GRID_ROWS, GRID_COLS, BLOCK_SIZE, COLOR_SCHEME)
    tetromino_factory = TetrominoFactory()

    # Запуск игры
    tetris_game = TetrisGame(game_grid, game_renderer, tetromino_factory)
    tetris_game.start()