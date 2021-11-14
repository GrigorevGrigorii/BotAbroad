import argparse
import logging

from libs.corona import corona_restrictions

logger = logging.getLogger(__name__)


def parse_args(command_args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--test', action='store_true')

    return parser.parse_args(command_args)


def main(command_args=None):
    args = parse_args(command_args)

    logger.info('Start collecting corona infos')
    corona_infos = {}
    for region in corona_restrictions.get_regions():
        corona_infos[region] = corona_restrictions.get_full_info_about_all_countries_in_region(region)

    if args.test:
        import json
        with open('test_corona_infos.json', 'w') as test_corona_infos_json:
            json.dump(corona_infos, test_corona_infos_json)
    else:
        logger.info('Save corona infos to DB')
        from database.lib.handler import DBHandler
        with DBHandler() as handler:
            handler.upload_corona_infos(corona_infos)


if __name__ == '__main__':
    main()
