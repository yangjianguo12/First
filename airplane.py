from PIL import Image
import pygame
import random
from pygame.locals import *
from os import path

#
pygame.init()
pygame.mixer.init()  #载入&b播放音效
screen = pygame.display.set_mode((480, 600)) # 左上角0点，X向右增加，Y向下增加
pygame.display.set_caption('Plane Battle') #设置窗口的标题
clock = pygame.time.Clock()  #时钟对象,管理定时器

#
FPS = 60  #画面每秒传输帧数画面每秒传输帧数,精灵效果用会流畅起来
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10
WIDTH = 480
HEIGHT = 600
height = -936
font_name = pygame.font.match_font('arial')
########图片和声音#############

#获取路径
img_dir = path.join(path.dirname(__file__),'planeimg')
sound_folder = path.join(path.dirname(__file__),'soundplane')

#将图片加载到内存
background = pygame.image.load(path.join(img_dir,'starfield.png'))#背景
background = pygame.transform.scale(background,(480,1536))
player_img = pygame.image.load(path.join(img_dir,'player.png'))#玩家
player_mini_img = pygame.transform.scale(player_img,(25,19))
#player_mini_img.set_colorkey((0,0,0))
bullet_img = pygame.image.load(path.join(img_dir,'bullet.png'))#玩家炮弹、导弹图片
missile_img = pygame.image.load(path.join(img_dir,'missile.png'))
enemies_images = []#敌人
enemies_list = [
    'enemies1.png',
    'enemies2.png',
    'enemies3.png'
]
for image in enemies_list:
    enemies_img = pygame.image.load(path.join(img_dir,image)).convert()
    enemies_img = pygame.transform.scale(enemies_img,(80, 60))
    enemies_images.append(enemies_img)
enemies_bullet_img = pygame.image.load(path.join(img_dir,'enemies_bullet.png'))#敌方子弹
#这个里面是盾和闪电，大括号是字典
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield.png')) #list列表数据类型
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt.png'))
#火山石
#爆炸
explosion_img = {}
explosion_img['ig'] = []
explosion_img['sm'] = []
explosion_img['player'] = []
for i in range(9):
    #机、火山石爆炸
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey((0,0,0))
    #
    img_lg = pygame.transform.scale(img,(75,75))
    explosion_img['ig'].append(img_lg)
    #
    img_sm = pygame.transform.scale(img,(32,32))
    explosion_img['sm'].append(img_sm)
    #玩家爆炸
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey((0,0,0)) #透明度
    explosion_img['player'].append(img)

##########sound####
#bgm = pygame.mixer.music(path.join(sound_folder,'Natural - Imagine Dragons.mp3'))
#音量
#pygame.mixer.set_volume(0,2)



#################
######函数################################################
##################

#初始和准备
def main_menu():
    global screen   #全局变量
    #menu_song = pygame.mixer.music.load('E:/Sound/plane/menu.ogg')
    #pygame.mixer.music.play(-1) #loop
    title = pygame.image.load(path.join(img_dir,"main.png")).convert()#背景
    title = pygame.transform.scale(title,(WIDTH,HEIGHT),screen)
    screen.blit(title,(0,0))
    pygame.display.update()
    #操作事件
    while True:
        ev = pygame.event.poll()   #事件处理
        #KEYDOWN键盘被按下
        if ev.type == pygame.KEYDOWN:
            break
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, 240,300)
            draw_text(screen, "[A] ←  [S] ↓  [D] →  [W] ↑", 30, 240,400)
            draw_text(screen, "[Space] fire", 30, 240, 450)
            pygame.display.update()

    #加载准备的声音
    #ready = pygame.mixer.Sound('E:/Sound/plane/getready.ogg')
    #ready.play() #播放
    #准备开始的背景和文字
    screen.fill((0,0,0))  #填充背景色
    draw_text(screen,"GET READY!",40,240,200)
    pygame.display.update()

#设置文本属性函数
def draw_text(surf,text,size,x,y):
      font = pygame.font.Font(font_name, size)
      text_surface = font.render(text, True, (255,255,255)) #在一个新 Surface 对象上绘制文本 (text, antialias, color, background=None)
      text_rect = text_surface.get_rect() #返回当text的rect对象
      text_rect.midtop = (x, y)
      surf.blit(text_surface, text_rect) #绘制区域的变化实现的动画 分别是图像，绘制的位置，绘制的截面框.

# 设置玩家血量条属性函数
def draw_shield_bar(surf, x, y, pct):
    pct = max(pct,0)
    fill = (pct/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,(0,255,0),fill_rect)
    pygame.draw.rect(surf,(255,255,255),outline_rect,2)

# 设置玩家生命数量属性函数
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x+30*i
        img_rect.y = y
        surf.blit(img,img_rect)


# 添加敌机函数
def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

######类#####################################################

 #爆炸
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_img[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frake_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_img[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_img[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


#玩家
class Player(pygame.sprite.Sprite):   #精灵封装成一个自定义的类，类继承自pygame.sprite.Sprite
    # pygame.sprite.Sprite就是Pygame里面用来实现精灵的一个类，
    #在__init__方法内部，就可以把各种属性绑定到self，因为self就指向创建的实例本身。
    def __init__(self):   #self不需要传，Python解释器自己会把实例变量传进去：
        # 定义精灵类，从Sprite继承，并重写update()函数
        # 这里必须在初始化函数中执行父类构造函数Sprite.__init__(self)
        pygame.sprite.Sprite.__init__(self)   #基类的init方法
        self.image = pygame.transform.scale(player_img,(50,38))
        self.image.set_colorkey((255,55,255))
        self.rect = self.image.get_rect()
        self.radius = 20    #半径
        self.rect.centerx = 240  #飞机中心x坐标
        self.rect.bottom = 500   #底部
        self.speedx = 0  #跟踪x方向上的移动速度
        self.speedy = 0
        self.shield = 100   #盾牌
        self.shoot_delay = 250   #射击延迟
        self.last_shot = pygame.time.get_ticks()  #得到以毫秒为间隔的时间
        self.lives = 3   #3条命
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    #update() 让精灵留在屏幕上
    def update(self):
            if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME :   #POWERUP_TIME= 5000
                self.power -=1
                self.power_time = pygame.time.get_ticks()
            if self.hidden and pygame.time.get_ticks() - self.hide_timer >1000:
                self.hidden = False
                self.rect.centerx = WIDTH/2
                self.rect.bottom = HEIGHT - 30
            self.speedx = 0
            self.speedy = 0
            # 键盘控制
            keystate = pygame.key.get_pressed()
            if keystate[K_a] or keystate[K_LEFT]:
                self.speedx = -5
            if keystate[K_d] or keystate[K_RIGHT] :
                self.speedx = 5
            if keystate[K_w] or keystate[K_UP] :
                self.speedy = -5
            if keystate[K_s] or keystate[K_DOWN] :
                self.speedy = 5
            if keystate[pygame.K_SPACE]:
                self.shoot()
            #移动范围
            if self.rect.right >WIDTH:
                self.rect.right = WIDTH
            if self.rect.left <0 :
                self.rect.left = 0
            if self.rect.top <10 :
                self.rect.top = 10
            if self.rect.bottom > HEIGHT - 10:
                self.rect.bottom = HEIGHT - 10
            self.rect.x += self.speedx
            self.rect.y += self.speedy

    def shoot(self):
        now = pygame.time.get_ticks()
        if now-self.last_shot >self.shoot_delay:
            self.last_shot = now
        #
        if self.power == 1:
            bullet = Bullet(self.rect.centerx,self.rect.top) #发射时的(x,y)
            all_sprites.add(bullet)
            bullets.add(bullet)
            #shooting_sound.play()
        #if self.power == 2:
        # if self.power >= 3:

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):  #？
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2 , HEIGHT+200)

#敌机
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(enemies_images)
        self.image_orig.set_colorkey((255,255,255))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.90/2)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-150,-100)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(5,10)
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if random.randrange(10) >= 6 : #
            self.enemies_shoot()
        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH+20) :
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

    def enemies_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >self.shoot_delay:
            self.last_shot = now
            enemies_bullet = EnemiesBullet(self.rect.centerx, self.rect.top)  # 发射时的(x,y)
            all_sprites.add(enemies_bullet)
            enemies_bullets.add(enemies_bullet)
            # shooting_sound.play()


#player炮弹
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0 : #超过画面自我了结
            self.kill()

#enemies炮弹
class EnemiesBullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemies_bullet_img
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.centerx = x
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top >600:
            self.kill()

#导弹
#class Missile(pygame.sprite.Sprite):

#补给
class Pow(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey((0,0,0,))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


######主循环##################################################

#游戏开始界面
running = True
menu_display = True

while running:
    if menu_display:
        main_menu()
        pygame.time.wait(3000)
        #pygame.mixer.music.stop()
        #pygame.mixer.music.load('E:/Sound/plane/tgfcoder-FrozenJam-SeamlessLoop.ogg')
        #pygame.mixer.music.play(-1)
        menu_display = False

        all_sprites = pygame.sprite.Group()#管理移动图像,精灵序列图
        player = Player()
        all_sprites.add(player)
        mobs = pygame.sprite.Group()    #敌机
        for i in range(4):
            newmob()
        bullets = pygame.sprite.Group()
        enemies_bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        score = 0  #分数

    #pygame.time模块给我们提供了一个Clock的对象 游戏就不会用掉你所有的CPU资源了
    #动画基于时间运作，我们需要知道上一个画面到现在经过了多少时间，然后我们才能决定是否开始绘制下一幅。
    clock.tick(FPS)

    for event in pygame.event.get():  #按键移动鼠标触发事件（退出
        if event.type == pygame.QUIT:
            running = False
        if event.type ==pygame.KEYDOWN:   #KEYDOWN键盘被按下
            if event.key ==pygame.K_ESCAPE:   #按键escape
                running = False

    all_sprites.update()

     #敌机和玩家子弹碰撞了么(im炸
    #?？？？？？
    hits = pygame.sprite.groupcollide(mobs,bullets,True,True)
    for hit in hits:
        score += 50-hit.radius  #打中加分,radius一个小库用于计分
        #random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center,'ig') #图片
        all_sprites.add(expl)
        if random.random() > 0.9:    #随机数
            pow = Pow(hit.rect.center)  # 补给？？随机给补给么？
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # 玩家与敌机碰撞检测（sm炸
    hits = pygame.sprite.spritecollide(player,mobs,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius*2   #？？？？
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:  #
            #player_die_spund.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()  #玩家是否躲避了
            player.lives -= 1 #生命少1
            player.shield = 100   #dun

    # 玩家与敌机炮弹碰撞检测(sm炸
    hits = pygame.sprite.spritecollide(player,enemies_bullets,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius*2
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        if player.shield <= 0 :
            #player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()  # 玩家死亡
            player.lives -= 1  #生命少1
            player.shield = 100

    #盾牌和闪电
    hits = pygame.sprite.spritecollide(player,powerups,True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10,30) #随机加血10到30
            if player.shield >= 100 :
                player.shield = 100
        if hit.type == 'gun' :           #
             player.powerup()

     #游戏结束
    if player.lives ==  0 and not death_explosion.alive():   #
        pygame.time.wait(1000)  #盾的时间
        screen.fill((0,0,0))
        draw_text(screen,"Ganem Over",40,240,200)
        pygame.display.update()
        pygame.time.wait(3000)
        menu_display = True   #


    #背景循环向下滚动
    screen.fill((0,0,0))
    screen.blit(background,(0,height))
    height +=2
    if height >=-168:
        height = -936

    all_sprites.draw(screen) #
    draw_text(screen,str(score),8,240,10) #字体
    draw_shield_bar(screen, 5, 5, player.shield) #
    draw_lives(screen,WIDTH-100,5, player.lives, player_mini_img) #

    pygame.display.flip()

pygame.quit()



