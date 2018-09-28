import os, sys, pygame
from pygame.locals import *
import objects, config

"这个模块包含游戏Squish的主游戏逻辑"

class State:

    """
    游戏状态超类，能够处理事件以及在指定表面上显示自己
    """

    def handle(self, event):
        """
        只处理退出事件的默认事件处理
        """
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

    def first_display(self, screen):
        """
        在首次显示状态时使用，它使用背景色填充屏幕
        """
        screen.fill(config.background_color)
        # Remember to call flip, to make the changes visible:
        pygame.display.flip()

    def display(self, screen):
        """
        在后续显示状态时使用，其默认行为是什么都不做
        """
        pass


class Level(State):
    """
    游戏关卡。它计算落下了多少个铅锤，移动精灵并执行其他与游戏逻辑相关的任务
    """

    def __init__(self, number=1):
        self.number = number
        # 还需躲开多少个铅锤才能通过当前关卡？
        self.remaining = config.weights_per_level

        speed = config.drop_speed
        # 每过一关都将速度提高speed_increase：
        speed += (self.number-1) * config.speed_increase
        # 创建铅锤和香蕉：
        self.weight = objects.Weight(speed)
        self.banana = objects.Banana()
        both = self.weight, self.banana # This could contain more sprites...
        self.sprites = pygame.sprite.RenderUpdates(both)

    def update(self, game):
        "更新游戏状态"
        # 更新所有的精灵
        self.sprites.update()
        # 如果香蕉和铅锤发生了碰撞，就让游戏切换到GameOver状态
        if self.banana.touches(self.weight):
            game.next_state = GameOver()
        # 否则，如果铅锤已落到地上，就将其复位
        # 如果躲开了当前关卡内的所有铅锤，就让游戏切换到LevelCleared状态
        elif self.weight.landed:
            self.weight.reset()
            self.remaining -= 1
            if self.remaining == 0:
                game.next_state = LevelCleared(self.number)

    def display(self, screen):
        """
        在第一次显示（清屏）后显示状态。不同于firstDisplay，
        这个方法调用pygame.display.update并向它传递一个需要
        更新的矩形列表，这个列表是由self.sprites.draw提供的
        """
        screen.fill(config.background_color)
        updates = self.sprites.draw(screen)
        pygame.display.update(updates)


class Paused(State):
    """
    简单的游戏暂停状态，用户可通过按任何键盘键或单击鼠标来结束这种状态
    """

    finished = 0 # 用户结束暂停了吗？
    image = None # 如果需要显示图像，将这个属性设置为一个文件名
    text = ''    # 将这个属性设置为一些说明性文本

    def handle(self, event):
        """
        这样来处理事件：将这项任务委托给State（它只处理退出事件），
        并对按键和鼠标单击做出响应。如果用户按下了键盘键或单击了鼠标，
        就将self.finished设置为True
        """
        State.handle(self, event)
        if event.type in [MOUSEBUTTONDOWN, KEYDOWN]:
            self.finished = 1

    def update(self, game):
        """
        更新关卡。如果用户按下了键盘键或单击了鼠标（即self.finished为True），
        就让游戏切换到（由子类实现的方法）self.next_state()返回的状态
        """
        if self.finished:
            game.next_state = self.next_state()

    def first_display(self, screen):
        """
        在首次显示暂停状态时调用，它绘制图像（如果指定了）并渲染文本
        """
        # 首先，通过使用背景色填充屏幕来清屏
        screen.fill(config.background_color)

        # 创建一个使用默认外观和指定字号的Font对象
        font = pygame.font.Font(None, config.font_size)

        # 获取self.text中的文本行，但忽略开头和末尾的空行
        lines = self.text.strip().splitlines()

        # 使用font.get_linesize()获取每行文本的高度，并计算文本的总高度
        height = len(lines) * font.get_linesize()

        # 计算文本的位置（在屏幕上居中）
        center, top = screen.get_rect().center
        top -= height // 2

        # 如果有图像要显示...
        if self.image:
            # 加载该图像
            image = pygame.image.load(self.image).convert()
            # 获取其rect
            r = image.get_rect()
            # 将文本下移图像高度一半的距离
            top += r.height // 2
            # 将图像放在文本上方20像素处
            r.midbottom = center, top - 20
            # 将图像传输到屏幕上
            screen.blit(image, r)

        antialias = 1   # 消除文本的锯齿
        black = 0, 0, 0 # 使用黑色渲染文本

        # 从计算得到的top处开始渲染所有的文本行
        # 每渲染一行都向下移动font.get_linesize()像素
        for line in lines:
            text = font.render(line.strip(), antialias, black)
            r = text.get_rect()
            r.midtop = center, top
            screen.blit(text, r)
            top += font.get_linesize()

        # 显示所做的所有修改
        pygame.display.flip()


class Info(Paused):

    """
    显示一些游戏信息的简单暂停状态，紧跟在这个状态后面的是Level状态（第一关）
    """

    next_state = Level
    text = '''
    In this game you are a banana,
    trying to survive a course in
    self-defense against fruit, where the
    participants will "defend" themselves
    against you with a 16 ton weight.'''

class StartUp(Paused):

    """
   显示启动图像和欢迎消息的暂停状态，紧跟在它后面的是Info状态
    """

    next_state = Info
    image = config.splash_image
    text = '''
    Welcome to Squish,
    the game of Fruit Self-Defense'''


class LevelCleared(Paused):
    """
    指出用户已过关的暂停状态，紧跟在它后面的是表示下一关的Level状态
    """

    def __init__(self, number):
        self.number = number
        self.text = '''Level {} cleared
        Click to start next level'''.format(self.number)

    def next_state(self):
        return Level(self.number + 1)

class GameOver(Paused):

    """
    指出游戏已结束的状态，紧跟在它后面的是表示第一关的Level状态
    """

    next_state = Level
    text = '''
    Game Over
    Click to Restart, Esc to Quit'''

class Game:

    """
    负责主事件循环（包括在不同游戏状态之间切换）的游戏对象
    """

    def __init__(self, *args):
        # 获取游戏和图像所在的目录
        path = os.path.abspath(args[0])
        dir = os.path.split(path)[0]
        # 切换到这个目录，以便之后能够打开图像文件
        os.chdir(dir)
        # 最初不处于任何状态
        self.state = None
        # 在第一次事件循环迭代中切换到StartUp状态
        self.next_state = StartUp()

    def run(self):
        """
        这个方法设置一些变量。它执行一些重要的初始化任务，并进入主事件循环
        """
        pygame.init() # 初始化所有的Pygame模块

        # 决定在窗口还是整个屏幕中显示游戏
        flag = 0                  # 默认在窗口中显示游戏
        
        if config.full_screen:
            flag = FULLSCREEN     # 全屏模式
        screen_size = config.screen_size
        screen = pygame.display.set_mode(screen_size, flag)

        pygame.display.set_caption('Fruit Self Defense')
        pygame.mouse.set_visible(False)

        # 主事件循环
        while True:
            # (1) )如果nextState被修改，就切换到修改后的状态并显示它（首次）
            if self.state != self.next_state:
                self.state = self.next_state
                self.state.first_display(screen)
            # (2) 将事件处理工作委托给当前状态
            for event in pygame.event.get():
                self.state.handle(event)
            # (3) 更新当前状态
            self.state.update(self)
            # (4) 显示当前状态
            self.state.display(screen)

if __name__ == '__main__':
    game = Game(*sys.argv)
    game.run()
