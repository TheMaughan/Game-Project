import arcade #py -m venv venv

# Size of tiles:
SPRITE_IMAGE_SIZE = 128

# Scale sprites
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_TILES = 0.5

# Scaled sprite size for tiles:
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles:
SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 36

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, hit_box_algorithm):

        super().__init__()
        self.has_lost: bool = False

        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = SPRITE_SCALING_PLAYER

        # Track our state
        #self.jumping: bool = False
        #self.climbing: bool = False
        #self.is_on_ladder: bool = False
        #self.ladder_list = ladder_list

        main_path = f"images/mario/mario"

        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png",
                                                            hit_box_algorithm=hit_box_algorithm)
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")

        self.walk_textures = []
        for i in range(3):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)
        
        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        #Hit box value:
        #self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        #self.points = [[-16, -40], [16, -40], [16, 28], [-16, 28]]
        #self.set_hit_box(self.texture.hit_box_points)
        self.hit_box = self.texture.hit_box_points

        #distance traveled since changed texture
        self.x_odometer = 0
        self.y_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        # Jumping animation
        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return
        
        # Idle animation
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

    def update(self):
        """ Move the view """

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        #This will need to change, based off of a set map size.
        elif self.right > SCREEN_WIDTH*5 - 160:
            self.right = SCREEN_WIDTH*5 - 160

        if self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1