import pygame
import os
import sys
import random
import sqlite3


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


if __name__ == '__main__':
    pygame.init()

    size = w, h = 1000, 800

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Super Flappy Bird')
    background0 = load_image('start.png')
    background1 = load_image('background.png')

    background0 = pygame.transform.scale(background0, (1000, 800))
    background1 = pygame.transform.scale(background1, (1000, 800))

    bird_sprite = pygame.sprite.Group()
    pipe_sprite = pygame.sprite.Group()

    fps = 60
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 64)


    class Bird(pygame.sprite.Sprite):
        image = load_image('bird.png', -1)
        image = pygame.transform.scale(image, (70, 50))

        def __init__(self):
            super().__init__(bird_sprite)
            self.con = sqlite3.connect("game.db")
            self.cur = self.con.cursor()
            self.image = Bird.image

            self.rect = self.image.get_rect()
            self.rect.x = 150
            self.rect.y = 450

            self.speed = 0
            self.mask = pygame.mask.from_surface(self.image)
            self.best_score = (self.cur.execute("""SELECT best FROM results
                                        WHERE id = 1""").fetchone())[0]
            self.last_score = 0
            self.score = 0

        def Restart(self):
            global death, pre_game, game
            pre_game = True
            game = False
            death = False
            self.rect.x = 150
            self.rect.y = 450
            self.speed = 0

        def Flying(self):
            global game, flying, death
            if 0 < self.rect.y < 750:
                self.speed += 0.2
                if self.speed > 30:
                    self.speed = 0
                if self.rect.bottom < 800:
                    self.rect.y += self.speed
            else:
                death = True
                flying = False

            if pygame.mouse.get_pressed()[0] == 1:
                self.speed = -5

        def Check(self, group):
            global death, flying
            for i in group:
                if pygame.sprite.collide_mask(self, i):
                    death = True
                    flying = False

        def Score(self):
            for i in pipe_sprite:
                if self.rect.x in range(i.rect.x + 90, i.rect.x + 105):
                    self.score += 1
                break
            self.last_score = self.score // 3
            self.cur.execute("""UPDATE results SET total = {} WHERE id = 1""".format(self.score // 3))
            self.con.commit()

            if (self.cur.execute("""SELECT best FROM results
                                        WHERE id = 1""").fetchone())[0] < (self.score // 3):
                self.cur.execute("""UPDATE results SET best = {} WHERE id = 1""".format(self.score // 3))
                self.best_score = self.score // 3
                self.con.commit()

            return (self.cur.execute("""SELECT total FROM results
                                        WHERE id = 1""").fetchone())[0]

        def Clear(self):
            self.score = 0


    def Switch():
        global up
        if not up:
            up = True
        elif up:
            up = False


    class Pipes(pygame.sprite.Sprite):
        image = load_image('pipe.png', -1)
        image = pygame.transform.scale(image, (200, 500))

        def __init__(self, group):
            super().__init__(group)
            self.image = Pipes.image
            self.rect = self.image.get_rect()
            self.rect.x = 0
            self.rect.y = 0
            self.speed = 7
            self.mask = pygame.mask.from_surface(self.image)

        def update(self):
            global death
            if death:
                self.kill()

            if self.rect.x <= -200:
                self.kill()

            self.rect.x -= self.speed

        def Spawn(self):
            global up, lasty
            self.rect.x = bird.rect.x + 1100

            if not up:
                self.rect.y = random.randrange(400, 700)
                lasty = self.rect.y

            elif up:
                self.image = pygame.transform.flip(self.image, False, True)
                self.rect.y = lasty - 800


    bird = Bird()
    dif = 100
    lasty = 0
    pause = False
    up = False
    spawn = False

    game_start = True
    pre_game = False
    game = False

    death = False
    running = True
    flying = False
    c = 0
    while running:
        clock.tick(fps)

        if pre_game:
            screen.blit(background1, (0, 0))
            bird_sprite.draw(screen)
            text3 = font2.render('Press mouse to fly!', True, (0, 0, 0))
            screen.blit(text3, (300, 300))

        if game:
            pre_game = False
            screen.blit(background1, (0, 0))

            pipe_sprite.draw(screen)
            bird_sprite.draw(screen)

            text12 = font1.render('{}'.format(bird.score // 3), True, (0, 0, 255))
            screen.blit(text12, (10, 10))

            if pause:
                flying = False
                pygame.draw.rect(screen, (0, 0, 0),
                                 (300, 150, 400, 80))
                text6 = font1.render('Paused', True, (255, 255, 255))
                screen.blit(text6, (417, 170))

        elif game_start:
            screen.blit(background0, (0, 0))

            font1 = pygame.font.SysFont(None, 64)
            text1 = font1.render('Super Flappy Bird', True, (255, 0, 0))
            screen.blit(text1, (50, 50))

            font2 = pygame.font.SysFont(None, 48)
            text2 = font2.render('Press spacebar to start', True, (0, 0, 0))
            screen.blit(text2, (50, 320))

            text13 = font1.render('Difficulty:', True, (0, 0, 0))
            screen.blit(text13, (50, 180))

            pygame.draw.rect(screen, (0, 255, 0),
                             (300, 180, 100, 50))
            text14 = font2.render('easy', True, (0, 0, 0))
            screen.blit(text14, (315, 187))

            pygame.draw.rect(screen, (0, 140, 175),
                             (450, 180, 100, 50))
            text15 = font2.render('mid', True, (0, 0, 0))
            screen.blit(text15, (470, 187))

            pygame.draw.rect(screen, (200, 0, 0),
                             (600, 180, 100, 50))
            text16 = font2.render('hard', True, (0, 0, 0))
            screen.blit(text16, (612, 187))

            text7 = font2.render('Your best score: {}'.format(bird.best_score), True, (0, 0, 0))
            screen.blit(text7, (62, 110))

        if death:
            c = 0

            bird.Clear()

            font1 = pygame.font.SysFont(None, 64)
            font2 = pygame.font.SysFont(None, 32)

            text3 = font1.render('YOU DIED', True, (220, 35, 0))
            text4 = font1.render('Play again?', True, (0, 0, 0))

            pygame.draw.rect(screen, (0, 0, 0),
                             (445, 450, 100, 60))
            text5 = font2.render('Yes', True, (255, 255, 255))

            pygame.draw.rect(screen, (0, 0, 0),
                             (350, 200, 300, 130))
            text8 = font2.render('TOTAL', True, (255, 255, 255))
            text9 = font1.render('{}'.format(bird.last_score), True, (255, 255, 255))

            text10 = font2.render('BEST', True, (255, 255, 255))
            text11 = font1.render('{}'.format(bird.best_score), True, (255, 255, 255))

            screen.blit(text3, (400, 130))
            screen.blit(text4, (380, 360))
            screen.blit(text5, (474, 470))

            screen.blit(text8, (390, 230))
            screen.blit(text10, (545, 230))
            screen.blit(text9, (392, 265))
            screen.blit(text11, (550, 265))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_start:
                if event.pos[1] in range(180, 230):
                    if event.pos[0] in range(300, 400):
                        dif = 140
                    elif event.pos[0] in range(450, 550):
                        dif = 100
                    elif event.pos[0] in range(600, 700):
                        dif = 75

            if event.type == pygame.KEYUP and game_start:
                game_start = False
                pre_game = True

            if event.type == pygame.MOUSEBUTTONDOWN and not flying and pre_game:
                game = True
                flying = True

            if event.type == pygame.MOUSEBUTTONDOWN and death:
                if 445 <= event.pos[0] <= 545:
                    if 450 <= event.pos[1] <= 510:
                        bird.Restart()
                        for _ in pipe_sprite:
                            _.kill()

            if event.type == pygame.KEYUP and not pause and game and not death:
                pause = True

            elif event.type == pygame.KEYUP and pause and game and not death:
                pause = False
                flying = True

        if flying:
            c += 1
            bird.Flying()
            pipe_sprite.update()

            if c % dif == 0:
                pipe1 = Pipes(pipe_sprite)
                pipe1.Spawn()
                Switch()
                pipe2 = Pipes(pipe_sprite)
                pipe2.Spawn()
                Switch()
            bird.Check(pipe_sprite)
            bird.Score()

        pygame.display.flip()
