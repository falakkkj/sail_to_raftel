import pygame, math, random

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sail to Raftel - Playable Demo")
clock = pygame.time.Clock()

# Colors
SEA_COLOR = (0, 105, 148)
WAVE_COLOR1 = (0, 150, 200, 80)
WAVE_COLOR2 = (0, 100, 180, 100)
WHITE = (255, 255, 255)

# Load Ship
ship = pygame.image.load("ship.png").convert_alpha()
ship = pygame.transform.smoothscale(ship, (160, 100))
ship_x = WIDTH // 2 - ship.get_width() // 2
ship_y = 300

# Load Obstacle (Rock)
rock_img = pygame.image.load("rock.png").convert_alpha()
rock_img = pygame.transform.smoothscale(rock_img, (80, 80))

# Load Raftel Island
island = pygame.image.load("island.png").convert_alpha()
island = pygame.transform.smoothscale(island, (300, 200))

# Game variables
obstacles = []
distance = 0
game_over = False
win = False

def spawn_obstacle():
    """Spawn a rock randomly in sea"""
    x = random.randint(50, WIDTH - 100)
    y = -100
    obstacles.append(pygame.Rect(x, y, 80, 80))

def draw_waves():
    """Draw layered sine waves"""
    t = pygame.time.get_ticks() * 0.002
    wave_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for x in range(WIDTH):
        y1 = 380 + int(20 * math.sin(0.02 * (x + t * 50)))
        y2 = 400 + int(15 * math.sin(0.015 * (x + t * 60)))
        pygame.draw.line(wave_surface, WAVE_COLOR1, (x, y1), (x, HEIGHT))
        pygame.draw.line(wave_surface, WAVE_COLOR2, (x, y2), (x, HEIGHT))

    screen.blit(wave_surface, (0, 0))
    return t

font = pygame.font.SysFont("Arial", 28, bold=True)

running = True
while running:
    screen.fill(SEA_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not win:
        # Waves
        t = draw_waves()

        # Controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship_x -= 5
        if keys[pygame.K_RIGHT]:
            ship_x += 5
        ship_x = max(0, min(WIDTH - ship.get_width(), ship_x))

        # Ship bobbing + tilt
        bob = int(10 * math.sin(t))
        angle = math.sin(t) * 3
        rotated_ship = pygame.transform.rotate(ship, angle)
        ship_rect = rotated_ship.get_rect(center=(ship_x + ship.get_width()//2, ship_y + bob))
        screen.blit(rotated_ship, ship_rect.topleft)

        # Update obstacles
        if random.randint(1, 60) == 1:  # spawn occasionally
            spawn_obstacle()

        new_obs = []
        for rect in obstacles:
            rect.y += 4
            screen.blit(rock_img, rect.topleft)
            if rect.y < HEIGHT:
                new_obs.append(rect)
            # Collision check
            if rect.colliderect(ship_rect):
                game_over = True
        obstacles = new_obs

        # Distance (progress)
        distance += 1
        progress = distance / 3000  # adjust difficulty here (3000 = journey length)

        # Show distance bar
        pygame.draw.rect(screen, WHITE, (50, 20, 700, 20), 2)
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, int(700 * min(progress, 1)), 20))

        # If reached Raftel
        if progress >= 1:
            win = True

    elif game_over:
        text = font.render("Game Over! You sank before reaching Raftel!", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    elif win:
        screen.blit(island, (WIDTH//2 - island.get_width()//2, HEIGHT//2 - 100))
        text = font.render("You Reached Raftel! 🏝️", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
