# WizOfOz_Chat
A html page based wizard of oz application to control what Nao or Pepper says using Flask.

When any of the preset text value button is clicked in the html>pepper_say_generic form , Pepper/Nao will say the text 
There is also provision to type in custom text for the robot to say.

### There are some additional functionalities:
* Speak Louder/Softer: For volume control
* Lock head : Robot instructed to stop moving head and lock the direction it is looking at. The head-angles are printed to command line
* Look at me : Unlocks  look direction and makes robot look around and find a human form to focus on. Making noise helps in this setting to get robot to look towards the noise (not reliable)
* Look here: Looks in the angles specified in the input box. (Usually angles given by the Lock head functionality) 

## Requirements 
* A Nao or Pepper robot
* Python 2.7 with Naoqi package installed as instructed on [Aldebaran](http://doc.aldebaran.com/2-8/dev/python/install_guide.html#python-install-guide)

Install the following packages. Some of these get automatically installed when Flask is installed.

certifi==2019.3.9

chardet==3.0.4

Click==7.0

decorator==4.3.0

Flask==1.1.1

idna==2.8

itsdangerous==1.1.0

Jinja2==2.10.1

MarkupSafe==1.1.1

numpy==1.14.3

Pillow==5.1.0

requests==2.22.0

tqdm==4.23.4

urllib3==1.25.3

Werkzeug==0.16.0

### Note: The ip of the robot has to be set to your robot's IP in code

##Running the code:

>> python pepperSays.py

This will start up the server side and the html page will be accessable by default at : http://127.0.0.1:5000/
It will show on the commandline what url it is running on. Copy it to any web browser and make your robot talk.
