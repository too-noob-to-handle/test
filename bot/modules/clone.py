from random import SystemRandom
from string import ascii_letters, digits
from telegram.ext import CommandHandler
from threading import Thread
from time import sleep

from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import *
from bot.helper.mirror_utils.download_utils.direct_link_generator import *
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

#জিডিটট ও এপড্রাইভ ইম্পোর্ট'স
import requests
import random
import re
from base64 import b64decode
from urllib.parse import urlparse, parse_qs

#জিডিটট ও এপড্রাইভ মডিউল 

APPDRIVE_ACCOUNTS = [
  {
    "email":"gdtot1@brccollege.edu.in",
    "password":"gdtot1@brccollege.edu.in"
  },

  {
    "email":"gdtot2@brccollege.edu.in",
    "password":"gdtot2@brccollege.edu.in"
  },

  {
    "email":"gdtot3@brccollege.edu.in",
    "password":"gdtot3@brccollege.edu.in"
  },

  {
    "email":"gdtot4@brccollege.edu.in",
    "password":"gdtot4@brccollege.edu.in"
  },

  {
    "email":"gdtot5@brccollege.edu.in",
    "password":"gdtot5@brccollege.edu.in"
  },
  
]


class AppDrive:
  def __init__(self, baseURL:str = "https://appdrive.info") -> None:
    self.loginData = random.choice(APPDRIVE_ACCOUNTS)
  
    self.keyRegex = '"key",\s+"(.*?)"'
    self.BaseURL = baseURL
    self.reqSes = requests.Session()
    self.headers = {
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'referer': self.BaseURL,
  }
    self.reqSes.headers.update(self.headers)
  
  def login(self) -> bool:
    login_ = self.reqSes.post(f'{self.BaseURL}/login', data=self.loginData)
    if login_.cookies.get("MD"):
      return True
    return False
  
  def download(self, url:str) -> str:

    if not self.login():
      raise Exception("Falied to login Please try again")

    try:
      res = self.reqSes.get(url)
      key = re.findall(self.keyRegex, res.text)[0]
    except:
      raise Exception("URl is Inavalid or Failed to get Key Value")

    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    while data['type'] <= 3:
        try:
            res = self.reqSes.post(url, data=data).json()
            break
        except: data['type'] += 1
    
    if res.get('url'):
      return res.get('url')
    else:
      raise Exception(str(res))


if __name__ == "__main__":
  print(AppDrive().download("https://appdrive.in/file/feff0b041a15d41fa714"))

GDTOT_COOKIES = [
    "NkVjQ0p1VFJ5cWFsdmZDOWI4bCszTjFVVHloU052Mm9pNGdyeUd4alJGWT0%3D",
    "Z0o0anBxemZUQUxJekQ4eWhBZ21VT25tdjNSYnFTYlUxb2V2cWZaVjY0ST0%3D",
    "Rnp2NWtkRURiZzJ3UEdEMm93MHRRSk12T0NNaExQVzcvb1pGa2lUNzZOQT0%3D",
    "TW94QVNXMUNMZjdqa3JXQi8vNFdUTW8vcUZNNHp0enJOSGVZZUh2bm5rcz0%3D",
    "TDVpOWtjR2RGSDFDVmxlMDFKZElvV1pUUGJYL24zeHJXK3lNY1lOcXQzVT0%3D",
]

class GdTot:
    def __init__(self, baseURL = "https://new.gdtot.nl") -> None:
        self.loginData = random.choice(GDTOT_COOKIES)
        self.gdRegex = 'gd=(.*?)&'
        self.BaseURL = baseURL
        self.reqSes = requests.Session()
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': self.BaseURL,
        'crypt':self.loginData
        }
        self.reqSes.headers.update(self.headers)
        self.reqSes.cookies.update({'crypt': self.loginData})

    def login(self) -> bool:
        login_ = self.reqSes.post(f'{self.BaseURL}')
        if "/login.php?action=logout" in login_.text:
            self.reqSes.cookies.update({"PHPSESSID":login_.cookies.get('PHPSESSID')})
            return True
        return False

    def download(self, url: str) -> str:

        self.baseURL = "https://{domain}".format(domain=urlparse(url).netloc)
        self.reqSes.headers.update({"referer":url})
        # Extracting Domain base url from URL path itself so we don't have to edit it again

        if not self.login():
            raise Exception("Falied to login Please try again")
        try:
            id = url.split('/')[-1]
            res = self.reqSes.get(f"{self.BaseURL}/dld?id={id}")
            urll = re.findall('URL=(.*?)\"', res.text)[0]
            qs = parse_qs(urlparse(urll).query)
            # getGDUrl = re.findall(self.gdRegex, res.text)
            # print(getGDUrl)
            if qs['gd'][0] == 'false':
                err_msg = qs['msgx'][0]
                raise Exception(err_msg)
            else:
                gdUrl = b64decode(str(qs['gd'])).decode('utf-8')
                return f'https://drive.google.com/file/d/{gdUrl}/view'
        except Exception as err:
            raise Exception(f"Failed to get download url Please try again - {str(err)}")
                    
if __name__ == "__main__":
    print(GdTot().download("https://new.gdtot.nl/file/161529855"))
    # print(GdTot().download("https://new.gdtot.nl/file/20395706860"))
    
#জিডিটট ও এপড্রাইভ মডিউল শেষ এইখানে।

def _clone(message, bot, multi=0):
    args = message.text.split(" ", maxsplit=1)
    reply_to = message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1]
        if 'new.gdtot' in link:
            try:
                msg = sendMessage(f"⚠️ 𝙂𝙙𝙏𝙩𝙤𝙩 𝙇𝙞𝙣𝙠 𝘿𝙚𝙩𝙚𝙘𝙩𝙚𝙙 𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩:- \n<code>{link}</code>", bot, message)
                link = GdTot().download(link)
                deleteMessage(bot, msg)
            except Exception as e:
                deleteMessage(bot, msg)
                return sendMessage(str(e), bot, message)

        if 'appdrive' in link:
            try:
                msg = sendMessage(f"⚠️ 𝘼𝙥𝙥𝙙𝙧𝙞𝙫𝙚 𝙇𝙞𝙣𝙠 𝘿𝙚𝙩𝙚𝙘𝙩𝙚𝙙 𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩:- \n<code>{link}</code>", bot, message)
                link = AppDrive().download(link)
                deleteMessage(bot, msg)
            except Exception as e:
                deleteMessage(bot, msg)
                return sendMessage(str(e), bot, message)
    is_unified = is_unified_link(link)
    is_udrive = is_udrive_link(link)
    is_sharer = is_sharer_link(link)
    if (is_unified or is_udrive or is_sharer):
        try:
            msg = sendMessage(f"⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙇𝙞𝙣𝙠 𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩: \n<code>{link}</code>", bot, message)
            LOGGER.info(f"Processing: {link}")
            if is_unified:
                link = unified(link)
            if is_udrive:
                link = udrive(link)
            if is_sharer:
                link = sharer_pw(link)
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_gdrive_link(link):
        gd = GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            return sendMessage(res, bot, message)
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "\n❗️❗️❗️ 𝘿𝙪𝙥𝙡𝙞𝙘𝙖𝙩𝙚 𝘿𝙚𝙩𝙚𝙘𝙩𝙚𝙙 ❗️❗️❗️\n\n🔸 𝙁𝙞𝙡𝙚/𝙁𝙤𝙡𝙙𝙚𝙧 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝙞𝙣 𝘿𝙧𝙞𝙫𝙚.\n🔸 𝙃𝙚𝙧𝙚 𝙖𝙧𝙚 𝙩𝙝𝙚 𝙨𝙚𝙖𝙧𝙘𝙝 𝙧𝙚𝙨𝙪𝙡𝙩𝙨:"
                return sendMarkup(msg3, bot, message, button)
        if CLONE_LIMIT is not None:
            LOGGER.info('Checking File/Folder Size...')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'𝙁𝙖𝙞𝙡𝙚𝙙, 𝘾𝙡𝙤𝙣𝙚 𝙡𝙞𝙢𝙞𝙩 𝙞𝙨 {CLONE_LIMIT}𝙂𝘽.\n𝙔𝙤𝙪𝙧 𝙁𝙞𝙡𝙚/𝙁𝙤𝙡𝙙𝙚𝙧 𝙨𝙞𝙯𝙚 𝙞𝙨 {get_readable_file_size(size)}.'
                return sendMessage(msg2, bot, message)
        if multi > 1:
            sleep(4)
            nextmsg = type('nextmsg', (object, ), {'chat_id': message.chat_id, 'message_id': message.reply_to_message.message_id + 1})
            nextmsg = sendMessage(args[0], bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            multi -= 1
            sleep(4)
            Thread(target=_clone, args=(nextmsg, bot, multi)).start()
        if files <= 20:
            msg = sendMessage(f"♻️ 𝘾𝙡𝙤𝙣𝙞𝙣𝙜: <code>{link}</code>", bot, message)
            result, button = gd.clone(link)
            deleteMessage(bot, msg)
        else:
            drive = GoogleDriveHelper(name)
            gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=12))
            clone_status = CloneStatus(drive, size, message, gid)
            with download_dict_lock:
                download_dict[message.message_id] = clone_status
            sendStatusMessage(message, bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass        
        if button in ["cancelled", ""]:
            sendMessage(f"{tag} {result}", bot, message)
        else:
            sendMarkup(result, bot, message, button)
            LOGGER.info(f'Cloning Done: {name}')
        if (is_unified or is_udrive or is_sharer):
            gd.deletefile(link)
    else:
        sendMessage('𝘿𝙪𝙙𝙚, 𝙎𝙚𝙣𝙙 𝙂𝙙𝙧𝙞𝙫𝙚 𝙤𝙧 𝙂𝘿𝙏𝙤𝙏, 𝘼𝙥𝙥𝘿𝙧𝙞𝙫𝙚, 𝘿𝙧𝙞𝙫𝙚𝘼𝙥𝙥, 𝙂𝘿𝙁𝙡𝙞𝙭, 𝘿𝙧𝙞𝙫𝙚𝘽𝙞𝙩, 𝘿𝙧𝙞𝙫𝙚𝙇𝙞𝙣𝙠𝙨, 𝘿𝙧𝙞𝙫𝙚𝙋𝙧𝙤, 𝘿𝙧𝙞𝙫𝙚𝘼𝙘𝙚, 𝘿𝙧𝙞𝙫𝙚𝙎𝙝𝙖𝙧𝙚𝙧, 𝙃𝙪𝙗𝘿𝙧𝙞𝙫𝙚, 𝘿𝙧𝙞𝙫𝙚𝙃𝙪𝙗, 𝙆𝙖𝙩𝘿𝙧𝙞𝙫𝙚, 𝙆𝙤𝙡𝙤𝙥, 𝘿𝙧𝙞𝙫𝙚𝙁𝙞𝙧𝙚, 𝙎𝙝𝙖𝙧𝙚𝙧𝙋𝙬 𝙡𝙞𝙣𝙠 𝙖𝙡𝙤𝙣𝙜 𝙬𝙞𝙩𝙝 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙧 𝙗𝙮 𝙧𝙚𝙥𝙡𝙮𝙞𝙣𝙜 𝙩𝙤 𝙩𝙝𝙚 𝙡𝙞𝙣𝙠 𝙗𝙮 𝙘𝙤𝙢𝙢𝙖𝙣𝙙', bot, message)

@new_thread
def cloneNode(update, context):
    _clone(update.message, context.bot)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
