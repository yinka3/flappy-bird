import pygame
import neat
import time
import os
import random
pygame.font.init()

WIND_WIDTH = 500
WIND_HEIGHT = 800
pygame.display.set_caption("Flappy Bird")
global score

bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]


pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

game_font = pygame.font.SysFont("comicsans", 50)

class Bird:
	imgs = bird_imgs
	max_rotation = 25
	animation_time = 5
	rot_vel = 20

	def __init__(self, x,y):
 		self.x = x
 		self.y = y 
 		self.tilt = 0
 		self.tick_count = 0
 		self.vel = 0 
 		self.height = self.y 
 		self.img_count = 0
 		self.img = self.imgs[0]

	def jump(self):
 		self.vel = -10.5
 		self.tick_count = 0
 		self.height = self.y 


	def move(self):
 		self.tick_count += 1

 		disp = self.vel * (self.tick_count) + 0.5*(3) * (self.tick_count)**2

 		if disp >= 16:
 			disp = (disp/abs(disp)) * 16

 		if disp < 0:
 			disp -= 2

 		self.y = self.y + disp

 		if disp < 0 or self.y < self.height + 50:
 			if self.tilt < self.max_rotation:
 				self.tilt = self.max_rotation
 		else:
 			if self.tilt > -90:
 				self.tilt -= self.rot_vel


	def draw(self, win):
 		self.img_count += 1

 		if self.img_count <= self.animation_time:
 			self.img = self.imgs[0]

 		elif self.img_count <= self.animation_time *2:
 			self.img = self.imgs[1]

 		elif self.img_count <= self.animation_time *3:
 			self.img = self.imgs[2]

 		elif self.img_count <= self.animation_time * 4:
 			self.img = self.imgs[1]

 		elif self.img_count == self.animation_time * 4 + 1:
 			self.img = self.imgs[0]
 			self.img_count = 0


 		if self.tilt <= -80:
 			self.img = self.imgs[1]
 			self.img_count = self.animation_time *2

 		rotated_bird = pygame.transform.rotate(self.img, self.tilt)
 		new_react = rotated_bird.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
 		win.blit(rotated_bird, new_react.topleft)


	def get_mask(self):
 		return pygame.mask.from_surface(self.img)


class Pipe:
	gap = 200
	vel = 5

	def __init__(self, x):
		self.x = x 
		self.height = 0
		#self.gap = 100

		self.top  = 0 
		self.bottom = 0 
		self.pipe_top = pygame.transform.flip(pipe_img, False, True)
		self.pipe_bottom = pipe_img

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.pipe_top.get_height() + 10
		self.bottom = self.height + self.gap + 10

	def move(self):
		self.x -= self.vel

	def draw(self, win):
		win.blit(self.pipe_top, (self.x, self.top))
		win.blit(self.pipe_bottom, (self.x, self.bottom))

	def collide(self, bird, win):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.pipe_top)
		bottom_mask = pygame.mask.from_surface(self.pipe_bottom)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if b_point or t_point:
			return True
		return False


class Base:
	vel = 5
	width = base_img.get_width()
	img = base_img

	def __init__(self, y):
		self.y = y 
		self.x1 = 0 
		self.x2 = self.width

	def move(self):
		self.x1 -= self.vel
		self.x2 -= self.vel

		if self.x1 + self.width < 0:
			self.x1 = self.x2 + self.width

		if self.x2 + self.width < 0:
			self.x2 = self.x1 + self.width


	def draw(self, win):
		win.blit(self.img, (self.x1, self.y))
		win.blit(self.img, (self.x2, self.y))


def draw_wind(win, birds, pipes, base, score):
	win.blit(bg_img, (0,0))

	for pipe in pipes:
		pipe.draw(win)


	text = game_font.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIND_WIDTH - 10 - text.get_width(), 10))

	base.draw(win)
	for bird in birds:
		bird.draw(win)
	pygame.display.update()

def fitness_genome(genomes, config):
	win = pygame.display.set_mode((WIND_WIDTH,WIND_HEIGHT))
	neural_nets = []
	birds = []
	gen = []
	

	for idx, g in genomes:
		g.fitness = 0
		net = neat.nn.FeedForwardNetwork.create(g, config)
		neural_nets.append(net)
		birds.append(Bird(230, 350)) 
		gen.append(g)


	base = Base(730)
	pipes = [Pipe(700)]
	score = 0
	clock = pygame.time.Clock()
	run = True
	while run and len(birds) > 0:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break

		pipe_idx = 0 
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width():
				pipe_idx = 1
	

		for x, bird in enumerate(birds):
			gen[x].fitness += 0.1
			bird.move()

			if gen[x].fitness >= 16:
				gen[x].fitness -= 5.3

			output = neural_nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_idx].height), abs(bird.y - pipes[pipe_idx].bottom)))

			if output[0] > 0.5:
				bird.jump()

		base.move()

		rem = []
		add_pipe = False
		for pipe in pipes:
			pipe.move()
			for bird in birds:
				if pipe.collide(bird, win):
					gen[birds.index(bird)].fitness -= 1
					neural_nets.pop(birds.index(bird))
					gen.pop(birds.index(bird))
					birds.pop(birds.index(bird))
                	
			if pipe.x + pipe.pipe_top.get_width() < 0:
				rem.append(pipe)

			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True

	
		if add_pipe:
		 	score += 1
		 	for g in gen:
		 		g.fitness += 0.1

		 		if g.fitness >= 16:
		 			g.fitness -= 5.3
		 	pipes.append(Pipe(600))

		for i in rem:
			pipes.remove(i)

		for bird in birds:
			if bird.y + bird.img.get_height() - 10 >= 705 or bird.y < -50:
				neural_nets.pop(birds.index(bird))
				gen.pop(birds.index(bird))
				birds.pop(birds.index(bird))

			# if score == 50:
			# 	#run(config_path)
			# 	pygame.quit()
			# 	quit()


		draw_wind(win, birds, pipes, base, score)


def run(config_file):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

	pop = neat.Population(config)

	pop.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	pop.add_reporter(stats)
	winner = pop.run(fitness_genome, 100)

if __name__ == '__main__':
	local_dirc = os.path.dirname(__file__)
	config_path = os.path.join(local_dirc, "config-feedforward.txt")
	run(config_path)


