import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
### the above packages are for plotting only
### they are never used in computation
import numpy as np

### assume segment must have 2 different vertices
### assume obstacle and robot must have at least 3 different vertices
### assume obstacle and robot cannot be self-intersecting, and can only be concave or convex

def load_objects(object_path):
    '''
    function to load a list of obstacles and the robot
    '''
    obstacles = []
    obstacle = []
    with open(object_path) as f:
        numObstacles = int(f.readline())
        coordinates = int(f.readline())
        for i in range(coordinates):
            line = f.readline()
            obstacle.append(tuple(map(int, line.strip().split(' '))))
        for line in f:
            coordinates = tuple(map(int, line.strip().split(' ')))
            if len(coordinates) == 1:
                obstacles.append(obstacle)
                obstacle = []
            else:
                obstacle.append(coordinates)
    robot = obstacle
    return obstacles, robot

def plot_verification(obstacles, robot):
    '''
    plot the positions of robot and obstacles on axes to visualize the correctness of our program
    '''
    fig, ax = plt.subplots(figsize=(12, 8))
    vertices = []
    codes = []
    for i, obstacle in enumerate(obstacles):
        centroid = np.mean(np.array(obstacle, float), axis=0)
        plt.text(centroid[0], centroid[1], str(i), size=10, ha="center", va="center", bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8),))
        for i, vertex in enumerate(obstacle):
            vertices.append(vertex)
            if i == 0:
                codes.append(Path.MOVETO)
            else:
                codes.append(Path.LINETO)  
        vertices.append((0, 0))
        codes.append(Path.CLOSEPOLY)
    path = Path(vertices, codes)
    pathpatch = patches.PathPatch(path, facecolor='None', edgecolor='xkcd:violet')
    ax.add_patch(pathpatch)
    # now, plot the robot
    robot_code = []
    for i, vertex in enumerate(robot):
        if i == 0:
            robot_code.append(Path.MOVETO)
        else:
            robot_code.append(Path.LINETO)
    robot.append((0, 0))
    robot_code.append(path.CLOSEPOLY)
    robot_path = Path(robot, robot_code)
    robot_patch = patches.PathPatch(robot_path, facecolor='None', edgecolor='orange')
    ax.add_patch(robot_patch)
    
    ax.set_title('Collision Checker')
    ax.dataLim.update_from_data_xy(vertices+robot)
    ax.autoscale_view()
    ax.invert_yaxis()
    plt.show()

def get_segments(obstacle):
    '''
    return a list of all segments in that obstacle
    '''
    segs = []
    for i in range(len(obstacle)-1):
        segs.append([obstacle[i], obstacle[i+1]])
    segs.append([obstacle[-1], obstacle[0]])
    return segs


def seg_seg_intersection(seg1, seg2):
    '''
    A segment is part of a line, which is bounded by two end points
    seg1: a list of tuples [(x1, y1), (x2, y2)]
    seg2: a list of tuples [(x1, y1), (x2, y2)]
    return whether two segments intersect or not (False if not intersecting)
    '''

    # the interval of x value where the intersection must lie in
    I_x = [max(min(seg1[0][0], seg1[1][0]), min(seg2[0][0], seg2[1][0])), 
            min(max(seg1[0][0], seg1[1][0]), max(seg2[0][0],seg2[1][0]))]
    # print(I_x)
    if I_x[0] > I_x[1]:
        return False
    # the interval of y value where the intersection must lie in
    I_y = [max(min(seg1[0][1], seg1[1][1]), min(seg2[0][1], seg2[1][1])), 
            min(max(seg1[0][1], seg1[1][1]), max(seg2[0][1],seg2[1][1]))]
    # print(I_y)
    if I_y[0] > I_y[1]:
        return False

    # none of the two segments are vertical to x-axis
    if seg1[0][0] != seg1[1][0] and seg2[0][0] != seg2[1][0]:
        k1 = (seg1[0][1]-seg1[1][1]) / (seg1[0][0]-seg1[1][0])
        k2 = (seg2[0][1]-seg2[1][1]) / (seg2[0][0]-seg2[1][0])
        b1 = seg1[0][1]-k1*seg1[0][0]
        b2 = seg2[0][1]-k2*seg2[0][0]

        if k1 == k2:
            if b1 == b2:
                return True
            else:
                return False
        # not sure why x_intersection is rounded here
        x_intersection = (b2 - b1) / (k1 - k2)
        if x_intersection < I_x[0] or x_intersection > I_x[1]:
            return False
        y_intersection = k1 * x_intersection + b1
        return (x_intersection, y_intersection)

    # seg1 is vertical
    if seg1[0][0] == seg1[1][0] and seg2[0][0] != seg2[1][0]:
        k2 = (seg2[0][1]-seg2[1][1]) / (seg2[0][0]-seg2[1][0])
        b2 = seg2[0][1]-k2*seg2[0][0]
        x_intersection = float(seg1[0][0])
        if x_intersection < I_x[0] or x_intersection > I_x[1]:
            return False
        y_intersection = k2 * x_intersection + b2
        if y_intersection < I_y[0] or y_intersection > I_y[1]:
            return False
        return (x_intersection, y_intersection)

    # seg2 is vertical
    if seg2[0][0] == seg2[1][0] and seg1[0][0] != seg1[1][0]:
        k1 = (seg1[0][1]-seg1[1][1]) / (seg1[0][0]-seg1[1][0])
        b1 = seg1[0][1]-k1*seg1[0][0]
        x_intersection = float(seg2[0][0])
        if x_intersection < I_x[0] or x_intersection > I_x[1]:
            return False
        y_intersection = k1 * x_intersection + b1
        if y_intersection < I_y[0] or y_intersection > I_y[1]:
            return False
        return (x_intersection, y_intersection)

    # both segments are vertical to the x-axis
    if seg1[0][0] == seg1[1][0] and seg2[0][0] == seg2[1][0]:
        if I_x[0] == I_x[1] and I_y[0] <= I_y[1]:
            return True
        return False

def seg_obstacle_intersection(seg, obstacle):
    '''
    seg: a list of 2 vertices, e.g. [(x1, y1), (x2, y2)]
    obstacle: a list of vertices (number of vertices > 2), e.g. [(x1, y1), (x2, y2), (x3, y3)]
    return False if not intersecting, True if intersecting
    '''
    obstacle_segs = get_segments(obstacle) 
    for obstacle_seg in obstacle_segs:
        # robot segment intersect with obstacle segments
        if seg_seg_intersection(obstacle_seg, seg)!=False:
            return True
    return False

def line_seg_intersection(point, seg):
    '''
    point: (x, y)
    seg: a list of 2 vertices, e.g. [(x1, y1), (x2, y2)]
    Given a point, draw a line through that point which is parallel to x-axis,
    return the positions of intersections between the line and the segment, return False if there is no intersection
    '''
    y = float(point[1])
    if max(seg[0][1], seg[1][1]) < y or min(seg[0][1], seg[1][1]) > y:
        return False
    # segment parallel to x-axis, this can even be true if the point is inside the obstacle. think about a concave polygon
    if seg[0][1] == seg[1][1]:
        x = float(seg[0][0])
        return (x, y)
    # segment vertical to x-axis
    if seg[0][0] == seg[1][0]:
        return ((seg[0][0], y))
    # segment not parallel nor vertical to x-axis
    k = (seg[0][1]-seg[1][1]) / (seg[0][0]-seg[1][0])
    b = seg[0][1]-k*seg[0][0]
    x = (y-b)/k #k!=0
    return (x, y)

def is_point_in_obstacle(point, obstacle):
    temp = []
    for seg in get_segments(obstacle):
        temp.append(line_seg_intersection(point, seg))
    ### if there are some intersections, check how many of them are on the right side and how many on the left side
    left = 0
    right = 0
    for intersection in temp:
        if intersection != False:
            # they can never be equal
            if point[0] < intersection[0]:
                right+=1
            else:
                left+=1
    ### if the point is in the polygon (no matter convex or concave)
    if left%2 == 1 or right%2 == 1:
        return True
    return False

def robot_obstacle_intersection(robot, obstacle):
    '''
    robot: a list of vertices (number of vertices > 2), e.g. [(x1, y1), (x2, y2), (x3, y3)]
    obstacle: a list of vertices (number of vertices > 2), e.g. [(x1, y1), (x2, y2), (x3, y3)]

    '''
    robot_segs = get_segments(robot)
    for robot_seg in robot_segs:
        # robot segment intersect with obstacle
        if seg_obstacle_intersection(robot_seg, obstacle)!=False:
            return True
    # IMPORTANT: now, check if the robot covered in the obstacle
    # randomly pick a point on the robot and see if it is in the obstacle
    robot_point = robot[0]
    if is_point_in_obstacle(robot_point, obstacle) == True:
        return True
    # also check if the obstacle is covered in the robot
    obstacle_point = obstacle[0]
    if is_point_in_obstacle(obstacle_point, robot) == True:
        return True
    return False

def collision_checker(obstacles, robot):
    '''
    obstacles: a list of lists of vertices of obstacles, e.g. [[(0,0), (0,1), (1,1)]] means there is one (triangle) obstacle whose vertices are (0,0), (0,1), (1,1).
    object: a list of vertices of an object, e.g. [(0,0), (0,1), (1,1)] means the object is triangle and its vertices are (0,0), (0,1), (1,1).
    '''
    results = []
    for obstacle in obstacles:
        if robot_obstacle_intersection(robot, obstacle)!=False:
            results.append(obstacles.index(obstacle))
    return results


def main():
    # load obstacles and robot
    obstacles, robot = load_objects('world_objects.txt')
    # run our collision checker to see which obstacles collide with the robot
    results = collision_checker(obstacles, robot)
    print(results)
    # plot obastacles and robot to validate our results
    plot_verification(obstacles, robot)


if __name__ == "__main__":
    # point = (6, 1)
    # obstacle = [(0, 0), (5, 0), (5, 5), (2, 5)]
    # print(is_point_in_obstacle(point, obstacle))
    main()