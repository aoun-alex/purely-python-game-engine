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

**Interacts with:** Used by **Composite Pattern** (Transform) to create child vectors and by **Flyweight Pattern** (SpriteAtlas) to create UV coordinates.

---

### 2. Singleton Pattern
**What it does:** Ensures only one instance of a class exists globally, providing a single access point.

**Code Example:**
```python
# engine/core/logger.py
_logger_manager = LoggerManager()  # Single global instance

def get_logger(name: str = "Engine") -> Logger:
    return _logger_manager.get_logger(name)

# Everyone accesses the same LoggerManager
logger = get_logger("MyGame")
```

**Interacts with:** Used throughout the engine by **Facade Pattern** (GameEngine) and **Template Method Pattern** (System classes) for centralized logging.

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

**Interacts with:** Uses **Chain of Responsibility Pattern** to traverse parent hierarchy, and **Proxy Pattern** to lazily compute world positions.

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

### 7. Flyweight Pattern
**What it does:** Shares common data between many objects to save memory.

**Code Example:**
```python
# engine/graphics/sprite.py
class SpriteAtlas:
    def __init__(self, texture_size: Vector2):
        self.sprites: Dict[str, Dict] = {}  # Shared data
    
    def add_sprite(self, name: str, position: Vector2, size: Vector2):
        # Multiple sprites reference same atlas instead of duplicating textures
        self.sprites[name] = {
            'position': position,
            'size': size,
            'uv_start': Vector2(position.x / self.texture_size.x, ...),
            'uv_end': Vector2(...)
        }
```

**Interacts with:** Used by **Visitor Pattern** (Renderer) which reads shared sprite data when rendering multiple instances.

---

### 8. Proxy Pattern
**What it does:** Provides a placeholder that controls access to another object, often for lazy evaluation.

**Code Example:**
```python
# engine/math/transform.py
class Transform:
    @property
    def world_position(self) -> Vector2:
        # Computed on-demand rather than stored
        if not self._parent:
            return self.position.copy()
        # Only calculates when accessed
        parent_world = self._parent.world_position
        scaled_pos = Vector2(self.position.x * parent_scale.x, ...)
        return parent_world + scaled_pos.rotate(parent_rotation)
```

**Interacts with:** Works with **Composite Pattern** by lazily computing transformations only when needed, improving performance.

---

## Behavioral Patterns

### 9. Observer Pattern
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

**Interacts with:** Used by **Facade Pattern** (GameEngine) to connect subsystems, and enables **Command Pattern** by triggering registered callbacks.

---

### 10. Strategy Pattern
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

### 11. Template Method Pattern
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

**Interacts with:** The core of **Facade Pattern** (GameEngine), coordinating **Observer Pattern** (input), **State Pattern** (scenes), and **Visitor Pattern** (rendering).

---

### 12. Command Pattern
**What it does:** Encapsulates requests as objects that can be stored, queued, and executed later.

**Code Example:**
```python
# engine/input/input_manager.py
class InputManager:
    def __init__(self):
        self.input_callbacks: Dict[str, Callable] = {}
    
    def register_input_callback(self, event_name: str, callback: Callable):
        """Store command"""
        self.input_callbacks[event_name] = callback
    
    def trigger_callback(self, event_name: str, *args, **kwargs):
        """Execute command"""
        if event_name in self.input_callbacks:
            self.input_callbacks[event_name](*args, **kwargs)
```

**Interacts with:** Extends **Observer Pattern** by storing callbacks as commands, and works with **Strategy Pattern** to map inputs to actions.

---

### 13. State Pattern
**What it does:** Changes object behavior when its internal state changes.

**Code Example:**
```python
# engine/core/engine.py
class GameEngine:
    def load_scene(self, scene: Scene):
        self.next_scene = scene
    
    def run(self):
        while self.is_running:
            # State transition handling
            if self.next_scene:
                if self.current_scene:
                    self.current_scene.cleanup()
                self.current_scene = self.next_scene  # Change state
                self.current_scene.initialize()
                self.next_scene = None
            
            # Behavior depends on current state (scene)
            self.current_scene.update(self.delta_time)
```

**Interacts with:** Managed by **Template Method Pattern** (game loop) and coordinates with **Visitor Pattern** to render the active scene.

---

### 14. Iterator Pattern
**What it does:** Provides a way to traverse collections without exposing internal structure.

**Code Example:**
```python
# engine/ecs/entity.py
class EntityManager:
    def get_all_entities(self) -> List[Entity]:
        return list(self.entities.values())
    
    def get_entities_with_components(self, *component_types: Type) -> List[Entity]:
        result_ids = self.component_index.get(component_types[0], set()).copy()
        for component_type in component_types[1:]:
            result_ids &= self.component_index.get(component_type, set())
        return [self.entities[eid] for eid in result_ids]

# Usage
for entity in entity_manager.get_all_entities():
    # Process each entity
```

**Interacts with:** Provides collections to **Visitor Pattern** (systems that process entities) and **Template Method Pattern** (update loops).

---

### 15. Visitor Pattern
**What it does:** Separates operations from the objects they operate on, letting you add new operations without modifying objects.

**Code Example:**
```python
# engine/scene/scene.py
class Scene:
    def render(self, renderer: Renderer):
        """Renderer visits each object"""
        sorted_objects = sorted(self.game_objects, key=lambda obj: obj.z_order)
        
        for obj in sorted_objects:
            obj.render(renderer)  # Object accepts visitor

# engine/scene/game_object.py
class GameObject:
    def render(self, renderer: 'Renderer'):
        """Accept visitor"""
        for component in self.components_list:
            component.render(renderer)
```

**Interacts with:** The Renderer visits objects organized by **Iterator Pattern**, drawing sprites managed by **Flyweight Pattern** (SpriteAtlas).

---

### 16. Chain of Responsibility Pattern
**What it does:** Passes requests along a chain of handlers until one handles it.

**Code Example:**
```python
# engine/math/transform.py
class Transform:
    @property
    def world_position(self) -> Vector2:
        if not self._parent:
            return self.position.copy()  # End of chain
        
        # Pass request up the chain
        parent_world = self._parent.world_position  # Recursive
        parent_rotation = self._parent.world_rotation
        parent_scale = self._parent.world_scale
        
        # Apply transformation and return
        scaled_pos = Vector2(self.position.x * parent_scale.x, ...)
        return parent_world + scaled_pos.rotate(parent_rotation)
```

**Interacts with:** Core mechanism of **Composite Pattern** for hierarchical transforms, used by **Proxy Pattern** for lazy evaluation.

---