# Fly-in: Optimal Drone Fleet Routing

*This project has been created as part of the 42 curriculum by mapadron.*

## Description

The **Fly-in** project is a fleet management and pathfinding optimization challenge. The goal is to route a variable number of drones (up to 30) from a starting hub to a target hub in the minimum number of turns.

The project operates on a complex graph network containing various constraints:

* **Hub Capacities:** Maximum drones allowed simultaneously in a hub.
* **Link Capacities:** Maximum drones allowed to traverse a connection in a single turn.
* **Zone Types:**
	- **Priority:** Hubs that should be favored if turn counts are equal.
	- **Restricted:** Connections that require 2 turns instead of 1.
	- **Blocked:** Non-traversable nodes.



The core challenge lies in the "Fly-in" formula: . To minimize the total time , the algorithm must balance the length of the paths with the number of parallel "lanes" used to send drones.

## Instructions

### Installation & Execution

This project uses a `Makefile` to automate environment setup and execution.



* **Run the project:**

    ```bash

    make

    ```

    This command automatically installs dependencies, sets up the virtual environment, and executes the program using the default `config.txt` file.



* **Manual Execution:**

    ```bash

    source .venv/bin/activate

    python3 a_maze_ing.py <map_file.txt>

    ```



* **Standard Makefile Rules:**

    * `make install`: Installs project dependencies.

    * `make run`: Executes the main script.

    * `make debug`: Runs the script in debug mode.

    * `make clean`: Removes temporary files and caches.

    * `make lint`: Executes flake8 and mypy checks.

	* `make lint-strict`: Executes flake8 and mypy --strict checks.

---

## Algorithm & Implementation Strategy

### 1. Min-Cost Max-Flow (MCMF)

The solver uses a **Successive Shortest Path** approach based on Min-Cost Max-Flow theory.

* **Graph Transformation:** Hubs are treated as vertices and connections as edges. Link capacities are mapped directly to edge capacities, while vertex capacities are managed via entry/exit flow constraints.
* **Augmenting Paths:** We utilize a modified **Dijkstra/SPFA** search to find the shortest path from start to end.
* **Residual Graphs:** To achieve global optimality, the algorithm supports "undoing" previous moves. By using residual edges with negative costs, the solver can "reroute" existing paths to unlock higher-capacity highways that were previously blocked by greedy choices.

### 2. Lexicographical Optimization

The "Cost" of an augmenting path is not a single integer, but a tuple: `(length, -priority_gain)`. This ensures the algorithm follows a strict priority hierarchy:

1. **Primary Objective:** Minimize total turns ().
2. **Secondary Objective:** Maximize the use of Priority Hubs.

### 3. Global Stop Condition

Unlike standard MCMF which runs until the flow is full, our solver evaluates the **global turn count** after every new path. If adding a new, longer path increases the total time , the solver stops and rolls back to the previous state.

---

## Visual Representation

The project includes a **Pygame-based GUI** designed to enhance the debugging and user experience:

* **Dynamic Mapping:** Hubs are positioned based on their map coordinates, with colors representing zone types (e.g., Orange for Restricted, Gold for Priority).
* **State Interpolation:** Drones do not simply "teleport" between hubs. The visualizer calculates the "In-Flight" state (LERP) for drones on connections, especially useful for visualizing the 2-turn delay in Restricted zones.
* **Real-time Synchronization:** The visualizer moves in lock-step with the terminal log, allowing for frame-by-frame analysis of fleet throughput and bottleneck detection.

---

## Resources

* Notes on optimization on graphs
* Peer-to-peer help
* Pygame documentation

### AI Usage

AI was utilized as a collaborative peer during development for the following tasks:

* **Architecture Design:** Assisting in the modularization of the `src/` directory to follow the Separation of Concerns principle.
* **Documentation:** Generating high-quality docstrings and formatting the final README according to the 42 Norm.
* **Map creation:** Assisted providing new test maps to check edge cases.
