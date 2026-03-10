import pygame
from pathlib import Path
import sys

pygame.init()


# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()    
FPS = 70
PADDLE_HITBOX_PAD_X = 10
PADDLE_HITBOX_PAD_Y = 6
BALL_HIT_COOLDOWN_MS = 90
GAME_START_FREEZE_MS = 6000
BALL_FREEZE_AFTER_SCORE_MS = 1200
BALL_NORMAL_SPEED = 6
BALL_SLOW_SPEED = 3
BALL_SLOW_AFTER_UNFREEZE_MS = 1500
BALL_FORCE_STEP = 0.8
BALL_FORCE_MAX = 6.0


def _find_app_icon_path():
    tools_dir = Path(__file__).resolve().parent
    app_dir = tools_dir.parent
    project_root = app_dir.parent
    repo_root = project_root.parent
    parent_repo_root = repo_root.parent
    frozen_base = Path(getattr(sys, "_MEIPASS", "")) if getattr(sys, "frozen", False) else None

    candidates = []
    if frozen_base:
        candidates.append(frozen_base / "assets" / "app.ico")

    candidates.extend((
        parent_repo_root / "assets" / "app.ico",
        repo_root / "assets" / "app.ico",
        project_root / "assets" / "app.ico",
        app_dir / "assets" / "app.ico",
    ))

    for icon_path in candidates:
        if icon_path.exists():
            return icon_path
    return None


def _apply_pong_icon():
    icon_path = _find_app_icon_path()
    if not icon_path:
        return
    try:
        icon_surface = pygame.image.load(str(icon_path))
        pygame.display.set_icon(icon_surface)
    except Exception:
        return


_apply_pong_icon()

# Striker class


class Striker:
        # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color, side):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.side = side
        # Rect that is used to control the position and collision of the object
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    # Used to display the object on the screen
    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, xFac, yFac):
        self.posx = self.posx + self.speed*xFac
        self.posy = self.posy + self.speed*yFac

        # Restricting the striker within the left and right boundaries
        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH-self.width

        # Restricting the striker to be below the top surface of the screen
        if self.posy <= 0:
            self.posy = 0
        # Restricting the striker to be above the bottom surface of the screen
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT-self.height

        # Keep visual rect in sync with position for drawing.
        self.geekRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text+str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.geekRect

    def getCollisionRect(self):
        # Invisible larger collision box so fast balls do not slip through edges.
        return self.geekRect.inflate(PADDLE_HITBOX_PAD_X * 2, PADDLE_HITBOX_PAD_Y * 2)

# Ball class


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)
        self.firstTime = 1
        self.last_hit_ms = -BALL_HIT_COOLDOWN_MS
        self.collision_locked = False
        self.force_owner = None
        self.force_streak = 0

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed*self.xFac
        self.posy += self.speed*self.yFac

        # If the ball hits the top or bottom surfaces, 
        # then the sign of yFac is changed and 
        # it results in a reflection
        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1

        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0
            return 1
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0
            return -1
        else:
            return 0
    
    def reset(self):
        self.posx = WIDTH//2
        self.posy = HEIGHT//2
        self.xFac *= -1
        self.firstTime = 1
        self.collision_locked = False
        self.force_owner = None
        self.force_streak = 0
        self._refresh_effective_speed()

    def _refresh_effective_speed(self):
        bonus_hits = max(0, self.force_streak - 1)
        force_bonus = min(BALL_FORCE_MAX, bonus_hits * BALL_FORCE_STEP)
        self.speed = self.base_speed + force_bonus

    def set_base_speed(self, new_speed):
        self.base_speed = float(new_speed)
        self._refresh_effective_speed()

    def apply_paddle_hit(self, paddle_side):
        # Paddle always sends the ball to the opposite side.
        if paddle_side == "left":
            self.xFac = 1
        else:
            self.xFac = -1

        if self.force_owner == paddle_side:
            self.force_streak += 1
        else:
            # Opposite paddle hit cancels previous force streak ownership.
            self.force_owner = paddle_side
            self.force_streak = 1

        self._refresh_effective_speed()

    def try_hit(self, paddle_side):
        if self.collision_locked:
            return False
        now_ms = pygame.time.get_ticks()
        if now_ms - self.last_hit_ms < BALL_HIT_COOLDOWN_MS:
            return False
        self.apply_paddle_hit(paddle_side)
        self.last_hit_ms = now_ms
        self.collision_locked = True
        return True

    def getRect(self):
        return self.ball

    def is_moving_towards_paddle(self, paddle_rect):
        ball_center_x = self.ball.centerx
        paddle_center_x = paddle_rect.centerx
        if self.xFac > 0:
            return paddle_center_x >= ball_center_x
        if self.xFac < 0:
            return paddle_center_x <= ball_center_x
        return False

# Game Manager


def main():
    running = True
    fps = FPS
    now_ms = pygame.time.get_ticks()
    ball_frozen_until_ms = now_ms + GAME_START_FREEZE_MS
    ball_slow_until_ms = 0

    # Defining the objects
    geek1 = Striker(20, 0, 10, 100, 10, BLUE, "left")
    geek2 = Striker(WIDTH-30, 0, 10, 100, 10, RED, "right")
    ball = Ball(WIDTH//2, HEIGHT//2, 7, BALL_NORMAL_SPEED, WHITE)

    listOfGeeks = [geek1, geek2]

    # Initial parameters of the players
    geek1Score, geek2Score = 0, 0
    geek1YFac, geek2YFac = 0, 0
    geek1XFac, geek2XFac = 0, 0

    def axis(negative_pressed, positive_pressed):
        if negative_pressed and positive_pressed:
            return 0
        if positive_pressed:
            return 1
        if negative_pressed:
            return -1
        return 0

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        geek1XFac = axis(keys[pygame.K_a], keys[pygame.K_d])
        geek1YFac = axis(keys[pygame.K_w], keys[pygame.K_s])
        geek2XFac = axis(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
        geek2YFac = axis(keys[pygame.K_UP], keys[pygame.K_DOWN])

        now_ms = pygame.time.get_ticks()

        # Paddles always move, including during initial ball freeze.
        geek1.update(geek1XFac, geek1YFac)
        geek2.update(geek2XFac, geek2YFac)

        paddle_collision_rects = [geek.getCollisionRect() for geek in listOfGeeks]
        overlapping_paddle = any(
            pygame.Rect.colliderect(ball.getRect(), paddle_rect)
            for paddle_rect in paddle_collision_rects
        )
        if not overlapping_paddle:
            ball.collision_locked = False

        point = 0
        if now_ms >= ball_frozen_until_ms:
            ball.set_base_speed(BALL_SLOW_SPEED if now_ms < ball_slow_until_ms else BALL_NORMAL_SPEED)

            # Collision detection
            for geek, paddle_collision_rect in zip(listOfGeeks, paddle_collision_rects):
                if (
                    pygame.Rect.colliderect(ball.getRect(), paddle_collision_rect)
                    and ball.is_moving_towards_paddle(paddle_collision_rect)
                ):
                    if ball.try_hit(geek.side):
                        break

            point = ball.update()
        else:
            seconds_left = max(1, (ball_frozen_until_ms - now_ms + 999) // 1000)
            start_text = font20.render(f"Starting in {seconds_left}", True, GREEN)
            start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start_text, start_rect)

        # -1 -> Geek_1 has scored
        # +1 -> Geek_2 has scored
        #  0 -> None of them scored
        if point == -1:
            geek1Score += 1
        elif point == 1:
            geek2Score += 1

        # Someone has scored a point and the ball is out of bounds.
        # Freeze the ball briefly, then resume at a temporary slow speed.
        if point:
            ball.reset()
            ball_frozen_until_ms = now_ms + BALL_FREEZE_AFTER_SCORE_MS
            ball_slow_until_ms = ball_frozen_until_ms + BALL_SLOW_AFTER_UNFREEZE_MS

        # Displaying the objects on the screen
        geek1.display()
        geek2.display()
        ball.display()

        # Displaying the scores of the players
        geek1.displayScore("Player 1 Score: ", 
                           geek1Score, 100, 20, BLUE)
        geek2.displayScore("Player 2 Score: ", 
                           geek2Score, WIDTH-100, 20, RED)

        pygame.display.update()
        clock.tick(fps)     


if __name__ == "__main__":
    main()
    pygame.quit()
