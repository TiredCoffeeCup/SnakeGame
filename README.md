## The Motive

This was just a fun project I took on when I was starting on OOP, The graphics are not too great and the code is quite messy, but I'm proud of it

## The Learning

I used this project to familiarize myself with OOP and create graphics-based programs.

## Prerequisites

Python

Modules: 
* Pygame

## Usage

# Startup
Running main.py will start the game and open the 'saves' screen.

Each save will be shown in the below format: <br/><br/>
![image](https://github.com/user-attachments/assets/ae260ac9-7f21-4a71-af53-68795b31a538) <br/>

The 3 buttons below the image are used to edit the save:

* The pencil icon: <br/>
    ![image](https://github.com/user-attachments/assets/f0dff6f9-1f14-4436-b1f3-a74c49a81008) <br/>
    This button is used to edit the world

* The '-' icon: <br/>
    ![image](https://github.com/user-attachments/assets/3e7213f9-5a65-4a22-9591-b70c2a5702b2) <br/>
    This button is used to delete the corresponding world.

* The play button: <br/>
    ![image](https://github.com/user-attachments/assets/8773cb03-63a6-4fe4-baf3-ffece36783eb) <br/>
    This button is used to play the corresponding world.

# Playing the Game

Once the game has started, a 3 long snake will be created which you can control using the up, down, left, and right arrow keys.

At the bottom of the window, you will see a scorecard:<br/>


which represents your current score in the game.<br/>

![image](https://github.com/user-attachments/assets/e9314804-ae95-4db7-851a-6d44cec6cea0)

At the bottom left of the window, you will see a HI scorecard:<br/>

![image](https://github.com/user-attachments/assets/9736584c-b795-43ec-9500-3410875f57d3)

which represents the highest score you have achieved in the current save.<br/>


and an edit button which you can use to edit the current world.

# Adding a Save

In the saves screen, you will see a '+' button, which you can use to create a new save.
Pressing it will open a tkinter window in which you will enter the details of your new save. <br/>

![image](https://github.com/user-attachments/assets/111c59d8-77ab-4601-be43-c5ce571e7848)

Pressing the OK button will create the new save and open it.

# Editing a Save

On pressing the edit button, the game will open a new window.

On the right side of the window, you will see a toolbar:  <br/> 
![image](https://github.com/user-attachments/assets/30d08644-2368-48f1-bc01-37ec91d9c65c)

The buttons in order from the top are:

* Wall: Place walls
* Snake: Places head of snake
* Empty: Replace cell with empty space
* Rows (- +): Add or remove rows
* Columns (- +): Add or remove columns
* Clear: Clears the whole slate
* Save: Saves the edits made to the world.

## Closing Notes

Overall the code is very badly documented (not for long hopefully) and not really formatted according to classic Python guidelines. It's just supposed to be something I experimented on and nothing too serious.

