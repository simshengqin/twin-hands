# Documentation

This folder contains all documentation for the Godot-ready refactor of Poker Grid.

## Files

### GODOT_ARCHITECTURE.md
**Comprehensive architecture guide**

Covers:
- Key learnings from Godot Deck Builder tutorial
- Architecture structure and patterns
- Resource vs Node vs Utils vs Autoload
- Signal flow examples
- Scene tree structure
- Porting to Godot step-by-step
- Best practices applied

**Read this first** to understand the overall architecture.

### PORTING_GUIDE.md
**Step-by-step Godot porting instructions**

Covers:
- Project setup in Godot
- Resource porting (Python → GDScript)
- Manager porting
- Autoload setup
- UI scene creation
- Translation tips
- Testing checklist
- Common issues

**Follow this** when you're ready to port to Godot Engine.

### README_REFACTOR.md
**High-level overview**

Quick reference:
- What changed
- New structure
- Architecture highlights
- Benefits
- Files reference

**Start here** for a quick overview.

### REFACTOR_SUMMARY.md
**Detailed transformation summary**

Covers:
- What was done
- Insights from deck builder
- Code transformation examples
- Signal flow examples
- Benefits of new architecture

**Read this** to understand the transformation process.

### ARCHITECTURE_DIAGRAM.txt
**Visual architecture diagrams**

Contains:
- Project structure
- Architecture layers
- Signal flow diagrams
- Data flow diagrams
- Godot scene tree (future)
- Comparison: old vs new

**Great for visual learners** - ASCII art diagrams of the architecture.

## Reading Order

### 1. Quick Start
```
README_REFACTOR.md
    ↓
ARCHITECTURE_DIAGRAM.txt
```

### 2. Deep Understanding
```
GODOT_ARCHITECTURE.md
    ↓
REFACTOR_SUMMARY.md
```

### 3. Ready to Port
```
PORTING_GUIDE.md
```

## Quick Reference

### What is a Resource?
See: `GODOT_ARCHITECTURE.md` → "Component Details" → "Resources"

### How do Signals work?
See: `GODOT_ARCHITECTURE.md` → "Signal Flow Example"

### How to port to Godot?
See: `PORTING_GUIDE.md` → "Detailed Steps"

### What's the folder structure?
See: `ARCHITECTURE_DIAGRAM.txt` → "PROJECT STRUCTURE"

### Why this architecture?
See: `REFACTOR_SUMMARY.md` → "Benefits of New Architecture"

## External Resources

- [Godot Best Practices](https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html)
- [Scene Organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)
- [Signals Documentation](https://docs.godotengine.org/en/stable/getting_started/step_by_step/signals.html)
- [Custom Resources](https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html)

## Questions?

All your questions should be answered in these docs. If not:

1. Check `GODOT_ARCHITECTURE.md` for concepts
2. Check `PORTING_GUIDE.md` for implementation
3. Check `ARCHITECTURE_DIAGRAM.txt` for visual reference
