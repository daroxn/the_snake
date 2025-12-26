from random import randint
from typing import Dict, List, Optional, Tuple

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION: Tuple[int, int] = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# Вариации поворотов
DIRECTIONS: Dict[Tuple[int, Tuple[int, int]], Tuple[int, int]] = {
    (pygame.K_UP, UP): UP,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,

    (pygame.K_DOWN, DOWN): DOWN,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,

    (pygame.K_LEFT, LEFT): LEFT,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,

    (pygame.K_RIGHT, RIGHT): RIGHT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR: Tuple[int, int, int] = (0, 0, 0)

# Цвет яблока
APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)

# Цвет камня
ROCK_COLOR: Tuple[int, int, int] = (128, 128, 128)

# Цвет неправильного корма
POISON_COLOR: Tuple[int, int, int] = (139, 0, 255)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Определяет все игровые объекты.

    Предоставляет общую функциональность для объектов на игровом поле,
    включая позиционирование и отрисовку.

    Attributes:
        position (tuple): Координаты объекта на игровом поле (x, y)
        body_color (tuple): Цвет объекта в формате RGB
    """

    def __init__(self, body_color=None) -> None:
        self.position: Tuple[int, int] = CENTER_POSITION
        self.body_color: Tuple[int, int, int] = body_color

    def draw(self) -> None:
        """Отрисовывает объект на экране.

        Рисует квадрат с заливкой основным цветом и границей.
        Может быть переопределен в дочерних классах
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко в игре.

    Съедобный объект, который увеличивает длину змейки
    при столкновении. Появляется в случайных позициях на игровом поле.

    Attributes:
        body_color (tuple): Цвет яблока (красный по умолчанию)
    """

    def __init__(
            self,
            body_color: Tuple[int, int, int] = APPLE_COLOR,
            occupied: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        super().__init__(body_color)
        self.randomize_position(occupied)

    def randomize_position(
            self,
            occupied: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """Устанавливает случайное положение яблока на экране.

        Подбирает случайные координаты для положения яблока на экране.
        Гарантирует, что яблоко не появится на занятых позициях.
        """
        if occupied is None:
            occupied = [CENTER_POSITION]

        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in occupied:
                self.position = new_position
                break


class Snake(GameObject):
    """Змейка в игре.

    Управляется игроком с помощью клавиш стрелок. Растет при поедании яблок
    и завершает игру при столкновении с самой собой.

    Attributes:
        length (int): Текущая длина змейки
        positions (list): Список координат всех сегментов змейки
        direction (tuple): Текущее направление движения
        next_direction (tuple): Следующее направление движения
        body_color (tuple): Цвет змейки (зеленый по умолчанию)
        last (tuple): Координаты последнего удаленного сегмента
    """

    def __init__(self, body_color: Tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.length: int
        self.positions: List[Tuple[int, int]]
        self.direction: Tuple[int, int]
        self.next_direction: Optional[Tuple[int, int]]
        self.last: List[Tuple[int, int]]
        self.reset()
        self.positions = [CENTER_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.last = []

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Перемещает змейку в текущем направлении.

        Вычисляет новую позицию головы, добавляет её в начало списка позиций
        Удаляет лишние сегменты в соответствии с текущей длиной змейки.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))

        self.last = []
        while len(self.positions) > self.length:
            self.last.append(self.positions.pop())

    def draw(self) -> None:
        """Отрисовывает змейку на игровом поле.

        Рисует все сегменты змейки с заливкой и границей,
        а также затирает последний удаленный сегмент.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(
            self.get_head_position(), (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            for pos in self.last:
                pygame.draw.rect(
                    screen,
                    BOARD_BACKGROUND_COLOR,
                    pygame.Rect(pos, (GRID_SIZE, GRID_SIZE))
                )

    def change_length(self, delta: int) -> None:
        """Изменяет длину змейки на указанное значение."""
        self.length = max(1, self.length + delta)

    def reset(self) -> None:
        """Сбрасывает змейку в случайную начальную позицию"""
        self.length = 1

        self.positions = [(
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )]
        self.direction = RIGHT
        self.next_direction = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки"""
        return self.positions[0]

    def get_collision(self, obj: Optional['GameObject'] = None) -> bool:
        """Проверяет столкновение змейки с объектом или самой собой."""
        if obj:
            return self.get_head_position() == obj.position
        else:
            return self.get_head_position() in self.positions[1:]


class Rock(GameObject):
    """Камень в игре.

    Препятствие размером в одну ячейку.
    При столкновении с камнем змейка принимает исходное состояние.
    Появляется в случайных позициях на игровом поле

    Attributes:
        body_color (tuple): Цвет яблока (красный по умолчанию)
    """

    def __init__(
            self,
            body_color: Tuple[int, int, int] = ROCK_COLOR
    ) -> None:
        super().__init__(body_color)
        self.position: Tuple[int, int] = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Poison(GameObject):
    """Несъедобный корм в игре.

    Препятствие в виде треугольника, занимает одну ячейку.
    При столкновении с таким кормом змейка уменьшается на один сегмент.
    Появляется в случайных позициях на игровом поле

    Attributes:
        body_color (tuple): Цвет корма (фиолетовый по умолчанию)
    """

    def __init__(
            self,
            body_color: Tuple[int, int, int] = POISON_COLOR
    ) -> None:
        super().__init__(body_color)
        self.position: Tuple[int, int] = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self) -> None:
        """Отрисовывает несъедобный корм на игровом поле."""
        x, y = self.position
        points = [
            (x + GRID_SIZE // 2, y),
            (x, y + GRID_SIZE),
            (x + GRID_SIZE, y + GRID_SIZE)
        ]
        pygame.draw.polygon(screen, self.body_color, points)
        pygame.draw.polygon(screen, BORDER_COLOR, points, 1)


def handle_keys(game_object: 'Snake') -> None:
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            new_direction = DIRECTIONS.get((event.key, game_object.direction))
            if new_direction is not None:
                game_object.next_direction = new_direction


def main() -> None:
    """Запускает игру"""
    pygame.init()

    apple = Apple()
    snake = Snake()
    rock = Rock()
    poison = Poison()
    screen.fill(BOARD_BACKGROUND_COLOR)
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_collision(apple):
            snake.change_length(1)
            apple.randomize_position(snake.positions)

        if snake.get_collision(poison):
            snake.change_length(-1)

        if snake.get_collision() or snake.get_collision(rock):
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        rock.draw()
        poison.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
