# space_invaders.py
import pygame
import random
import sys

# --- Config ---
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_SPEED = 6
BULLET_SPEED = -10
ENEMY_SPEED_X = 1.0      # base horizontal speed
ENEMY_DROP = 20          # pixels to drop when changing direction
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_X_PADDING = 60
ENEMY_Y_PADDING = 45
ENEMY_START_Y = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 40, 40)
BLUE = (50, 150, 255)
YELLOW = (240, 220, 60)

# --- Initialize pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Python (Pygame)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 48)

# --- Game objects ---
class Player:
    def __init__(self):
        self.width = 50
        self.height = 20
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.speed = PLAYER_SPEED
        self.color = BLUE
        self.cooldown = 0            # frames until next shot allowed
        self.cooldown_max = 12       # fire rate

    def update(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x - self.width//2 > 0:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x + self.width//2 < WIDTH:
            self.x += self.speed
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surf):
        # triangle-like ship
        points = [
            (self.x, self.y - self.height),
            (self.x - self.width//2, self.y),
            (self.x + self.width//2, self.y),
        ]
        pygame.draw.polygon(surf, self.color, points)
        # small cockpit
        pygame.draw.rect(surf, YELLOW, (self.x - 6, self.y - self.height + 6, 12, 6))

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = self.cooldown_max
        bx = self.x
        by = self.y - self.height - 6
        return Bullet(bx, by, 3, 12, BULLET_SPEED, WHITE)


class Bullet:
    def __init__(self, x, y, w, h, vy, color):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.vy = vy
        self.color = color
        self.alive = True

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.alive = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)


class Enemy:
    def __init__(self, x, y, size=36, row=0, col=0):
        self.size = size
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.alive = True
        self.row = row
        self.col = col

    def draw(self, surf):
        # stylized invader — blocks and eyes
        s = self.size
        rx, ry = self.rect.topleft
        # main body
        pygame.draw.rect(surf, GREEN, (rx + s*0.1, ry + s*0.2, s*0.8, s*0.7))
        # left antenna
        pygame.draw.rect(surf, GREEN, (rx, ry + s*0.45, s*0.1, s*0.15))
        # right antenna
        pygame.draw.rect(surf, GREEN, (rx + s*0.9, ry + s*0.45, s*0.1, s*0.15))
        # eyes
        eye_w = int(s*0.12)
        pygame.draw.rect(surf, BLACK, (rx + s*0.25, ry + s*0.35, eye_w, eye_w))
        pygame.draw.rect(surf, BLACK, (rx + s*0.63, ry + s*0.35, eye_w, eye_w))
        # legs
        pygame.draw.rect(surf, GREEN, (rx + s*0.18, ry + s*0.82, s*0.18, s*0.18))
        pygame.draw.rect(surf, GREEN, (rx + s*0.64, ry + s*0.82, s*0.18, s*0.18))


# --- Helper functions ---
def create_enemies(rows, cols):
    enemies = []
    total_width = (cols - 1) * ENEMY_X_PADDING
    start_x = (WIDTH - total_width) // 2
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * ENEMY_X_PADDING
            y = ENEMY_START_Y + r * ENEMY_Y_PADDING
            enemies.append(Enemy(x, y, size=40, row=r, col=c))
    return enemies

def draw_text_center(surf, text, y, font_obj, color=WHITE):
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH//2, y))
    surf.blit(txt, rect)

# --- Main Game State ---
def main():
    player = Player()
    bullets = []
    enemies = create_enemies(ENEMY_ROWS, ENEMY_COLS)
    enemy_direction = 1   # 1 right, -1 left
    enemy_speed_x = ENEMY_SPEED_X
    score = 0
    game_over = False
    level = 1

    # defensive barriers (simple rectangles)
    barriers = []
    barrier_w, barrier_h = 90, 20
    for i in range(4):
        bx = (i+1) * WIDTH // 5
        by = HEIGHT - 140
        barriers.append(pygame.Rect(bx - barrier_w//2, by, barrier_w, barrier_h))

    while True:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        # ----- Events -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and not game_over:
                    if player.can_shoot():
                        bullets.append(player.shoot())
                if event.key == pygame.K_r and game_over:
                    # restart
                    return main()

        # ----- Update -----
        if not game_over:
            player.update(keys)

            # update bullets
            for b in bullets:
                b.update()
            bullets = [b for b in bullets if b.alive]

            # enemy movement: compute boundaries
            if enemies:
                leftmost = min(e.rect.left for e in enemies if e.alive)
                rightmost = max(e.rect.right for e in enemies if e.alive)
            else:
                leftmost, rightmost = 0, 0

            # change direction if hitting sides
            if rightmost >= WIDTH - 10:
                enemy_direction = -1
                for e in enemies:
                    e.rect.y += ENEMY_DROP
                enemy_speed_x = ENEMY_SPEED_X + level * 0.15
            elif leftmost <= 10:
                enemy_direction = 1
                for e in enemies:
                    e.rect.y += ENEMY_DROP
                enemy_speed_x = ENEMY_SPEED_X + level * 0.15

            # move enemies
            for e in enemies:
                e.rect.x += enemy_direction * enemy_speed_x

            # check bullet collisions with enemies
            # Only player's bullets should hit enemies (they travel upwards => vy < 0).
            # Enemy bullets pass through other enemies without killing them.
            for b in bullets:
                if b.vy >= 0:
                    # skip bullets moving downwards (enemy bullets)
                    continue
                for e in enemies:
                    if e.alive and b.rect.colliderect(e.rect):
                        e.alive = False
                        b.alive = False
                        score += 10 + (ENEMY_ROWS - e.row) * 2
                        break

            # remove dead enemies
            enemies = [e for e in enemies if e.alive]

            # enemies reaching player (game over)
            for e in enemies:
                if e.rect.bottom >= player.y:
                    game_over = True

            # simple enemy shooting: random chance by existing rows
            # optional: more advanced AI can be added
            if random.random() < 0.005 + level * 0.001:
                # choose a random alive enemy near bottom of its column
                if enemies:
                    shooter = random.choice(enemies)
                    b = Bullet(shooter.rect.centerx, shooter.rect.bottom + 8, 4, 10, -BULLET_SPEED, RED)
                    # enemy bullets fall down (so positive vy)
                    b.vy = abs(b.vy)
                    bullets.append(b)

            # bullets colliding with barriers or player
            for b in bullets:
                # barriers
                for bar in barriers:
                    if bar.colliderect(b.rect):
                        # damage barrier: shrink it
                        if b.vy < 0:  # player's bullet hitting barrier
                            bar.inflate_ip(-10, -2)
                        else:         # enemy bullet hitting barrier
                            bar.inflate_ip(-8, -4)
                        b.alive = False
                        break
                # player hit by enemy bullet
                if b.vy > 0 and b.rect.colliderect(pygame.Rect(player.x - player.width//2, player.y - player.height, player.width, player.height)):
                    game_over = True
                    b.alive = False

            # clean barriers that shrunk
            barriers = [b for b in barriers if b.width > 10 and b.height > 6]

            # level up when all enemies destroyed
            if not enemies:
                level += 1
                # increase difficulty and recreate enemies
                new_rows = min(6, ENEMY_ROWS + (level - 1) // 2)
                new_cols = min(10, ENEMY_COLS + (level - 1) // 3)
                enemies = create_enemies(new_rows, new_cols)
                # reset barriers
                barriers = []
                for i in range(4):
                    bx = (i+1) * WIDTH // 5
                    by = HEIGHT - 140
                    barriers.append(pygame.Rect(bx - barrier_w//2, by, barrier_w, barrier_h))
                # slightly increase player fire rate a bit
                player.cooldown_max = max(6, player.cooldown_max - 1)

        # ----- Draw -----
        screen.fill(BLACK)

        # HUD
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (8, 8))
        level_surf = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_surf, (WIDTH - 110, 8))

        # draw player
        player.draw(screen)

        # draw bullets (player and enemy)
        for b in bullets:
            b.draw(screen)

        # draw enemies
        for e in enemies:
            e.draw(screen)

        # draw barriers
        for b in barriers:
            pygame.draw.rect(screen, (120, 120, 120), b)

        # draw ground line
        pygame.draw.line(screen, (40, 40, 40), (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), 2)

        if game_over:
            draw_text_center(screen, "GAME OVER", HEIGHT//2 - 40, big_font, RED)
            draw_text_center(screen, f"Final Score: {score}", HEIGHT//2 + 10, font, WHITE)
            draw_text_center(screen, "Press R to restart or Esc to quit", HEIGHT//2 + 50, font, WHITE)

        pygame.display.flip()


if __name__ == "__main__":
    main()
