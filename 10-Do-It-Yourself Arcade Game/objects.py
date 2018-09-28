# @author: Neil
# 2018-09-27

import pygame, config, os
from random import randrange

"这个模块包含游戏Squish使用的游戏对象"
class SquishSprite(pygame.sprite.Sprite):
    """
    游戏Squish中所有精灵的超类。构造函数加载一幅图像，
    设置及精灵的外接矩形和移动范围。移动范围取决于屏
    幕尺寸和边距
    """
    def __init__(self, image):
        super().__init__()
        self.image = pygame.image.load(image).convert()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        shrink = -config.margin * 2
        self.area = screen.get_rect().inflate(shrink, shrink)
        
class Weight(SquishSprite):
    """
    从天而降的铅锤。它使用SquishSprite的构造函数来设置表
    示铅锤的图像，并以其构造函数的一个参数指定的速度下降
    """
    def __init__(self, speed):
        super().__init__(config.weight_image)
        self.speed = speed
        self.reset()
        
    def reset(self):
        """
        将铅锤移到屏幕顶端，并放在一个随机的水平位置
        """
        x = randrange(self.area.left, self.area.right)
        self.rect.midbottom = x, 0
        
    def update(self):
        """
        根据铅锤的速度垂直向下移动相应的距离。同时，根据
        铅锤是否已到达屏幕底部相应地设置属性landed
        """
        self.rect.top += self.speed
        self.landed = self.rect.top >= self.area.bottom
        
class Banana(SquishSprite):
    """
    绝望的香蕉。它使用SquishSprite的构造函数来设置香蕉图像，并停留
    在屏幕底部附近，且水平位置由鼠标的当前位置决定。
    """
    def __init__(self):
        super().__init__(config.banana_image)
        self.rect.bottom = self.area.bottom
        # 这些内边距表示图像中不属于香蕉的部分
        # 如果铅锤进入这些区域，并不认为它砸到了香蕉
        self.pad_top = config.banana_pad_top
        self.pad_side = config.banana_pad_side
        
    def update(self):
        """
        将香蕉中心的x坐标设置为鼠标的当前x坐标，再使用
        矩形的方法clamp确保香蕉位于允许移动的范围内
        """
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect = self.rect.clamp(self.area)

    def touches(self, other):
        """
        判断香蕉是否与另一个精灵（如铅锤）发生了碰撞。这里没有直接
        使用矩形的方法colliderect，而是先使用矩形的方法inflat以及
        pad_side和pad_top计算出一个新的矩形，这个矩形不包含香蕉图
        像顶部和两边的“空白”区域
        """
        # 通过剔除内边距来计算bounds：
        bounds = self.rect.inflate(-self.pad_side, -self.pad_top)
        # 将bounds移动到与香蕉底部对齐：
        bounds.bottom = self.rect.bottom
        # 检查bounds是否与另一个对象的rect重叠
        return bounds.colliderect(other.rect)