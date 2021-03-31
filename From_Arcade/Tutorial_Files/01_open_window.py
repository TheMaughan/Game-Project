"""
Platformer Game
"""
from typing import Optional
import arcade
from pyglet.libs.win32.constants import OUT_CHARACTER_PRECIS

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

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

        # Made in the Tiled Mapmaker:
        self.wall_list = None
        self.coin_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None

        # The Player's avatar:
        self.player_list = None
        self.player = None
        
        #The world Physics:
        self.physics_engine = None

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
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        # ------ Player Setup ------ #
        P_sprite = "./images/mario/mario"
        self.player = arcade.Sprite(f"{P_sprite}_idle.png", CHARACTER_SCALING)
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player_list.append(self.player)


        #self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, GRAVITY)

        #---------------------------- Map Code ----------------------------#
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
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
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        

        #- Read the Map:
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # -- Map Layers -- #
                                                      
        # Background Layer:
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)

        # Foreground Layer:
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)
        # Platforms & Boundry objects (player cannot move through)
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        
        # -- Map Coins -- #
        # Name of the layer that has items for pick-up
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # Insta-death Layer Name (lava, fall off map, spikes, etc.):
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)
        # --- Other Map Details -- #
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        # ^^^^^^^^^^^^^^^^^^^ End of Map Code ^^^^^^^^^^^^^^^^^^^ #

        # --------- Physics Engine & Logic --------- #
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        # Code to draw the screen goes here

        # - Map Objects (IMPORTANT! The Order Objects are
        #       drawn matter, Objects drawn first will appear behind other objects!):
        self.background_list.draw()
        self.dont_touch_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.WHITE, 18)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

        # ----- Coin Logic: ----- #
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)

        for coin in coin_hit_list: #- Remove a coin, add a point, make a sound:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # ------> Player Death Event <------ #
        changed_viewport = False # - Setting the View to the Game, for now...
        # - Did the Player Die?
        if (self.player.center_y < -100) or (arcade.check_for_collision_with_list(self.player,
                                                                                self.dont_touch_list)): #- Restart Position:
            # Reset Player
            self.player.center_x = 0
            self.player.center_y = 0
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y

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



    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = 0

def main():
    """ Main method """
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()
