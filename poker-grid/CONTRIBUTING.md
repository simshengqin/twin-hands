# Contributing to Poker Grid

## For AI Assistants (Claude)

**Read [`claude.md`](claude.md) first!** It contains complete instructions for working with this codebase.

Quick rules:
1. Never modify `legacy_code/` or `party-house/`
2. All new code goes in `src/`
3. Follow the Godot-ready architecture patterns
4. Use lowercase config attributes: `config.max_hands` not `config.MAX_HANDS`

## For Human Developers

### Architecture

This project follows **Godot 4.5 best practices**:

```
src/
├── resources/    # Data (extends Resource in Godot)
├── managers/     # Logic (extends Node in Godot)
├── utils/        # Static helpers
└── autoload/     # Global singletons
```

### Key Principles

1. **Resources = Data**
   - Pure data structures
   - No complex game logic
   - Can be serialized

2. **Managers = Logic**
   - Game controllers
   - Single responsibility
   - Emit events via Events singleton

3. **Utils = Helpers**
   - Static functions
   - No state
   - Reusable

4. **Events = Communication**
   - Global event bus
   - Decouples systems
   - Signal pattern

### Adding New Code

#### New Resource
```python
# src/resources/example_resource.py
from dataclasses import dataclass

@dataclass
class ExampleResource:
    property: type
```

#### New Manager
```python
# src/managers/example_manager.py
from src.autoload.events import Events

class ExampleManager:
    def __init__(self, state, config):
        self.state = state
        self.config = config

    def do_something(self):
        # Logic here
        Events.emit_something()
```

#### New Utility
```python
# src/utils/example_util.py
class ExampleUtil:
    @staticmethod
    def helper(input):
        return output
```

### Testing

#### Manual Tests (Quick validation)
```bash
python src/tests_manual/test_something.py
```

#### Automated Tests (Future)
Use pytest in `tests/` folder (to be created)

### Code Style

- Follow existing patterns
- Use type hints
- Document with docstrings
- Keep functions focused

### Import Conventions

```python
# Always import from src
from src.resources.card_resource import CardResource
from src.managers.game_manager import GameManager
from src.utils.poker_evaluator import PokerEvaluator
from src.autoload.events import Events
```

### Configuration

Use lowercase attributes:
```python
config.max_hands      # ✅ Correct
config.MAX_HANDS      # ❌ Wrong
```

Class constants are uppercase:
```python
GameConfigResource.HAND_SCORES  # ✅ Correct
```

### Documentation

When making significant changes:
1. Update relevant docs in `src/docs/`
2. Update `claude.md` if architecture changes
3. Update tests if behavior changes

### Pull Request Process

1. Test your changes: `python run.py`
2. Run manual tests if relevant
3. Update documentation
4. Describe what changed and why

### Questions?

- **Architecture**: Read `src/docs/GODOT_ARCHITECTURE.md`
- **Porting to Godot**: Read `src/docs/PORTING_GUIDE.md`
- **Structure**: Read `STRUCTURE.md`
- **For AI**: Read `claude.md`

## Design Decisions

### Why This Architecture?

1. **Godot-Ready**: Direct mapping to Godot Engine concepts
2. **Maintainable**: Clear separation of concerns
3. **Testable**: Each system can be tested independently
4. **Extensible**: Easy to add new features
5. **Professional**: Follows industry best practices

### Why Resources?

Resources are Godot's way of storing serializable data:
- Can be saved as `.tres` files
- Editable in Inspector
- Reusable across scenes
- Type-safe

### Why Managers?

Managers (Nodes in Godot) coordinate game systems:
- Part of scene tree
- Can run code (_ready, _process)
- Natural for game logic
- Easy to test

### Why Events Singleton?

Signal-driven architecture:
- Decouples systems
- Easy to extend
- Natural for UI updates
- Professional pattern

## Code Review Checklist

- [ ] Code is in `src/`, not `legacy_code/`
- [ ] Follows architecture patterns (Resource/Manager/Util/Event)
- [ ] Uses lowercase config attributes
- [ ] Imports from `src.`
- [ ] No circular dependencies
- [ ] Documented with docstrings
- [ ] Tested (at least manually)
- [ ] Follows existing code style

## Getting Help

1. Read `claude.md` for complete instructions
2. Read `src/docs/` for architecture details
3. Look at existing code for patterns
4. Ask in issues if unsure

## License

[Your License Here]
