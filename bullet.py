import pygame
import math


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

        # Track relative position to player
        self.rel_x = 0
        self.rel_y = 0

    def update(self, screen_width, screen_height, player_dx=0, player_dy=0):
        """
        Update bullet position.

        Args:
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
            player_dx (int): Player's x movement in this frame
            player_dy (int): Player's y movement in this frame
        """
        # Move the bullet with the player
        self.x += player_dx
        self.y += player_dy

        # Also move the start position with the player to maintain correct distance calculation
        self.start_x += player_dx
        self.start_y += player_dy

        # Move the bullet according to its direction and speed
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