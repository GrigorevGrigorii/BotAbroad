import logging

from database.lib.handler import DBHandler
from libs.corona import corona_restrictions
from libs.bot.bot_abroad import BotAbroad

logger = logging.getLogger(__name__)


def main():
    def _main(handler):
        corona_infos = {}
        for region in corona_restrictions.get_regions():
            corona_infos[region] = corona_restrictions.get_full_info_about_all_countries_in_region(region)

        logger.info('Save corona infos to DB')
        changed_countries = set(handler.get_changed_and_upload_corona_infos(corona_infos))

        all_chats = handler.get_all_chats()
        for chat in all_chats:
            changed_countries_from_subscriptions = changed_countries & set(chat.subsciptions)
            if changed_countries_from_subscriptions:
                with BotAbroad(handler, chat.chat_id) as bot_abroad:
                    bot_abroad.send_info_about_subscriptions(changed_countries_from_subscriptions)

    logger.info('Start collecting corona infos')
    with DBHandler() as handler:
        _main(handler)


if __name__ == '__main__':
    main()
