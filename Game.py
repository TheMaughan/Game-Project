"""
Platformer Game
"""
from typing import Optional
import arcade
from pyglet.libs.win32.constants import OUT_CHARACTER_PRECIS
from Player_Obj import Player

SCREEN_TITLE = "PyMunk Platformer"

# How big are our image tiles?
SPRITE_IMAGE_SIZE = 128

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_TILES = 0.5

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles
SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# --- Physics forces. Higher number, faster accelerating.

# Gravity
GRAVITY = 1500

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1800

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 64
PLAYER_START_Y = 225


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.jump_needs_reset: bool = False

        # Made in the Tiled Mapmaker:
        self.wall_list: Optional[arcade.SpriteList] = None
        self.coin_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None
        self.foreground_list: Optional[arcade.SpriteList] = None
        self.background_list: Optional[arcade.SpriteList] = None
        self.dont_touch_list: Optional[arcade.SpriteList] = None

        self.item_list: Optional[arcade.SpriteList] = None

        # The Player's avatar:
        self.player_list: Optional[arcade.SpriteList] = None
        #self.player = None
        self.player: Optional[Player] = None
        
        #The world Physics:
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]

        # Used to keep track of our scrolling:
        self.view_bottom = 0
        self.view_left = 0

        # Player Prograssion:
        self.score = 0

        # Map Stuff:
        self.end_of_map = 0
        self.level = 1

        # Load sounds:
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/gameover1.wav")
        
    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """
        
        # Used to keep track of our scrolling:
        self.view_bottom = 0
        self.view_left = 0

        # Player Prograssion:
        self.score = 0        

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        
        #self.foreground_list = arcade.SpriteList()
        #self.background_list = arcade.SpriteList()
        #self.wall_list = arcade.SpriteList()
        #self.coin_list = arcade.SpriteList()
        #self.item_list = arcade.SpriteList()
        #self.ladder_list = arcade.SpriteList()

        #self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, GRAVITY)

        #---------------------------- Map Code ----------------------------#
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer containing moving platforms:
        moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        # --- Load File --- #
        # Name of map file to load
        map_name = f"level_{level}.tmx"
        #map_name = f"test_map_7.tmx"
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        

        #- Read the Map:
        self.end_of_map = my_map.map_size.width * SPRITE_IMAGE_SIZE

        # Moving Sprite
        self.moving_sprites_list = arcade.tilemap.process_layer(my_map,
                                                                'Moving Platforms',
                                                                SPRITE_SCALING_TILES)

        # -- Map Layers -- #

        # Platforms & Boundry objects (player cannot move through)
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      platforms_layer_name,
                                                      SPRITE_SCALING_TILES,
                                                      hit_box_algorithm="Detailed")
        # -- Moving Platforms -- #
        # Moving Sprite
        self.moving_sprites_list = arcade.tilemap.process_layer(my_map,
                                                                moving_platforms_layer_name,
                                                                SPRITE_SCALING_TILES,
                                                                hit_box_algorithm="Detailed")
        #for sprite in self.moving_sprites_list:
            #self.wall_list.append(sprite)
                                                      
        # Background Layers:
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            SPRITE_SCALING_TILES)
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                        'Ladders',
                                                        SPRITE_SCALING_TILES,
                                                        use_spatial_hash=True,
                                                        hit_box_algorithm="Detailed")

        # Foreground Layer:
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            SPRITE_SCALING_TILES)
        
        self.item_list = arcade.tilemap.process_layer(my_map, 'Dynamic Items',
                                                     SPRITE_SCALING_TILES,
                                                     hit_box_algorithm="Detailed")

        # -- Map Coins -- #
        # Name of the layer that has items for pick-up
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name,
                                                      SPRITE_SCALING_TILES,
                                                      hit_box_algorithm="Detailed")

        # Insta-death Layer Name (lava, fall off map, spikes, etc.):
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            SPRITE_SCALING_TILES,
                                                            hit_box_algorithm="Detailed")
        # --- Other Map Details -- #
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        # ^^^^^^^^^^^^^^^^^^^ End of Map Code ^^^^^^^^^^^^^^^^^^^ #

        # ------ Player Setup ------ #
        # Create player sprite
        self.player = Player(self.ladder_list, hit_box_algorithm="Detailed")
        #P_sprite = "./images/mario/mario"
        #self.player = arcade.Sprite(f"{P_sprite}_idle.png", CHARACTER_SCALING)
         # Set player location
        grid_x = 1
        grid_y = 1
        self.player.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player)

        # --------- Physics Engine & Logic --------- #
        damping = DEFAULT_DAMPING

        gravity = (0, -GRAVITY)
        # Create the physics engine
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)
        # Add the player.
        # For the player, we set the damping to a lower value, which increases
        # the damping rate. This prevents the character from traveling too far
        # after the player lets off the movement keys.
        # Setting the moment to PymunkPhysicsEngine.MOMENT_INF prevents it from
        # rotating.
        # Friction normally goes between 0 (no friction) and 1.0 (high friction)
        # Friction is between two objects in contact. It is important to remember
        # in top-down games that friction moving along the 'floor' is controlled
        # by damping.
        self.physics_engine.add_sprite(self.player,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

        # Create the walls.
        # By setting the body type to PymunkPhysicsEngine.STATIC the walls can't
        # move.
        # Movable objects that respond to forces are PymunkPhysicsEngine.DYNAMIC
        # PymunkPhysicsEngine.KINEMATIC objects will move, but are assumed to be
        # repositioned by code and don't respond to physics forces.
        # Dynamic is default.
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        # Create the items
        self.physics_engine.add_sprite_list(self.item_list,
                                            friction=DYNAMIC_ITEM_FRICTION,
                                            collision_type="item")

        # Add kinematic sprites
        self.physics_engine.add_sprite_list(self.moving_sprites_list,
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)
    

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        #Player Jumping trigger
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
            if self.physics_engine.is_on_ground(self.player):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player, impulse)
                arcade.play_sound(self.jump_sound)

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True


        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        #self.process_keychange()
    
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        #self.process_keychange()
    
    def on_update(self, delta_time):
        """ Movement and game logic """
        
        # -------------------- Manage Player Movement -------------------- #
        is_on_ground = self.physics_engine.is_on_ground(self.player)
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
            if is_on_ground:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player, 0)
        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player, 1.0)
        """
        elif self.up_pressed and not self.down_pressed:
            # Create a force to the right. Apply it.
            if self.player.is_on_ladder:
                force = (0, PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)
        elif self.down_pressed and not self.up_pressed:
            # Create a force to the right. Apply it.
            if self.player.is_on_ladder:
                force = (0, -PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)
        """
        

        # Move items in the physics engine
        self.physics_engine.step()

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ End of player movement ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ #
        #self.physics_engine.update()

        self.player_list.update_animation()

        #update map animations:
        self.coin_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)
        self.foreground_list.update_animation(delta_time)

        # ----- Moving Platform Logic ----- #
        #update moving platforms:
        self.wall_list.update()
        # See if the moving wall hit a boundary and needs to reverse direction.
       # For each moving sprite, see if we've reached a boundary and need to
        # reverse course.
        for moving_sprite in self.moving_sprites_list:
            if moving_sprite.boundary_right and \
                    moving_sprite.change_x > 0 and \
                    moving_sprite.right > moving_sprite.boundary_right:
                moving_sprite.change_x *= -1
            elif moving_sprite.boundary_left and \
                    moving_sprite.change_x < 0 and \
                    moving_sprite.left > moving_sprite.boundary_left:
                moving_sprite.change_x *= -1
            if moving_sprite.boundary_top and \
                    moving_sprite.change_y > 0 and \
                    moving_sprite.top > moving_sprite.boundary_top:
                moving_sprite.change_y *= -1
            elif moving_sprite.boundary_bottom and \
                    moving_sprite.change_y < 0 and \
                    moving_sprite.bottom < moving_sprite.boundary_bottom:
                moving_sprite.change_y *= -1

        
        # ----- Coin Logic: ----- #
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)

        for coin in coin_hit_list: #- Remove a coin, add a point, make a sound:

            #- Different coin objects have different values
            #- Set the coin object values in the map editor
            if 'Points' not in coin.properties:
                print("Warning, collected a coin without a Points property.")
            else:
                points = int(coin.properties['Points'])
                self.score += points
            
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            #self.score += 1
        
        # ------> Player Death Event <------ #
        changed_viewport = False # - Setting the View to the Game, for now...
        # - Did the Player Die?
        if (self.player.center_y < -100) or (arcade.check_for_collision_with_list(self.player,
                                                                                self.dont_touch_list)): #- Restart Position:
            self.physics_engine.player
            #self.setup(self.level) # Restart Game at new Level
            # Reset View
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)
        

        # ------> Player Win Event <------ #
        if self.player.center_x >= self.end_of_map:
            self.level += 1 # Advance a level
            self.setup(self.level) # Restart Game at new Level
            # Reset the Viewport
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
        





        # -------------------- Manage Scrolling -------------------- #

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ End of Scrolling logic ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ #
       
    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        # Code to draw the screen goes here

        # - Map Objects (IMPORTANT! The Order Objects are
        #       drawn matter, Objects drawn first will appear behind other objects!):
        self.background_list.draw()
        self.dont_touch_list.draw()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.moving_sprites_list.draw()
        self.coin_list.draw()
        self.item_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.WHITE, 18)

def main():
    """ Main method """
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()
