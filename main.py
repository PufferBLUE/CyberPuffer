from utils import globals, config, log, functions
from queue import Queue
from telegram import Bot, Update
from telegram.ext import Dispatcher
from telegram.utils.request import Request

logger = log.get_logger(name = 'Bot')

# Use global varible cache to optimize speed
dispatcher = None

# Entrypoint for GCE Cloud Functions
def webhook(request):
    globals.webhook = True
    bot = Bot(token=config.telegram_api_secret)
    bot._request=Request(proxy_url=config.proxy_url)

    global dispatcher
    if not dispatcher:
        dispatcher = Dispatcher(bot, Queue())
        functions.load_funcs(dispatcher)

    if request.method == "POST":
        update_text = request.get_json(force=True)
        update = Update.de_json(update_text, bot)
        dispatcher.process_update(update)
    return "ok"

def polling():
    from telegram import constants
    from telegram.ext import Updater
    from distutils.version import LooseVersion
    from telegram import __version__ as ptb_version
    REQUEST_KWARGS={'proxy_url': config.proxy_url}
    updater = Updater(token=config.telegram_api_secret, use_context=True, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher
    functions.load_funcs(dispatcher)
    if LooseVersion(ptb_version) >= LooseVersion('13.5'):
        updater.start_polling(allowed_updates=constants.UPDATE_ALL_TYPES)
    else:
        logger.warn('PTB version < 13.5, not all update types are listening')
        updater.start_polling()

if __name__ == "__main__":
    polling()