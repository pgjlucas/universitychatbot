'''
    Slack Bot for StaCIA
    Group: G1 

    Source: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
    
    How to Get it running:

        Change FRANK_USER to your frank username

        Terminal Commands
        * pip install --user slackclient
        * python3 SlackBot.py

        Slack (Channels that work - #general and #stacia)
        * @StaCIA's Mom  [type something here]

'''

import os, sys, re, time
ORIGINAL_SYS = sys.path
FRANK_USER = 'mkong02466'
sys.path.insert(0, '/home/' + FRANK_USER + '/.local/lib/python3.5/site-packages')
from slackclient import *
sys.path.insert(0, ORIGINAL_SYS)

from answer import get_answer

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# BOT USER OAUTH TOKEN
SLACK_BOT_TOKEN = "xoxb-660667343527-658847352373-YBL7ksAtjOaVMz5JEdYL2QvP"
#starterbot_id = None

# instantiate slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)


# Parses events for messages 
# Returns the command,channel OR None,none
def parse_bot_commands(slack_events, starterbot_id):

    print("\nEvent: ")
    print(slack_events)

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            print("\nuser Id: " )
            print(user_id)
            print("startbot id: ")
            print(starterbot_id)
            print("\nmessage: ")
            print(message)
            if user_id == starterbot_id:
                return message, event["channel"]

    return None, None


# Splits message into Bot User Id and Message Contents
# returns BOT USERID , MESSAGE CONTENTS
def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


# Executes the bot command
def handle_command(command, channel):

    default_response = "Not sure what you mean. Ask *{}*.".format("What questions can I ask?")
    response = None

    # This is where you start to implement more commands!
    if command.startswith("hi"):
        response = "Hi back!"
    
    elif command.startswith("What questions can I ask?"):
        response = "You can ask anything about the Stats Major, Stats Minor, and their curricula."

    # send the question to our program
    else:
        response = get_answer(command)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
   


def main():

    # check connection
    bool = slack_client.rtm_connect(with_team_state=False)
    if (bool):
        print("StaCia is connected and running!")

        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        print("\nStarterbot Id: " + starterbot_id)

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read(),starterbot_id)

            print("\ncommand: ")
            print(command)
            print("\nchannel: ")
            print(channel)

            if command:
                handle_command(command,channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

    return

if __name__=="__main__":
    main()
