import pygame
import sys


class Player:
    def __init__(self, x, y, radius, color, speed):
        """
        Initialize the player circle.

        Args:
            x (int): Initial x position
            y (int): Initial y position
            radius (int): Circle radius
            color (tuple): RGB color value as (R, G, B)
            speed (int): Movement speed in pixels
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed

    def move(self, dx, dy, screen_width, screen_height):
        """
        Move the player by the given delta, keeping within screen bounds.

        Args:
            dx (int): Change in x position
            dy (int): Change in y position
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
        """
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy

        # Keep player within screen bounds
        if new_x - self.radius >= 0 and new_x + self.radius <= screen_width:
            self.x = new_x
        if new_y - self.radius >= 0 and new_y + self.radius <= screen_height:
            self.y = new_y

    def draw(self, screen):
        """
        Draw the player circle on the screen.

        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Game:
    def __init__(self, width=800, height=600, title="Circle Movement Game"):
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

        # Game state
        self.running = True

        # Background color (light beige)
        self.bg_color = (245, 245, 220)

    def handle_events(self):
        """Handle pygame events like quit and keypresses."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Get pressed keys for continuous movement
        keys = pygame.key.get_pressed()

        # Reset movement deltas
        dx, dy = 0, 0

        # WASD movement
        if keys[pygame.K_w]:
            dy -= self.player.speed
        if keys[pygame.K_s]:
            dy += self.player.speed
        if keys[pygame.K_a]:
            dx -= self.player.speed
        if keys[pygame.K_d]:
            dx += self.player.speed

        # Apply movement
        self.player.move(dx, dy, self.width, self.height)

    def update(self):
        """Update game state."""
        pass  # Will be used for additional game logic in the future

    def render(self):
        """Render the game screen."""
        # Clear the screen
        self.screen.fill(self.bg_color)

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


if __name__ == "__main__":
    # Create and run the game
    game = Game()
    game.run()