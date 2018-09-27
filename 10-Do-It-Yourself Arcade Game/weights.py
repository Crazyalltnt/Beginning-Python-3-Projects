#@author: Neil
#2018-09-26

import sys, pygame
from pygame.locals import *
from random import randrange

class Weight(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        # 绘制Sprite对象时要用到的图像和矩形：
        self.image = weight_image
        self.rect = self.image.get_rect()
        self.reset()
        
    def reset(self):
        """
        将铅锤移到屏幕顶端的一个随机位置
        """
        self.rect.top = -self.rect.height
        self.rect.centerx = randrange(screen_size[0])
        
    def update(self):
        """
        更新下一帧中的铅锤
        """
        self.rect.top += self.speed
        if self.rect.top > screen_size[1]:
            self.reset()
            
#初始化
pygame.init()
screen_size = 800, 600
pygame.display.set_mode(screen_size, FULLSCREEN)
pygame.mouse.set_visible(0)

#加载铅锤图像
weight_image = pygame.image.load('weight.png')
weight_image = weight_image.convert()  # 以便与显示匹配

speed = 5  # 速度

#创建一个Sprite对象编组，并在其中添加一个Weight实例
sprites = pygame.sprite.RenderUpdates()
sprites.add(Weight(speed))

#获取并填充屏幕表面
screen = pygame.display.get_surface()
bg = (255, 255, 255)  # 白色
screen.fill(bg)
pygame.display.flip()

#用于清除Sprite对象
def clear_callback(surf, rect):
    surf.fill(bg, rect)

while True:
    # 检查退出事件
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
    # 清除以前的位置
    sprites.clear(screen, clear_callback)
    # 更新所有的Sprite对象
    sprites.update()
    # 绘制所有的Sprite对象
    updates = sprites.draw(screen)
    # 更新必要的显示部分
    pygame.display.update(updates)