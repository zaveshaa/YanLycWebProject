from flask import Flask, render_template_string
import random
import time
from enum import Enum

app = Flask(__name__)

class BranchType(Enum):
    TRUNK = 0
    SHOOT_LEFT = 1
    SHOOT_RIGHT = 2
    DYING = 3
    DEAD = 4

class TreeGenerator:
    def __init__(self):
        self.width = 80
        self.height = 24
        self.tree_grid = {}
        self.counters = {'branches': 0, 'shoots': 0, 'shoot_counter': 0}
        self.config = {
            'live': False,
            'infinite': False,
            'life_start': 32,
            'multiplier': 5,
            'leaves': ["@", "#", "*", "%", "&"],
            'time_step': 0.03,
            'seed': int(time.time())
        }
        random.seed(self.config['seed'])

    def choose_color(self, branch_type):
        colors = {
            BranchType.TRUNK: '<span style="color: #ccaa44;">',
            BranchType.SHOOT_LEFT: '<span style="color: #ccaa44;">',
            BranchType.SHOOT_RIGHT: '<span style="color: #ccaa44;">',
            BranchType.DYING: '<span style="color: #44cc44;">',
            BranchType.DEAD: '<span style="color: #aaaaaa;">'
        }
        return colors[branch_type]

    def set_deltas(self, branch_type, life, age):
        dx, dy = 0, 0
        multiplier = self.config['multiplier']

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

    def choose_string(self, branch_type, life, dx, dy):
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
            return random.choice(self.config['leaves'])

    def branch(self, y, x, branch_type, life):
        self.counters['branches'] += 1
        dx, dy = 0, 0
        age = 0
        shoot_cooldown = self.config['multiplier']
        
        while life > 0:
            life -= 1
            age = self.config['life_start'] - life
            
            dx, dy = self.set_deltas(branch_type, life, age)
            
            if life < 3:
                self.branch(y, x, BranchType.DEAD, life)
            elif branch_type == BranchType.TRUNK and life < (self.config['multiplier'] + 2):
                self.branch(y, x, BranchType.DYING, life)
            elif branch_type in [BranchType.SHOOT_LEFT, BranchType.SHOOT_RIGHT] and life < (self.config['multiplier'] + 2):
                self.branch(y, x, BranchType.DYING, life)
            elif branch_type == BranchType.TRUNK and (random.randint(0, 2) == 0 or life % self.config['multiplier'] == 0):
                if random.randint(0, 7) == 0 and life > 7:
                    shoot_cooldown = self.config['multiplier'] * 2
                    self.branch(y, x, BranchType.TRUNK, life + random.randint(-2, 2))
                elif shoot_cooldown <= 0:
                    shoot_cooldown = self.config['multiplier'] * 2
                    shoot_life = life + self.config['multiplier']
                    self.counters['shoots'] += 1
                    self.counters['shoot_counter'] += 1
                    
                    shoot_type = BranchType.SHOOT_LEFT if self.counters['shoot_counter'] % 2 else BranchType.SHOOT_RIGHT
                    self.branch(y, x, shoot_type, shoot_life)
            
            shoot_cooldown -= 1
            
            x += dx
            y += dy
            
            branch_str = self.choose_string(branch_type, life, dx, dy)
            color_span = self.choose_color(branch_type)
            
            self.tree_grid[(x, y)] = f"{color_span}{branch_str}</span>"

    def generate_tree_html(self):
        self.tree_grid = {}
        self.counters = {'branches': 0, 'shoots': 0, 'shoot_counter': 0}
        
        start_y = self.height - 1
        start_x = self.width // 2
        
        self.branch(start_y, start_x, BranchType.TRUNK, self.config['life_start'])
        
        tree_html = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                if (x, y) in self.tree_grid:
                    line.append(self.tree_grid[(x, y)])
                else:
                    line.append(' ')
            tree_html.append(''.join(line))
        
        return '<br>'.join(tree_html)

@app.route('/')
def show_tree():
    generator = TreeGenerator()
    tree_html = generator.generate_tree_html()
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>ASCII Tree Generator</title>
    <style>
        body {
            font-family: monospace;
            background-color: #222;
            color: #ddd;
            margin: 20px;
        }
        .tree {
            white-space: pre;
            line-height: 1;
            font-size: 16px;
        }
        a {
            color: #4af;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            padding: 5px 10px;
            background: #333;
            border-radius: 3px;
        }
        a:hover {
            background: #444;
        }
    </style>
</head>
<body>
    <h1>ASCII Tree Generator</h1>
    <a href="/">Generate New Tree</a>
    <div class="tree">{{ tree|safe }}</div>
</body>
</html>
    ''', tree=tree_html)

if __name__ == '__main__':
    app.run(debug=True)