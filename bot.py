import telebot
import os
import re
import subprocess
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
allow_user_ids = [int(i) for i in os.getenv('USERS').split(',')]

bot = telebot.TeleBot(token)


def bash(string):
    """
    Define bash to call bash shell command return 
    """
    output = subprocess.run(string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return output.stdout

def check_inject_bash(string):
    """
    Remove inject in bash allow only a-z,A-Z,0-9,-_
    """
    if (1 <= len(string) <= 25 and re.match('^[0-9a-zA-Z\-\_]+$', string) and 
        not string.startswith("-") and not string.startswith("_") and
        not string.endswith("-") and not string.endswith("_")):
        return False
    else:
        return True

def parse_command(text):
    command = ''
    service = ''
    if text.startswith('/start '):
        command = 'start'
        service = text.replace('/start ', '')
    if text.startswith('/restart '):
        command = 'restart'
        service = text.replace('/restart ', '')
    if text.startswith('/stop '):
        command = 'stop'
        service = text.replace('/stop ', '')
    if text.startswith('/status '):
        command = 'status'
        service = text.replace('/status ', '')
    return command, service

@bot.message_handler(commands = ['help'])
def greet(message):
    if message.from_user.id not in allow_user_ids:
        bot.reply_to(message, 'Access Denied.')
    else:
        msg = """/status <service> - Check Status Service
/start <service> - Start service 
/stop <service> - Stop service 
/restart <service> - Restart service
/deploy - Run script deploy in config
/help - Print help menu of bot
"""
        bot.reply_to(message, msg)

@bot.message_handler(commands = ['start', 'stop', 'status', 'restart'])
def service(message):
    if message.from_user.id not in allow_user_ids:
        bot.reply_to(message, 'Access Denied.')
        return
    command, service = parse_command(message.text)
    if not service:
        bot.reply_to(message, 'Missing service')
        return
    if check_inject_bash(service):
        bot.reply_to(message, 'WARNING-Inject detect')
        return
    msg = bash('service ' + service + ' ' + command)
    bot.reply_to(message, '\n' + msg)

@bot.message_handler(commands = ['deploy'])
def deploy(message):
    if message.from_user.id not in allow_user_ids:
        bot.reply_to(message, 'Access Denied.')
        return
    script = os.getenv('SCRIPT')
    msg = bash('bash ' + script)
    bot.reply_to(message, '\n' + msg)

def main():
    bot.polling() # looking for message

if __name__ == '__main__':
    main() 