import random

class TreeGenerator:
    def __init__(self, width=30, height=15):
        self.width = width
        self.height = height
        self.colors = {
            'trunk': '\033[38;2;139;69;19m',
            'branch': '\033[38;2;160;82;45m',
            'leaves': '\033[38;2;34;139;34m',
            'reset': '\033[0m'
        }
        self.chars = {
            'trunk': ['║', '│', '┃'],
            'branch': ['╱', '╲', '/', '\\'],
            'leaves': ["@", "#", "*", "%", "&"]
        }

    def generate_tree(self, stage):
        life = min(5 + stage * 2, 20)
        grid = {}
        self._grow_branch(grid, self.height - 1, self.width // 2, life)
        return self._format_tree(grid)

    def _grow_branch(self, grid, y, x, life):
        if life <= 0 or x < 1 or x >= self.width - 1 or y < 1:
            return

        if life > 7:
            char_type = 'trunk'
        elif life > 3:
            char_type = 'branch'
        else:
            char_type = 'leaves'

        color = self.colors[char_type]
        grid[(x, y)] = f"{color}{random.choice(self.chars[char_type])}{self.colors['reset']}"

        if life > 2:
            self._grow_branch(grid, y - 1, x, life - 1)
            if random.random() > 0.6:
                self._grow_branch(grid, y - 1, x - 1, life - 3)
            if random.random() > 0.6:
                self._grow_branch(grid, y - 1, x + 1, life - 3)

    def _format_tree(self, grid):
        tree_rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(grid.get((x, y), ' '))
            tree_rows.append(''.join(row))
        return '\n'.join(tree_rows)