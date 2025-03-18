import pygame
import sys
from player import Player


class Game:
    def __init__(self, width=800, height=600, title="Brawlstars Dodge Trainer"):
        """
        Initialize the game.

        Args:
            width (int): Screen width
            height (int): Screen height
            title (str): Window title
        """
        # Initialize Pygame
        pygame.init()

        # Set up display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # Set up clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Create player
        self.player = Player(
            x=width // 2,
            y=height // 2,
            radius=30,
            color=(255, 0, 0),  # Red
            speed=5
        )

        # Initialize bullets list
        self.bullets = []

        # Game state
        self.running = True

        # Background color (light beige)
        self.bg_color = (245, 245, 220)

    def handle_events(self):
        """Handle pygame events like quit and keypresses."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right mouse button
                    self.player.aiming = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and self.player.aiming:  # Right mouse button release
                    self.player.aiming = False
                    self.player.start_shooting()

        # Get mouse position for aiming
        mouse_pos = pygame.mouse.get_pos()
        self.player.update_aim(mouse_pos)

    def update(self):
        """Update game state."""
        # Get player movement for this frame
        keys = pygame.key.get_pressed()
        player_dx, player_dy = 0, 0

        if keys[pygame.K_w]:
            player_dy -= self.player.speed
        if keys[pygame.K_s]:
            player_dy += self.player.speed
        if keys[pygame.K_a]:
            player_dx -= self.player.speed
        if keys[pygame.K_d]:
            player_dx += self.player.speed

        # Apply movement with screen bounds checking
        old_x, old_y = self.player.x, self.player.y
        self.player.move(player_dx, player_dy, self.width, self.height)

        # Calculate actual movement (in case of screen bounds)
        actual_dx = self.player.x - old_x
        actual_dy = self.player.y - old_y

        # Update player
        self.player.update_ammo()

        # Update player shooting state
        if self.player.shooting:
            self.player.update_shooting(self.bullets, self.width, self.height)

        # Update bullets - pass the player movement
        for bullet in self.bullets[:]:
            bullet.update(self.width, self.height, actual_dx, actual_dy)
            if not bullet.active:
                self.bullets.remove(bullet)

    def render(self):
        """Render the game screen."""
        # Clear the screen
        self.screen.fill(self.bg_color)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw the player
        self.player.draw(self.screen)

        # Update the display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            self.handle_events()

            # Update game state
            self.update()

            # Render
            self.render()

            # Control frame rate
            self.clock.tick(self.fps)

        # Clean up
        pygame.quit()
        sys.exit()