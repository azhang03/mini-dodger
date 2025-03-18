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

        # Set up fonts
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 72)

        # Set up clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Initialize game
        self.init_game()

        # Background color (light beige)
        self.bg_color = (245, 245, 220)

    def init_game(self):
        """Initialize or reset the game state."""
        # Create player
        self.player = Player(
            x=self.width // 4,
            y=self.height // 2,
            radius=30,
            color=(255, 0, 0),  # Red
            speed=5
        )

        # Create enemy
        self.enemy = Enemy(
            x=self.width * 3 // 4,
            y=self.height // 2,
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
        self.game_over = False

        # Damage values
        self.player_bullet_damage = 10
        self.enemy_bullet_damage = 1

        # Hit notification
        self.show_hit_notification = False
        self.hit_notification_timer = 0
        self.hit_notification_duration = 30  # frames (half second at 60fps)

    def handle_events(self):
        """Handle pygame events like quit and keypresses."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    # Check for Try Again button click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.try_again_rect.collidepoint(mouse_pos):
                        self.init_game()  # Reset the game
                    elif self.quit_rect.collidepoint(mouse_pos):
                        self.running = False
                elif event.button == 3:  # Right mouse button (when game is active)
                    self.player.aiming = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.game_over and event.button == 3 and self.player.aiming:
                    self.player.aiming = False
                    self.player.start_shooting()

        if not self.game_over:
            # Get mouse position for aiming
            mouse_pos = pygame.mouse.get_pos()
            self.player.update_aim(mouse_pos)

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Update hit notification
        if self.show_hit_notification:
            self.hit_notification_timer -= 1
            if self.hit_notification_timer <= 0:
                self.show_hit_notification = False

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
        self.player.move(player_dx, player_dy, self.width, self.height)

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
                is_dead = self.enemy.take_damage(self.player_bullet_damage)
                bullet.active = False
                self.player_bullets.remove(bullet)

                # Respawn enemy if dead
                if is_dead:
                    self.respawn_enemy()

        # Update enemy and its movement
        self.enemy.move_towards_target(self.width, self.height)

        # Update enemy state
        self.enemy.update(self.enemy_bullets, self.width, self.height)

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
                # Hit player
                is_dead = self.player.take_damage(self.enemy_bullet_damage)
                bullet.active = False
                self.enemy_bullets.remove(bullet)

                # Show hit notification
                self.show_hit_notification = True
                self.hit_notification_timer = self.hit_notification_duration

                # Check if player is dead
                if is_dead:
                    self.game_over = True

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

        if self.game_over:
            self.render_game_over()
        else:
            self.render_gameplay()

        # Update the display
        pygame.display.flip()

    def render_gameplay(self):
        """Render the main gameplay elements."""
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

        # Draw hit notification if active
        if self.show_hit_notification:
            hit_text = self.font.render("Hit!", True, (255, 0, 0))
            text_rect = hit_text.get_rect(center=(self.width // 2, self.height // 4))
            self.screen.blit(hit_text, text_rect)

    def render_game_over(self):
        """Render the game over screen."""
        # Game over text
        game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
        go_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(game_over_text, go_rect)

        # Button dimensions
        button_width = 200
        button_height = 50
        button_spacing = 20

        # Try Again button
        try_again_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            self.height // 2,
            button_width,
            button_height
        )
        self.try_again_rect = try_again_button
        pygame.draw.rect(self.screen, (0, 200, 0), try_again_button)
        pygame.draw.rect(self.screen, (0, 100, 0), try_again_button, 3)
        try_text = self.font.render("Try Again", True, (255, 255, 255))
        try_text_rect = try_text.get_rect(center=try_again_button.center)
        self.screen.blit(try_text, try_text_rect)

        # Quit button
        quit_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            self.height // 2 + button_height + button_spacing,
            button_width,
            button_height
        )
        self.quit_rect = quit_button
        pygame.draw.rect(self.screen, (200, 0, 0), quit_button)
        pygame.draw.rect(self.screen, (100, 0, 0), quit_button, 3)
        quit_text = self.font.render("Quit", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)

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