"""
Snake Game built with the 2D Game Engine
Classic snake gameplay with scoring and increasing difficulty
"""

from engine import (
    GameEngine, Scene, GameObject, Vector2,
    Renderer, InputManager, Sprite
)
import random
import math


class SnakeSegment(GameObject):
    """Individual snake body segment"""

    def __init__(self, position: Vector2, is_head: bool = False):
        super().__init__("SnakeHead" if is_head else "SnakeSegment")
        self.set_position(position)

        # Visual component
        color = '#00FF00' if is_head else '#00AA00'
        sprite = Sprite(color=color, size=Vector2(18, 18), shape='rectangle')
        self.add_component(sprite)

        self.is_head = is_head
        self.grid_pos = Vector2(int(position.x / 20), int(position.y / 20))


class Food(GameObject):
    """Food item for snake to eat"""

    def __init__(self, position: Vector2):
        super().__init__("Food")
        self.set_position(position)

        # Visual component - red circle
        sprite = Sprite(color='#FF0000', size=Vector2(16, 16), shape='circle')
        self.add_component(sprite)

        self.grid_pos = Vector2(int(position.x / 20), int(position.y / 20))

        # Pulsing animation
        self.pulse_timer = 0.0


class Wall(GameObject):
    """Wall obstacle"""

    def __init__(self, position: Vector2):
        super().__init__("Wall")
        self.set_position(position)

        # Visual component
        sprite = Sprite(color='#666666', size=Vector2(20, 20), shape='rectangle')
        self.add_component(sprite)


class SnakeGame(GameEngine):
    """Main Snake Game"""

    def __init__(self):
        super().__init__("Snake Game", (800, 600), target_fps=60)

        # Game state
        self.grid_width = 40
        self.grid_height = 30
        self.cell_size = 20

        self.snake_segments = []
        self.direction = Vector2(1, 0)  # Start moving right
        self.next_direction = Vector2(1, 0)
        self.move_timer = 0.0
        self.move_delay = 0.15  # Seconds between moves

        self.food = None
        self.score = 0
        self.game_over = False
        self.game_started = False

        # UI elements
        self.score_text = None
        self.title_text = None
        self.game_over_text = None

    def initialize(self):
        """Initialize the game"""
        # Create main scene
        self.game_scene = Scene("Game")
        self.load_scene(self.game_scene)

        # Create walls
        self.create_walls()

        # Create initial snake
        self.create_snake()

        # Spawn first food
        self.spawn_food()

        print("Snake Game Started!")
        print("Controls: Arrow Keys or WASD")
        print("Press Space to start")
        print("Press R to restart after game over")

    def create_walls(self):
        """Create boundary walls"""
        # Top and bottom walls
        for x in range(self.grid_width):
            # Top wall
            wall = Wall(Vector2(x * self.cell_size + 10, 10))
            self.game_scene.add_object(wall)
            # Bottom wall
            wall = Wall(Vector2(x * self.cell_size + 10, (self.grid_height - 1) * self.cell_size + 10))
            self.game_scene.add_object(wall)

        # Left and right walls
        for y in range(1, self.grid_height - 1):
            # Left wall
            wall = Wall(Vector2(10, y * self.cell_size + 10))
            self.game_scene.add_object(wall)
            # Right wall
            wall = Wall(Vector2((self.grid_width - 1) * self.cell_size + 10, y * self.cell_size + 10))
            self.game_scene.add_object(wall)

    def create_snake(self):
        """Create the initial snake"""
        # Start in the middle
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2

        # Create 3 segments
        for i in range(3):
            x = (start_x - i) * self.cell_size + 10
            y = start_y * self.cell_size + 10
            segment = SnakeSegment(Vector2(x, y), is_head=(i == 0))
            self.snake_segments.append(segment)
            self.game_scene.add_object(segment)

    def spawn_food(self):
        """Spawn food at random empty position"""
        # Remove old food if exists
        if self.food:
            self.game_scene.remove_object(self.food)

        # Find empty position
        while True:
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)

            # Check if position is occupied by snake
            occupied = False
            for segment in self.snake_segments:
                if segment.grid_pos.x == x and segment.grid_pos.y == y:
                    occupied = True
                    break

            if not occupied:
                world_x = x * self.cell_size + 10
                world_y = y * self.cell_size + 10
                self.food = Food(Vector2(world_x, world_y))
                self.game_scene.add_object(self.food)
                break

    def update(self, delta_time: float):
        """Main game update loop"""
        if self.game_over:
            # Check for restart
            if self.input_manager.is_key_just_pressed('r'):
                self.restart_game()
            return

        # Start game on space press
        if not self.game_started:
            if self.input_manager.is_key_just_pressed('space'):
                self.game_started = True
            return

        # Handle input
        self.handle_input()

        # Update snake movement
        self.move_timer += delta_time
        if self.move_timer >= self.move_delay:
            self.move_timer = 0.0
            self.move_snake()

        # Animate food
        if self.food:
            self.food.pulse_timer += delta_time * 5
            sprite = self.food.get_component(Sprite)
            if sprite:
                # Pulsing effect
                scale = 1.0 + math.sin(self.food.pulse_timer) * 0.1
                self.food.set_scale(Vector2(scale, scale))

    def handle_input(self):
        """Handle player input"""
        # Only allow perpendicular direction changes
        if self.input_manager.is_key_pressed('up') or self.input_manager.is_key_pressed('w'):
            if self.direction.y == 0:  # Not already moving vertically
                self.next_direction = Vector2(0, -1)
        elif self.input_manager.is_key_pressed('down') or self.input_manager.is_key_pressed('s'):
            if self.direction.y == 0:
                self.next_direction = Vector2(0, 1)
        elif self.input_manager.is_key_pressed('left') or self.input_manager.is_key_pressed('a'):
            if self.direction.x == 0:  # Not already moving horizontally
                self.next_direction = Vector2(-1, 0)
        elif self.input_manager.is_key_pressed('right') or self.input_manager.is_key_pressed('d'):
            if self.direction.x == 0:
                self.next_direction = Vector2(1, 0)

    def move_snake(self):
        """Move the snake one step"""
        # Update direction
        self.direction = self.next_direction

        # Get current head position
        head = self.snake_segments[0]
        current_grid_pos = head.grid_pos.copy()

        # Calculate new head position
        new_grid_pos = Vector2(
            current_grid_pos.x + self.direction.x,
            current_grid_pos.y + self.direction.y
        )

        # Check collision with walls
        if (new_grid_pos.x <= 0 or new_grid_pos.x >= self.grid_width - 1 or
                new_grid_pos.y <= 0 or new_grid_pos.y >= self.grid_height - 1):
            self.end_game()
            return

        # Check collision with self
        for segment in self.snake_segments:
            if segment.grid_pos.x == new_grid_pos.x and segment.grid_pos.y == new_grid_pos.y:
                self.end_game()
                return

        # Check if eating food
        ate_food = False
        if self.food and new_grid_pos.x == self.food.grid_pos.x and new_grid_pos.y == self.food.grid_pos.y:
            ate_food = True
            self.score += 10
            self.spawn_food()

            # Speed up slightly
            self.move_delay = max(0.05, self.move_delay - 0.005)

            print(f"Score: {self.score}")

        # Move snake segments
        if ate_food:
            # Add new head without removing tail (snake grows)
            new_world_pos = Vector2(
                new_grid_pos.x * self.cell_size + 10,
                new_grid_pos.y * self.cell_size + 10
            )
            new_head = SnakeSegment(new_world_pos, is_head=True)
            new_head.grid_pos = new_grid_pos

            # Old head becomes body
            old_head = self.snake_segments[0]
            old_head.is_head = False
            old_head_sprite = old_head.get_component(Sprite)
            if old_head_sprite:
                old_head_sprite.color = '#00AA00'

            self.snake_segments.insert(0, new_head)
            self.game_scene.add_object(new_head)
        else:
            # Move all segments forward
            # Remove tail
            tail = self.snake_segments.pop()
            self.game_scene.remove_object(tail)

            # Add new head
            new_world_pos = Vector2(
                new_grid_pos.x * self.cell_size + 10,
                new_grid_pos.y * self.cell_size + 10
            )
            new_head = SnakeSegment(new_world_pos, is_head=True)
            new_head.grid_pos = new_grid_pos

            # Old head becomes body
            old_head = self.snake_segments[0]
            old_head.is_head = False
            old_head_sprite = old_head.get_component(Sprite)
            if old_head_sprite:
                old_head_sprite.color = '#00AA00'

            self.snake_segments.insert(0, new_head)
            self.game_scene.add_object(new_head)

    def end_game(self):
        """End the game"""
        self.game_over = True
        print(f"Game Over! Final Score: {self.score}")
        print("Press R to restart")

    def restart_game(self):
        """Restart the game"""
        # Clear scene
        self.game_scene.cleanup()

        # Reset state
        self.snake_segments = []
        self.direction = Vector2(1, 0)
        self.next_direction = Vector2(1, 0)
        self.move_timer = 0.0
        self.move_delay = 0.15
        self.food = None
        self.score = 0
        self.game_over = False
        self.game_started = False

        # Recreate game
        self.create_walls()
        self.create_snake()
        self.spawn_food()

        print("Game Restarted!")

    def render(self):
        """Custom rendering for UI"""
        # Draw score
        self.renderer.draw_text(
            Vector2(400, 30),
            f"Score: {self.score}",
            '#FFFFFF',
            font_size=20
        )

        # Draw instructions
        if not self.game_started:
            self.renderer.draw_text(
                Vector2(400, 300),
                "Press SPACE to start",
                '#FFFF00',
                font_size=24
            )
            self.renderer.draw_text(
                Vector2(400, 340),
                "Use Arrow Keys or WASD to move",
                '#FFFFFF',
                font_size=16
            )

        # Draw game over message
        if self.game_over:
            self.renderer.draw_text(
                Vector2(400, 250),
                "GAME OVER!",
                '#FF0000',
                font_size=32
            )
            self.renderer.draw_text(
                Vector2(400, 290),
                f"Final Score: {self.score}",
                '#FFFFFF',
                font_size=24
            )
            self.renderer.draw_text(
                Vector2(400, 330),
                "Press R to restart",
                '#FFFF00',
                font_size=20
            )

        # Draw FPS
        self.renderer.draw_text(
            Vector2(50, 30),
            f"FPS: {int(self.get_fps())}",
            '#888888',
            font_size=12
        )


# Run the game
if __name__ == "__main__":
    game = SnakeGame()
    game.run()