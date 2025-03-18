import pygame
import math
import random
from collections import deque
from bullet import Bullet


class Enemy:
    def __init__(self, x, y, radius, color, speed):
        """
        Initialize the enemy.

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

        # Health System
        self.max_health = 100
        self.health = 100

        # AI properties
        self.target = None
        self.attack_range = 300  # Same as bullet indicator length
        self.attack_cooldown = 0
        self.min_attack_cooldown = 60  # Frames between attack attempts

        # ----- BULLET CONFIGURATION -----
        # You can edit these values to change bullet behavior
        self.bullet_count = 12  # Number of bullets in a burst (total bullets across both columns)
        self.bullet_delay = 10  # Frames between each bullet in the same column
        self.bullet_speed = 10  # Speed of bullets
        self.bullet_size = (20, 8)  # Size of bullets (width, height)
        self.bullet_color = (0, 255, 0)  # Bullet color (green)
        self.bullet_spread = 0.05  # Random spread factor (0 = no spread, higher = more spread)
        self.column_offset = 15  # Distance between left and right columns

        # Store the indicator length for bullet max distance
        self.indicator_length = 300

    def move_towards_target(self, screen_width, screen_height):
        """Move towards the target if it exists and is out of range."""
        if not self.target:
            return 0, 0  # No movement if no target

        # Calculate distance to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # If target is out of range, move towards it
        if distance > self.attack_range - self.radius - self.target.radius:
            # Normalize direction
            if distance > 0:
                dx /= distance
                dy /= distance

            # Calculate movement
            move_x = dx * self.speed
            move_y = dy * self.speed

            # Apply movement
            self.move(move_x, move_y, screen_width, screen_height)
            return move_x, move_y

        return 0, 0  # No movement if target is in range

    def move(self, dx, dy, screen_width, screen_height):
        """
        Move the enemy by the given delta, keeping within screen bounds.

        Args:
            dx (int): Change in x position
            dy (int): Change in y position
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
        """
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy

        # Keep enemy within screen bounds
        if new_x - self.radius >= 0 and new_x + self.radius <= screen_width:
            self.x = new_x
        if new_y - self.radius >= 0 and new_y + self.radius <= screen_height:
            self.y = new_y

    def update_aim(self):
        """Update the aim direction based on target position."""
        if not self.target:
            return

        # Calculate direction vector from enemy to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y

        # Normalize the direction vector
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:  # Avoid division by zero
            self.aim_direction = (dx / length, dy / length)

    def has_ammo(self):
        """Check if enemy has any ammo available."""
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

        # Recharge ammo sequentially (left to right)
        for i in range(len(self.ammo)):
            if self.ammo[i] < 1.0:
                self.ammo[i] += self.ammo_recharge_rate
                if self.ammo[i] > 1.0:
                    self.ammo[i] = 1.0
                break  # Only recharge one slot at a time

    def can_attack_target(self):
        """Check if the enemy can attack the target."""
        if not self.target or self.shooting or not self.has_ammo():
            return False

        # Calculate distance to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check if target is in range and cooldown is over
        return (distance <= self.attack_range - self.radius - self.target.radius and
                self.attack_cooldown <= 0)

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
        self.attack_cooldown = self.min_attack_cooldown  # Set cooldown

        # Calculate perpendicular vector for column positioning
        perp_x = -self.aim_direction[1]
        perp_y = self.aim_direction[0]

        # Pre-calculate all bullet directions for consistent trajectory
        # Creating a staggered pattern in two columns like Colt in Brawlstars
        for i in range(self.bullet_count):
            # Apply random spread to direction
            spread_x = random.uniform(-self.bullet_spread, self.bullet_spread)
            spread_y = random.uniform(-self.bullet_spread, self.bullet_spread)

            # Normalize the direction vector after adding spread
            dir_x = self.aim_direction[0] + spread_x
            dir_y = self.aim_direction[1] + spread_y
            length = math.sqrt(dir_x ** 2 + dir_y ** 2)
            bullet_dir = (dir_x / length, dir_y / length)

            # Determine if this bullet is in the left or right column (alternating)
            is_left_column = (i % 2 == 0)

            # Calculate offset based on column
            offset_factor = -0.5 if is_left_column else 0.5
            offset_x = perp_x * self.column_offset * offset_factor
            offset_y = perp_y * self.column_offset * offset_factor

            # Calculate delay: stagger left and right columns
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
        queue_list = list(self.bullet_queue)
        for i in sorted(to_remove, reverse=True):
            queue_list.pop(i)
        self.bullet_queue = deque(queue_list)

        # Check if shooting is complete
        if len(self.bullet_queue) == 0:
            self.shooting = False
            self.is_recharging = True  # Start recharging again

    def update(self, bullets, screen_width, screen_height):
        """Update enemy state."""
        # Update ammo
        self.update_ammo()

        # Decrease attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update aim if we have a target
        self.update_aim()

        # If not shooting, check if we can attack
        if not self.shooting and self.can_attack_target():
            self.start_shooting()

        # Update shooting state if we're shooting
        if self.shooting:
            self.update_shooting(bullets, screen_width, screen_height)

    def take_damage(self, damage):
        """Apply damage to the enemy."""
        self.health -= damage
        self.health = max(0, self.health)  # Don't go below 0
        return self.health <= 0  # Return True if dead

    def draw(self, screen):
        """
        Draw the enemy on the screen.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw the enemy circle
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        # Draw health bar
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        """
        Draw health bar above the enemy.

        Args:
            screen: Pygame surface to draw on
        """
        # Health bar settings
        bar_width = 60
        bar_height = 8
        bar_offset_y = 20  # Distance above enemy

        # Colors
        background_color = (64, 64, 64)  # Dark gray
        health_color = (255, 0, 0)  # Red

        # Position bar above the enemy
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - bar_offset_y

        # Draw background
        pygame.draw.rect(screen, background_color, (bar_x, bar_y, bar_width, bar_height))

        # Draw filled portion based on health percentage
        health_width = int(bar_width * (self.health / self.max_health))
        if health_width > 0:
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))