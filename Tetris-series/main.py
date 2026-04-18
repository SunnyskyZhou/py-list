import pygame
import random

# -------------------------- 游戏常量配置 --------------------------
# 基础尺寸
BLOCK_SIZE = 25  # 单个方块大小（像素）
GAME_COLS = 10  # 游戏区域列数
GAME_ROWS = 20  # 游戏区域行数
SIDE_PANEL = 6  # 右侧面板宽度（列数）

# 窗口尺寸
SCREEN_WIDTH = (GAME_COLS + SIDE_PANEL) * BLOCK_SIZE
SCREEN_HEIGHT = GAME_ROWS * BLOCK_SIZE

# 颜色配置（深灰背景、白色边框、红色结束线）
DARK_GRAY = (40, 40, 40)  # 背景深灰色
WHITE = (255, 255, 255)  # 边框、文字、网格线颜色
RED = (255, 0, 0)  # 顶层2格结束线（红色，核心修改）
# 方块颜色（7种经典方块）
BLOCK_COLORS = [
    (0, 255, 255),  # I型
    (255, 0, 255),  # T型
    (0, 255, 0),  # S型
    (255, 0, 0),  # Z型
    (255, 255, 0),  # O型
    (255, 165, 0),  # L型
    (0, 0, 255)  # J型
]

# 俄罗斯方块7种经典形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1], [1, 1]],  # O
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 0, 0], [1, 1, 1]]  # J
]


# -------------------------- 游戏核心类 --------------------------
class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 | 消一行+100分")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 24, bold=True)
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 0.5

        # 游戏网格初始化
        self.grid = [[None for _ in range(GAME_COLS)] for _ in range(GAME_ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    # 生成新方块
    def new_piece(self):
        shape = random.choice(SHAPES)
        color = BLOCK_COLORS[SHAPES.index(shape)]
        x = GAME_COLS // 2 - len(shape[0]) // 2
        y = 0
        return [x, y, shape, color]

    # 碰撞检测
    def check_collision(self, x, y, shape):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if new_x < 0 or new_x >= GAME_COLS or new_y >= GAME_ROWS:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False

    # 旋转方块
    def rotate(self):
        if self.game_over:
            return
        x, y, shape, color = self.current_piece
        rotated = list(zip(*shape[::-1]))
        if not self.check_collision(x, y, rotated):
            self.current_piece[2] = rotated

    # 移动方块
    def move(self, dx, dy):
        if self.game_over:
            return
        x, y, shape, color = self.current_piece
        new_x = x + dx
        new_y = y + dy
        if not self.check_collision(new_x, new_y, shape):
            self.current_piece[0] = new_x
            self.current_piece[1] = new_y
            return True
        if dy > 0:
            self.lock_piece()
        return False

    # 锁定方块
    def lock_piece(self):
        x, y, shape, color = self.current_piece
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    self.grid[y + row_idx][x + col_idx] = color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        # 触碰顶层2格红色结束线 = 游戏结束
        if self.check_collision(self.current_piece[0], self.current_piece[1], self.current_piece[2]):
            self.game_over = True

    # 消行计分（1行100分）
    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        for row in self.grid:
            if None not in row:
                lines_cleared += 1
            else:
                new_grid.append(row)
        for _ in range(lines_cleared):
            new_grid.insert(0, [None for _ in range(GAME_COLS)])
        self.grid = new_grid
        self.score += lines_cleared * 100

    # 快速落地
    def hard_drop(self):
        while self.move(0, 1):
            pass

    # -------------------------- 绘制模块 --------------------------
    def draw_grid(self):
        self.screen.fill(DARK_GRAY)

        # 绘制所有格子 + 白色边框
        for y in range(GAME_ROWS):
            for x in range(GAME_COLS):
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # 核心修改：绘制【顶层2格红色结束线】
        end_line_y = 2 * BLOCK_SIZE
        pygame.draw.line(
            self.screen, RED,
            (0, end_line_y), (GAME_COLS * BLOCK_SIZE, end_line_y),
            width=3  # 加粗红线更醒目
        )

    # 绘制当前方块
    def draw_current_piece(self):
        x, y, shape, color = self.current_piece
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    draw_x = (x + col_idx) * BLOCK_SIZE
                    draw_y = (y + row_idx) * BLOCK_SIZE
                    rect = pygame.Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    # 绘制下一个方块预览
    def draw_next_piece(self):
        label = self.font.render("下一个", True, WHITE)
        self.screen.blit(label, (GAME_COLS * BLOCK_SIZE + 20, 30))

        x, y, shape, color = self.next_piece
        offset_x = GAME_COLS * BLOCK_SIZE + 20
        offset_y = 80
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    draw_x = offset_x + col_idx * BLOCK_SIZE
                    draw_y = offset_y + row_idx * BLOCK_SIZE
                    rect = pygame.Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    # 绘制分数+操作说明
    def draw_score(self):
        score_label = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_label, (GAME_COLS * BLOCK_SIZE + 20, 200))

        tips = [
            "操作说明:",
            "← → ：左右移动",
            "↓   ：加速下落",
            "↑   ：旋转方块",
            "空格：快速落地",
            "ESC ：退出游戏"
        ]
        for i, tip in enumerate(tips):
            tip_text = self.font.render(tip, True, WHITE)
            self.screen.blit(tip_text, (GAME_COLS * BLOCK_SIZE + 20, 250 + i * 30))

    # 游戏结束提示
    def draw_game_over(self):
        over_text = self.font.render("游戏结束!", True, WHITE)
        self.screen.blit(over_text, (GAME_COLS * BLOCK_SIZE // 2 - 40, SCREEN_HEIGHT // 2))

    # -------------------------- 主循环 --------------------------
    def run(self):
        while True:
            current_time = pygame.time.get_ticks() / 1000
            self.screen.fill(DARK_GRAY)

            # 按键事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        if event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        if event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        if event.key == pygame.K_UP:
                            self.rotate()
                        if event.key == pygame.K_SPACE:
                            self.hard_drop()

            # 自动下落
            if not self.game_over and current_time - self.fall_time > self.fall_speed:
                self.move(0, 1)
                self.fall_time = current_time

            # 渲染所有元素
            self.draw_grid()
            self.draw_current_piece()
            self.draw_next_piece()
            self.draw_score()
            if self.game_over:
                self.draw_game_over()

            pygame.display.update()
            self.clock.tick(60)


# 启动游戏
if __name__ == "__main__":
    game = Tetris()
    game.run()