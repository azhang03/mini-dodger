import pygame
import math
import random
from collections import deque
from bullet import Bullet


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

        # Ammo System
        self.max_ammo = 3
        self.ammo = [1.0, 1.0, 1.0]  # Start with full ammo
        self.ammo_recharge_rate = 0.005  # Amount recharged per frame
        self.is_recharging = True

        # ----- BULLET CONFIGURATION -----
        # You can edit these values to change bullet behavior
        self.bullet_count = 12  # Number of bullets in a burst (total bullets across both columns)
        self.bullet_delay = 5  # Frames between each bullet in the same column
        self.bullet_speed = 10  # Speed of bullets
        self.bullet_size = (20, 8)  # Size of bullets (width, height)
        self.bullet_color = (0, 0, 255)  # Bullet color (blue)
        self.bullet_spread = 0  # Random spread factor (0 = no spread, higher = more spread)
        self.column_offset = 15  # Distance between left and right columns

        # Store the indicator length (will be set in draw_aim_indicator)
        self.indicator_length = 300

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

    def has_ammo(self):
        """Check if player has any ammo available."""
        for ammo in self.ammo:
            if ammo >= 1.0:
                return True
        return False

    def consume_ammo(self):
        """
        Consume one ammo unit from right to left, transferring partial charge.
        Returns True if successful, False if no ammo.
        """
        # Check if we have enough ammo to shoot (at least one full segment)
        total_ammo = sum(self.ammo)
        if total_ammo < 1.0:
            return False

        # Find rightmost ammo with any charge
        rightmost_index = -1
        for i in range(len(self.ammo) - 1, -1, -1):
            if self.ammo[i] > 0:
                rightmost_index = i
                break

        if rightmost_index == -1:
            return False  # No ammo found (shouldn't happen if total_ammo >= 1.0)

        # If the rightmost ammo is full, just consume it
        if self.ammo[rightmost_index] >= 1.0:
            self.ammo[rightmost_index] = 0.0
            return True

        # Otherwise, we need to consume from multiple segments
        remaining_to_consume = 1.0

        # Start with the rightmost segment with charge
        remaining_to_consume -= self.ammo[rightmost_index]
        self.ammo[rightmost_index] = 0.0

        # Move left consuming more ammo until we've consumed a full unit
        for i in range(rightmost_index - 1, -1, -1):
            if self.ammo[i] > 0:
                if self.ammo[i] >= remaining_to_consume:
                    self.ammo[i] -= remaining_to_consume
                    break
                else:
                    remaining_to_consume -= self.ammo[i]
                    self.ammo[i] = 0.0

        return True

    def update_ammo(self):
        """Update ammo recharge."""
        if not self.is_recharging:
            return

        # Recharge ammo sequentially (still left to right)
        for i in range(len(self.ammo)):
            if self.ammo[i] < 1.0:
                self.ammo[i] += self.ammo_recharge_rate
                if self.ammo[i] > 1.0:
                    self.ammo[i] = 1.0
                break  # Only recharge one slot at a time

    def start_shooting(self):
        """Start the shooting process."""
        # Don't allow shooting if already shooting or no ammo
        if self.shooting or not self.has_ammo():
            return

        # Consume one ammo
        if not self.consume_ammo():
            return

        self.shooting = True
        self.bullets_to_fire = self.bullet_count
        self.is_recharging = False  # Stop recharging while shooting

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
            self.is_recharging = True  # Start recharging again

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

        # Draw ammo bars
        self.draw_ammo_bars(screen)

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

    def draw_ammo_bars(self, screen):
        """
        Draw ammo bars below the player.

        Args:
            screen: Pygame surface to draw on
        """
        # Constants for ammo bars
        bar_width = 30
        bar_height = 8
        bar_spacing = 5
        bar_offset_y = 20  # Distance below player

        # Colors
        empty_color = (128, 128, 128)  # Gray
        filled_color = (255, 165, 0)  # Orange

        # Position bars below the player
        total_width = bar_width * len(self.ammo) + bar_spacing * (len(self.ammo) - 1)
        start_x = self.x - total_width / 2

        # Draw each ammo bar
        for i, ammo in enumerate(self.ammo):
            # Bar position
            bar_x = start_x + i * (bar_width + bar_spacing)
            bar_y = self.y + self.radius + bar_offset_y

            # Draw empty bar background
            pygame.draw.rect(screen, empty_color, (bar_x, bar_y, bar_width, bar_height))

            # Draw filled portion
            fill_width = int(bar_width * ammo)
            if fill_width > 0:
                pygame.draw.rect(screen, filled_color, (bar_x, bar_y, fill_width, bar_height))