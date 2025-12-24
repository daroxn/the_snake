from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (0, 0, 0)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет камня
ROCK_COLOR = (128, 128, 128)

# Цвет неправильного корма
POISON_COLOR = (139, 0, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс для всех игровых объектов.

    Предоставляет общую функциональность для объектов на игровом поле,
    включая позиционирование и отрисовку.

    Attributes:
        position (tuple): Координаты объекта на игровом поле (x, y)
        body_color (tuple): Цвет объекта в формате RGB
    """

    def __init__(self) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """
        Метод для отрисовки объекта на экране.

        Рисует квадрат с заливкой основным цветом и границей.
        Может быть переопределен в дочерних классах
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """
        Метод установки случайного положения объекта на экране.

        Подбирает случайные координаты для положения объекта на экране.
        Может быть переопределен в дочерних классах
        """
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Apple(GameObject):
    """
    Класс, представляющий яблоко в игре.

    Яблоко является съедобным объектом, который увеличивает длину змейки
    при столкновении. Появляется в случайных позициях на игровом поле.

    Attributes:
        body_color (tuple): Цвет яблока (красный по умолчанию)
    """

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR


class Snake(GameObject):
    """
    Класс, представляющий змейку в игре.

    Управляется игроком с помощью клавиш стрелок. Растет при поедании яблок
    и завершает игру при столкновении с самой собой.

    Attributes:
        length (int): Текущая длина змейки
        positions (list): Список координат всех сегментов змейки
        direction (tuple): Текущее направление движения
        next_direction (tuple): Следующее направление движения (буферизация)
        body_color (tuple): Цвет змейки (зеленый по умолчанию)
        last (tuple): Координаты последнего удаленного сегмента
    """

    def __init__(self):
        super().__init__()
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """
        Обновляет направление движения змейки на основе буферизованного ввода.

        Если было задано следующее направление (next_direction), применяет его
        и очищает.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Перемещает змейку в текущем направлении.

        Вычисляет новую позицию головы, добавляет её в начало списка позиций
        Удаляет лишние сегменты в соответствии с текущей длиной змейки.
        """
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))

        while len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """
        Отрисовывает змейку на игровом поле.

        Рисует все сегменты змейки с заливкой и границей,
        а также затирает последний удаленный сегмент.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def change_length(self, delta) -> None:
        """Изменяет длину змейки на указанное значение."""
        self.length = max(1, self.length + delta)

    def reset(self):
        """Метод сброса змейки в случайную начальную позицию"""
        self.length = 1

        self.positions = [(
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )]
        self.direction = RIGHT
        self.next_direction = None

    @property
    def get_head_position(self):
        """Метод получения позиции головы змейки"""
        return self.positions[0]

    def get_collision(self, obj=None) -> bool:
        """Проверяет столкновение змейки с объектом или самой собой."""
        if obj:
            # Проверка столкновения с объектом
            return self.get_head_position == obj.position
        else:
            # Проверка столкновения с самой собой
            return self.get_head_position in self.positions[1:]


class Rock(GameObject):
    """
    Класс, представляющий камень в игре.

    Является препятствием размером в одну ячейку.
    При столкновении с камнем змейка принимает исходное состояние.
    Появляется в случайных позициях на игровом поле

    Attributes:
        body_color (tuple): Цвет яблока (красный по умолчанию)
    """

    def __init__(self):
        super().__init__()
        self.body_color = ROCK_COLOR


class Poison(GameObject):
    """
    Класс, представляющий несъедобный корм в игре.

    Является препятствием в виде треугольника, занимает одну ячейку.
    При столкновении с таким кормом змейка уменьшается на один сегмент.
    Появляется в случайных позициях на игровом поле

    Attributes:
        body_color (tuple): Цвет корма (фиолетовый по умолчанию)
    """

    def __init__(self):
        super().__init__()
        self.body_color = POISON_COLOR

    def draw(self):
        """Отрисовывает несъедобный корм на игровом поле."""
        x, y = self.position
        points = [
            (x + GRID_SIZE // 2, y),
            (x, y + GRID_SIZE),
            (x + GRID_SIZE, y + GRID_SIZE)
        ]
        pygame.draw.polygon(screen, self.body_color, points)
        pygame.draw.polygon(screen, BORDER_COLOR, points, 1)


def handle_keys(game_object) -> None:
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Функция запуска игры"""
    pygame.init()

    apple = Apple()
    snake = Snake()
    rock = Rock()
    poison = Poison()
    apple.randomize_position()
    rock.randomize_position()
    poison.randomize_position()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка столкновения с яблоком
        if snake.get_collision(apple):
            snake.change_length(1)
            apple.randomize_position()

        # Проверка столкновения с ядом
        if snake.get_collision(poison):
            snake.change_length(-1)
            poison.randomize_position()

        # Проверка столкновения с самой собой
        if snake.get_collision() or snake.get_collision(rock):
            snake.reset()
            apple.randomize_position()
            rock.randomize_position()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        rock.draw()
        poison.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
