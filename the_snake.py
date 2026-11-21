"""Классическая игра «Змейка» на Pygame."""

from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)
KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игровых объектов с позицией и цветом."""

    def __init__(self, position=CENTER, body_color=None):
        """Создать объект в указанной позиции."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Определить интерфейс отрисовки для дочерних классов."""
        pass

    def draw_cell(self, position, color):
        """Нарисовать одну клетку игрового поля."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко, возникающее на свободной клетке поля."""

    def __init__(self, occupied=None):
        """Создать яблоко и выбрать для него позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=None):
        """Выбрать случайную клетку вне занятых змейкой."""
        free_cells = ALL_CELLS - set(occupied or ())
        self.position = choice(tuple(free_cells)) if free_cells else None

    def draw(self):
        """Нарисовать яблоко на игровом поле."""
        if self.position is not None:
            self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка, умеющая перемещаться, расти и начинать заново."""

    def __init__(self):
        """Создать змейку длиной в одну клетку."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()
        self.direction = RIGHT

    def update_direction(self):
        """Применить направление, выбранное игроком."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Сместить голову на клетку, при необходимости удалив хвост."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        self.position = new_head

    def draw(self):
        """Нарисовать сегменты змейки и удалить старый хвост."""
        if self.last is not None and self.last not in self.positions:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        for position in self.positions:
            self.draw_cell(position, self.body_color)

    def reset(self):
        """Сбросить длину и положение, выбрав новое направление."""
        self.length = 1
        self.position = CENTER
        self.positions = [CENTER]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать выход из игры и изменение направления."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            direction = KEY_DIRECTIONS.get(event.key)
            if direction is None:
                continue
            opposite = (-game_object.direction[0],
                        -game_object.direction[1])
            if direction != opposite:
                game_object.next_direction = direction


def main():
    """Запустить игру и обновлять её состояние каждый кадр."""
    pygame.init()
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple(snake.positions)
    record = 1

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        elif head == apple.position:
            snake.length += 1
            record = max(record, snake.length)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pygame.display.set_caption(f'Змейка | Рекорд: {record}')
        pygame.display.update()


if __name__ == '__main__':
    main()
