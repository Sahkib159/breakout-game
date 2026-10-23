import asyncio
import math
import random

import pygame

pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 28)
BIG_FONT = pygame.font.Font(None, 64)

BG_COLOR = (20, 20, 40)
WHITE = (240, 240, 240)
BALL_COLOR = (255, 200, 60)
ROW_COLORS = [
    (231, 76, 60),
    (230, 126, 34),
    (241, 196, 15),
    (46, 204, 113),
    (52, 152, 219),
    (155, 89, 182),
    (236, 240, 241),
]


def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 30, 100, 12)
        self.speed = 8

    def move_to(self, x):
        """Used for mouse / touch control."""
        self.rect.centerx = x
        self.rect.clamp_ip(screen.get_rect())

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=6)


class Ball:
    RADIUS = 8
    MAX_SPEED = 9

    def __init__(self, speed):
        self.speed = speed
        self.x = 0.0
        self.y = 0.0
        self.dx = 0.0
        self.dy = 0.0

    @property
    def rect(self):
        r = self.RADIUS
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def attach_to(self, paddle):
        """Sit on top of the paddle, waiting to be launched."""
        self.x = paddle.rect.centerx
        self.y = paddle.rect.top - self.RADIUS - 1
        self.dx = 0.0
        self.dy = 0.0

    def launch(self):
        angle = math.radians(random.choice([-1, 1]) * random.uniform(15, 40))
        self.dx = self.speed * math.sin(angle)
        self.dy = -self.speed * math.cos(angle)

    def update(self):
        r = self.RADIUS
        self.x += self.dx
        self.y += self.dy

        # walls: left, right, top
        if self.x - r <= 0:
            self.x = r
            self.dx = abs(self.dx)
        elif self.x + r >= WIDTH:
            self.x = WIDTH - r
            self.dx = -abs(self.dx)
        if self.y - r <= 0:
            self.y = r
            self.dy = abs(self.dy)

    def bounce_off_paddle(self, paddle):
        # where the ball hits the paddle decides the bounce angle
        offset = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)
        offset = max(-1, min(1, offset))
        angle = offset * math.radians(60)
        speed = math.hypot(self.dx, self.dy)
        self.dx = speed * math.sin(angle)
        self.dy = -speed * math.cos(angle)
        self.y = paddle.rect.top - self.RADIUS - 1

    def speed_up(self, factor=1.01):
        if math.hypot(self.dx, self.dy) < self.MAX_SPEED:
            self.dx *= factor
            self.dy *= factor

    @property
    def fell_off(self):
        return self.y - self.RADIUS > HEIGHT

    def draw(self):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.RADIUS)


class Brick:
    def __init__(self, rect, color, points):
        self.rect = rect
        self.color = color
        self.points = points

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)


def build_bricks(level):
    rows = min(4 + level, 7)
    cols = 10
    brick_w, brick_h, gap = 56, 18, 4
    left = (WIDTH - (cols * brick_w + (cols - 1) * gap)) // 2
    top = 50
    bricks = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(
                left + col * (brick_w + gap),
                top + row * (brick_h + gap),
                brick_w,
                brick_h,
            )
            bricks.append(Brick(rect, ROW_COLORS[row], 10 * (rows - row)))
    return bricks


class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.start_level()

    def start_level(self):
        self.bricks = build_bricks(self.level)
        self.ball = Ball(min(4 + 0.5 * (self.level - 1), 7))
        self.paddle.rect.centerx = WIDTH // 2
        self.ball.attach_to(self.paddle)
        self.state = "ready"  # ready | playing | gameover

    # ---------- input ----------
    def action(self):
        """Space bar or click/tap."""
        if self.state == "ready":
            self.ball.launch()
            self.state = "playing"
        elif self.state == "gameover":
            self.reset()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.action()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.action()
        elif event.type == pygame.MOUSEMOTION:
            self.paddle.move_to(event.pos[0])

    # ---------- logic ----------
    def update(self):
        if self.state == "gameover":
            return

        self.paddle.update()

        if self.state == "ready":
            self.ball.attach_to(self.paddle)
            return

        ball = self.ball
        ball.update()

        # paddle
        if ball.dy > 0 and ball.rect.colliderect(self.paddle.rect):
            ball.bounce_off_paddle(self.paddle)

        # bricks
        ball_rect = ball.rect
        for brick in self.bricks:
            if ball_rect.colliderect(brick.rect):
                self.bricks.remove(brick)
                self.score += brick.points

                # bounce on the side with the smallest overlap
                overlap_x = min(
                    ball_rect.right - brick.rect.left,
                    brick.rect.right - ball_rect.left,
                )
                overlap_y = min(
                    ball_rect.bottom - brick.rect.top,
                    brick.rect.bottom - ball_rect.top,
                )
                if overlap_x < overlap_y:
                    ball.dx = -ball.dx
                else:
                    ball.dy = -ball.dy

                ball.speed_up()
                break  # one brick per frame

        # lost the ball
        if ball.fell_off:
            self.lives -= 1
            if self.lives <= 0:
                self.state = "gameover"
            else:
                ball.attach_to(self.paddle)
                self.state = "ready"
            return

        # level cleared
        if not self.bricks:
            self.score += 100 * self.level
            self.level += 1
            self.start_level()

    # ---------- drawing ----------
    def draw(self):
        screen.fill(BG_COLOR)

        for brick in self.bricks:
            brick.draw()
        self.paddle.draw()
        self.ball.draw()

        # HUD
        score_text = FONT.render(f"Score: {self.score}", True, WHITE)
        lives_text = FONT.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(score_text, (12, 12))
        screen.blit(lives_text, lives_text.get_rect(topright=(WIDTH - 12, 12)))
        draw_text(f"Level {self.level}", FONT, WHITE, (WIDTH // 2, 22))

        if self.state == "ready":
            draw_text(
                "Press SPACE or click to launch",
                FONT,
                WHITE,
                (WIDTH // 2, HEIGHT // 2 + 60),
            )
        elif self.state == "gameover":
            draw_text("GAME OVER", BIG_FONT, (231, 76, 60), (WIDTH // 2, HEIGHT // 2 - 20))
            draw_text(
                f"Final score: {self.score}", FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 25)
            )
            draw_text(
                "Press SPACE or click to play again",
                FONT,
                WHITE,
                (WIDTH // 2, HEIGHT // 2 + 60),
            )

        pygame.display.flip()


async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update()
        game.draw()
        clock.tick(60)
        await asyncio.sleep(0)  # required for the browser build


asyncio.run(main())