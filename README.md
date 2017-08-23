# Multi-agent Cargo-handling system

The project simulates a cargo-handling system, where different type of agents interact to perform a job. The agents are Lego robots having Raspberry Pi as the controller and BrickPi as the interface between lego motor and sensors to Raspberry Pi. The project uses JADE as the multi-agent framework. JADE platforms are responsible for agent interaction and inter-agent communication. Here, one static and two mobile agents are present to simulate the situation. The task is to find the best agent to take the cargo from static agent to the point defined by the user. 

## Getting Started

### Prerequisites

Install modified Raspbian image from Dexter Industries at the Raspberry Pi. Install netbeans and downlaod JADE at the raspberry Pi. Make sure that all the agents are connected to same wifi network. Import the jar files for each project. install putty and VNC to control the Raspberry Pi from local machine.

### Installing

install required imports in the python codes.

## Running the tests

Follow the follwing steps:
1. run the code path_server.py in the local - PC - Responsible for the map of the workspace.
2. run mobile_robotServer.py in the mobile agents and static_robotServer.py in the static agent.
3. open netbeans at the Rpi agents and the respective IDE at local-PC. Give the following input as shown below:
Setup at local-PC
![capture](https://user-images.githubusercontent.com/25124540/29600662-e6417454-87df-11e7-9893-ae9073a53b04.PNG)
Setup at Rpi-
replace the program arguments with "-container -host 192.168.1.34 -port 1099" where IP address and port should be that of local-PC
4. run the java application



### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc

# Special-Assignment-in-Factory-Automation--Cargo-Handling-system-using-Multi-agent-system
The projects simulates a Cargo handling system. 
video links:https://www.youtube.com/playlist?list=PLUgit2Zvqw2MoTt3fwD6ZBDVkgKlAu8R9
