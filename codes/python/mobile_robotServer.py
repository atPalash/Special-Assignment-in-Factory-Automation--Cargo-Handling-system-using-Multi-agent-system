from BrickPi import *
from basicRobot_planner import PathPlanner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import urllib2
import json
from statistics import mode, StatisticsError

BrickPiSetup()  # setup the serial port for communication

# set motor PORT's
motor1 = PORT_A
motor2 = PORT_B
motor3 = PORT_C
BrickPi.MotorEnable[motor1] = 1  # Enable the Motor A
BrickPi.MotorEnable[motor2] = 1  # Enable the Motor B
BrickPi.MotorEnable[motor3] = 1  # Enable the Motor C

# set sensor PORT's
sensor1 = PORT_1
sensor2 = PORT_2
BrickPi.SensorType[sensor1] = TYPE_SENSOR_ULTRASONIC_CONT
BrickPi.SensorType[sensor2] = TYPE_SENSOR_ULTRASONIC_CONT

BrickPiSetupSensors()  # Send the properties of sensors to BrickPi

# reset the motor Encoder values
BrickPi.EncoderOffset[motor1] = BrickPi.Encoder[motor1]
BrickPi.EncoderOffset[motor2] = BrickPi.Encoder[motor2]
BrickPi.EncoderOffset[motor3] = BrickPi.Encoder[motor3]
BrickPiUpdateValues()

ini_coordinates = [0, 0]  # set initial coordinates to be set to user defined coordinates from java_reply.txt
start_coordinates = [0, 0]  # initialise start coordinates ie. 1st goal coordinates
end_coordinates = [0, 0]  # initialise end coordinates ie. 2nd goal coordinates
step = 0  # steps of execution
current_position = [0, 0]  # initialise current position coordinates to be updated during execution of program
grid_object = PathPlanner()  # define a grid object of PathPlanner class
count = 0  # count the execution number of while loop
obstruction_flag = False  # set on detection of obstruction or after completion of one step of movement
fs = os.sep  # operating system separator
prev_grid = [0, 0]  # initialise previous grid location
prev_movement = ''  # initialise previous movement of vehicle
gyration_angle = 0  # initialise vehicle orientation, U=0, L=-90, R=90, D=180
# movement_step = 700  # set steps for linear motion
rotation_step = 510  # set steps for rotational motion
observer_flag = True  # file system observer flag, detects change in file system


# update the grid-map with the new obstruction coordinate
def obstruction(obst_crd):
    BrickPiUpdateValues()
    grid_object.set_grid(obst_crd)
    print grid_object.optimum_policy()
    try:
        req = urllib2.Request("http://130.230.146.209:8000/path")
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(grid_object.get_grid()))
    except urllib2.URLError:
        print "path server not found"


# create an array of ten samples with the higher mounted "ultrasonic sensor(sensor1)" value and return the mode of
#  the samples
def coordinate_finder(ang):
    BrickPiUpdateValues()
    deg = [ang]
    port = [motor1]
    power = [100]
    if ang != 1:
        motorRotateDegree(power, deg, port, 0, 0)
    while True:
        coordinate_list = []
        for i in range(11):
            BrickPiUpdateValues()
            coordinate_list.append(int(BrickPi.Sensor[sensor1]))
        print coordinate_list
        try:
            crd = mode(coordinate_list)
            return crd
        except StatisticsError:
            time.sleep(.01)
            continue


# return a 2D-array with different combination of observations of X-Y values, as observed by higher mounted
# "ultrasonic sensor( sensor1). the sensor is rotated by a motor in steps of "90" to look at the four sides of the
# enclosure."
def coordinates(gyr):
    BrickPiUpdateValues()
    port = [motor1]
    power = [100]
    angle = [1, 90, 180, -90]
    x_pos = 0
    x_neg = 0
    y_pos = 0
    y_neg = 0

    if gyr == 0:
        for ang in angle:
            if ang == angle[0]:
                x_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[1]:
                y_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[2]:
                x_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[3]:
                y_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
        coordinates_array = [[x_pos, y_pos], [x_pos, y_neg], [x_neg, y_pos], [x_neg, y_neg]]
        deg = [angle[0]]
        motorRotateDegree(power, deg, port, 0, 0)
        stop()
        time.sleep(0.1)
        return coordinates_array
    elif gyr == -90:
        for ang in angle:
            if ang == angle[0]:
                y_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[1]:
                x_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[2]:
                y_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[3]:
                x_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
        coordinates_array = [[x_pos, y_pos], [x_pos, y_neg], [x_neg, y_pos], [x_neg, y_neg]]
        deg = [angle[0]]
        motorRotateDegree(power, deg, port, 0, 0)
        stop()
        time.sleep(0.1)
        return coordinates_array
    elif gyr == 90:
        for ang in angle:
            if ang == angle[0]:
                y_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[1]:
                x_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[2]:
                y_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[3]:
                x_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
        coordinates_array = [[x_pos, y_pos], [x_pos, y_neg], [x_neg, y_pos], [x_neg, y_neg]]
        deg = [angle[0]]
        motorRotateDegree(power, deg, port, 0, 0)
        stop()
        time.sleep(0.1)
        return coordinates_array
    elif gyr == 180:
        for ang in angle:
            if ang == angle[0]:
                x_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[1]:
                y_neg = 80 - coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[2]:
                x_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
            elif ang == angle[3]:
                y_pos = coordinate_finder(ang)
                stop()
                time.sleep(0.01)
        coordinates_array = [[x_pos, y_pos], [x_pos, y_neg], [x_neg, y_pos], [x_neg, y_neg]]
        deg = [angle[0]]
        motorRotateDegree(power, deg, port, 0, 0)
        stop()
        time.sleep(0.1)
        return coordinates_array


# localise the current position of the vehicle in the 4 X 4 matrix of size - 20 X 20
def localise_in_grid(coord):
    BrickPiUpdateValues()
    x = coord[0]
    y = coord[1]
    x_grid = x // 20
    y_grid = y // 20
    grid_crd = [x_grid, y_grid]
    print "--grid coord--", grid_crd
    return grid_crd


# keeps a record of the previous state (coordinates in the 4 X 4 matrix) and the previous movement of the vehicle
def set_previous_states(loc, mov):
    global prev_grid
    prev_grid = loc
    global prev_movement
    prev_movement = mov


# set the orientation of the vehicle
def set_gyro(angle):
    global gyration_angle
    gyration_angle = angle


# return the encoder values optimal for linear movement of the vehicle
def get_movement_step(obs):
    if obs > 20:
        movement_step = 700
        return movement_step
    else:
        movement_step = (700 / 20) * obs
        return movement_step


# move the vehicle according to the encoder values provided, this function enables the vehicle for both linear motion
#  and rotational motion. To check "slip" the vehicle is moved back by the same amount as the extra encoder values.
def move(enc1, enc2):
    print "-----------------------------------------------------"
    print((BrickPi.Encoder[motor2]) / 2, (BrickPi.Encoder[motor3]) / 2)
    BrickPi.EncoderOffset[motor2] = BrickPi.Encoder[motor2]
    BrickPi.EncoderOffset[motor3] = BrickPi.Encoder[motor3]
    BrickPiUpdateValues()
    print((BrickPi.Encoder[motor2]) / 2, enc1, (BrickPi.Encoder[motor3]) / 2, enc2)
    deg = [enc1, enc2]
    port = [motor2, motor3]
    power = [150, 150]
    motorRotateDegree(power, deg, port, 0, 0)
    enc1_rot = BrickPi.Encoder[motor2] / 2
    enc2_rot = BrickPi.Encoder[motor3] / 2
    print enc1_rot, enc2_rot
    diff_enc1 = abs(enc1) - abs(enc1_rot)
    diff_enc2 = abs(enc2) - abs(enc2_rot)
    print "diff_enc,", diff_enc1, diff_enc2
    if enc1 >= 0:
        enc1 = diff_enc1
    else:
        enc1 = -diff_enc1
    if enc2 >= 0:
        enc2 = diff_enc2
    else:
        enc2 = -diff_enc2
    BrickPi.EncoderOffset[motor2] = BrickPi.Encoder[motor2]
    BrickPi.EncoderOffset[motor3] = BrickPi.Encoder[motor3]
    BrickPiUpdateValues()
    deg = [enc1, enc2]
    port = [motor2, motor3]
    power = [150, 150]
    motorRotateDegree(power, deg, port, 0, 0)
    BrickPi.EncoderOffset[motor2] = BrickPi.Encoder[motor2]
    BrickPi.EncoderOffset[motor3] = BrickPi.Encoder[motor3]
    BrickPiUpdateValues()
    print((BrickPi.Encoder[motor2]) / 2, enc1, (BrickPi.Encoder[motor3]) / 2, enc2)
    print "------------------------------------------------------"


# this function takes a sample of 19 readings to calculate the mode of the readings. the mode is then checked whether
#  it is occuring for more than 50% of the samples. the obstruction distance is then taken as the true distance.
def get_obstruction_distance():
    BrickPiUpdateValues()
    need_mode = True
    while need_mode:
        BrickPiUpdateValues()
        readings = []
        for i in range(19):
            BrickPiUpdateValues()
            obs1 = BrickPi.Sensor[sensor2]
            readings.append(obs1)
            time.sleep(.01)
        print "obstruction readings", readings
        try:
            obs = mode(readings)
            print "obstruction mode", obs
            if readings.count(obs) >= 9:
                need_mode = False
                return obs
        except StatisticsError:
            time.sleep(0.01)


# initiate vehicle motion at the direction given, set grid if no obstruction is present, set obstruction flag in case
#  of obstruction, call move command with appropriate encoder values for achieving the desired motion of the vehicle.
#  the obstruction is detected by the lower "ultrasonic sensor(sensor2)". this sensor is fixed and the vehicle can
# observe obstruction in front of it. It is assumed that the obstruction is not high enough to come is sight of the
# higher ultrasonic sensor (sensor1)
def fwd(direction, c_pos, g_pos):
    curr_pos = c_pos
    grd_pos = g_pos
    if direction == 'U':
        set_gyro(0)
        init_obs = get_obstruction_distance()
        if (curr_pos[0] - 6) - init_obs <= 10:
            print "--this X-lane clear--EOF at", init_obs
            grid_object.reset_grid(grd_pos)
            grid_object.optimum_policy()
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
        else:
            print "obstruction detected at X, direction", init_obs, direction
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
    elif direction == 'D':
        if gyration_angle != 180:
            move(-2 * rotation_step, 2 * rotation_step)
            stop()
            set_gyro(180)
        init_obs = get_obstruction_distance()
        if (80 - (curr_pos[0] - 6)) - init_obs <= 10:
            print "--this X-lane is clear--EOF at", init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
        else:
            print 'obstruction detected at X', init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
    elif direction == 'L':
        if gyration_angle != -90:
            move(rotation_step, -rotation_step)
            stop()
            set_gyro(-90)
        init_obs = get_obstruction_distance()
        if curr_pos[1] - init_obs <= 10:
            print "--this Y-lane is clear--EOF at", init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
        else:
            print 'obstruction detected at Y', init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag

    elif direction == 'R':
        if gyration_angle != 90:
            move(-rotation_step, rotation_step)
            stop()
            set_gyro(90)
        init_obs = get_obstruction_distance()
        if (80 - curr_pos[1]) - init_obs <= 10:
            print "--this Y-lane is clear--EOF at", init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag
        else:
            print 'obstruction detected at Y', init_obs
            if init_obs >= 17:
                movement_step = get_movement_step(init_obs)
                move(movement_step, movement_step)
                obs_flag = True
                if movement_step > 200:
                    set_previous_states(grd_pos, direction)
                stop()
                return obs_flag
            else:
                obs_flag = True
                stop()
                return obs_flag


# Stop
def stop():
    BrickPi.MotorSpeed[motor1] = 0
    BrickPi.MotorSpeed[motor2] = 0
    BrickPi.MotorSpeed[motor3] = 0
    BrickPiUpdateValues()


# class for handling file read when a change in the file occurs. The class listens for files system change event.
# here the "java_reply.txt" is the file which initiates the process by providing the initial coordinates,
# 1st goal coordinates, 2nd goal coordinate
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('java_reply.txt'):
            path_javareply = os.path.join(
                fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17" + fs + "java_reply.txt")
            fo = open(path_javareply, "r+")
            msg = fo.read(20)
            print "Read String is : ", msg
            msg0 = msg.split(",")[0]
            msg_split = msg0.split(' ')
            first = msg_split[0].split('-')
            second = msg_split[1].split('-')
            if first[0] == 'start' and second[0] == 'end':
                global ini_coordinates
                ini_coordinates_x = int(msg.split(",")[1][0])
                ini_coordinates_y = int(msg.split(",")[1][1])
                ini_coordinates = [ini_coordinates_x, ini_coordinates_y]
                fo = open(path_javareply, "w")
                fo.write("route taken")
                fo.close()
                x = int(first[1][0])
                y = int(first[1][1])
                global start_coordinates
                start_coordinates = [x, y]
                x = int(second[1][0])
                y = int(second[1][1])
                global end_coordinates
                end_coordinates = [x, y]
                global observer_flag
                observer_flag = False


while True:
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17",
                      recursive=False)  # wait for file change and start the loop
    observer.start()
    while observer_flag:
        BrickPiUpdateValues()
        time.sleep(1)
    observer.stop()
    BrickPiUpdateValues()
    try:
        grid_array = json.loads(
            urllib2.urlopen(
                "http://130.230.146.209:8000/path").read())  # GET request to local PC to get the 4 X 4 matrix
        print "---grid_array--", grid_array
        grid_object.set_initial_grid(grid_array)  # initialise the grid object with the 4 X 4 matrix
    except urllib2.URLError:
        print "path server not found"
    BrickPiUpdateValues()
    while True:
        BrickPiUpdateValues()
        if step == 0:
            print "in step 0"
            goal = start_coordinates  # set goal to 1st START coordinate
            grid_object.set_goal(goal)
        elif step == 1:
            print "in step 1"
            goal = end_coordinates  # set goal to 2nd END coordinate
            grid_object.set_goal(goal)
        elif step == 2:
            print "in step 2-job complete"
            step = 0
            observer_flag = True
            break
        count += 1
        print "counter", count
        grid_path = grid_object.optimum_policy()  # get the updated 4 X 4 matrix with the  directions to reach goal
        print grid_path
        print "---gyration angle---", gyration_angle  # orientation of vehicle
        # receive the 2D array of X-Y coordinates for vehicle position
        current_position_array = coordinates(gyration_angle)
        i = 0
        for i in range(len(current_position_array)):  # go through the 2D array
            current_position = current_position_array[i]
            print 'current_position', current_position
            print 'previous movement, coord', prev_movement, prev_grid
            if current_position is None:  # None value of current is ignored and the loop is continues
                current_position = [-1, -1]
                print "skipping"
                continue
            else:
                # filtering of erroneous value of X-Y coordinates
                if 0 >= current_position[0] or current_position[0] >= 80 or 0 >= current_position[1] or \
                                current_position[1] >= 80:
                    print "skipping"
                    continue
                else:
                    grid_location = localise_in_grid(current_position)  # get the grid coordinates for the vehicle
                    movement = grid_path[grid_location[0]][grid_location[1]]  # get direction of motion
                    # since the vehicle moves in steps the grid location of the vehicle can be accurately predicted.
                    # the prediction is confirmed by the sensor observation. the erroneous values are filtered out.
                    if (prev_grid[0] == 0 and prev_grid[1] == 0) and (
                                    grid_location[0] != ini_coordinates[0] or grid_location[1] != ini_coordinates[1]):
                        print "skipping initial coordinates mismatch"
                        continue
                    elif (count != 1 and prev_movement == "U") and (
                                    prev_grid[1] != grid_location[1] or prev_grid[0] != grid_location[0] + 1):
                        print "skipping U"
                        continue
                    elif (count != 1 and prev_movement == "D") and (
                                    prev_grid[1] != grid_location[1] or prev_grid[0] != grid_location[0] - 1):
                        print "skipping D"
                        continue
                    elif (count != 1 and prev_movement == "L") and (
                                    prev_grid[0] != grid_location[0] or prev_grid[1] != grid_location[1] + 1):
                        print "skipping L"
                        continue
                    elif (count != 1 and prev_movement == "R") and (
                                    prev_grid[0] != grid_location[0] or prev_grid[1] != grid_location[1] - 1):
                        print "skipping R"
                        continue
                    else:
                        print "matched with ", i

                    # each movement of vehicle sets the obstruction flag which next again checked to confirm the
                    # obstruction and set the grid accordingly
                    if obstruction_flag:
                        obs_dist = get_obstruction_distance()
                        print 'obstruction, next-movement, previous-movement gyro', obs_dist, movement, prev_movement, gyration_angle
                        if gyration_angle == -90:
                            if 5 <= obs_dist <= 15:
                                if grid_location[1] - 1 >= 0:
                                    obstruction_crd = [grid_location[0], grid_location[1] - 1]
                                    print 'obstruction_crd', obstruction_crd
                                    if obstruction_crd != start_coordinates and obstruction_crd != end_coordinates:
                                        obstruction(obstruction_crd)
                            grid_path = grid_object.optimum_policy()
                            movement = grid_path[grid_location[0]][grid_location[1]]
                            if prev_movement != movement or movement == "*":
                                move(-rotation_step, rotation_step)
                                print "reseting to 0, L"
                                stop()
                                set_gyro(0)
                            obstruction_flag = False
                        elif gyration_angle == 90:
                            if 5 <= obs_dist <= 15:
                                if grid_location[1] + 1 <= 3:
                                    obstruction_crd = [grid_location[0], grid_location[1] + 1]
                                    print 'obstruction_crd', obstruction_crd
                                    if obstruction_crd != start_coordinates and obstruction_crd != end_coordinates:
                                        obstruction(obstruction_crd)
                            grid_path = grid_object.optimum_policy()
                            movement = grid_path[grid_location[0]][grid_location[1]]
                            if prev_movement != movement or movement == "*":
                                move(rotation_step, -rotation_step)
                                print "reseting to 0, R"
                                stop()
                                set_gyro(0)
                            obstruction_flag = False
                        elif gyration_angle == 0:
                            if 5 <= obs_dist <= 15:
                                if grid_location[0] - 1 >= 0:
                                    obstruction_crd = [grid_location[0] - 1, grid_location[1]]
                                    print 'obstruction_crd', obstruction_crd
                                    if obstruction_crd != start_coordinates and obstruction_crd != end_coordinates:
                                        obstruction(obstruction_crd)
                            grid_path = grid_object.optimum_policy()
                            movement = grid_path[grid_location[0]][grid_location[1]]
                            if prev_movement != movement or movement == "*":
                                print "reseting to 0, U"
                                set_gyro(0)
                            obstruction_flag = False
                        elif gyration_angle == 180:
                            if 5 <= obs_dist <= 15:
                                if grid_location[0] + 1 <= 3:
                                    obstruction_crd = [grid_location[0] + 1, grid_location[1]]
                                    print 'obstruction_crd', obstruction_crd
                                    if obstruction_crd != start_coordinates and obstruction_crd != end_coordinates:
                                        obstruction(obstruction_crd)
                            grid_path = grid_object.optimum_policy()
                            movement = grid_path[grid_location[0]][grid_location[1]]
                            if prev_movement != movement or movement == "*":
                                move(2 * rotation_step, -2 * rotation_step)
                                print "reseting to 0, D"
                                stop()
                                set_gyro(0)
                            obstruction_flag = False
                        print '(prev_grid[0] != grid_location[0]) and (prev_grid[1] != grid_location[1])', prev_grid, grid_location
                        print "Lower movement", movement
                    if movement == "*":
                        print "=====REACHED GOAL====="
                        time.sleep(5)
                        # write the python_reply.txt to inform the initiator agent that the mobile agent has reached
                        # to receive the cargo
                        path_pythonReply = os.path.join(
                            fs + "home" + fs + "pi" + fs + "Desktop" + fs + "testingFiles" + fs + "19.08.17" + fs + "python_reply.txt")
                        if step == 0:
                            fp = open(path_pythonReply, "w")
                            # inform initiator agent the mobile agent has reached the 2nd END point and the 1st step
                            # is complete
                            fp.write("reached start")
                            fp.close()
                            step = 1
                            BrickPiUpdateValues()
                            ini_coordinates = grid_location
                        elif step == 1:
                            fp = open(path_pythonReply, "w")
                            # inform initiator agent the mobile agent has reached the 2nd END point and the job is
                            # complete
                            fp.write("reached end")
                            fp.close()
                            step = 2
                            BrickPiUpdateValues()
                            ini_coordinates = grid_location
                    else:
                        print "---searching path to goal, movement---", movement
                        obstruction_flag = fwd(movement, current_position, grid_location)
                    time.sleep(1)
            break
