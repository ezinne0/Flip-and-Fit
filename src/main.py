import pygame
import sys
import random
import os
import unicodedata
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Try initializing the mixer (sound system)
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Audio initialization failed: {e}")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets", "logos")
SOUNDS_DIR = os.path.join(BASE_DIR, "..", "assets", "sounds")

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1300, 1100
FPS = 60
CARD_WIDTH, CARD_HEIGHT = 120, 180
GRID_ROWS, GRID_COLS = 5, 6
GAP = 20
BOARD_TOP_LEFT = ((SCREEN_WIDTH - (GRID_COLS * (CARD_WIDTH + GAP))) // 2,
                  (SCREEN_HEIGHT - (GRID_ROWS * (CARD_HEIGHT + GAP))) // 2)
FONT_COLOR = (74, 60, 64)
MATCH_COLOR = (69, 171, 176)
BG_COLOR = (244, 235, 232)
TIMER_START = 150000  # 2.5 minutes in milliseconds

match_sound = mismatch_sound = tap_sound = None

if pygame.mixer.get_init():
    try:
        match_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "match.wav"))
        mismatch_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "wrong.wav"))
        tap_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "tap.wav"))
    except Exception as e:
        print(f"Error loading sound files: {e}")
else:
    print("Sound disabled: mixer not initialized.")

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flip and Fit: Fashion Match Challenge")
clock = pygame.time.Clock()

# Load fonts
try:
    title_font = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36)
except:
    title_font = pygame.font.SysFont("sans", 36)

try:
    card_font = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
except:
    card_font = pygame.font.SysFont("sans", 18)

# Brands
BRANDS = [
    "YSL", "Gucci", "Loro Piana", "Ferragamo", "Louis Vuitton",
    "Fendi", "Hermés", "Cartier", "Prada", "Balenciaga",
    "Chanel", "Dior", "Bottega Veneta", "Celine", "Loewe"
]

# Normalize brand string for filenames
def normalize_filename(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().replace(' ', '_')

# Card class
class Card:
    def __init__(self, card_type, brand, pos):
        self.card_type = card_type
        self.brand = brand
        self.rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
        self.flipped = False
        self.matched = False
        self.image = None

        if self.card_type == 'logo':
            base_path = os.path.join(ASSETS_DIR, normalize_filename(self.brand))
            for ext in [".png", ".jpg", ".jpeg"]:
                full_path = base_path + ext
                if os.path.exists(full_path):
                    try:
                        raw_img = pygame.image.load(full_path).convert_alpha()
                        self.image = pygame.transform.scale(raw_img, (CARD_WIDTH, CARD_HEIGHT))
                        break
                    except Exception as e:
                        print(f"Error loading logo for {self.brand}: {e}")
                        self.image = None

    def draw(self, surface):
        if self.flipped or self.matched:
            pygame.draw.rect(surface, MATCH_COLOR if self.matched else (171, 204, 216), self.rect, border_radius=12)
            if self.card_type == 'logo' and self.image:
                surface.blit(self.image, self.rect)
            else:
                text = card_font.render(self.brand, True, FONT_COLOR)
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
        else:
            pygame.draw.rect(surface, FONT_COLOR, self.rect, border_radius=12)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Init game
cards = []
def init_cards():
    global cards
    cards = []
    paired_data = [(brand, t) for brand in BRANDS for t in ('logo', 'name')]
    random.shuffle(paired_data)
    for idx, (brand, t) in enumerate(paired_data):
        row = idx // GRID_COLS
        col = idx % GRID_COLS
        x = BOARD_TOP_LEFT[0] + col * (CARD_WIDTH + GAP)
        y = BOARD_TOP_LEFT[1] + row * (CARD_HEIGHT + GAP)
        cards.append(Card(t, brand, (x, y)))

# Game state
first_card = None
second_card = None
match_timer = 0
score = 0
timer = TIMER_START
init_cards()

# Welcome popup
def show_welcome():
    screen.fill(BG_COLOR)

    lines = [
        "WELCOME TO FLIP AND FIT",
        "",
        "Match each brand logo with its correct name.",
        "• +40 points if matched in the first 30 seconds",
        "• +15 points after that",
        "• -5 points for wrong guesses",
        "You have 2 minutes and 30 seconds!",
        "",
        "Click anywhere to start!"
    ]

    y = SCREEN_HEIGHT // 2 - len(lines) * 20
    for line in lines:
        text = title_font.render(line, True, FONT_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(text, rect)
        y += 40

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (MOUSEBUTTONDOWN, KEYDOWN):
                waiting = False

show_welcome()

def show_game_over(final_score):
    screen.fill(BG_COLOR)
    lines = [
        "GAME OVER!",
        f"Final Score: {final_score}",
        "Thanks for playing!",
        "Press any key or click to exit."
    ]

    y = SCREEN_HEIGHT // 2 - len(lines) * 20
    for line in lines:
        text = title_font.render(line, True, FONT_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(text, rect)
        y += 40

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (MOUSEBUTTONDOWN, KEYDOWN):
                waiting = False

# Game loop
running = True
start_ticks = pygame.time.get_ticks()
while running:
    dt = clock.tick(FPS)
    screen.fill(BG_COLOR)
    timer -= dt
    all_matched = all(card.matched for card in cards)
    if timer <= 0 or all_matched:
        running = False
        continue

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if tap_sound: #safer
                tap_sound.play()
            if match_timer == 0:
                for card in cards:
                    if card.is_clicked(event.pos) and not card.flipped and not card.matched:
                        card.flipped = True
                        if not first_card:
                            first_card = card
                        elif not second_card:
                            second_card = card

    if first_card and second_card and match_timer == 0:
        if first_card.brand == second_card.brand and first_card.card_type != second_card.card_type:
            if match_sound:
                match_sound.play()
            first_card.matched = True
            second_card.matched = True
            time_elapsed = pygame.time.get_ticks() - start_ticks
            if time_elapsed < 30000:
                score += 40
            else:
                score += 15
            first_card = None
            second_card = None
        else:
            if mismatch_sound:
                mismatch_sound.play()
            score -= 5
            match_timer = 1000

    if match_timer > 0:
        match_timer -= dt
        if match_timer <= 0:
            first_card.flipped = False
            second_card.flipped = False
            first_card = None
            second_card = None
            match_timer = 0

    for card in cards:
        card.draw(screen)

    # Score and timer
    score_text = card_font.render(f"Score: {score}", True, FONT_COLOR)
    time_text = card_font.render(f"Time Left: {max(timer // 1000, 0)}s", True, FONT_COLOR)
    screen.blit(score_text, (20, 20))
    screen.blit(time_text, (20, 50))

    pygame.display.flip()

show_game_over(score)
pygame.quit()
sys.exit()