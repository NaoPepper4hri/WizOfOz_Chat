import argparse
import logging
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request
from naoqi import ALProxy

# Looks in templates folder for topic.html
app = Flask(__name__, template_folder='./templates')

# replace with IP needed for your pepper or Nao robot
ROBOT_IP = '192.168.8.100'
ROBOT_PORT = 9559

iLogger = None

def add_logger(log_path):
    logger = logging.getLogger("Interaction")
    logger.setLevel(logging.INFO)
    filename = "Interaction_%s.log" % (datetime.now().strftime("%H%M%S_%d%m%Y"))
    filePath = os.path.join(log_path, filename)
    
    # create error file handler and set level to info
    handler = logging.FileHandler(os.path.join(log_path, filename),"w", encoding=None, delay="true")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    
    # add file handler to log
    logger.addHandler(handler)
    
    return logger

class RobotHandler(object):
    __instance = None
    
    def __new__(cls):
        if not RobotHandler.__instance:
            RobotHandler.__instance = object.__new__(cls)
            RobotHandler.__instance.speech_proxy = ALProxy("ALAnimatedSpeech", ROBOT_IP, ROBOT_PORT)
            RobotHandler.__instance.configuration = {'bodyLanguageMode': 'contextual'}
            RobotHandler.__instance.motion_handler = ALProxy("ALMotion", ROBOT_IP, ROBOT_PORT)
            RobotHandler.__instance.basic_awareness = ALProxy("ALBasicAwareness", ROBOT_IP, ROBOT_PORT)
            RobotHandler.__instance.life_proxy = ALProxy("ALAutonomousLife", ROBOT_IP, ROBOT_PORT) 
            try:
                # This will actually put pepper to sleep as well as switch of peppers
                # independent listening. We will have to wake it up again. In experiment 
                # it does not look right
                #RobotHandler.__instance.life_proxy.life_proxy.setState("disabled")
                pass
            except:
                pass
            RobotHandler.__instance.tts = ALProxy("ALTextToSpeech",ROBOT_IP, ROBOT_PORT)
            RobotHandler.__instance.motion_handler.wakeUp()
            RobotHandler.__instance.basic_awareness.setEngagementMode("FullyEngaged")
            RobotHandler.__instance.basic_awareness.startAwareness()
            
            RobotHandler.__instance.robot_volume = 60
            RobotHandler.__instance.audio_proxy = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
            RobotHandler.__instance.audio_proxy.setOutputVolume(60)
            RobotHandler.__instance.motion_handler.setBreathConfig([['Bpm', 2.0], ['Amplitude', 1.0]])
            RobotHandler.__instance.motion_handler.setBreathEnabled ('Body', False)
            RobotHandler.__instance.headLockPitch = None
            RobotHandler.__instance.headLockYaw = None
            
            
            
        return RobotHandler.__instance

    def say(self, text):
        """
        robot proxy to say the text
        """
        self.speech_proxy(text, self.configuration)
        
        # Send robot to Stand Init
        #postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
        #postureProxy.goToPosture("StandInit", 0.5)
        
    def close(self):
        RobotHandler.__instance.basic_awareness.stopAwareness()
        #RobotHandler.__instance.motion_handler.setBreathEnabled ('Body', False)
    

@app.route('/')
def startUp():
    print "Starting up"
    pepper = RobotHandler()
    
    return render_template('topic.html')


@app.route('/pepper_focus/', methods=['POST'])
def tryingToFocus():
    """
    This handles the buttons that tries to switch the robot's focus from
    locking to one person or position to looking around to seek out other people.
    This has been extended to add some volume control. 
    There was also another extension made to reset the autonomous mode so that pepper
    does not actually listen to  users and speaking without Wizard-of-Oz control from this program
    """
    global iLogger
    pepper = RobotHandler()
    if request.form["focus"] == "Look at me":
        # This is to get Pepper to look around
        pepper.headLockPitch = None
        pepper.headLockYaw = None
        pepper.basic_awareness.startAwareness()
        print "Pepper trying to focus"
    elif request.form["focus"] == "Lock head":
         # Lock head in the current position. The coordinates are printed on the 
         # commandline. These coordinates can be used fo looking at predefined spots
         pepper.basic_awareness.stopAwareness() 
         pepper.motion_handler.setBreathEnabled ('Body', False)
         pepper.headLockPitch = float(pepper.motion_handler.getAngles("HeadPitch", False)[0])
         pepper.headLockYaw =  float(pepper.motion_handler.getAngles("HeadYaw", False)[0])
         pepper.motion_handler.setBreathEnabled ('Arms', True)
         print"PLEASE NOTE DOWN!! the head pitch yaw anlges : (%0.5f,%0.5f)"% (pepper.headLockPitch,
                                                                       pepper.headLockYaw)
    elif request.form["focus"] == "Speak louder":
        # Robot speaks louder
        pepper.robot_volume += 10
        pepper.audio_proxy.setOutputVolume(pepper.robot_volume)
        pepper.speech_proxy.say("Is that better?")
        
    elif request.form["focus"] == "Speak softer":
        # Robot speaks softer
        pepper.robot_volume -= 10
        pepper.audio_proxy.setOutputVolume(pepper.robot_volume)
        pepper.speech_proxy.say("Is that better?")
        
    elif request.form["focus"] == "Wake up":
        # Robot is forced to wake up
        pepper.motion_handler.wakeUp()
        pepper.basic_awareness.setEngagementMode("FullyEngaged")
        pepper.motion_handler.setBreathEnabled ('Body', True)
        pepper.basic_awareness.startAwareness()
        
    elif request.form["focus"] == "Rest":
        # Robot is forced to sleep. This is to be used if the
        # robot has started talking
        try:
            pepper.basic_awareness.stopAwareness() 
            pepper.motion_handler.setBreathEnabled ('Body', False)
            pepper.life_proxy.setState("disabled")
        except:
            pass
        
    return render_template('topic.html')
 
@app.route('/pepper_look_at/', methods=['POST'])
def lookHere():
    """
    Robot looks at preset position co-ordinates
    """
    pepper = RobotHandler()
    positionStr = str(request.form["lookAt"])
    if not positionStr:
         #print 1
         print"Please enter head pitch and yaw angles as comma seperated integers: (pitch,yaw)"
    else:
        positionList = positionStr.strip().strip(')').strip('(').split(',')
        if not len(positionList) == 2:
            #print 2
            print"Please enter head pitch and yaw angles as comma seperated decimal numbers : (pitch,yaw)"
        else:
            print positionList
            try:
                pepper.headLockPitch = float(positionList[0].strip())
                pepper.headLockYaw = float(positionList[1].strip())
                look_at_preset_dir(pepper)
            except:
                #print 3
                print"Please enter head pitch and yaw angles as comma seperated integers: (pitch,yaw)"
                raise 
        
    return render_template('topic.html')

def look_at_preset_dir(pepper):
    """
    Common function to handle setting of robot head angle for looking direction
    """
    if pepper.headLockPitch != None and pepper.headLockYaw != None :
        pepper.basic_awareness.stopAwareness() 
        pepper.motion_handler.angleInterpolation(['HeadPitch', 'HeadYaw'], 
                                                [pepper.headLockPitch, pepper.headLockYaw],
                                                [4, 4], 
                                                True)
        
        pepper.motion_handler.setBreathEnabled ('Arms', True)
        

@app.route('/pepper_introduction/', methods=['POST'])
def introduction():
    """
    Saying a preset introduction. May or maynot be required
    """
    introText = "Hello! I'm Pepper. I'm a member of the research department, at SoBA Lab. Please take a seat next to me, so we can get started."
    pepper = RobotHandler()
    try:
        look_at_preset_dir(pepper)
    except:
        pass
    #iLogger.info("Introduction")
    pepper.speech_proxy.say(introText, pepper.configuration) 
    return render_template('topic.html')

@app.route('/pepper_say_generic/', methods=['POST'])
def say_generic():
    """
    Pepper says the value that comes in the POST form in field "preset_text"
    """
    global iLogger
    pepper = RobotHandler()
    try:
        look_at_preset_dir(pepper)
    except:
        pass
    
    pepper.speech_proxy.say(str(request.form["preset_text"]), pepper.configuration)
    pepper.motion_handler.setBreathEnabled ('Arms', True) 
    return render_template('topic.html')
    
@app.route('/pepper_say_text/', methods=['POST'])
def say_text():
    """
    Say the text that the experimentor has typed in
    """
    global iLogger
    pepper = RobotHandler()
    try:
        look_at_preset_dir(pepper)
    except:
        pass
    
    pepper.speech_proxy.say(request.form["pepper_says"].encode('utf-8', 'ignore'), pepper.configuration)
    pepper.motion_handler.setBreathEnabled ('Arms', True) 
    return render_template('topic.html')



def main():
    global iLogger
    
    try:
        parser = argparse.ArgumentParser()
        # optional argument if logging is needed
        parser.add_argument("--participantNumber", type=int, default=0,
                          help="Participant number is required to match interaction log to participant") 
        args = parser.parse_args()
        """
        #This is if logging is needed
        log_path = os.path.join(os.path.abspath(os.sep), './logs')
        if not log_path  or not os.path.isdir(log_path):
            print("Please create the log directory '%s' on your system." % log_path)
            exit(0)
        else:
            if args.participantNumber:
                log_path = os.path.join(log_path, '%s' % args.participantNumber)
                if not os.path.isdir(log_path):
                    os.mkdir(log_path)
            iLogger = add_logger(log_path)  
        """
        app.run(debug=False)
           
    finally:
        #iLogger.info(" End of Wizard" )
        
        pass

if __name__ =='__main__':
    main()
