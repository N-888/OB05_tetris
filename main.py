from abc import ABC, abstractmethod
import random
import pygame
import time
from typing import List, Tuple, Dict, Optional, Type

# ----- Основные структуры -----

class Position:
    def __init__(self, row: int, col: int):
        self.row = row  # строка на поле
        self.col = col  # столбец на поле

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

class Block:
    def __init__(self, color: Tuple[int, int, int]):
        self.color = color  # цвет блока

class GameGrid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows  # количество строк
        self.cols = cols  # количество столбцов
        # клетки, None если пусто, Block если занято
        self.cells: List[List[Optional[Block]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]

    def is_valid_position(self, position: Position) -> bool:
        # проверка: внутри границ
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_cell_empty(self, position: Position) -> bool:
        # проверка: валидно И пусто
        return self.is_valid_position(position) and self.cells[position.row][position.col] is None

    def place_block(self, position: Position, block: Block):
        # размещение блока, если валидно
        if self.is_valid_position(position):
            self.cells[position.row][position.col] = block

    def clear_lines(self) -> int:
        # удаление полных строк, возвращает сколько суммарно строк удалено
        lines_cleared = 0
        row = self.rows - 1
        # идём снизу вверх
        while row >= 0:
            if all(cell is not None for cell in self.cells[row]):
                # строка полная
                lines_cleared += 1
                # перемещаем всё вниз
                for r in range(row, 0, -1):
                    self.cells[r] = self.cells[r - 1][:]
                # первая строка пуста
                self.cells[0] = [None] * self.cols
                # не двигаем row, проверяем новую строку на этой позиции
            else:
                row -= 1
        return lines_cleared

# ----- Фигуры -----

class Tetromino(ABC):
    def __init__(self, start_row: int, start_col: int):
        self.pivot = Position(start_row, start_col)
        self.positions: List[Position] = []
        self._color: Tuple[int, int, int] = (0, 0, 0)
        self.initialize_positions()  # задаём начальные позиции

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color

    @abstractmethod
    def initialize_positions(self):
        pass

    def rotate(self):
        # вращение относительно pivot (классика)
        new_positions = []
        for pos in self.positions:
            row_offset = pos.row - self.pivot.row
            col_offset = pos.col - self.pivot.col
            new_row = self.pivot.row - col_offset
            new_col = self.pivot.col + row_offset
            new_positions.append(Position(int(new_row), int(new_col)))
        self.positions = new_positions

    def move(self, row_offset: int, col_offset: int):
        # сдвиг фигуры и pivot
        self.pivot.row += row_offset
        self.pivot.col += col_offset
        for pos in self.positions:
            pos.row += row_offset
            pos.col += col_offset

class ITetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 255, 255)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 2),
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
        ]

class OTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 255, 0)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col + 1),
        ]

    def rotate(self):
        # квадрат не вращаем
        pass

class TTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (128, 0, 128)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col),
        ]

class STetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 255, 0)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col - 1),
            Position(self.pivot.row + 1, self.pivot.col),
        ]

class ZTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 0, 0)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col),
            Position(self.pivot.row + 1, self.pivot.col + 1),
        ]

class JTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (0, 0, 255)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col + 1),
        ]

class LTetromino(Tetromino):
    def __init__(self, start_row: int, start_col: int):
        self._color = (255, 165, 0)
        super().__init__(start_row, start_col)

    def initialize_positions(self):
        # В классическом виде L: коромысло внизу справа
        self.positions = [
            Position(self.pivot.row, self.pivot.col - 1),
            Position(self.pivot.row, self.pivot.col),
            Position(self.pivot.row, self.pivot.col + 1),
            Position(self.pivot.row + 1, self.pivot.col + 1),
        ]

class TetrominoFactory:
    @staticmethod
    def create_random(start_row: int, start_col: int) -> Tetromino:
        types: List[Type[Tetromino]] = [
            ITetromino, OTetromino, TTetromino,
            STetromino, ZTetromino, JTetromino, LTetromino
        ]
        return random.choice(types)(start_row, start_col)

# ----- Рендеринг через pygame -----

class Renderer(ABC):
    @abstractmethod
    def render(self, grid: GameGrid, current_piece: Optional[Tetromino], score: int, paused: bool):
        pass

class PyGameRenderer(Renderer):
    def __init__(self, grid_rows: int, grid_cols: int, block_size: int, colors: Dict[str, Tuple[int,int,int]]):
        self.block_size = block_size
        self.colors = colors
        pygame.init()
        # инициализируем окно
        self.screen = pygame.display.set_mode((grid_cols * block_size, grid_rows * block_size + 40))
        pygame.display.set_caption("Tetris")
        self.font = pygame.font.SysFont("Arial", 24)  # шрифт для очков

    def render(self, grid: GameGrid, current_piece: Optional[Tetromino], score: int, paused: bool):
        # фон
        self.screen.fill(self.colors['background'])

        # отрисовка сетки + уже упавших блоков
        for r in range(grid.rows):
            for c in range(grid.cols):
                rect = pygame.Rect(c*self.block_size, r*self.block_size, self.block_size, self.block_size)
                pygame.draw.rect(self.screen, self.colors['grid'], rect, 1)
                block = grid.cells[r][c]
                if block is not None:
                    pygame.draw.rect(self.screen, block.color,
                                     pygame.Rect(c*self.block_size+1, r*self.block_size+1,
                                                 self.block_size-2, self.block_size-2))

        # отрисовка текущей блок-составляющей
        if current_piece:
            for pos in current_piece.positions:
                if 0 <= pos.row < grid.rows and 0 <= pos.col < grid.cols:
                    pygame.draw.rect(self.screen, current_piece.color,
                                     pygame.Rect(pos.col*self.block_size+1, pos.row*self.block_size+1,
                                                 self.block_size-2, self.block_size-2))

        # вывод очков
        score_surf = self.font.render(f"Score: {score}", True, (255,255,255))
        self.screen.blit(score_surf, (5, grid.rows*self.block_size + 5))

        # если на паузе — надпись
        if paused:
            pause_surf = self.font.render("PAUSED", True, (255,0,0))
            rect = pause_surf.get_rect(center=(grid.cols*self.block_size//2, grid.rows*self.block_size//2))
            self.screen.blit(pause_surf, rect)

        pygame.display.flip()

# ----- Логика игры -----

class TetrisGame:
    def __init__(self, grid: GameGrid, renderer: Renderer, factory: TetrominoFactory):
        self.grid = grid
        self.renderer = renderer
        self.factory = factory
        self.current_piece: Optional[Tetromino] = None
        self.game_over = False
        self.score = 0
        self.fall_speed = 0.5
        self.last_move_down = time.time()
        self.paused = False

    def start(self):
        self._spawn_new_piece()
        clock = pygame.time.Clock()

        while not self.game_over:
            now = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # пауза
                        self.paused = not self.paused
                    if not self.paused:
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

            if not self.paused and now - self.last_move_down > self.fall_speed:
                self._update()
                self.last_move_down = now

            self.renderer.render(self.grid, self.current_piece, self.score, self.paused)
            clock.tick(60)

        pygame.quit()

    def _spawn_new_piece(self):
        start_c = self.grid.cols // 2 - 1
        self.current_piece = self.factory.create_random(0, start_c)
        if self._has_collision():
            self.game_over = True

    def _rotate_piece(self):
        if not self.current_piece:
            return
        original = [Position(p.row, p.col) for p in self.current_piece.positions]
        pivot_orig = Position(self.current_piece.pivot.row, self.current_piece.pivot.col)
        self.current_piece.rotate()
        if self._has_collision():
            self.current_piece.positions = original
            self.current_piece.pivot = pivot_orig

    def _hard_drop(self):
        while self._try_move_piece(1,0):
            pass

    def _update(self):
        if not self._try_move_piece(1,0):
            self._lock_piece()
            lines = self.grid.clear_lines()
            self._update_score(lines)
            self._spawn_new_piece()

    def _try_move_piece(self, dr: int, dc: int) -> bool:
        if not self.current_piece:
            return False
        orig_pos = [Position(p.row, p.col) for p in self.current_piece.positions]
        orig_pivot = Position(self.current_piece.pivot.row, self.current_piece.pivot.col)
        self.current_piece.move(dr, dc)
        if self._has_collision():
            self.current_piece.positions = orig_pos
            self.current_piece.pivot = orig_pivot
            return False
        return True

    def _has_collision(self) -> bool:
        if not self.current_piece:
            return True
        for p in self.current_piece.positions:
            if not self.grid.is_valid_position(p) or not self.grid.is_cell_empty(p):
                return True
        return False

    def _lock_piece(self):
        if not self.current_piece:
            return
        for p in self.current_piece.positions:
            if self.grid.is_valid_position(p):
                self.grid.place_block(p, Block(self.current_piece.color))
        self.current_piece = None

    def _update_score(self, lines: int):
        self.score += {0:0,1:100,2:300,3:500,4:800}[lines]
        # ускорение после каждых 5 очков
        if self.score % 500 == 0:
            self.fall_speed = max(0.05, self.fall_speed - 0.05)

# ----- Точка входа -----

if __name__ == "__main__":
    GRID_ROWS, GRID_COLS = 20, 10
    BLOCK_SIZE = 30
    COLORS = {
        'background': (0,0,0),
        'grid': (50,50,50),
        'I': (0,255,255), 'O': (255,255,0), 'T': (128,0,128),
        'S': (0,255,0), 'Z': (255,0,0), 'J': (0,0,255), 'L': (255,165,0),
    }

    grid = GameGrid(GRID_ROWS, GRID_COLS)
    renderer = PyGameRenderer(GRID_ROWS, GRID_COLS, BLOCK_SIZE, COLORS)
    factory = TetrominoFactory()
    game = TetrisGame(grid, renderer, factory)
    game.start()
