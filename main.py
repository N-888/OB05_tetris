from abc import ABC, abstractmethod
import random
import pygame
import time
from typing import List, Tuple, Dict, Optional


# --------------------------------------------
# Принцип единственной ответственности (SRP)
# --------------------------------------------

class Position:
    """Хранит координаты позиции"""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col


class Block:
    """Представляет один блок фигуры"""

    def __init__(self, color: Tuple[int, int, int]):
        self.color = color


class Grid:
    """Управляет игровым полем"""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def is_valid_position(self, position: Position) -> bool:
        """Проверяет, находится ли позиция в пределах поля"""
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_cell_empty(self, position: Position) -> bool:
        """Проверяет, пуста ли клетка"""
        return self.grid[position.row][position.col] is None

    def place_block(self, position: Position, block: Block):
        """Помещает блок на поле"""
        self.grid[position.row][position.col] = block

    def clear_lines(self) -> int:
        """Удаляет заполненные линии и возвращает количество удалённых"""
        lines_cleared = 0
        for row in range(self.rows):
            if all(self.grid[row]):
                lines_cleared += 1
                del self.grid[row]
                self.grid.insert(0, [None for _ in range(self.cols)])
        return lines_cleared


# --------------------------------------------
# Принцип открытости/закрытости (OCP) и LSP
# --------------------------------------------

class Tetromino(ABC):
    """Абстрактный класс для всех тетромино"""

    def __init__(self):
        self.blocks: List[Block] = []
        self.positions: List[Position] = []
        self.pivot = Position(0, 0)
        self.color: Tuple[int, int, int]

    @abstractmethod
    def initialize_positions(self):
        pass

    def rotate(self):
        """Поворот фигуры вокруг pivot"""
        new_positions = []
        for pos in self.positions:
            # Матрица поворота 90° по часовой стрелке
            row_offset = pos.row - self.pivot.row
            col_offset = pos.col - self.pivot.col
            new_row = self.pivot.row - col_offset
            new_col = self.pivot.col + row_offset
            new_positions.append(Position(new_row, new_col))
        self.positions = new_positions

    def move(self, row_offset: int, col_offset: int):
        """Смещение фигуры"""
        self.pivot.row += row_offset
        self.pivot.col += col_offset
        for pos in self.positions:
            pos.row += row_offset
            pos.col += col_offset


# Конкретные реализации фигур
class I_Tetromino(Tetromino):
    def __init__(self):
        super().__init__()
        self.color = (0, 255, 255)  # Cyan
        self.initialize_positions()

    def initialize_positions(self):
        self.positions = [
            Position(0, 0), Position(0, 1),
            Position(0, 2), Position(0, 3)
        ]
        self.pivot = Position(0, 1.5)


class O_Tetromino(Tetromino):
    def __init__(self):
        super().__init__()
        self.color = (255, 255, 0)  # Yellow
        self.initialize_positions()

    def initialize_positions(self):
        self.positions = [
            Position(0, 0), Position(0, 1),
            Position(1, 0), Position(1, 1)
        ]
        self.pivot = Position(0.5, 0.5)

    def rotate(self):
        pass  # Квадрат не вращается


# Аналогично реализуются T, S, Z, J, L

# --------------------------------------------
# Принцип подстановки Барбары Лисков (LSP)
# --------------------------------------------

class TetrominoFactory:
    """Создает фигуры, заменяемые через базовый класс"""

    @staticmethod
    def create_random() -> Tetromino:
        tetrominoes = [I_Tetromino, O_Tetromino]  # + другие фигуры
        return random.choice(tetrominoes)()


# --------------------------------------------
# Принцип разделения интерфейса (ISP)
# --------------------------------------------

class Renderer(ABC):
    """Абстракция для отрисовки"""

    @abstractmethod
    def render(self, grid: Grid, current_piece: Tetromino):
        pass


class PyGameRenderer(Renderer):
    """Реализация отрисовки через PyGame"""

    def __init__(self, block_size: int, colors: Dict[str, Tuple[int, int, int]]):
        self.block_size = block_size
        self.colors = colors
        pygame.init()
        self.screen = pygame.display.set_mode((
            grid.cols * block_size,
            grid.rows * block_size
        ))

    def render(self, grid: Grid, current_piece: Tetromino):
        self.screen.fill(self.colors['background'])
        # Отрисовка сетки и фигур
        # ...
        pygame.display.flip()


# --------------------------------------------
# Принцип инверсии зависимостей (DIP)
# --------------------------------------------

class Game:
    """Управление игровой логикой"""

    def __init__(
            self,
            grid: Grid,
            renderer: Renderer,
            piece_factory: TetrominoFactory
    ):
        self.grid = grid
        self.renderer = renderer
        self.piece_factory = piece_factory
        self.current_piece = None
        self.game_over = False
        self.score = 0

    def start(self):
        """Запуск игрового цикла"""
        self._spawn_new_piece()
        while not self.game_over:
            self._handle_input()
            self._update()
            self.renderer.render(self.grid, self.current_piece)
            time.sleep(0.3)

    def _spawn_new_piece(self):
        self.current_piece = self.piece_factory.create_random()
        # Проверка коллизий при появлении

    def _handle_input(self):
        # Обработка клавиатуры
        pass

    def _update(self):
        """Обновление игрового состояния"""
        if not self._try_move_piece(1, 0):
            self._lock_piece()
            lines = self.grid.clear_lines()
            self._update_score(lines)
            self._spawn_new_piece()

    def _try_move_piece(self, row_delta: int, col_delta: int) -> bool:
        """Пытается переместить фигуру, возвращает успех"""
        # Сохраняем исходные позиции
        original_positions = self.current_piece.positions.copy()

        # Пробуем переместить
        self.current_piece.move(row_delta, col_delta)

        # Проверяем коллизии
        if self._has_collision():
            # Откатываем при коллизии
            self.current_piece.positions = original_positions
            return False
        return True

    def _has_collision(self) -> bool:
        """Проверяет коллизии текущей фигуры"""
        for pos in self.current_piece.positions:
            if (
                    not self.grid.is_valid_position(pos) or
                    not self.grid.is_cell_empty(pos)
            ):
                return True
        return False

    def _lock_piece(self):
        """Фиксирует фигуру на поле"""
        for pos in self.current_piece.positions:
            self.grid.place_block(pos, Block(self.current_piece.color))

    def _update_score(self, lines_cleared: int):
        """Обновление счёта"""
        self.score += {1: 100, 2: 300, 3: 500, 4: 800}.get(lines_cleared, 0)


# --------------------------------------------
# Конфигурация и запуск
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
        # ... другие цвета
    }

    # Инициализация компонентов
    grid = Grid(GRID_ROWS, GRID_COLS)
    renderer = PyGameRenderer(BLOCK_SIZE, COLORS)
    factory = TetrominoFactory()

    # Запуск игры
    game = Game(grid, renderer, factory)
    game.start()
