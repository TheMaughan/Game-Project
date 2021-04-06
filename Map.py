import arcade
from typing import Optional
from pyglet.libs.win32.constants import OUT_CHARACTER_PRECIS

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

class MapTiles(arcade.Window):
    def __init__(self):
        super().__init__()
        self.create()
        self.level = 1


    def setup(self, level):
        #---------------------------- Map Code ----------------------------#
        # Name of the layer in the file that has our platforms/walls
        #platforms_layer_name = 'Platforms'
        # Name of the layer containing moving platforms:
        #moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer that has items for pick-up
        #coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        #foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        #background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        #dont_touch_layer_name = "Don't Touch"
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
                                                      'Platforms',
                                                      SPRITE_SCALING_TILES,
                                                      hit_box_algorithm="Detailed")
        # -- Moving Platforms -- #
        # Moving Sprite
        self.moving_sprites_list = arcade.tilemap.process_layer(my_map,
                                                                'Moving Platforms',
                                                                SPRITE_SCALING_TILES,
                                                                hit_box_algorithm="Detailed")
        for sprite in self.moving_sprites_list:
            self.wall_list.append(sprite) #- The wall object list also owns moving platforms
                                                      
        # Background Layers:
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            'Background',
                                                            SPRITE_SCALING_TILES)
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                        'Ladders',
                                                        SPRITE_SCALING_TILES,
                                                        use_spatial_hash=True,
                                                        hit_box_algorithm="Detailed")

        # Foreground Layer:
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            'Foreground',
                                                            SPRITE_SCALING_TILES)
        
        self.item_list = arcade.tilemap.process_layer(my_map, 'Dynamic Items',
                                                     SPRITE_SCALING_TILES,
                                                     hit_box_algorithm="Detailed")

        # -- Map Coins -- #
        # Name of the layer that has items for pick-up
        self.coin_list = arcade.tilemap.process_layer(my_map, 'Coins',
                                                      SPRITE_SCALING_TILES,
                                                      hit_box_algorithm="Detailed")

        # Insta-death Layer Name (lava, fall off map, spikes, etc.):
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            "Don't Touch",
                                                            SPRITE_SCALING_TILES,
                                                            hit_box_algorithm="Detailed")
        # --- Other Map Details -- #
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        # ^^^^^^^^^^^^^^^^^^^ End of Map Code ^^^^^^^^^^^^^^^^^^^ #

    def on_draw(self):
        # - Map Objects (IMPORTANT! The Order Objects are
        #       drawn matter, Objects drawn first will appear behind other objects!):
        self.background_list.draw()
        self.dont_touch_list.draw()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.moving_sprites_list.draw()
        self.coin_list.draw()
        self.item_list.draw()

    
        

        
    def create_map(self):
        # Made in the Tiled Mapmaker:
        # I don't know exactly what 'Optional' does, I assume that it helps with processing the game and
            # helps with writing less code.
        self.wall_list: Optional[arcade.SpriteList] = None
        self.coin_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None
        self.foreground_list: Optional[arcade.SpriteList] = None
        self.background_list: Optional[arcade.SpriteList] = None
        self.dont_touch_list: Optional[arcade.SpriteList] = None
        # Non-animated Objects that the physics engine controlls.
        self.item_list: Optional[arcade.SpriteList] = None

        # Map Stuff:
        self.end_of_map = 0
        self.level = 1