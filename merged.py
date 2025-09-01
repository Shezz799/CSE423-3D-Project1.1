from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18


player_alive = True
CHEAT_ON = False            # Top-down cheat camera + absolute movement
first_person = True         # Toggle with 'f' or right mouse


final_run_active = False
final_run_start_time = 0.0
game_won = False
CRUSHING_WALL_SPEED = 25.0

# Avoid re-creating quadric objects
spike_quadric = None
gun_quadric = None

colors = {
	'WHITE': (1.0, 1.0, 1.0),
	'LILAC': (0.85, 0.75, 0.95),
	'BLUE': (0.0, 0.0, 1.0),
	'CYAN': (0.0, 1.0, 1.0),
	'GREEN': (0.0, 1.0, 0.0),
	'BLACK': (0.0, 0.0, 0.0),
	'YELLOW': (1.0, 1.0, 0.0),
	'BROWN': (0.59, 0.29, 0.0),
}

# Fire effect
NUM_PARTICLES = 200
FIRE_MAX_HEIGHT = 80.0
FIRE_SPEED = 0.8
fire_particles = []

# Water waves
WAVE_SUBDIV = 20
WAVE_AMPLITUDE = 3.0

fovY = 120
GRID = 1000
rand_var = 423

# Camera
camera_radius = 1000
camera_angle = 0
camera_height = 1200

mouse_x = 480
mouse_y = 540
mouse_sensitivity = 0.12

# Maze grid construction
co = []
i = 0
dist = -1000
p = 170
w = 10
b = 15
height = 300
while True:
	co += [dist]
	if i == 0:
		dist += b
	elif i == 22:
		dist += b
		co += [dist]
		break
	elif i % 2 == 1:
		dist += p
	else:
		dist += w
	i += 1

print(co)

# Player position and stats
player_x = (co[1] + co[2]) // 2 #600
player_y = (co[19] + co[20]) // 2 # -700
player_movement_speed = 20.0
player_radius = 5.0
player_hp = 100

# Stamina/Jump (from temp1.py)
player_stamina = 100.0
max_stamina = 100.0
stamina_regen_rate = 0.02
stamina_drain_rate = 8.0
stamina_jump_cost = 25.0
is_sprinting = False
is_jumping = False

player_z = 0.0
jump_height = 80.0
jump_speed = 8.0
jump_gravity = 0.8
jump_velocity = 0.0
jump_forward_velocity = 0.0
jump_forward_speed = 15.0
is_grounded = True
is_jumping_forward = False
jump_cooldown = 0
jump_cooldown_max = 10

# Enemies
attack_range = 250.0
ENEMY_CHASE_SPEED = 20.0
ENEMY_RADIUS = 12.0

# Shooting
BULLET_SPEED = 20.0
BULLET_SIZE = 4.0
BULLET_MAX_DIST = 2000.0
ENEMY_HIT_RADIUS = 35.0
MAX_AMMO = 30
ammo_remaining = MAX_AMMO
bullets = []   # {x,y,z,dir_deg,dist,alive}

# Character model dims
CHAR_HEAD = (15.0, 15.0, 15.0)
CHAR_TORSO = (25.0, 10.0, 30.0)
CHAR_ARM = (9.0, 7.0, 25.0)
CHAR_LEG = (9.0, 7.0, 25.0)

# Player view
player_yaw = 90.0
yaw_step = 4.0
eye_height = 120.0

# Walls cache for collision
walls_rects = []


# ------------------------------
# Helpers and geometry
# ------------------------------
def _cell_center(ix, iy):
	return ((co[ix] + co[ix + 1]) // 2, (co[iy] + co[iy + 1]) // 2)


def add_wall_rect(x1, y1, x2, y2):
	x_min, x_max = (x1, x2) if x1 <= x2 else (x2, x1)
	y_min, y_max = (y1, y2) if y1 <= y2 else (y2, y1)
	walls_rects.append((x_min, y_min, x_max, y_max))


def build_walls_rects():
	walls_rects.clear()
	# Boundaries
	add_wall_rect(co[0], co[0], co[23], co[1])
	add_wall_rect(co[0], co[22], co[23], co[23])
	add_wall_rect(co[0], co[0], co[1], co[19])
	add_wall_rect(co[0], co[20], co[1], co[23])
	add_wall_rect(co[22], co[0], co[23], co[3])
	add_wall_rect(co[22], co[4], co[23], co[23])

	# Insides (same layout from both files)
	add_wall_rect(co[0], co[20], co[6], co[21])
	add_wall_rect(co[10], co[21], co[11], co[23])
	add_wall_rect(co[12], co[20], co[19], co[21])
	add_wall_rect(co[18], co[21], co[19], co[23])
	add_wall_rect(co[20], co[16], co[21], co[23])

	add_wall_rect(co[0], co[18], co[4], co[19])
	add_wall_rect(co[8], co[18], co[9], co[20])
	add_wall_rect(co[8], co[18], co[14], co[19])
	add_wall_rect(co[12], co[16], co[13], co[21])
	add_wall_rect(co[17], co[18], co[19], co[19])

	add_wall_rect(co[3], co[16], co[5], co[17])
	add_wall_rect(co[6], co[15], co[7], co[18])
	add_wall_rect(co[6], co[16], co[13], co[17])
	add_wall_rect(co[14], co[16], co[16], co[17])
	add_wall_rect(co[18], co[15], co[19], co[18])
	add_wall_rect(co[18], co[16], co[21], co[17])

	add_wall_rect(co[2], co[14], co[5], co[15])
	add_wall_rect(co[4], co[14], co[5], co[17])
	add_wall_rect(co[8], co[12], co[9], co[17])
	add_wall_rect(co[10], co[14], co[15], co[15])
	add_wall_rect(co[14], co[14], co[15], co[17])
	add_wall_rect(co[16], co[14], co[17], co[17])
	add_wall_rect(co[20], co[14], co[23], co[15])

	add_wall_rect(co[2], co[10], co[3], co[15])
	add_wall_rect(co[4], co[12], co[9], co[13])
	add_wall_rect(co[10], co[13], co[11], co[15])
	add_wall_rect(co[12], co[8], co[13], co[15])
	add_wall_rect(co[12], co[8], co[13], co[12])
	add_wall_rect(co[17], co[12], co[19], co[13])
	add_wall_rect(co[20], co[10], co[21], co[15])

	add_wall_rect(co[0], co[10], co[3], co[11])
	add_wall_rect(co[4], co[6], co[5], co[13])
	add_wall_rect(co[6], co[10], co[11], co[11])
	add_wall_rect(co[14], co[9], co[15], co[13])
	add_wall_rect(co[14], co[10], co[17], co[11])
	add_wall_rect(co[18], co[10], co[19], co[13])
	add_wall_rect(co[18], co[10], co[21], co[11])

	add_wall_rect(co[6], co[8], co[7], co[11])
	add_wall_rect(co[6], co[8], co[9], co[9])
	add_wall_rect(co[10], co[5], co[11], co[11])
	add_wall_rect(co[10], co[8], co[13], co[9])
	add_wall_rect(co[16], co[6], co[17], co[11])
	add_wall_rect(co[16], co[8], co[23], co[9])

	add_wall_rect(co[2], co[0], co[3], co[8])
	add_wall_rect(co[4], co[6], co[6], co[7])
	add_wall_rect(co[8], co[2], co[9], co[9])
	add_wall_rect(co[12], co[6], co[17], co[7])
	add_wall_rect(co[18], co[6], co[20], co[7])

	add_wall_rect(co[4], co[4], co[9], co[5])
	add_wall_rect(co[12], co[2], co[13], co[7])
	add_wall_rect(co[14], co[5], co[15], co[7])
	add_wall_rect(co[17], co[4], co[23], co[5])
	add_wall_rect(co[18], co[5], co[19], co[7])

	add_wall_rect(co[4], co[3], co[5], co[5])
	add_wall_rect(co[6], co[2], co[10], co[3])
	add_wall_rect(co[12], co[2], co[14], co[3])
	add_wall_rect(co[19], co[2], co[23], co[3])
	add_wall_rect(co[6], co[0], co[7], co[3])
	add_wall_rect(co[16], co[0], co[17], co[2])


build_walls_rects()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=None):
	if color is not None:
		glColor3f(*color)
	else:
		glColor3f(1, 1, 1)
	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	gluOrtho2D(0, 1000, 0, 800)
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()
	glRasterPos2f(x, y)
	for ch in text:
		glutBitmapCharacter(font, ord(ch))
	glPopMatrix()
	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	glMatrixMode(GL_MODELVIEW)


def _draw_cuboid(w, d, h, color):
	glColor3f(*color)
	glPushMatrix()
	glScalef(w, d, h)
	glutSolidCube(1.0)
	glPopMatrix()


def cuboids(p1, p2, p3, p4, h, color):
	glColor3f(*color)
	glBegin(GL_QUADS)
	# right
	glVertex3f(p4[0], p4[1], 0)
	glVertex3f(p4[0], p4[1], h)
	glVertex3f(p3[0], p3[1], h)
	glVertex3f(p3[0], p3[1], 0)
	# left
	glVertex3f(p2[0], p2[1], 0)
	glVertex3f(p2[0], p2[1], h)
	glVertex3f(p1[0], p1[1], h)
	glVertex3f(p1[0], p1[1], 0)
	# back
	glVertex3f(p2[0], p2[1], 0)
	glVertex3f(p2[0], p2[1], h)
	glVertex3f(p3[0], p3[1], h)
	glVertex3f(p3[0], p3[1], 0)
	# front
	glVertex3f(p1[0], p1[1], 0)
	glVertex3f(p1[0], p1[1], h)
	glVertex3f(p4[0], p4[1], h)
	glVertex3f(p4[0], p4[1], 0)
	# top
	glVertex3f(p1[0], p1[1], h)
	glVertex3f(p2[0], p2[1], h)
	glVertex3f(p3[0], p3[1], h)
	glVertex3f(p4[0], p4[1], h)
	glEnd()


def draw_walls():
	for (x1, y1, x2, y2) in walls_rects:
		cuboids((x1, y1), (x1, y2), (x2, y2), (x2, y1), height, colors['BROWN'])


def is_valid_position(x, y):
	if x < co[0] or x > co[23] or y < co[0] or y > co[23]:
		return False
	pr = player_radius
	for (x1, y1, x2, y2) in walls_rects:
		if (x1 - pr <= x <= x2 + pr) and (y1 - pr <= y <= y2 + pr):
			return False
	return True


# --------------- Character (merged: supports CHEAT and jump height) ---------------
def draw_character(position):
	x, y, base_z = position
	total_z = base_z + max(0.0, player_z)

	skin = (1.0, 0.85, 0.7)
	shirt = (0.2, 0.5, 0.9)
	pants = (0.15, 0.25, 0.55)
	boots = (0.25, 0.12, 0.05)

	torso_w, torso_d, torso_h = CHAR_TORSO
	head_w, head_d, head_h = CHAR_HEAD
	arm_w, arm_d, arm_h = CHAR_ARM
	leg_w, leg_d, leg_h = CHAR_LEG

	glPushMatrix()
	glTranslatef(x, y, total_z)
	try:
		glRotatef(player_yaw, 0.0, 0.0, 1.0)
	except NameError:
		pass

	# Legs
	leg_x_offset = (torso_w * 0.33)
	leg_y_offset = (torso_d * 0.25)
	leg_z = leg_h * 0.5
	glPushMatrix(); glTranslatef(-leg_x_offset, -leg_y_offset, leg_z)
	_draw_cuboid(leg_w, leg_d, leg_h, pants)
	glTranslatef(0.0, 0.0, -leg_h * 0.5 + 10.0)
	_draw_cuboid(leg_w, leg_d, 16.0, boots)
	glPopMatrix()
	glPushMatrix(); glTranslatef(+leg_x_offset, +leg_y_offset, leg_z)
	_draw_cuboid(leg_w, leg_d, leg_h, pants)
	glTranslatef(0.0, 0.0, -leg_h * 0.5 + 10.0)
	_draw_cuboid(leg_w, leg_d, 16.0, boots)
	glPopMatrix()

	# Torso
	torso_z = leg_h + torso_h * 0.5
	glPushMatrix(); glTranslatef(0.0, 0.0, torso_z)
	_draw_cuboid(torso_w, torso_d, torso_h, shirt)
	glPopMatrix()

	# Arms
	arm_x_offset = torso_w * 0.5 + arm_w * 0.55
	arm_y_offset = torso_d * 0.05
	arm_z = leg_h + torso_h - arm_h * 0.5 + 5.0
	glPushMatrix(); glTranslatef(-arm_x_offset, -arm_y_offset, arm_z)
	_draw_cuboid(arm_w, arm_d, arm_h, skin)
	glTranslatef(0.0, 0.0, -arm_h * 0.5 + 10.0)
	_draw_cuboid(arm_w, arm_d, 20.0, skin)
	glPopMatrix()
	glPushMatrix(); glTranslatef(+arm_x_offset, +arm_y_offset, arm_z)
	_draw_cuboid(arm_w, arm_d, arm_h, skin)
	glTranslatef(0.0, 0.0, -arm_h * 0.5 + 10.0)
	_draw_cuboid(arm_w, arm_d, 20.0, skin)
	glPopMatrix()

	# Head
	head_z = leg_h + torso_h + head_h * 0.5 + 4.0
	glPushMatrix()
	glTranslatef(0.0, 0.0, head_z)
	if CHEAT_ON:
		glScalef(1, 1, 30)
		_draw_cuboid(head_w, head_d, head_h, (1.0, 0.0, 0.0))
	else:
		_draw_cuboid(head_w, head_d, head_h, skin)
	glPopMatrix()

	glPopMatrix()


# --------------- Enemies ---------------
ENEMY_SPAWNS = [
	_cell_center(2 - 1, 19),
	_cell_center(6 - 1, 19),
	_cell_center(12 - 1, 10),
	_cell_center(16 - 1, 10),
	_cell_center(12 - 1, 16),
	_cell_center(18 - 1, 6),
	_cell_center(20 - 1, 14),
]

enemies = []
_enemies_initialized = False


def _draw_enemy(position, yaw=None, down=False):
	palette = {
		'skin': (0.35, 0.75, 0.35),
		'shirt': (0.6, 0.0, 0.0),
		'pants': (0.15, 0.15, 0.18),
		'boots': (0.1, 0.05, 0.05),
	}
	x, y, z = position
	glPushMatrix()
	glTranslatef(x, y, z)
	if yaw is not None:
		glRotatef(yaw, 0.0, 0.0, 1.0)
	if down:
		glRotatef(90.0, 1.0, 0.0, 0.0)
		glTranslatef(0.0, 0.0, CHAR_LEG[2] + CHAR_TORSO[2] * 0.5)

	torso_w, torso_d, torso_h = CHAR_TORSO
	head_w, head_d, head_h = CHAR_HEAD
	arm_w, arm_d, arm_h = CHAR_ARM
	leg_w, leg_d, leg_h = CHAR_LEG

	pants = palette['pants']
	boots = palette['boots']
	leg_x_offset = (torso_w * 0.33)
	leg_y_offset = (torso_d * 0.25)
	leg_z = leg_h * 0.5
	glPushMatrix(); glTranslatef(-leg_x_offset, -leg_y_offset, leg_z)
	_draw_cuboid(leg_w, leg_d, leg_h, pants)
	glTranslatef(0.0, 0.0, -leg_h * 0.5 + 10.0)
	_draw_cuboid(leg_w, leg_d, 16.0, boots)
	glPopMatrix()
	glPushMatrix(); glTranslatef(+leg_x_offset, +leg_y_offset, leg_z)
	_draw_cuboid(leg_w, leg_d, leg_h, pants)
	glTranslatef(0.0, 0.0, -leg_h * 0.5 + 10.0)
	_draw_cuboid(leg_w, leg_d, 16.0, boots)
	glPopMatrix()

	shirt = palette['shirt']
	torso_z = leg_h + torso_h * 0.5
	glPushMatrix(); glTranslatef(0.0, 0.0, torso_z)
	_draw_cuboid(torso_w, torso_d, torso_h, shirt)
	glPopMatrix()

	skin = palette['skin']
	arm_x_offset = torso_w * 0.5 + arm_w * 0.55
	arm_y_offset = torso_d * 0.05
	arm_z = leg_h + torso_h - arm_h * 0.5 + 5.0
	glPushMatrix(); glTranslatef(-arm_x_offset, -arm_y_offset, arm_z)
	_draw_cuboid(arm_w, arm_d, arm_h, skin)
	glTranslatef(0.0, 0.0, -arm_h * 0.5 + 10.0)
	_draw_cuboid(arm_w, arm_d, 20.0, skin)
	glPopMatrix()
	glPushMatrix(); glTranslatef(+arm_x_offset, +arm_y_offset, arm_z)
	_draw_cuboid(arm_w, arm_d, arm_h, skin)
	glTranslatef(0.0, 0.0, -arm_h * 0.5 + 10.0)
	_draw_cuboid(arm_w, arm_d, 20.0, skin)
	glPopMatrix()

	head_z = leg_h + torso_h + head_h * 0.5 + 4.0
	glPushMatrix(); glTranslatef(0.0, 0.0, head_z)
	_draw_cuboid(head_w, head_d, head_h, skin)
	glPopMatrix()
	glPopMatrix()


def init_enemies():
	global enemies, _enemies_initialized
	if _enemies_initialized:
		return
	enemies.clear()
	for (sx, sy) in ENEMY_SPAWNS:
		enemies.append({'x': float(sx), 'y': float(sy), 'yaw': 0.0, 'last_hit_time': None, 'down': False})
	_enemies_initialized = True


def update_enemies(dt):
	global player_hp
	if not enemies:
		return
	now = time.perf_counter()
	for e in enemies:
		if e.get('down'):
			continue
		dx = player_x - e['x']
		dy = player_y - e['y']
		dist = math.hypot(dx, dy)
		if dist <= attack_range:
			if dist > 1e-4:
				e['yaw'] = math.degrees(math.atan2(dx, dy))
			step = ENEMY_CHASE_SPEED * dt
			if step > 0:
				nx = e['x'] + (dx / dist) * step
				ny = e['y'] + (dy / dist) * step
				if is_valid_position(nx, ny):
					e['x'], e['y'] = nx, ny
				elif is_valid_position(nx, e['y']):
					e['x'] = nx
				elif is_valid_position(e['x'], ny):
					e['y'] = ny
		if dist <= (player_radius + ENEMY_RADIUS):
			if e['last_hit_time'] is None or (now - e['last_hit_time']) >= 2.0:
				player_hp = max(0, player_hp - 10)
				e['last_hit_time'] = now
		else:
			e['last_hit_time'] = None


def draw_enemies(spawns=None):
	global ENEMY_SPAWNS
	if spawns is not None and len(spawns) == 7:
		ENEMY_SPAWNS = [(float(x), float(y)) for (x, y) in spawns]
	init_enemies()
	for e in enemies:
		_draw_enemy((e['x'], e['y'], 0.0), yaw=e['yaw'], down=e.get('down', False))


# --------------- Shooting/viewmodel ---------------
def fire_bullet():
	global ammo_remaining
	if ammo_remaining <= 0:
		return
	rad = math.radians(player_yaw)
	bx = player_x + 48.0 * math.sin(rad)
	by = player_y + 48.0 * math.cos(rad)
	bz = (CHAR_LEG[2] + CHAR_TORSO[2]) - 10.0 + player_z
	bullets.append({'x': bx, 'y': by, 'z': bz, 'dir_deg': float(player_yaw), 'dist': 0.0, 'alive': True})
	ammo_remaining -= 1


def update_bullets():
	for b in bullets:
		if not b['alive']:
			continue
		rad = math.radians(b['dir_deg'])
		b['x'] += BULLET_SPEED * math.sin(rad)
		b['y'] += BULLET_SPEED * math.cos(rad)
		b['dist'] += BULLET_SPEED
		if not (co[0] < b['x'] < co[23] and co[0] < b['y'] < co[23] and b['dist'] < BULLET_MAX_DIST):
			b['alive'] = False
			continue
		for e in enemies:
			if e.get('down'):
				continue
			dx = b['x'] - e['x']
			dy = b['y'] - e['y']
			if math.hypot(dx, dy) <= ENEMY_HIT_RADIUS:
				e['down'] = True
				b['alive'] = False
				break


def draw_bullets():
	glPointSize(6.0)
	glBegin(GL_POINTS)
	glColor3f(1.0, 0.2, 0.1)
	for b in bullets:
		if b.get('alive', False):
			glVertex3f(b['x'], b['y'], b['z'])
	glEnd()


def draw_gun_overlay():
	if not first_person:
		return
	global gun_quadric
	if gun_quadric is None:
		gun_quadric = gluNewQuadric()
	glDisable(GL_DEPTH_TEST)
	glMatrixMode(GL_PROJECTION)
	glPushMatrix(); glLoadIdentity()
	glOrtho(0, 960, 0, 1080, -200, 200)
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix(); glLoadIdentity()
	glPushMatrix()
	glTranslatef(480, 60, 50)       # centered bottom
	glRotatef(-90, 1, 0, 0)
	glRotatef(12, 0, 0, 1)          # slight left yaw
	glColor3f(0.45, 0.45, 0.5)
	gluCylinder(gun_quadric, 20.0, 12.0, 140.0, 20, 1)
	glPopMatrix()
	glPopMatrix()
	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	glMatrixMode(GL_MODELVIEW)
	glEnable(GL_DEPTH_TEST)


# --------------- Traps ---------------
def water_patch(x1, y1, x2, y2):
	t = time.perf_counter()
	base_height = 5.0
	step_x = (x2 - x1) / float(WAVE_SUBDIV)
	step_y = (y2 - y1) / float(WAVE_SUBDIV)
	cuboids((x1, y1), (x1, y2), (x2, y2), (x2, y1), 2, (0.27, 0.51, 0.71))
	glBegin(GL_QUADS)
	for i in range(WAVE_SUBDIV):
		for j in range(WAVE_SUBDIV):
			vx0 = x1 + i * step_x
			vy0 = y1 + j * step_y
			vx1 = vx0 + step_x
			vy1 = vy0 + step_y
			z00 = base_height + math.sin((vx0 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy0 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
			z01 = base_height + math.sin((vx0 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy1 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
			z10 = base_height + math.sin((vx1 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy0 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
			z11 = base_height + math.sin((vx1 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy1 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
			glColor3f(0.4, 0.7, 0.9)
			glVertex3f(vx0, vy0, z00)
			glVertex3f(vx1, vy0, z10)
			glVertex3f(vx1, vy1, z11)
			glVertex3f(vx0, vy1, z01)
	glEnd()


def fire_patch(x1, y1, x2, y2):
	cuboids((x1, y1), (x1, y2), (x2, y2), (x2, y1), 2, (1.0, 0.4, 0.0))
	global fire_particles
	base_height = 5.0
	if not fire_particles:
		for _ in range(NUM_PARTICLES):
			ix = random.uniform(x1, x2)
			iy = random.uniform(y1, y2)
			life = random.uniform(0.0, FIRE_MAX_HEIGHT)
			fire_particles.append([ix, iy, 0.0, life])
	glPointSize(3)
	glBegin(GL_POINTS)
	for p in fire_particles:
		p[3] += FIRE_SPEED
		if p[3] > FIRE_MAX_HEIGHT:
			p[0] = random.uniform(x1, x2)
			p[1] = random.uniform(y1, y2)
			p[3] = 0.0
			continue
		p[2] = base_height + p[3]
		life_ratio = 1.0 - (p[3] / FIRE_MAX_HEIGHT)
		glColor3f(1.0, life_ratio * 0.5, 0.0)
		glVertex3f(p[0], p[1], p[2])
	glEnd()


def spikes_patch(p1, p2):
	global spike_quadric
	SPIKE_HEIGHT = 100.0
	SPIKE_RADIUS = 15.0
	NUM_SPIKES = 6
	PAUSE_DURATION = 0.5
	MOVE_DURATION = 0.2
	CYCLE_DURATION = 2 * PAUSE_DURATION + 2 * MOVE_DURATION
	time_in_cycle = time.time() % CYCLE_DURATION
	phase1_end = PAUSE_DURATION
	phase2_end = phase1_end + MOVE_DURATION
	phase3_end = phase2_end + PAUSE_DURATION
	if time_in_cycle < phase1_end:
		animation_progress = 0.0
	elif time_in_cycle < phase2_end:
		progress = (time_in_cycle - phase1_end) / MOVE_DURATION
		animation_progress = (math.sin(progress * math.pi - math.pi / 2) + 1) / 2
	elif time_in_cycle < phase3_end:
		animation_progress = 1.0
	else:
		progress = (time_in_cycle - phase3_end) / MOVE_DURATION
		animation_progress = 1.0 - ((math.sin(progress * math.pi - math.pi / 2) + 1) / 2)
	z_offset = -SPIKE_HEIGHT + animation_progress * SPIKE_HEIGHT
	if spike_quadric is None:
		spike_quadric = gluNewQuadric()
	glColor3f(0.75, 0.75, 0.75)
	x1, y1 = p1
	x2, y2 = p2
	dx, dy = x2 - x1, y2 - y1
	distance = math.sqrt(dx * dx + dy * dy)
	if distance == 0:
		return
	norm_dx, norm_dy = dx / distance, dy / distance
	start_center_x = x1 + norm_dx * SPIKE_RADIUS
	start_center_y = y1 + norm_dy * SPIKE_RADIUS
	end_center_x = x2 - norm_dx * SPIKE_RADIUS
	end_center_y = y2 - norm_dy * SPIKE_RADIUS
	center_dx = end_center_x - start_center_x
	center_dy = end_center_y - start_center_y
	for i in range(NUM_SPIKES):
		fraction = i / (NUM_SPIKES - 1) if NUM_SPIKES > 1 else 0.5
		spike_x = start_center_x + center_dx * fraction
		spike_y = start_center_y + center_dy * fraction
		glPushMatrix()
		glTranslatef(spike_x, spike_y, 0)
		glTranslatef(0, 0, z_offset)
		gluCylinder(spike_quadric, SPIKE_RADIUS, 0.0, SPIKE_HEIGHT, 16, 1)
		glPopMatrix()


def draw_traps():
	water_patch(co[10], co[1], co[12], co[2])
	fire_patch(co[3], co[5], co[4], co[8])
	spikes_patch((co[13], co[10]), (co[14], co[10]))
	spikes_patch((co[12], co[16]), (co[12], co[15]))


# --------------- Final run (crushing walls) ---------------
def draw_crushing_walls():
	if not final_run_active:
		return
	elapsed_time = time.time() - final_run_start_time
	travel_distance = co[4] - co[3]
	current_offset = min(travel_distance, elapsed_time * CRUSHING_WALL_SPEED)
	# Bottom wall (moves up)
	glPushMatrix()
	glTranslatef(0, current_offset, 0)
	p1 = (co[19], co[2]); p2 = (co[19], co[3]); p3 = (co[23], co[3]); p4 = (co[23], co[2])
	cuboids(p1, p2, p3, p4, height, colors['BROWN'])
	glPopMatrix()
	# Top wall (moves down)
	glPushMatrix()
	glTranslatef(0, -current_offset, 0)
	p1 = (co[19], co[4]); p2 = (co[19], co[5]); p3 = (co[23], co[5]); p4 = (co[23], co[4])
	cuboids(p1, p2, p3, p4, height, colors['BROWN'])
	glPopMatrix()


def final_run():
	global final_run_active, final_run_start_time, player_alive, game_won
	if not final_run_active and player_x >= co[19] and co[3] <= player_y <= co[4]:
		final_run_active = True
		final_run_start_time = time.time()
		print("--- FINAL RUN ACTIVATED! ESCAPE! ---")
	if final_run_active and player_alive:
		elapsed_time = time.time() - final_run_start_time
		wall1_edge = co[2] + elapsed_time * CRUSHING_WALL_SPEED
		wall2_edge = co[5] - elapsed_time * CRUSHING_WALL_SPEED
		if player_x >= co[23]:
			game_won = True
			player_alive = False
			print("--- YOU ESCAPED! YOU WIN! ---")
		elif wall1_edge >= wall2_edge:
			player_alive = False
			print("--- YOU WERE CRUSHED! GAME OVER. ---")


# --------------- Movement ---------------
def _move_along_facing(forward_deg: float):
	global player_x, player_y
	step = player_movement_speed
	rad = math.radians(forward_deg)
	dx = step * math.sin(rad)
	dy = step * math.cos(rad)
	new_x = player_x + dx
	new_y = player_y + dy
	if is_valid_position(new_x, new_y):
		player_x, player_y = new_x, new_y


def enhanced_move_along_facing(forward_deg: float, is_sprint: bool = False):
	global player_x, player_y
	current_speed = player_movement_speed
	if is_sprint and player_stamina > 0:
		current_speed *= 1.8
	elif player_stamina <= 0:
		current_speed *= 0.5
	step = current_speed
	rad = math.radians(forward_deg)
	dx = step * math.sin(rad)
	dy = step * math.cos(rad)
	new_x = player_x + dx
	new_y = player_y + dy
	if is_valid_position(new_x, new_y):
		player_x, player_y = new_x, new_y


# --------------- Stamina/Jump ---------------
def update_stamina():
	global player_stamina, is_sprinting
	if is_sprinting and player_stamina > 0:
		player_stamina = max(0.0, player_stamina - stamina_drain_rate)
	if not is_sprinting and player_stamina < max_stamina:
		player_stamina = min(max_stamina, player_stamina + stamina_regen_rate)
	if player_stamina <= 0:
		is_sprinting = False


def is_valid_jump_position(x, y):
	return is_valid_position(x, y)


def perform_jump():
	global is_jumping, jump_velocity, jump_forward_velocity, is_grounded, is_jumping_forward, jump_cooldown, player_stamina
	if is_grounded and jump_cooldown <= 0 and player_stamina >= stamina_jump_cost:
		is_jumping = True
		is_jumping_forward = True
		jump_velocity = jump_speed
		jump_forward_velocity = jump_forward_speed
		is_grounded = False
		jump_cooldown = jump_cooldown_max
		player_stamina -= stamina_jump_cost


def update_jump():
	global player_z, jump_velocity, jump_forward_velocity, is_grounded, is_jumping_forward, jump_cooldown, player_x, player_y, is_jumping
	if jump_cooldown > 0:
		jump_cooldown -= 1
	if not is_grounded:
		jump_velocity -= jump_gravity
		player_z += jump_velocity
		if is_jumping_forward:
			rad = math.radians(player_yaw)
			forward_dx = math.sin(rad) * jump_forward_velocity
			forward_dy = math.cos(rad) * jump_forward_velocity
			new_x = player_x + forward_dx
			new_y = player_y + forward_dy
			if is_valid_jump_position(new_x, new_y):
				player_x = new_x
				player_y = new_y
			jump_forward_velocity = max(0, jump_forward_velocity - 0.5)
		if player_z <= 0:
			player_z = 0
			jump_velocity = 0
			jump_forward_velocity = 0
			is_grounded = True
			is_jumping_forward = False
			is_jumping = False
	else:
		if player_z <= 0:
			player_z = 0
			jump_velocity = 0
			jump_forward_velocity = 0
			is_grounded = True
			is_jumping_forward = False
			is_jumping = False


def draw_jump_direction_indicator():
	if is_grounded and jump_cooldown <= 0:
		rad = math.radians(player_yaw)
		indicator_length = 50.0
		start_x = player_x; start_y = player_y; start_z = player_z + 5
		end_x = player_x + math.sin(rad) * indicator_length
		end_y = player_y + math.cos(rad) * indicator_length
		end_z = start_z + 20
		glColor3f(1.0, 1.0, 0.0)
		glLineWidth(3.0)
		glBegin(GL_LINES)
		glVertex3f(start_x, start_y, start_z)
		glVertex3f(end_x, end_y, end_z)
		glEnd()
		glLineWidth(1.0)


# --------------- Input ---------------
def keyboardListener(key, x, y):
	global camera_height, player_x, player_y, camera_angle, player_yaw, eye_height, first_person, CHEAT_ON, is_sprinting
	# Universal toggles
	if key in (b'c', b'C'):
		CHEAT_ON = not CHEAT_ON
		return
	if key in (b'i', b'I'):
		camera_height -= 50; eye_height = max(20.0, eye_height - 10.0); return
	if key in (b'o', b'O'):
		camera_height += 50; eye_height = min(250.0, eye_height + 10.0); return
	# Jump
	if key == b' ':
		perform_jump(); return
	# Sprint toggle (optional key)
	if key in (b'x', b'X', b'p', b'P', b't', b'T'):
		is_sprinting = not is_sprinting; return

	if CHEAT_ON:
		# Absolute movement in cheat mode
		new_x, new_y = player_x, player_y
		step = player_movement_speed
		if key in (b'w', b'W'): new_y += step
		elif key in (b's', b'S'): new_y -= step
		elif key in (b'a', b'A'): new_x -= step
		elif key in (b'd', b'D'): new_x += step
		if is_valid_position(new_x, new_y):
			player_x, player_y = new_x, new_y
		glutPostRedisplay(); return

	# First/third person controls
	if key in (b'f', b'F'):
		first_person = not first_person
		if not first_person:
			camera_angle = player_yaw % 360.0
		return

	if key in (b'd', b'D'):
		player_yaw = (player_yaw + yaw_step) % 360.0
	elif key in (b'a', b'A'):
		player_yaw = (player_yaw - yaw_step) % 360.0
	elif key in (b'w', b'W'):
		enhanced_move_along_facing(player_yaw, is_sprinting)
	elif key in (b's', b'S'):
		enhanced_move_along_facing((player_yaw + 180.0) % 360.0, is_sprinting)


def specialKeyListener(key, x, y):
	global camera_radius, camera_angle, player_yaw, first_person, is_sprinting
	if key == GLUT_KEY_LEFT:
		camera_angle = (camera_angle + 3) % 360.0
		if first_person:
			player_yaw = camera_angle
	elif key == GLUT_KEY_RIGHT:
		camera_angle = (camera_angle - 3) % 360.0
		if first_person:
			player_yaw = camera_angle
	elif key == GLUT_KEY_UP:
		if camera_radius != 1:
			camera_radius = camera_radius - 49 if camera_radius == 50 else camera_radius - 50
	elif key == GLUT_KEY_DOWN:
		camera_radius += 50
	elif key in (16, 17, 112, 113):  # various shift codes and P
		is_sprinting = not is_sprinting


def mouseListener(button, state, x, y):
	global first_person
	if state == GLUT_DOWN:
		if button == GLUT_LEFT_BUTTON:
			fire_bullet()
		elif button == GLUT_RIGHT_BUTTON:
			first_person = not first_person


def mouseMotionListener(x, y):
	global camera_angle, mouse_x, mouse_y
	delta_x = x - mouse_x
	camera_angle = (camera_angle - delta_x * mouse_sensitivity + 360.0) % 360.0
	mouse_x = x; mouse_y = y


# --------------- Camera/loop/render ---------------
def setupCamera():
	global camera_angle
	glMatrixMode(GL_PROJECTION); glLoadIdentity()
	gluPerspective(fovY, 0.88, 0.1, 4000)
	glMatrixMode(GL_MODELVIEW); glLoadIdentity()

	if CHEAT_ON:
		maze_center_x = 0; maze_center_y = 0
		camera_x = maze_center_x; camera_y = maze_center_y; camera_z = 1500
		gluLookAt(camera_x, camera_y, camera_z, maze_center_x, maze_center_y, 0.0, 0, 1, 0)
		return

	if first_person:
		camera_angle = player_yaw
		angle_rad = math.radians(player_yaw)
		camera_x = player_x; camera_y = player_y; camera_z = eye_height + player_z
		target_x = camera_x + math.sin(angle_rad) * 100.0
		target_y = camera_y + math.cos(angle_rad) * 100.0
		target_z = camera_z
		gluLookAt(camera_x, camera_y, camera_z, target_x, target_y, target_z, 0, 0, 1)
	else:
		angle_rad = math.radians(camera_angle)
		camera_offset_x = camera_radius * math.sin(angle_rad)
		camera_offset_y = camera_radius * math.cos(angle_rad)
		camera_x = player_x + camera_offset_x
		camera_y = player_y + camera_offset_y
		camera_z = camera_height
		gluLookAt(camera_x, camera_y, camera_z, player_x, player_y, 50.0, 0, 0, 1)


def idle():
	global _prev_time_for_enemies
	now = time.perf_counter()
	if '_prev_time_for_enemies' not in globals() or _prev_time_for_enemies is None:
		_prev_time_for_enemies = now
	dt = max(0.0, now - _prev_time_for_enemies)
	_prev_time_for_enemies = now
	try:
		update_enemies(dt)
		update_bullets()
		update_stamina()
		update_jump()
	except Exception as _e:
		print('[UpdateError]', _e)
	glutPostRedisplay()


def showScreen():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glViewport(0, 0, 960, 1080)

	setupCamera()

	# Ground
	glBegin(GL_QUADS)
	glColor3f(0.8, 0.52, 0.25)
	glVertex3f(-1000, -1000, 0)
	glVertex3f(-1000, 1000, 0)
	glVertex3f(1000, 1000, 0)
	glVertex3f(1000, -1000, 0)
	glEnd()

	final_run()
	draw_walls()
	draw_crushing_walls()
	draw_traps()
	draw_enemies([
		ENEMY_SPAWNS[0], ENEMY_SPAWNS[1], ENEMY_SPAWNS[2],
		ENEMY_SPAWNS[3], ENEMY_SPAWNS[4], ENEMY_SPAWNS[5], ENEMY_SPAWNS[6]
	])
	draw_character((player_x, player_y, 0.0))
	draw_jump_direction_indicator()
	draw_bullets()
	draw_gun_overlay()

	# HUD
	draw_text(10, 770, f"Health = {player_hp}   Bullets = {ammo_remaining}", color=colors['GREEN'])
	draw_text(10, 740, f"Stamina: {player_stamina:.1f}/{max_stamina:.0f}")

	glutSwapBuffers()


def main():
	glutInit()
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize(960, 1080)
	glutInitWindowPosition(0, 0)
	glutCreateWindow(b"Maze Runner 3D - Merged")
	glEnable(GL_DEPTH_TEST)
	glutDisplayFunc(showScreen)
	glutKeyboardFunc(keyboardListener)
	glutSpecialFunc(specialKeyListener)
	glutMouseFunc(mouseListener)
	glutMotionFunc(mouseMotionListener)
	glutIdleFunc(idle)
	glutMainLoop()


if __name__ == "__main__":
	main()

