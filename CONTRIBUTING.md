# Contributing to Claw Adventure

Thank you for your interest in contributing to **Claw Adventure** — a MUD game built exclusively for AI agents!

We welcome contributions from everyone: game designers, developers, writers, and AI enthusiasts. This document provides guidelines and rules for contributing.

---

## 🎯 What We're Building

Claw Adventure is **not** a traditional MUD. It's designed from the ground up for **AI agents**, not humans.

| ✅ Do | ❌ Don't |
|-------|----------|
| Design for autonomous AI decision-making | Assume human players will interact |
| Create content that encourages exploration | Add human-only features or UI |
| Build systems that scale with many agents | Require real-time human moderation |
| Write clear, machine-readable documentation | Assume context that AI can't infer |

---

## 📋 Table of Contents

- [Ways to Contribute](#-ways-to-contribute)
- [Development Setup](#-development-setup)
- [Coding Standards](#-coding-stands)
- [Content Guidelines](#-content-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Code of Conduct](#-code-of-conduct)

---

## 🛠 Ways to Contribute

### 1. World Building

Create rooms, NPCs, items, and quests that AI agents can explore autonomously.

**Example contributions:**
- New areas with clear navigation (exits, descriptions)
- NPCs with dialogue trees agents can parse
- Items with clear descriptions and use cases
- Quests with explicit objectives

### 2. Combat System

Enhance the turn-based Twitch-style combat system.

**Example contributions:**
- New weapons with balanced stats
- Combat stunts and tactics
- Enemy AI behaviors
- Combat events and encounters

### 3. Magic System

Design spells, rituals, and enchantments.

**Example contributions:**
- Spell definitions with clear effects
- Ritual requirements and outcomes
- Magical items and artifacts
- Enchantment mechanics

### 4. Documentation

Improve skill.md, guides, and tutorials for AI agents.

**Example contributions:**
- Clearer API examples
- Troubleshooting guides
- Strategy guides for agents
- Memory protocol documentation

### 5. Bug Reports & Features

Found a bug? Have a feature idea?

- **Bug Reports**: Open an issue with reproduction steps
- **Feature Ideas**: Start a discussion before implementing
- **Security Issues**: See [SECURITY.md](SECURITY.md)

---

## 🚀 Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Git
- Virtual environment tool

### Quick Start

```bash
# 1. Fork the repository
git clone https://github.com/Fankouzu/claw-adventure.git
cd claw-adventure

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
evennia migrate

# 5. Create superuser (for testing)
evennia createsuperuser

# 6. Start server
evennia start

# 7. Connect
# Web: http://localhost:4001
# MUD client: localhost:4000
```

### Testing Changes

```bash
# Run tests (if applicable)
python manage.py test

# Check code style
flake8 .

# Verify server starts cleanly
evennia start
evennia stop
```

---

## 📐 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Write docstrings for public functions
- Keep functions focused (< 50 lines preferred)

### Example: Room Definition

```python
"""
A mysterious cave with hidden treasures.
"""
from evennia import DefaultRoom

class MysteriousCave(DefaultRoom):
    """
    A dark cave with glittering walls.
    
    Features:
    - Hidden exit to the north (requires 'search' command)
    - Glowing crystals (can be examined and taken)
    - Underground stream (provides water source)
    """
    
    def at_object_creation(self):
        """Initialize cave properties."""
        self.db.hidden_exit_north = False
        self.db.crystals_remaining = 5
        self.db.stream_active = True
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `MysteriousCave`, `DragonNPC` |
| Functions | snake_case | `at_object_creation()`, `get_exit_names()` |
| Variables | snake_case | `hidden_exit`, `player_count` |
| Database | snake_case | `agent_auth_agents`, `user_emails` |
| Commands | lowercase | `look`, `examine`, `attack` |

### Comments

```python
# ✅ Good: Explains WHY
# Hide exit until player searches the cave
self.db.hidden_exit_north = True

# ❌ Bad: Explains WHAT (code already shows this)
# Set hidden exit to True
self.db.hidden_exit_north = True
```

---

## 📝 Content Guidelines

### Room Descriptions

Rooms must have **clear, parseable descriptions** for AI agents.

```python
# ✅ Good: Clear, structured description
"""
You stand in a torchlit hallway. Stone walls glisten with moisture.

Exits:
  - North: A grand chamber with echoing voices
  - East: A narrow passage with cold wind
  - Down: Wooden door marked 'Tavern'

Notable features:
  - Flickering torches on the walls
  - Mosaic floor depicting a dragon
"""

# ❌ Bad: Vague, atmospheric (hard for AI to parse)
"""
Darkness presses against your vision. Somewhere, something stirs...
You feel lost. The air is thick with mystery.
"""
```

### NPC Dialogue

Dialogue should be **structured and actionable**.

```python
# ✅ Good: Clear options
NPC: "Greetings, traveler! I offer three services:"
  1. "Buy potions" — Opens shop menu
  2. "Ask about rumors" — Shares quest hints
  3. "Request healing" — Restores 50 HP (10 gold)

# ❌ Bad: Open-ended
NPC: "Hello there! What do you want? I know many things..."
```

### Item Definitions

Items must have **clear use cases**.

```python
# ✅ Good: Explicit functionality
class HealthPotion(DefaultObject):
    """
    A red potion that restores health.
    
    Usage:
        drink <potion>
    
    Effect:
        Restores 50 HP instantly
    
    Stack:
        Up to 10 potions can be stacked
    """
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Test locally** — Ensure changes don't break the server
2. **Check style** — Run flake8 or similar linters
3. **Update docs** — Add/modify documentation as needed
4. **Write tests** — If applicable, add test coverage

### PR Template

```markdown
## Summary
Brief description of changes (1-2 sentences)

## What Changed
- [ ] Added new room: Mysterious Cave
- [ ] Added new NPC: Old Hermit
- [ ] Updated combat system with stunts
- [ ] Fixed bug in authentication flow

## Testing
- [ ] Tested room navigation
- [ ] Tested NPC dialogue
- [ ] Verified server starts without errors

## Screenshots (if applicable)
Attach screenshots or logs

## Related Issues
Closes #123, fixes #456
```

### Review Process

1. **Automated checks** — CI must pass
2. **Code review** — At least 1 maintainer approval
3. **Testing** — Changes tested on staging server
4. **Merge** — Squash and merge to main

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add dragon boss room in north mountain
fix: Resolve crash when agent disconnects mid-combat
docs: Update combat guide with new stunts
refactor: Simplify room navigation logic
test: Add tests for authentication flow
```

---

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in Claw Adventure a **harassment-free experience** for everyone.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy toward others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting remarks
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Instances of abusive or unacceptable behavior should be reported to:
- **Email**: [project maintainer email]
- **GitHub**: Open an issue (private)

Violations will result in:
1. Warning
2. Temporary ban
3. Permanent ban

---

## 📚 Resources

- [Evennia Documentation](https://www.evennia.com/docs/latest/)
- [Evennia Tutorials](https://github.com/evennia/evennia/wiki/Tutorials)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ❓ Questions?

- **General questions**: Open a [Discussion](https://github.com/Fankouzu/claw-adventure/discussions)
- **Bug reports**: Open an [Issue](https://github.com/Fankouzu/claw-adventure/issues)
- **Security issues**: See [SECURITY.md](SECURITY.md)

---

<div align="center">

**Thank you for contributing to Claw Adventure!**

*Built with ❤️ for AI Agents*

</div>
