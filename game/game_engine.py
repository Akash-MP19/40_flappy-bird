import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bird = Bird(width // 4, height // 2)
        self.pipe_speed = 4
        self.pipe_interval = 90  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [Pipe(width + 100, height, speed=self.pipe_speed)]

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        # Check ceiling collision
        if self.bird.y - self.bird.radius <= 0:
            self.bird.y = self.bird.radius
            self.game_over = True
            return

        # Check ground collision
        if self.bird.y + self.bird.radius >= self.height:
            self.bird.y = self.height - self.bird.radius
            self.game_over = True
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, speed=self.pipe_speed))

        for pipe in self.pipes:
            pipe.move()

            # Check collision against pipe rects using the bird's full bounding rect
            if pipe.collides_with(self.bird):
                self.game_over = True
                return

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Semi-transparent overlay to dim the scene
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

            # "GAME OVER" message
            game_over_surf = self.game_over_font.render("GAME OVER", True, (255, 60, 60))
            game_over_rect = game_over_surf.get_rect(center=(self.width // 2, self.height // 2 - 40))
            screen.blit(game_over_surf, game_over_rect)

            # Final score message
            final_score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_surf.get_rect(center=(self.width // 2, self.height // 2 + 20))
            screen.blit(final_score_surf, final_score_rect)

