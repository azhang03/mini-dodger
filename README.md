# Brawlstars Dodge Trainer

A Python-based training application to help players improve their dodging and aiming skills (it's for Brawlstars but uhhh... let's avoid some copyright).

## Project Overview

This project aims to create a dedicated training environment where players can practice their dodging mechanics against various enemy types with different attack patterns, while simultaneously improving their aim and shooting precision.

### Current Status

Currently implemented:
- Basic player movement using WASD controls
- Object-oriented structure for future expansion
- Simple game loop with collision boundary enforcement

### Planned Features

- Multiple enemy types with different attack patterns and projectiles
- Difficulty progression system (either this or a difficulty menu)
- Performance metrics and scoring
- Visual feedback for hits and successful dodges
- Statistics tracking to measure improvement

## Controls

- **W**: Move up
- **A**: Move left
- **S**: Move down
- **D**: Move right
- *(Future)* **Mouse**: Aim
- *(Future)* **Right Click HOLD**: Aim-reticle
- *(Future)* **Right Click**: Shoot

## Project Structure

The application follows an object-oriented design to allow for easy expansion:

- `Player` class: Handles the player character, movement, and attributes
- `Game` class: Manages the game state, rendering, and main loop
- *(Future)* `Enemy` class: Base class for various enemy types
- *(Future)* `Projectile` class: Handles projectiles from both player and enemies
- *(Future)* `PowerUp` class: Special items that enhance player abilities

## Acknowledgements

- Inspired by the gameplay mechanics of Brawlstars by Supercell
- This is a fan project and is not affiliated with or endorsed by Supercell
