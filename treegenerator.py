import random
import time
import sys
from enum import Enum
from typing import List, Tuple, Optional, Dict

class BranchType(Enum):
    TRUNK = 0
    SHOOT_LEFT = 1
    SHOOT_RIGHT = 2
    DYING = 3
    DEAD = 4

class Config:
    def __init__(self):
        self.live = False
        self.infinite = False
        self.screensaver = False
        self.print_tree = False
        self.verbosity = 0
        self.life_start = 32
        self.multiplier = 5
        self.base_type = 1
        self.seed = 0
        self.leaves_size = 0
        self.save = False
        self.load = False
        self.target_branch_count = 0
        self.time_wait = 4.0
        self.time_step = 0.03
        self.message = None
        self.leaves = ["&"]
        self.save_file = ""
        self.load_file = ""

class Counters:
    def __init__(self):
        self.branches = 0
        self.shoots = 0
        self.shoot_counter = 0

class TreeGenerator:
    def __init__(self):
        self.conf = Config()
        self.counters = Counters()
        self.tree_grid: Dict[Tuple[int, int], str] = {}
        self.width = 80
        self.height = 24

    def init_config(self):
        if self.conf.seed == 0:
            self.conf.seed = int(time.time())
        random.seed(self.conf.seed)

        if not self.conf.leaves:
            self.conf.leaves = ["&"]
            self.conf.leaves_size = 1

    def choose_color(self, branch_type: BranchType) -> str:
        colors = {
            BranchType.TRUNK: ["\033[33m", "\033[1;33m"],
            BranchType.SHOOT_LEFT: ["\033[33m", "\033[1;33m"],
            BranchType.SHOOT_RIGHT: ["\033[33m", "\033[1;33m"],
            BranchType.DYING: ["\033[32m", "\033[1;32m"],
            BranchType.DEAD: ["\033[37m", "\033[1;37m"]
        }
        return random.choice(colors[branch_type])

    def set_deltas(self, branch_type: BranchType, life: int, age: int) -> Tuple[int, int]:
        dx, dy = 0, 0
        multiplier = self.conf.multiplier

        if branch_type == BranchType.TRUNK:
            if age <= 2 or life < 4:
                dy = 0
                dx = random.randint(-1, 1)
            elif age < (multiplier * 3):
                if age % int(multiplier * 0.5) == 0:
                    dy = -1
                else:
                    dy = 0
                
                dice = random.randint(0, 9)
                if dice == 0: dx = -2
                elif 1 <= dice <= 3: dx = -1
                elif 4 <= dice <= 5: dx = 0
                elif 6 <= dice <= 8: dx = 1
                else: dx = 2
            else:
                if random.randint(0, 9) > 2:
                    dy = -1
                else:
                    dy = 0
                dx = random.randint(-1, 1)
        
        elif branch_type == BranchType.SHOOT_LEFT:
            dice = random.randint(0, 9)
            if dice <= 1: dy = -1
            elif 2 <= dice <= 7: dy = 0
            else: dy = 1
            
            dice = random.randint(0, 9)
            if dice <= 1: dx = -2
            elif 2 <= dice <= 5: dx = -1
            elif 6 <= dice <= 8: dx = 0
            else: dx = 1
        
        elif branch_type == BranchType.SHOOT_RIGHT:
            dice = random.randint(0, 9)
            if dice <= 1: dy = -1
            elif 2 <= dice <= 7: dy = 0
            else: dy = 1
            
            dice = random.randint(0, 9)
            if dice <= 1: dx = 2
            elif 2 <= dice <= 5: dx = 1
            elif 6 <= dice <= 8: dx = 0
            else: dx = -1
        
        elif branch_type == BranchType.DYING:
            dice = random.randint(0, 9)
            if dice <= 1: dy = -1
            elif 2 <= dice <= 8: dy = 0
            else: dy = 1
            
            dice = random.randint(0, 14)
            if dice == 0: dx = -3
            elif 1 <= dice <= 2: dx = -2
            elif 3 <= dice <= 5: dx = -1
            elif 6 <= dice <= 8: dx = 0
            elif 9 <= dice <= 11: dx = 1
            elif 12 <= dice <= 13: dx = 2
            else: dx = 3
        
        else:  # DEAD
            dice = random.randint(0, 9)
            if dice <= 2: dy = -1
            elif 3 <= dice <= 6: dy = 0
            else: dy = 1
            dx = random.randint(-1, 1)
        
        return dx, dy

    def choose_string(self, branch_type: BranchType, life: int, dx: int, dy: int) -> str:
        if life < 4:
            branch_type = BranchType.DYING
        
        if branch_type == BranchType.TRUNK:
            if dy == 0: return "/~"
            elif dx < 0: return "\\|"
            elif dx == 0: return "/|\\"
            elif dx > 0: return "|/"
        
        elif branch_type == BranchType.SHOOT_LEFT:
            if dy > 0: return "\\"
            elif dy == 0: return "\\_"
            elif dx < 0: return "\\|"
            elif dx == 0: return "/|"
            elif dx > 0: return "/"
        
        elif branch_type == BranchType.SHOOT_RIGHT:
            if dy > 0: return "/"
            elif dy == 0: return "_/"
            elif dx < 0: return "\\|"
            elif dx == 0: return "/|"
            elif dx > 0: return "/"
        
        else:  # DYING or DEAD
            return random.choice(self.conf.leaves)

    def branch(self, y: int, x: int, branch_type: BranchType, life: int):
        self.counters.branches += 1
        dx, dy = 0, 0
        age = 0
        shoot_cooldown = self.conf.multiplier
        
        while life > 0:
            life -= 1
            age = self.conf.life_start - life
            
            dx, dy = self.set_deltas(branch_type, life, age)
            
            # Near-dead branch should branch into a lot of leaves
            if life < 3:
                self.branch(y, x, BranchType.DEAD, life)
            # Dying trunk should branch into a lot of leaves
            elif branch_type == BranchType.TRUNK and life < (self.conf.multiplier + 2):
                self.branch(y, x, BranchType.DYING, life)
            # Dying shoot should branch into a lot of leaves
            elif branch_type in [BranchType.SHOOT_LEFT, BranchType.SHOOT_RIGHT] and life < (self.conf.multiplier + 2):
                self.branch(y, x, BranchType.DYING, life)
            # Trunks should re-branch
            elif branch_type == BranchType.TRUNK and (random.randint(0, 2) == 0 or life % self.conf.multiplier == 0):
                if random.randint(0, 7) == 0 and life > 7:
                    shoot_cooldown = self.conf.multiplier * 2
                    self.branch(y, x, BranchType.TRUNK, life + random.randint(-2, 2))
                elif shoot_cooldown <= 0:
                    shoot_cooldown = self.conf.multiplier * 2
                    shoot_life = life + self.conf.multiplier
                    self.counters.shoots += 1
                    self.counters.shoot_counter += 1
                    
                    # Create shoot (alternate between left and right)
                    shoot_type = BranchType.SHOOT_LEFT if self.counters.shoot_counter % 2 else BranchType.SHOOT_RIGHT
                    self.branch(y, x, shoot_type, shoot_life)
            
            shoot_cooldown -= 1
            
            # Move in x and y directions
            x += dx
            y += dy
            
            # Choose string to use for this branch
            branch_str = self.choose_string(branch_type, life, dx, dy)
            
            # Store in grid
            self.tree_grid[(x, y)] = f"{self.choose_color(branch_type)}{branch_str}\033[0m"
            
            if self.conf.live and not (self.conf.load and self.counters.branches < self.conf.target_branch_count):
                self.print_tree()
                time.sleep(self.conf.time_step)

    def print_tree(self):
        # Clear screen
        print("\033[2J\033[H", end="")
        
        # Print each character in the grid
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.tree_grid:
                    print(self.tree_grid[(x, y)], end="")
                else:
                    print(" ", end="")
            print()

    def grow_tree(self):
        # Reset counters and grid
        self.counters = Counters()
        self.tree_grid = {}
        
        # Start growing from bottom center
        start_y = self.height - 1
        start_x = self.width // 2
        
        # Recursively grow tree trunk and branches
        self.branch(start_y, start_x, BranchType.TRUNK, self.conf.life_start)
        
        # Final print
        if not self.conf.live:
            self.print_tree()

    def run(self):
        self.init_config()
        
        try:
            while True:
                self.grow_tree()
                
                if not self.conf.infinite:
                    break
                
                if self.conf.screensaver and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    break
                
                time.sleep(self.conf.time_wait)
                
                # Reseed for next tree
                random.seed(int(time.time()))
                
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    generator = TreeGenerator()
    
    # Example configuration
    generator.conf.live = True
    generator.conf.infinite = False
    generator.conf.leaves = ["@", "#", "*", "%", "&"]
    generator.conf.leaves_size = len(generator.conf.leaves)
    
    generator.run()