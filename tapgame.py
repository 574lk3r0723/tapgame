import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.25
JUMP_SPEED = -5
PLAYER_SPEED = 5
OBJECT_GAP = 200
BULLET_SPEED = 7
BULLET_COOLDOWN = 20  # Cooldown in frames between shots
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCORE_FONT = pygame.font.Font(None, 36)
HIGHSCORE_FILE = "highscore.txt"
STAR_COUNT = 50
STAR_SPEED_RANGE = (1, 5)
STAR_SIZE_RANGE = (1, 3)
STAR_COLOR_RANGE = [(255, 255, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]  # White, Yellow, Magenta, Cyan

# Function to load high score from file
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as file:
            return int(file.read())
    else:
        return 0

# Function to save high score to file
def save_highscore(highscore):
    with open(HIGHSCORE_FILE, "w") as file:
        file.write(str(highscore))

# Function to create shooting stars
def create_star():
    size = random.randint(*STAR_SIZE_RANGE)
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    speed = random.choice(range(*STAR_SPEED_RANGE))
    color = random.choice(STAR_COLOR_RANGE)
    return pygame.Rect(x, y, size, size), color, speed

# Function to move and draw shooting stars
def move_stars(stars):
    new_stars = []
    for star in stars:
        star_rect, color, speed = star
        star_rect.x -= speed
        if star_rect.right < 0:
            star_rect.x = SCREEN_WIDTH
            star_rect.y = random.randint(0, SCREEN_HEIGHT)
            speed = random.choice(range(*STAR_SPEED_RANGE))
            color = random.choice(STAR_COLOR_RANGE)
        pygame.draw.rect(screen, color, star_rect)
        new_stars.append((star_rect, color, speed))
    return new_stars

# Function to display text on screen
def draw_text(surface, text, size, color, x, y):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Function to draw start menu overlay
def draw_start_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    draw_text(screen, "Press Enter to Start", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tap Game")

# Create player
player_rect = pygame.Rect(0, 0, 50, 50)
player_rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
player_velocity = 0
bullets = []
bullet_cooldown = 0

# Object Groups
objects = []

# Shooting stars
stars = [create_star() for _ in range(STAR_COUNT)]

# Game variables
score = 0
highscore = load_highscore()
game_over = False
level = 1
object_speed = 3
start_menu = True

# Main Loop
clock = pygame.time.Clock()
running = True
object_counter = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if start_menu:
                if event.key == pygame.K_RETURN:
                    start_menu = False
            else:
                if not game_over:
                    if event.key == pygame.K_SPACE:
                        # Jump
                        player_velocity = JUMP_SPEED
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        # Shoot bullet
                        if bullet_cooldown <= 0:
                            bullet = pygame.Rect(player_rect.right, player_rect.centery - 2, 10, 4)
                            bullets.append(bullet)
                            bullet_cooldown = BULLET_COOLDOWN
                    elif event.key == pygame.K_LEFT:
                        player_rect.x -= PLAYER_SPEED
                    elif event.key == pygame.K_RIGHT:
                        player_rect.x += PLAYER_SPEED
                else:
                    if event.key == pygame.K_RETURN:
                        # Reset game
                        player_rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                        player_velocity = 0
                        objects = []
                        score = 0
                        game_over = False
                        level = 1
                        object_speed = 3
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not start_menu:
        if not game_over:
            # Update player
            player_velocity += GRAVITY
            player_rect.y += player_velocity

            # Cooldown for shooting bullets
            if bullet_cooldown > 0:
                bullet_cooldown -= 1

            # Update bullets
            bullets = [bullet for bullet in bullets if bullet.x < SCREEN_WIDTH]
            for bullet in bullets:
                bullet.x += BULLET_SPEED

            # Create objects
            object_counter += 1
            if object_counter >= 100:
                object_counter = 0
                new_object_height = random.randint(50, 200)
                obj = pygame.Rect(SCREEN_WIDTH, 0, 30, new_object_height)
                top_rect = pygame.Rect(obj.left, obj.top, obj.width, obj.height - OBJECT_GAP)
                bottom_rect = pygame.Rect(obj.left, obj.bottom + OBJECT_GAP, obj.width, SCREEN_HEIGHT - obj.bottom - OBJECT_GAP)
                objects.append((obj, top_rect, bottom_rect))

            # Move objects
            for obj_group in objects:
                obj_group[0].x -= object_speed
                obj_group[1].x -= object_speed
                obj_group[2].x -= object_speed

            # Check collisions between bullets and objects
            for bullet in bullets:
                for obj_group in objects:
                    if obj_group[0].colliderect(bullet) or obj_group[1].colliderect(bullet) or obj_group[2].colliderect(bullet):
                        objects.remove(obj_group)
                        bullets.remove(bullet)
                        score += 10

            # Check collisions between player and objects
            for obj_group in objects:
                if obj_group[0].colliderect(player_rect) or obj_group[1].colliderect(player_rect) or obj_group[2].colliderect(player_rect):
                    game_over = True

            # Remove off-screen objects
            objects = [obj_group for obj_group in objects if obj_group[0].right > 0]

            # Update score
            score += 1

            # Update level
            if score % 5000 == 0:
                level += 1
                object_speed += 1

        # Draw
        screen.fill(BLACK)

        # Draw shooting stars
        for star in stars:
            pygame.draw.rect(screen, star[1], star[0])

        # Draw objects
        for obj_group in objects:
            pygame.draw.rect(screen, WHITE, obj_group[0])
            pygame.draw.rect(screen, WHITE, obj_group[1])
            pygame.draw.rect(screen, WHITE, obj_group[2])

        # Draw player
        pygame.draw.rect(screen, WHITE, player_rect)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        # Update score and level display
        draw_text(screen, f"Score: {score}", 24, WHITE, SCREEN_WIDTH // 2, 10)
        draw_text(screen, f"Highscore: {highscore}", 24, WHITE, SCREEN_WIDTH // 2, 40)
        draw_text(screen, f"Level: {level}", 24, WHITE, SCREEN_WIDTH // 2, 70)

        if game_over:
            draw_text(screen, "Game Over! Press Enter to play again", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        draw_text(screen, "Press Esc to exit", 20, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

    else:
        draw_start_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()



