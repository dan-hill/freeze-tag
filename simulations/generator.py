import numpy as np
import time
import yaml
import logging
import os
class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Robot:
    def __init__(self, id, location, speed, release):
        self.release = release
        self.location = location
        self.id = id
        self.speed = speed
        self.claimed = False
        self.target = None
        self.status = "off"

class FreezeTagProblem:
    def __init__(self, robots):
        self.robots = robots
        self.size = len(robots)

    def save(self, file):

        robots = dict()
        for robot in self.robots:
            robots[robot.id] = {
                "location": {"x": robot.location.x, "y": robot.location.y},
                "speed": robot.speed,
                "status": robot.status,
                "release": robot.release
            }

        obj = {
            "size": self.size,
            "robots": robots
        }
        with open(file, 'w') as yaml_file:
            yaml_file.write( yaml.dump(obj, default_flow_style=False))

x = 50
while x < 1001:
    for j in range(0, 10):
        robots = list()
        random_location = Location(np.random.randint(0, 10000), np.random.randint(0, 10000))
        robots.append(Robot(str(0), random_location, 1, np.random.randint(0, 10000)))
        robots[0].status = "on"

        for i in range(1, x):
            random_location = Location(np.random.randint(0, 10000), np.random.randint(0, 10000))
            robots.append(Robot(str(i), random_location, 1, np.random.randint(0, 5000)))

        ftp = FreezeTagProblem(robots)

        directory = "data-sets/" + str(x) + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        ftp.save(directory + str(j) + ".yaml")

    x = x + 50