# collision_checker
A simple checker of polygon collisions, with plotting visualization.

## Examples
Orange polygon represents the robot, violet polygons represent obstacles

Senario 1: Robot collides with obstacles by intersecting edges
- **output**: ```[4, 8, 9]```
![](https://github.com/JingxiXu/collision_checker/blob/master/images/edges.png)

Senario 2: Robot collides with obstacles by containing obstacles
- **output**: ```[8, 9]```
![](https://github.com/JingxiXu/collision_checker/blob/master/images/outside.png)

Senario 3: Robot collides with obstacles by being contained in an obstacle
- **output**: ```[3]```
![](https://github.com/JingxiXu/collision_checker/blob/master/images/inside.png)

Senario 4: Robot free (no collision)
- **output**: ```None```
![](https://github.com/JingxiXu/collision_checker/blob/master/images/no_collision.png)

## Usage:
```cd``` inside this folder and run ```python collision_checker.py```. It outputs a list of obstacle indices in command line and then plot the positions of the robot and obstacles to visualize the collision. ```None``` is returned if no collision occurs.

```world_objects.txt``` is a text file holding information about the positions of all obstacles and the robot. This file will be loaded by ```collision_checker.py```. 

The first line of it indicates the total number of objects (obstacles + robot), followed by information about each object. The first line of each object is the number of its edges, followed by positions of each vertices. Whether these vertices show up in a clock-wise or counter clock-wise manner does not make a difference here as long as they are recorded in order. 

The last object is interpretted by the program as robot.
