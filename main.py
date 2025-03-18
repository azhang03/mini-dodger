import pygame
import sys
import math
import random
from collections import deque


class Bullet:
    def __init__(self, x, y, direction, speed, size, color, max_distance):
        """
        Initialize a bullet.

        Args:
            x (int): Starting x position
            y (int): Starting y position
            direction (tuple): Direction vector (dx, dy)
            speed (int): Bullet speed in pixels per frame
            size (tuple): Width and height of the bullet
            color (tuple): RGB color value as (R, G, B)
            max_distance (float): Maximum travel distance for the bullet
        """
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.direction = direction
        self.speed = speed
        self.width, self.height = size
        self.color = color
        self.active = True
        self.max_distance = max_distance
        self.distance_traveled = 0

    def update(self, screen_width, screen_height):
        """
        Update bullet position.

        Args:
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
        """
        # Move the bullet
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        # Calculate distance traveled
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        self.distance_traveled = math.sqrt(dx * dx + dy * dy)

        # Check if bullet has traveled its maximum distance
        if self.distance_traveled >= self.max_distance:
            self.active = False
            return

        # Check if bullet is off-screen
        if (self.x < -self.width or self.x > screen_width + self.width or
                self.y < -self.height or self.y > screen_height + self.height):
            self.active = False

    def draw(self, screen):
        """
        Draw the bullet on the screen.

        Args:
            screen: Pygame surface to draw on
        """
        # Calculate the rectangle for the bullet
        rect = pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )

        # Rotate the bullet to match its direction
        angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))

        # Create a surface for the rotated bullet
        bullet_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, self.color, (0, 0, self.width, self.height))

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(bullet_surface, angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

        # Draw the rotated bullet
        screen.blit(rotated_surface, rotated_rect)


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
        self.aiming = False
        self.aim_direction = (1, 0)  # Default direction (right)

        # Shooting properties
        self.shooting = False
        self.bullets_to_fire = 0
        self.bullet_queue = deque()

        # ----- BULLET CONFIGURATION -----
        # You can edit these values to change bullet behavior
        self.bullet_count = 12  # Number of bullets in a burst (total bullets across both columns)
        self.bullet_delay = 10  # Frames between each bullet in the same column
        self.bullet_speed = 10  # Speed of bullets
        self.bullet_size = (20, 8)  # Size of bullets (width, height)
        self.bullet_color = (0, 0, 255)  # Bullet color (blue)
        self.bullet_spread = 0  # Random spread factor (0 = no spread, higher = more spread)
        self.column_offset = 15  # Distance between left and right columns
        # ------------------------------

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

    def update_aim(self, mouse_pos):
        """
        Update the aim direction based on mouse position.

        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        """
        # Calculate direction vector from player to mouse
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y

        # Normalize the direction vector (make it length 1)
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:  # Avoid division by zero
            self.aim_direction = (dx / length, dy / length)

    def start_shooting(self):
        """Start the shooting process."""
        self.shooting = True
        self.bullets_to_fire = self.bullet_count

        # Calculate perpendicular vector for column positioning
        perp_x = -self.aim_direction[1]
        perp_y = self.aim_direction[0]

        # Pre-calculate all bullet directions for consistent trajectory
        # Creating a staggered pattern in two columns like Colt in Brawlstars
        for i in range(self.bullet_count):
            # Apply random spread to direction
            # ----- BULLET SPREAD CONFIGURATION -----
            # Modify bullet_spread above to change the amount of spread
            spread_x = random.uniform(-self.bullet_spread, self.bullet_spread)
            spread_y = random.uniform(-self.bullet_spread, self.bullet_spread)

            # Normalize the direction vector after adding spread
            dir_x = self.aim_direction[0] + spread_x
            dir_y = self.aim_direction[1] + spread_y
            length = math.sqrt(dir_x ** 2 + dir_y ** 2)
            bullet_dir = (dir_x / length, dir_y / length)

            # Determine if this bullet is in the left or right column (alternating)
            # Even indices go to left column, odd to right column
            is_left_column = (i % 2 == 0)

            # Calculate offset based on column
            offset_factor = -0.5 if is_left_column else 0.5
            offset_x = perp_x * self.column_offset * offset_factor
            offset_y = perp_y * self.column_offset * offset_factor

            # Calculate delay: stagger left and right columns
            # Each column fires at twice the delay rate, with the right column delayed by half the interval
            column_delay = self.bullet_delay * (i // 2)  # Integer division to group by pairs
            if not is_left_column:
                column_delay += self.bullet_delay // 2  # Half delay offset for right column

            # Add to queue with position offset and delay counter
            self.bullet_queue.append((bullet_dir, column_delay, offset_x, offset_y))

    def update_shooting(self, bullets, screen_width, screen_height):
        """
        Update shooting state and create bullets as needed.

        Args:
            bullets (list): List of active bullets
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
        """
        # Process bullet queue
        to_remove = []
        for i, (bullet_dir, delay, offset_x, offset_y) in enumerate(self.bullet_queue):
            if delay <= 0:
                # Create the bullet with column offset
                # ----- BULLET CREATION CONFIGURATION -----
                # Modify bullet_size, bullet_speed, and bullet_color above
                # to change the appearance and behavior of bullets
                start_x = self.x + offset_x
                start_y = self.y + offset_y

                new_bullet = Bullet(
                    start_x,
                    start_y,
                    bullet_dir,
                    self.bullet_speed,
                    self.bullet_size,
                    self.bullet_color,
                    self.indicator_length  # Pass the max distance to match indicator length
                )
                bullets.append(new_bullet)
                to_remove.append(i)
            else:
                # Decrease delay counter
                self.bullet_queue[i] = (bullet_dir, delay - 1, offset_x, offset_y)

        # Remove processed bullets from queue
        # Convert to list, modify, then convert back to deque (since deque doesn't support pop with index)
        queue_list = list(self.bullet_queue)
        for i in sorted(to_remove, reverse=True):
            queue_list.pop(i)
        self.bullet_queue = deque(queue_list)

        # Check if shooting is complete
        if len(self.bullet_queue) == 0:
            self.shooting = False

    def draw(self, screen):
        """
        Draw the player circle on the screen.

        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        # Draw aim indicator if aiming
        if self.aiming:
            self.draw_aim_indicator(screen)

    def draw_aim_indicator(self, screen):
        """
        Draw the rectangular aim indicator when right-clicking.

        Args:
            screen: Pygame surface to draw on
        """
        # Constants for the aim indicator
        indicator_length = 300
        indicator_width = 30
        indicator_color = (255, 255, 0)  # Yellow

        # Store the indicator length for bullet max distance
        self.indicator_length = indicator_length

        # Calculate the endpoint of the indicator
        end_x = self.x + self.aim_direction[0] * indicator_length
        end_y = self.y + self.aim_direction[1] * indicator_length

        # Calculate the perpendicular vector for width
        perp_x = -self.aim_direction[1]
        perp_y = self.aim_direction[0]

        # Calculate the four corners of the rectangle
        half_width = indicator_width / 2
        points = [
            (self.x + perp_x * half_width, self.y + perp_y * half_width),
            (self.x - perp_x * half_width, self.y - perp_y * half_width),
            (end_x - perp_x * half_width, end_y - perp_y * half_width),
            (end_x + perp_x * half_width, end_y + perp_y * half_width)
        ]

        # Draw the rectangle
        pygame.draw.polygon(screen, indicator_color, points)


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
        # Update player shooting state
        if self.player.shooting:
            self.player.update_shooting(self.bullets, self.width, self.height)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(self.width, self.height)
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


if __name__ == "__main__":
    # Create and run the game
    game = Game()
    game.run()