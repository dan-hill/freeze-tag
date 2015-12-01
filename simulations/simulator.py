import yaml
import numpy as np
import glob
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
from logging.config import fileConfig
import os
fileConfig('loggin-config.ini')
logger = logging.getLogger()


SLEEPING = np.array([])
OFF = np.array([])
ON = np.array([])


class Robot:
    def __init__(self):
        self.target = None
        self.location = np.array([0, 0])
        self.velocity = None
        self.speed = 0
        self.claimed = False
        self.id = None

    def get_nearest(self):
        closest = None
        for s in SLEEPING:
            if s.claimed is False and self.target is None:
                closest = s
            elif self.target is not None:
                if self.distance(self.target) > self.distance(s):
                    closest = s
        return closest

    def nearest_neighbor(self):
        if self.target is None:
            self.target = self.get_nearest()
            if self.target is not None and self.target.claimed is False:
                logger.debug('Robot %s targets %s', self.id, self.target.id)
                self.target.claimed = True
        elif self.target is not None:
            if np.array_equal(self.location, self.target.location):
                logger.debug('Robot %s wakes robot %s', self.id, self.target.id)
                self.target.status = 'on'
                self.target = None
            else:
                self.set_velocity()
                logger.debug('Robot %s moves from %s to %s toward robot %s at %s', self.id, self.location, np.rint(self.location + self.velocity), self.target.id, self.target.location)
                self.location = np.rint(self.location + self.velocity)

    def tick(self, alg):
        if alg == "nearest-neighbor":
            self.nearest_neighbor()

    def set_velocity(self):
        rad = self.get_angle_to_target()
        velocity = np.array([np.cos(rad), np.sin(rad)])
        velocity *= self.speed
        logger.debug('Setting robot %s velocity to %s', self.id, self.velocity)

        self.velocity = velocity

    def get_angle_to_target(self):
        xdiff = self.target.location[0] - self.location[0]
        ydiff = self.target.location[1] - self.location[1]
        return np.arctan2(ydiff, xdiff)

    def distance(self, r):
        return np.linalg.norm(self.location - r.location)




x = 50
while x < 1001:

    results = {}
    files = glob.glob("data-sets/"+ str(x) + "/*.yaml")
    for file in files:
        SLEEPING = np.array([])
        OFF = np.array([])
        ON = np.array([])
        with open(file, 'r') as f:
            yaml_obj = yaml.load(f)

            for robot in yaml_obj["robots"]:
                r = Robot()
                r.id = robot
                r.release = yaml_obj["robots"][robot]["release"]
                r.status = yaml_obj["robots"][robot]["status"]
                r.speed = yaml_obj["robots"][robot]["speed"]

                r.location = np.array([
                    float(yaml_obj["robots"][robot]["location"]["x"]),
                    float(yaml_obj["robots"][robot]["location"]["y"])])

                if r.status == "on":
                    ON = np.append(ON, [r])
                if r.status == "sleeping":
                    SLEEPING = np.append(SLEEPING, [r])
                if r.status == 'off':
                    OFF = np.append(OFF, [r])

        time = 0

        while SLEEPING.shape[0] > 0 or OFF.shape[0] > 0:
            SLEEPING = np.hstack((SLEEPING, np.array(filter(lambda x:x.release <= time, OFF))))
            OFF = np.array(filter(lambda x:x.release > time, OFF))

            for r in ON:
                r.tick( "nearest-neighbor")

            ON = np.append(ON, np.array(filter(lambda x:x.status == "on", SLEEPING)))

            SLEEPING = np.array(filter(lambda x:x.status != "on", SLEEPING))

            time += 1

        results[file] = time
        print file + " Done: " + str(time)



    directory = "data-sets/" + str(x) + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(str(x) + "-results.yaml", 'w') as yaml_file:
        yaml_file.write( yaml.dump(results, default_flow_style=False))

    x += 50