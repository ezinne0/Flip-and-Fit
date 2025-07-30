import pygame
import sys
import random
from pygame.locals import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of this script
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets", "logos")  # move one up, then assets/logos

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
FPS = 60
CARD_WIDTH, CARD_HEIGHT = 100, 150
GRID_ROWS, GRID_COLS = 6, 5
GAP = 20
BOARD_TOP_LEFT = ((SCREEN_WIDTH - (GRID_COLS * (CARD_WIDTH + GAP))) // 2,
                  (SCREEN_HEIGHT - (GRID_ROWS * (CARD_HEIGHT + GAP))) // 2)
FONT_COLOR = (70, 73, 76)
MATCH_COLOR = (239, 121, 138)
BG_COLOR = (250, 250, 250)

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flip and Fit: Fashion Match Challenge")
clock = pygame.time.Clock()

# Load fonts
font = pygame.font.SysFont("sans", 24)

# Placeholder brand data (use real images/names in assets later)
BRANDS = [
    "YSL", "Gucci", "Loro Piana", "Ferragamo", "Louis Vuitton",
    "Fendi", "Hermés", "Cartier", "Prada", "Balenciaga",
    "Chanel", "Dior", "Bottega Veneta", "Celine", "Loewe"
]


# Card class
class Card:
    def __init__(self, card_type, brand, pos):
        self.card_type = card_type  # 'logo' or 'name'
        self.brand = brand
        self.rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
        self.flipped = False
        self.matched = False
        self.image = None

        if self.card_type == 'logo':
          base_path = os.path.join(ASSETS_DIR, self.brand.lower().replace(' ', '_'))
          for ext in [".png", ".jpg", ".jpeg"]:
            full_path = base_path + ext
            print(f"Trying to load image from: {full_path}")
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
            pygame.draw.rect(surface, MATCH_COLOR if self.matched else (247, 169, 168), self.rect, border_radius=12)

            if self.card_type == 'logo' and self.image:
                surface.blit(self.image, self.rect)
            else:
                # Display the brand name in text
                text = font.render(self.brand, True, FONT_COLOR)
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
        else:
            # Unflipped card — display as dark back
            pygame.draw.rect(surface, FONT_COLOR, self.rect, border_radius=12)

    def is_clicked(self, pos):
      return self.rect.collidepoint(pos)

# Generate cards
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
init_cards()

# Game loop
running = True
while running:
    dt = clock.tick(FPS)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if match_timer == 0:
                for card in cards:
                    if card.is_clicked(event.pos) and not card.flipped and not card.matched:
                        card.flipped = True
                        if not first_card:
                            first_card = card
                        elif not second_card:
                            second_card = card

    # Match logic
    if first_card and second_card and match_timer == 0:
        if first_card.brand == second_card.brand and first_card.card_type != second_card.card_type:
            first_card.matched = True
            second_card.matched = True
            score += 10
            first_card = None
            second_card = None
        else:
            match_timer = 1000  # milliseconds

    if match_timer > 0:
        match_timer -= dt
        if match_timer <= 0:
            first_card.flipped = False
            second_card.flipped = False
            first_card = None
            second_card = None
            match_timer = 0

    # Draw all cards
    for card in cards:
        card.draw(screen)

    # Display score
    score_text = font.render(f"Score: {score}", True, FONT_COLOR)
    screen.blit(score_text, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()