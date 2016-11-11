import requests
import time
import subprocess
import sys
import os
import json
import logging
import ctypes
import psutil
import pynotify
from colorama import init, Fore

init()

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

logging.basicConfig(
    filename="logs/idlemaster_time_" + str(time.time()) + ".log",
    filemode="w",
    format="[ %(asctime)s ] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%d-%m-%Y %H:%M:%S"))
logging.getLogger('').addHandler(console)
logging.getLogger("requests").setLevel(logging.WARNING)

if sys.platform.startswith('win32'):
    ctypes.windll.kernel32.SetConsoleTitleA("Idle Master")

DEVNULL = open(os.devnull, 'w')

process_idle = {}
idle_time = {}
settings = {}


def stop():
    try:
        raw_input("Press [Enter] to continue ...")
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()


def toast(title, message, category):
    images = {
        'error': "./img/notify_error.png",
        'warning': "./img/notify_warning.png"
    }
    pynotify.init("steam-idle-time")
    image = os.path.realpath(images[category])
    notice = pynotify.Notification('Steam-Idle-Time ' + title, message, image)
    notice.set_timeout(10 * 1000)
    notice.show()


def debug(message):
    logging.debug(message + Fore.RESET)


def info(message):
    logging.info(Fore.GREEN + message + Fore.RESET)


def warning(message):
    logging.warning(Fore.YELLOW + message + Fore.RESET)
    toast('Warning', message, 'warning')
    stop()


def error(message):
    logging.error(Fore.RED + message + Fore.RESET)
    toast('Error', message, 'error')
    stop()


info("WELCOME TO IDLE MASTER (GAMES BY TIME)")

try:
    execfile("./settings.py", settings)
except Exception, e:
    error("Error loading settings file: " + str(e))

if not settings["apiKey"]:
    warning("No apiKey set")

if not settings["steamId"]:
    warning("No steamId set")


def idle_open(app_id):
    try:
        debug(Fore.GREEN + u'\u2713' + Fore.RESET + " " + get_app_name(app_id))
        global process_idle
        global idle_time

        idle_time[app_id] = time.time()

        if sys.platform.startswith('win32'):
            process_idle[app_id] = subprocess.Popen("./libs/steam-idle.exe " + str(app_id), stdout=DEVNULL, stderr=DEVNULL)
        elif sys.platform.startswith('darwin'):
            process_idle[app_id] = subprocess.Popen(["./libs/steam-idle", str(app_id)], stdout=DEVNULL, stderr=DEVNULL)
        elif sys.platform.startswith('linux'):
            process_idle[app_id] = subprocess.Popen(["python2", "./libs/steam-idle.py", str(app_id)], stdout=DEVNULL, stderr=DEVNULL)
        else:
            error("Operating system not supported: " + sys.platform)
    except Exception, e:
        error("Error starting steam-idle with game ID " + str(app_id) + ": " + str(e))


def idle_close(app_id):
    try:
        debug(Fore.RED + u'\u2715' + Fore.RESET + " " + get_app_name(app_id))
        process_idle[app_id].terminate()
    except Exception, e:
        error("Error closing steam-idle with game ID " + str(app_id) + ": " + str(e))


def get_app_name(app_id):
    try:
        api = requests.get("http://store.steampowered.com/api/appdetails/?appids=" + str(app_id) + "&filters=basic")
        api_data = json.loads(api.text)
        return Fore.CYAN + api_data[str(app_id)]["data"]["name"].encode('ascii', 'ignore') + Fore.RESET
    except:
        return Fore.CYAN + "App " + str(app_id) + Fore.RESET


def get_blacklist():
    try:
        with open('blacklist.txt', 'r') as f:
            lines = f.readlines()
        blacklist = [int(n.strip()) for n in lines]
    except:
        blacklist = []

    if not blacklist:
        debug("No games have been blacklisted")

    return blacklist


def get_whitelist():
    try:
        with open('whitelist.txt', 'r') as f:
            lines = f.readlines()
        whitelist = [int(n.strip()) for n in lines]
    except:
        whitelist = []

    if not whitelist:
        debug("No games have been whitelisted")

    return whitelist


def get_key(item):
    return item['playtime_forever']


def get_games():
    global settings
    info("Searching for " + str(settings['parallel']) + " games to idle")

    blacklist = get_blacklist()
    whitelist = get_whitelist()
    game_list = []

    try:
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?format=json&key=" + settings[
            'apiKey'] + "&steamid=" + settings['steamId'] + "&time=" + str(time.time())
        api = requests.get(url)
        game_data = json.loads(api.text)['response']['games']
        for game_id in whitelist:
            game_list.append({
                "appid": game_id,
                "playtime_2weeks": 0,
                "playtime_forever": 0
            })

        for data in game_data:
            game_id = data['appid']
            if game_id in blacklist:
                continue
            else:
                game_list.append(data)

        return sorted(game_list, key=get_key)[:settings['parallel']]
    except Exception, e:
        error("Error reading games api: " + str(e))


def is_running(program):
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if program in p.name():
            return True

    return False


def steam_check():
    if not is_running('steam'):
        error('Steam is not running')
    else:
        debug('Steam is running')


while True:
    try:
        steam_check()
        games = get_games()
        for game in games:
            idle_open(game['appid'])

        sleeping = settings['sleeping']
        info("Idling for " + str(sleeping) + " minutes")
        idle = sleeping * 60
        idled = 0
        delay = 60

        while idled <= idle:
            time.sleep(delay)
            steam_check()
            idled += delay

        for game in games:
            idle_close(game['appid'])
    except KeyboardInterrupt:
        warning("Closing cause of keyboard interrupt")
    except Exception, e:
        error("error in main loop: " + str(e))

info("Successfully completed idling process")
stop()
