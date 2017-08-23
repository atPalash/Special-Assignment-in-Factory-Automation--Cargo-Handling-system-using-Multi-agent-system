# Multi-agent Cargo-handling system

The project simulates a cargo-handling system, where different type of agents interact to perform a job. The agents are Lego robots having Raspberry Pi as the controller and BrickPi as the interface between lego motor and sensors to Raspberry Pi. The project uses JADE as the multi-agent framework. JADE platforms are responsible for agent interaction and inter-agent communication. Here, one static and two mobile agents are present to simulate the situation. The task is to find the best agent to take the cargo from static agent to the point defined by the user. 

## Implementation

### Concept

* JADE is used as the multi-agent frame-work. JADE is responsible for agent commnication and decision making.
* The behavior of the robots is written in python. The python files run as server and listen to change in ".txt" files included in the project files. On detecting a file change having specified format the robot begin to work accordingly. for example, on reaching the 1st goal point the mobile agent (responder) informs static agent (initiator) that it is ready to receive package, this changes the java_reply.txt in initiator agent which informs the python code to turn ON the motor.
* Dynamic path planning approach has been used to compute the path the mobile agent need to take to perform the task. On detecting an obstruction it changes the map and the algorithm decides next optimum path to reach goal point.
* create a system that is easily extendable. it is possible to easily add other agents (static and mobile) as containers attached to local PC

### Robot and workspace construction

* static agent: it has one motor and one conveyor belt. 
* mobile agent: it has two base motor for motion of robot and one motor for rotating the top mounted ultrasonic sensor. two ultrasonic sensors are used one for obstruction detection and one for localisation.
* workspace: a 800 X 800 enclosure. this workspace was selected as the ultrasonic sensor sensitivity decreases with higher distance.

## Getting Started

### Prerequisites

Install modified Raspbian image from Dexter Industries at the Raspberry Pi. Install netbeans and downlaod JADE at the raspberry Pi. Make sure that all the agents are connected to same wifi network. Import the jar files for each project. install putty and VNC to control the Raspberry Pi from local machine.

### Installing

install required imports in the python codes.

## Running the tests

Follow the follwing steps:
1. run the code path_server.py in the local - PC - Responsible for the map of the workspace.
2. run mobile_robotServer.py in the mobile agents and static_robotServer.py in the static agent.
3. open netbeans at the Rpi agents and the respective IDE at local-PC, import the JAR files as given in JADE/jarFiles folder. Give the following input as shown below:
Setup at local-PC
![capture](https://user-images.githubusercontent.com/25124540/29600662-e6417454-87df-11e7-9893-ae9073a53b04.PNG)
Setup at Rpi-
replace the program arguments with "-container -host 192.168.1.34 -port 1099" where IP address and port should be that of local-PC
4. run the java application. 
5. A GUI will appear with all the Rpi connected to local-PC as "containers". right-click on the containers and start respective classes namely: initiator_Agent in static agent and responder_Agent in mobile agent. the rest of the steps can be found in the video link below.

### video for setup and robots in action
Please watch the video with subtitles 
video links:https://www.youtube.com/watch?v=WeKIt4D5sHQ&list=PLUgit2Zvqw2MoTt3fwD6ZBDVkgKlAu8R9
