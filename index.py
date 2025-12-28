import pygame
import math
import random
import sys

pygame.init()

# -------------------- SETTINGS --------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sail to Raftel - Endless Sea")
CLOCK = pygame.time.Clock()

# -------------------- COLORS --------------------
SEA_COLOR = (0, 105, 148)
NIGHT_SEA = (10, 40, 80)
WHITE = (255, 255, 255)
GREEN = (0, 220, 0)
WAVE_COLOR_1 = (0, 150, 200, 80)
WAVE_COLOR_2 = (0, 100, 180, 100)
INPUT_BG = (50, 50, 70)

# -------------------- CONSTANTS --------------------
SHIP_SPEED = 5
OBSTACLE_SPEED = 4

# -------------------- LOAD IMAGES --------------------
def load_image(name, size=None, optional=False):
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except:
        if optional:
            return None
        print(f"Error loading image: {name}")
        pygame.quit()
        sys.exit()

SHIP_IMG = load_image("ship.png", (160, 100))
ROCK_IMG = load_image("rock.png", (80, 80))
FONT = pygame.font.SysFont("Arial", 26, bold=True)

# -------------------- SKY --------------------
def draw_day_sky():
    for y in range(HEIGHT // 2):
        pygame.draw.line(SCREEN, (80, 170 + y // 5, 235), (0, y), (WIDTH, y))

def draw_night_sky():
    for y in range(HEIGHT // 2):
        pygame.draw.line(SCREEN, (10, 20 + y // 10, 60 + y // 6), (0, y), (WIDTH, y))
    for _ in range(60):
        SCREEN.set_at((random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)), WHITE)

# -------------------- CLASSES --------------------
class Ship:
    def __init__(self):
        self.x = WIDTH // 2 - 80
        self.y = 320
        self.hitbox = pygame.Rect(self.x + 30, self.y + 20, 100, 50)

    def update(self, keys, t):
        if keys[pygame.K_LEFT]:
            self.x -= SHIP_SPEED
        if keys[pygame.K_RIGHT]:
            self.x += SHIP_SPEED
        self.x = max(0, min(WIDTH - 160, self.x))
        bob = int(10 * math.sin(t))
        self.hitbox.topleft = (self.x + 30, self.y + bob + 20)

    def draw(self, t):
        bob = int(10 * math.sin(t))
        angle = math.sin(t) * 3
        rotated = pygame.transform.rotate(SHIP_IMG, angle)
        rect = rotated.get_rect(center=(self.x + 80, self.y + bob))
        SCREEN.blit(rotated, rect.topleft)

class Rock:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(50, WIDTH - 130), -80, 80, 80)

    def update(self):
        self.rect.y += OBSTACLE_SPEED

    def draw(self):
        SCREEN.blit(ROCK_IMG, self.rect.topleft)

class WaveSystem:
    def draw(self, t):
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, 3):
            y1 = 380 + int(20 * math.sin(0.02 * (x + t * 50)))
            y2 = 400 + int(15 * math.sin(0.015 * (x + t * 60)))
            pygame.draw.line(surface, WAVE_COLOR_1, (x, y1), (x, HEIGHT))
            pygame.draw.line(surface, WAVE_COLOR_2, (x, y2), (x, HEIGHT))
        SCREEN.blit(surface, (0, 0))

# -------------------- UI --------------------
def draw_score(score):
    text = FONT.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(text, (20, 20))

def draw_game_over():
    msg = FONT.render("Game Over! Press R to Restart", True, WHITE)
    SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

def draw_leaderboard(leaderboard):
    SCREEN.fill(INPUT_BG)
    title = FONT.render("🏆 Leaderboard 🏆", True, WHITE)
    SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    if leaderboard:
        for i, (name, score) in enumerate(leaderboard[:5]):
            entry = FONT.render(f"{i+1}. {name} - {score}", True, WHITE)
            SCREEN.blit(entry, (WIDTH//2 - entry.get_width()//2, 120 + i*40))
    else:
        empty_msg = FONT.render("No scores yet", True, WHITE)
        SCREEN.blit(empty_msg, (WIDTH//2 - empty_msg.get_width()//2, HEIGHT//2))
    info = FONT.render("Press R to Play Again", True, WHITE)
    SCREEN.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT-60))
    pygame.display.flip()

# -------------------- GAME LOOP --------------------
def game_loop(player_name, leaderboard):
    ship = Ship()
    waves = WaveSystem()
    obstacles = []
    score = 0
    game_over = False
    is_night = False

    SPAWN_ROCK = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ROCK, 900)

    while True:
        CLOCK.tick(FPS)
        t = pygame.time.get_ticks() * 0.002

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    is_night = True
                if event.key == pygame.K_d:
                    is_night = False
                if event.key == pygame.K_r and game_over:
                    return

            if not game_over and event.type == SPAWN_ROCK:
                obstacles.append(Rock())

        # BACKGROUND
        draw_night_sky() if is_night else draw_day_sky()
        pygame.draw.rect(SCREEN, NIGHT_SEA if is_night else SEA_COLOR,
                         (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        waves.draw(t)

        keys = pygame.key.get_pressed()
        if not game_over:
            ship.update(keys, t)
            ship.draw(t)

            for rock in obstacles[:]:
                rock.update()
                rock.draw()
                if rock.rect.colliderect(ship.hitbox):
                    game_over = True
                if rock.rect.y > HEIGHT:
                    obstacles.remove(rock)

            score += 1
            draw_score(score)

        else:
            # Update leaderboard: unique player name
            existing_index = next((i for i, (n, s) in enumerate(leaderboard) if n == player_name), None)
            if existing_index is not None:
                if score > leaderboard[existing_index][1]:
                    leaderboard[existing_index] = (player_name, score)
            else:
                leaderboard.append((player_name, score))

            leaderboard.sort(key=lambda x: x[1], reverse=True)
            draw_leaderboard(leaderboard)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                return

        pygame.display.flip()

# -------------------- NAME INPUT --------------------
def name_input_screen():
    name = ""
    input_active = True
    while input_active:
        SCREEN.fill(INPUT_BG)
        prompt = FONT.render("Enter Your Name: " + name, True, WHITE)
        info = FONT.render("Press Enter to Start", True, WHITE)
        SCREEN.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 30))
        SCREEN.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 30))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip() != "":
                    input_active = False
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:
                        name += event.unicode

# -------------------- MAIN --------------------
def main():
    leaderboard = []  # Empty at start
    while True:
        player_name = name_input_screen()
        game_loop(player_name, leaderboard)

if __name__ == "__main__":
    main()

