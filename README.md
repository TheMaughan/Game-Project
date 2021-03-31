# Overview

This is a game that I'm working on, right now there are 2 different versions of this game. One uses the Pymunk physics engine and one does not. I initially didn't realize that Pymunk would requre me to rewite some of my code to make the game work, this is why I've kept the non-physics version to reference off of.

There is 1 main issues with the non-physics game:

* The player sprite will get stuck on corners which produces infinate loops and breaking the game.

I tried to fix the above problem along while adding some extra fun features by using more in-depth physics... this broke the moving platforms, player respawn, and level progression. The pymunk API classes claimed ownership of my sprites, and I'm learning more about how Arcade and Pymunk work together so I can fix this issue.

The game levels, sprite, and tilesets are all placeholders right now. I'm only using them so I can learn more about Python Arcade, Tiled, Pymunk, and any other technology that I end up adding later.

# Development Environment

I am using the Tiled map editor for building all my levels/maps.

The game is all writen in the Python language.

Python Arcade is the main script I'm using for handling the game mechanics.

Pymunk is being used for the physics. Most Pymunk integration is currently a work-in-progress.

# Useful Websites

* [Python Arcade](https://arcade.academy/index.html)
  * [Platform Tutorial](https://arcade.academy/examples/platform_tutorial/index.html)
  * [Tiled Tutorial](https://arcade.academy/examples/platform_tutorial/step_08.html)
* [Tiled Main Site](https://www.mapeditor.org/)
* [Kenny](https://www.kenney.nl/)
  * Kenny is an amazing free resource made for anyone looking for quick game assets without risking viruses or paying money. Arcade uses Kenny's resources in the all its tutorials.
  * If you have downloaded the arcade package, you can find more Kenny assets following this path on your computer: (look mainly in the 'resources' folder, but 'examples' and 'experimental' are also worth a look)
    * C:\Python\Python39\Lib\site-packages\arcade

# Future Work

* Right now I'm working on fixing the game so it works with the Pymunk physics engine without problems.
* I'm planning on including a menu and UI interface including a 'save/load game' feature and some simple player customizations.
* I'm still looking for a focused theme with a simple story to give the project better direction.
