# Fire effect constants
NUM_PARTICLES = 200
FIRE_MAX_HEIGHT = 80.0  # Controls how high sparks go
FIRE_SPEED = 0.8        # Controls how fast sparks rise
# particle data
fire_particles = []      


WAVE_SUBDIV = 20      # Grid resolution for the water surface
WAVE_AMPLITUDE = 3.0  # How high the waves are

#Traps n all

def water_patch(x1, y1, x2, y2):
    # Animate using a continuous time value.
    t = time.perf_counter()
    # Set water level above the ground.
    base_height = 5.0
    # Calculate size of each quad in the water grid.
    step_x = (x2 - x1) / float(WAVE_SUBDIV)
    step_y = (y2 - y1) / float(WAVE_SUBDIV)
    # Draw the boundary of the water patch.
    cuboids((x1, y1), (x1, y2), (x2, y2), (x2, y1), 2, (0.27, 0.51, 0.71))

    glBegin(GL_QUADS)
    # Loop through the grid to create the water mesh.
    for i in range(WAVE_SUBDIV):
        for j in range(WAVE_SUBDIV):
            # Get the four (x, y) corners of the current quad.
            vx0 = x1 + i * step_x
            vy0 = y1 + j * step_y
            vx1 = vx0 + step_x
            vy1 = vy0 + step_y

            # Calculate vertex Z-height using sine waves for a ripple effect.
            z00 = base_height + math.sin((vx0 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy0 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
            z01 = base_height + math.sin((vx0 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy1 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
            z10 = base_height + math.sin((vx1 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy0 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE
            z11 = base_height + math.sin((vx1 * 0.02 + t * 2.0)) * WAVE_AMPLITUDE * 2 + math.cos((vy1 * 0.015 - t * 1.5)) * WAVE_AMPLITUDE

            # Set color and draw the quad.
            glColor3f(0.4, 0.7, 0.9)
            glVertex3f(vx0, vy0, z00)
            glVertex3f(vx1, vy0, z10)
            glVertex3f(vx1, vy1, z11)
            glVertex3f(vx0, vy1, z01)
    glEnd()

def fire_patch(x1, y1, x2, y2):
    # Draw the boundary of the fire patch.
    cuboids((x1, y1), (x1, y2), (x2, y2), (x2, y1), 2, (1.0, 0.4, 0.0))
    global fire_particles
    base_height = 5.0

    # Initialize particles on the first run.
    if not fire_particles:
        for _ in range(NUM_PARTICLES):
            # Create each particle with a random position and starting life.
            ix = random.uniform(x1, x2)
            iy = random.uniform(y1, y2)
            life = random.uniform(0.0, FIRE_MAX_HEIGHT)
            fire_particles.append([ix, iy, 0.0, life])

    glPointSize(3)
    glBegin(GL_POINTS)

    for p in fire_particles:
        # Move spark up by increasing its 'life'.
        p[3] += FIRE_SPEED

        # If spark is too high, reset it at the bottom.
        if p[3] > FIRE_MAX_HEIGHT:
            p[0] = random.uniform(x1, x2)
            p[1] = random.uniform(y1, y2)
            p[3] = 0.0
            continue

        # Z position is based on life.
        p[2] = base_height + p[3]
        # Ratio from 1.0 (bottom) to 0.0 (top) for color fade.
        life_ratio = 1.0 - (p[3] / FIRE_MAX_HEIGHT)
        # Fade color from yellow to red.
        glColor3f(1.0, life_ratio * 0.5, 0.0)
        glVertex3f(p[0], p[1], p[2])
    glEnd()

def spikes_patch(p1, p2):
    global spike_quadric

    # Spike properties.
    SPIKE_HEIGHT = 100.0
    SPIKE_RADIUS = 15.0
    NUM_SPIKES = 6
    
    # Define animation phase durations.
    PAUSE_DURATION = 0.5
    MOVE_DURATION = 0.2
    CYCLE_DURATION = 2 * PAUSE_DURATION + 2 * MOVE_DURATION

    # Get current position in the animation cycle.
    time_in_cycle = time.time() % CYCLE_DURATION
    
    # Define when each phase ends.
    phase1_end = PAUSE_DURATION
    phase2_end = phase1_end + MOVE_DURATION
    phase3_end = phase2_end + PAUSE_DURATION

    # Determine animation progress (0.0=down, 1.0=up) based on the current phase.
    if time_in_cycle < phase1_end:
        # Phase 1: Paused down.
        animation_progress = 0.0
    elif time_in_cycle < phase2_end:
        # Phase 2: Moving up, smoothed with a sine curve.
        progress = (time_in_cycle - phase1_end) / MOVE_DURATION
        animation_progress = (math.sin(progress * math.pi - math.pi / 2) + 1) / 2
    elif time_in_cycle < phase3_end:
        # Phase 3: Paused up.
        animation_progress = 1.0
    else:
        # Phase 4: Moving down.
        progress = (time_in_cycle - phase3_end) / MOVE_DURATION
        animation_progress = 1.0 - ((math.sin(progress * math.pi - math.pi / 2) + 1) / 2)

    # Convert progress to a Z-offset for translation.
    z_offset = -SPIKE_HEIGHT + animation_progress * SPIKE_HEIGHT

    # Initialize the cylinder object once.
    if spike_quadric is None:
        spike_quadric = gluNewQuadric()

    glColor3f(0.75, 0.75, 0.75)

    # Calculate spike positions.
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0: return

    # Get a normalized direction vector.
    norm_dx, norm_dy = dx / distance, dy / distance
    # Offset start/end points by radius so spikes fit perfectly.
    start_center_x = x1 + norm_dx * SPIKE_RADIUS
    start_center_y = y1 + norm_dy * SPIKE_RADIUS
    end_center_x = x2 - norm_dx * SPIKE_RADIUS
    end_center_y = y2 - norm_dy * SPIKE_RADIUS
    center_dx = end_center_x - start_center_x
    center_dy = end_center_y - start_center_y

    for i in range(NUM_SPIKES):
        # Position spike along the line.
        fraction = i / (NUM_SPIKES - 1) if NUM_SPIKES > 1 else 0.5
        spike_x = start_center_x + center_dx * fraction
        spike_y = start_center_y + center_dy * fraction

        glPushMatrix()
        # Move to spike's base position.
        glTranslatef(spike_x, spike_y, 0)
        # Apply vertical animation.
        glTranslatef(0, 0, z_offset)
        # Draw spike as a cone.
        gluCylinder(spike_quadric, SPIKE_RADIUS, 0.0, SPIKE_HEIGHT, 16, 1)
        glPopMatrix()

def draw_traps():

    water_patch(co[10],co[1],co[12],co[2])
    fire_patch(co[3],co[5],co[4],co[8])
    spikes_patch((co[13],co[10]), (co[14],co[10]))
    spikes_patch((co[12],co[16]), (co[12],co[15]))
