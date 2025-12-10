# Design patterns in my purely python game engine

This game engine demonstrates different classic GoF design patterns working together.

---

## Creational Patterns

### 1. Factory Method Pattern
**What it does:** Creates objects using named static methods instead of constructors, making object creation more readable and flexible.

**Code Example:**
```python
# engine/math/vector2.py
class Vector2:
    @staticmethod
    def zero() -> 'Vector2':
        return Vector2(0, 0)
    
    @staticmethod
    def from_angle(angle: float, magnitude: float = 1.0) -> 'Vector2':
        return Vector2(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

# Usage
position = Vector2.zero()
velocity = Vector2.from_angle(math.pi / 4, 5.0)
```

**Interacts with:** Used by **Composite Pattern** (Transform) to create child vectors and by **Template Method Pattern** (game loop) to initialize objects.

---

### 2. Builder Pattern
**What it does:** Constructs complex objects step by step, allowing different configurations of the same object type.

**Code Example:**
```python
# engine/audio/sound_generator.py
class Sound:
    def __init__(self, name: str):
        self.name = name
        self.samples: List[float] = []
    
    def generate_tone(self, frequency: float, duration: float, wave_type: str = 'sine'):
        """Build sound with tone"""
        # ... generate samples
        return self
    
    def generate_sweep(self, start_freq: float, end_freq: float, duration: float):
        """Build sound with frequency sweep"""
        # ... generate samples
        return self

# Usage - build complex sounds step by step
laser_sound = Sound("laser").generate_sweep(800, 200, 0.1)
explosion_sound = Sound("explosion").generate_explosion(0.5)
```

**Interacts with:** Used by **Facade Pattern** (SoundGenerator) to create complex audio effects, and enables **Template Method Pattern** games to define custom sounds.

---

### 3. Prototype Pattern
**What it does:** Clones existing objects to create new ones, useful for copying complex state.

**Code Example:**
```python
# engine/math/vector2.py
class Vector2:
    def copy(self) -> 'Vector2':
        return Vector2(self.x, self.y)

# Usage
original = Vector2(10, 20)
clone = original.copy()  # New instance with same values
```

**Interacts with:** Essential for **Composite Pattern** (Transform) to avoid shared references when copying parent/child relationships.

---

## Structural Patterns

### 4. Composite Pattern
**What it does:** Organizes objects into tree structures where parent operations affect all children.

**Code Example:**
```python
# engine/math/transform.py
class Transform:
    def __init__(self):
        self._parent = None
        self._children = []
    
    @property
    def world_position(self) -> Vector2:
        if not self._parent:
            return self.position.copy()
        # Child inherits parent's transformation
        parent_world = self._parent.world_position
        # Apply parent transform to local position
        return parent_world + self.position.rotate(self._parent.world_rotation)
```

**Interacts with:** Uses **Prototype Pattern** to safely copy transform hierarchies, and works with **Facade Pattern** to provide simple transform access to users.

---

### 5. Facade Pattern
**What it does:** Provides a simple interface to hide complex subsystems.

**Code Example:**
```python
# engine/core/engine.py
class GameEngine:
    def __init__(self, title: str = "2D Game Engine", size: tuple = (800, 600)):
        # User doesn't need to know about these complex subsystems
        self.window = Window(title, size)
        self.input_manager = InputManager()
        self.renderer = Renderer(self.window.canvas)
        
        # Automatically connects them
        self.window.set_key_press_callback(self.input_manager.on_key_press)

# Simple usage - complexity hidden
engine = GameEngine("My Game", (800, 600))
engine.run()
```

**Interacts with:** Coordinates **Observer Pattern** (callbacks), **Strategy Pattern** (input profiles), and **Template Method Pattern** (game loop).

---

### 6. Adapter Pattern
**What it does:** Makes incompatible interfaces work together by wrapping one interface to match another.

**Code Example:**
```python
# engine/ecs/components.py
class TransformComponent(Component):  # ECS component interface
    def __init__(self, position: Vector2 = None, rotation: float = 0.0):
        super().__init__()
        self.position = position or Vector2(0, 0)
        
        # ADAPTER: Wraps regular Transform to work in ECS system
        self.transform = EngineTransform()
        self.transform.position = self.position
```

**Interacts with:** Bridges between the **Composite Pattern** (GameObject system) and the pure ECS architecture, allowing both paradigms to coexist.

---

## Behavioral Patterns

### 7. Observer Pattern
**What it does:** Notifies multiple objects when an event occurs without tight coupling.

**Code Example:**
```python
# engine/core/window.py
class Window:
    def set_key_press_callback(self, callback: Callable):
        self.key_press_callback = callback
    
    def _on_key_press(self, event):
        if self.key_press_callback:
            self.key_press_callback(event.keysym, event.keycode)

# engine/core/engine.py
self.window.set_key_press_callback(self.input_manager.on_key_press)
```

**Interacts with:** Used by **Facade Pattern** (GameEngine) to connect subsystems, and works with **Strategy Pattern** to enable configurable input handling.

---

### 8. Strategy Pattern
**What it does:** Allows swapping algorithms at runtime without changing client code.

**Code Example:**
```python
# engine/input/input_manager.py
class InputProfile:
    def __init__(self, name: str):
        self.key_mappings: Dict[str, str] = {}

class InputManager:
    def set_active_profile(self, profile_name: str):
        self.active_profile = self.profiles[profile_name]
    
    def is_action_pressed(self, action: str) -> bool:
        # Uses current strategy to map action to key
        key = self.active_profile.get_key_for_action(action)
        return self.is_key_pressed(key)

# Switch strategies at runtime
input_manager.set_active_profile("arrow_keys")  # or "default_keyboard"
```

**Interacts with:** Integrates with **Observer Pattern** (input events) and **Template Method Pattern** (game update loop) to provide flexible input handling.

---

### 9. Template Method Pattern
**What it does:** Defines the skeleton of an algorithm, letting subclasses override specific steps.

**Code Example:**
```python
# engine/core/engine.py
class GameEngine:
    def initialize(self):
        """Override this in your game"""
        pass
    
    def update(self, delta_time: float):
        """Override this in your game"""
        pass
    
    def run(self):
        """Template - defines the structure"""
        self.initialize()  # Hook point
        
        while self.is_running:
            self.input_manager.update()
            self.current_scene.update(self.delta_time)
            self.update(self.delta_time)  # Hook point
            self.render()  # Hook point
            self.window.update()
```

**Interacts with:** The core of **Facade Pattern** (GameEngine), coordinating **Observer Pattern** (input) and **Strategy Pattern** (configurable behaviors) in a fixed execution flow.

---