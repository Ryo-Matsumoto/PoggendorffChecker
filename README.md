# Poggendorff Checker
<img width="550" alt="overview" src="https://user-images.githubusercontent.com/56620904/188892949-4b8b7081-480d-4009-877d-777643925221.png">

## Outline
![demo](https://user-images.githubusercontent.com/56620904/189052109-763b2cf7-9f50-4827-a840-cb9af7a3fec2.gif)

Look at the figure above. When straight line PQ is occluded by rectangle ABCD, it appears to be not straight and continuous. This illusion is called __"Poggendorff illusion."__<br>
This software is an experimental tool to examine how many centimeters the perceived straight line PQ is differented from the true straight line PQ.

## How to Start
There are 2 ways to start.
+ Download exe file from Releases.
+ Install some Python libraries and execute ```main.py``` in the source directly.

If you choose the latter one, please follow the steps below.
1. Install some Python libraries by ```pip``` command as follow referring to ```requirement.txt``` in the source.
```concole
pip install -r requirements.txt
```
2. Execute ```main.py``` as follow.
```concole
python main.py
```

## How to Use
1. Set _θ_ [°] : the angle of the line to the rectangle.

2. Click ```start/stop``` button or press the space key to play the animation.

3. Viewing the animation. And if you recognize the continuous lines separated by the rectangle, click  ```start/stop``` button or press the space key to stop.

4. The console outputs _θ_ and the difference _d_ [cm] from the true straight line.
    - You can save or clear the contents of the console.

- You can display the true straight line as check the box in the upper left corner. 

## Development Language and Technology
- Python
- Tkinter
- PySDL

The know-how to integrate PySDL into Tkinter was used for UI development during a long-term internship I joined in 2022, and received technical evaluation from the supervisor.
