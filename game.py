import pygame
import sys
import random
from player import Player
from enemy import Enemy


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
            x=width // 4,
            y=height // 2,
            radius=30,
            color=(255, 0, 0),  # Red
            speed=5
        )

        # Create enemy
        self.enemy = Enemy(
            x=width * 3 // 4,
            y=height // 2,
            radius=30,
            color=(0, 0, 255),  # Blue
            speed=3
        )

        # Set target for enemy to player
        self.enemy.target = self.player

        # Initialize bullets lists
        self.player_bullets = []
        self.enemy_bullets = []

        # Game state
        self.running = True

        # Background color (light beige)
        self.bg_color = (245, 245, 220)

        # Damage values
        self.bullet_damage = 10

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
            self.player.update_shooting(self.player_bullets, self.width, self.height)

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.update(self.width, self.height)
            if not bullet.active:
                self.player_bullets.remove(bullet)
                continue

            # Check collision with enemy
            dx = bullet.x - self.enemy.x
            dy = bullet.y - self.enemy.y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < self.enemy.radius:
                # Hit enemy
                is_dead = self.enemy.take_damage(self.bullet_damage)
                bullet.active = False
                self.player_bullets.remove(bullet)

                # Respawn enemy if dead
                if is_dead:
                    self.respawn_enemy()

        # Update enemy and its movement
        old_enemy_x, old_enemy_y = self.enemy.x, self.enemy.y
        enemy_dx, enemy_dy = self.enemy.move_towards_target(self.width, self.height)

        # Update enemy state
        self.enemy.update(self.enemy_bullets, self.width, self.height)

        # Calculate actual enemy movement
        actual_enemy_dx = self.enemy.x - old_enemy_x
        actual_enemy_dy = self.enemy.y - old_enemy_y

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update(self.width, self.height)
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
                continue

            # Check collision with player
            dx = bullet.x - self.player.x
            dy = bullet.y - self.player.y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < self.player.radius:
                # Hit player (could implement player health in the future)
                bullet.active = False
                self.enemy_bullets.remove(bullet)

    def respawn_enemy(self):
        """Respawn the enemy at a random position."""
        # Respawn with full health
        self.enemy.health = self.enemy.max_health

        # Find a position away from the player
        min_distance = 300  # Minimum distance from player

        while True:
            x = random.randint(self.enemy.radius, self.width - self.enemy.radius)
            y = random.randint(self.enemy.radius, self.height - self.enemy.radius)

            dx = x - self.player.x
            dy = y - self.player.y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance >= min_distance:
                self.enemy.x = x
                self.enemy.y = y
                break

    def render(self):
        """Render the game screen."""
        # Clear the screen
        self.screen.fill(self.bg_color)

        # Draw player bullets
        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        # Draw the enemy
        self.enemy.draw(self.screen)

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