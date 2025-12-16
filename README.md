(i made this before the openai codex tool even existed lol)

# Codex 

A **gamified task management system** written in Python that combines a classic to-do list with RPG-like progression mechanics.

This project was designed to encourage consistency, discipline, and prioritization through rewards and consequences.

---

## Features

### Task management

* Simple task manager stuff
* Intuitive UI

### Mandatory tasks

* Tasks that activate on a **specific weekday**
* Can only be completed on their activation day
* Completing a certain number of mandatory tasks can skip the day penalties (more on that later)

### Gamification System

* **XP and Levels**

  * Completing tasks grants XP
  * Levels increase XP requirements progressively
* **Tokens**

  * Earned from completing tasks
  * Used to buy rewards or skip day penalties
* **Streak system**

  * Completing a minimum number of tasks per day builds streaks
  * Streaks increase XP and token rewards

### Day pause

* Spend tokens to pause the current day
* Paused days:

  * Do not break streaks
  * Do not apply XP penalties

### ! Penalties !

* XP loss for inactivity on weekdays
* Weekly XP penalty for unfinished **urgent tasks**
* Automatic priority escalation for unfinished tasks

### Daily and weekly logic

* Daily reset of:

  * Completed tasks counters
  * Mandatory task completion status
* Weekly checks:

  * Increase priorities
  * Apply urgent task penalties

### Persistent storage

* All progress is saved to a local `data.json` file
* Automatically loaded on startup

---

## Core concepts

### Difficulty multipliers

Used to calculate base XP and token rewards.

### Priority multipliers

Higher priority tasks grant more rewards.

### Streak multiplier

Increases rewards based on consecutive productive days.

Coincidentally be **UI-agnostic**, meaning it can be reused with custom tkinter, CLI or even Web UIs

---

## Ideas for future Improvements

* Separate gamification logic into its own module
* Add achievements
* Add statistics and history tracking
* Cloud sync instead of local JSON
* Multiple profiles
