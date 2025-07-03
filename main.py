# Импортируем необходимые модули
import pygame  # библиотека для работы с графикой и звуком
import random  # для случайного выбора фигур

# Инициализируем Pygame
pygame.init()

# Устанавливаем размеры игрового окна
WINDOW_WIDTH = 300  # ширина окна в пикселях
WINDOW_HEIGHT = 600  # высота окна в пикселях
BLOCK_SIZE = 30  # размер одного блока фигурки в пикселях

# Устанавливаем размеры игрового поля в блоках
COLUMNS = WINDOW_WIDTH // BLOCK_SIZE  # количество столбцов
ROWS = WINDOW_HEIGHT // BLOCK_SIZE  # количество строк

# Задаём цвета RGB (красный, зелёный, синий)
BLACK = (0, 0, 0)        # чёрный цвет
WHITE = (255, 255, 255)  # белый цвет
GRAY = (128, 128, 128)   # серый цвет
RED = (255, 0, 0)        # красный для фигурок
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Список возможных цветов фигур
colors = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

# Определяем все возможные формы фигур и их повороты
SHAPES = [
    [[1, 1, 1, 1]],  # I

    [[1, 1],
     [1, 1]],        # O

    [[0, 1, 0],
     [1, 1, 1]],     # T

    [[1, 0, 0],
     [1, 1, 1]],     # J

    [[0, 0, 1],
     [1, 1, 1]],     # L

    [[0, 1, 1],
     [1, 1, 0]],     # S

    [[1, 1, 0],
     [0, 1, 1]]      # Z
]

# Функция для создания новой случайной фигурки
def get_new_piece():
    shape = random.choice(SHAPES)  # случайная форма
    color = random.choice(colors)  # случайный цвет
    x = COLUMNS // 2 - len(shape[0]) // 2  # центрируем по горизонтали
    y = 0  # старт сверху
    return {'shape': shape, 'color': color, 'x': x, 'y': y}

# Функция для создания пустого игрового поля
def create_grid():
    return [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

# Функция для отрисовки игрового поля, фигур и сетки
def draw_window(surface, grid, score, paused):
    surface.fill(BLACK)  # заливаем фон чёрным

    # Рисуем каждый блок на игровом поле
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x],
                             (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Рисуем сетку поверх блоков
    for x in range(COLUMNS):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, WINDOW_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (WINDOW_WIDTH, y * BLOCK_SIZE))

    # Отображаем счёт
    font = pygame.font.SysFont('arial', 24)
    score_text = font.render(f'Очки: {score}', True, WHITE)
    surface.blit(score_text, (10, 10))

    # Если игра на паузе — выводим сообщение
    if paused:
        pause_text = font.render('Пауза', True, YELLOW)
        surface.blit(pause_text, (WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - 20))

    pygame.display.update()  # обновляем экран

# Функция для отображения текущей фигурки
def draw_piece(surface, piece):
    shape = piece['shape']
    color = piece['color']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, color,
                                 ((piece['x'] + x) * BLOCK_SIZE, (piece['y'] + y) * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 0)

# Проверка, можно ли разместить фигурку на позиции
def valid_space(piece, grid):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece['x'] + x
                new_y = piece['y'] + y
                if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != BLACK:
                    return False
    return True

# Закрепляем упавшую фигурку на поле
def lock_piece(grid, piece):
    shape = piece['shape']
    color = piece['color']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[piece['y'] + y][piece['x'] + x] = color

# Проверяем заполненные линии и убираем их
def clear_lines(grid):
    lines_cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            del grid[i]  # удаляем заполненную строку
            grid.insert(0, [BLACK for _ in range(COLUMNS)])  # добавляем пустую сверху
            lines_cleared += 1
    return lines_cleared

# Основная функция игры
def main():
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # создаём окно
    pygame.display.set_caption("Тетрис от Natali")  # заголовок окна

    clock = pygame.time.Clock()  # для управления FPS
    grid = create_grid()  # создаём игровое поле
    current_piece = get_new_piece()  # текущая фигурка
    fall_time = 0  # время падения
    fall_speed = 0.5  # скорость падения фигур (секунд)
    score = 0  # начальный счёт
    paused = False  # флаг паузы

    running = True
    while running:
        fall_time += clock.get_rawtime() / 1000  # сколько времени прошло с прошлого кадра
        clock.tick(60)  # ограничиваем FPS

        # Обработка событий клавиатуры и выхода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # пауза
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece['x'] -= 1
                        if not valid_space(current_piece, grid):
                            current_piece['x'] += 1
                    if event.key == pygame.K_RIGHT:
                        current_piece['x'] += 1
                        if not valid_space(current_piece, grid):
                            current_piece['x'] -= 1
                    if event.key == pygame.K_DOWN:
                        current_piece['y'] += 1
                        if not valid_space(current_piece, grid):
                            current_piece['y'] -= 1
                    if event.key == pygame.K_UP:
                        # Поворот фигурки
                        rotated_shape = list(zip(*current_piece['shape'][::-1]))
                        old_shape = current_piece['shape']
                        current_piece['shape'] = rotated_shape
                        if not valid_space(current_piece, grid):
                            current_piece['shape'] = old_shape

        if not paused:
            # Двигаем фигурку вниз с заданной скоростью
            if fall_time > fall_speed:
                fall_time = 0
                current_piece['y'] += 1
                if not valid_space(current_piece, grid):
                    current_piece['y'] -= 1
                    lock_piece(grid, current_piece)
                    lines = clear_lines(grid)
                    score += lines * 100  # начисляем очки
                    current_piece = get_new_piece()
                    if not valid_space(current_piece, grid):
                        print("Игра окончена!")
                        running = False

        # Отрисовка окна, фигурки и поля
        draw_window(win, grid, score, paused)
        draw_piece(win, current_piece)
        pygame.display.update()

    pygame.quit()

# Запуск игры
if __name__ == "__main__":
    main()
