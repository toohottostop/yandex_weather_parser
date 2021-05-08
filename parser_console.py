import argparse
from datetime import datetime, timedelta

from parser_engine import Manager
from database_config import pg_db

if __name__ == '__main__':
    manager = Manager()

    parser = argparse.ArgumentParser(description='Weather Forecast')
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='description')

    """Parser for drawing weather_card"""
    image_parser = subparsers.add_parser('draw_card', help='draw and show weather card. Date format YY-MM-DD')
    image_parser.add_argument('-date', default=datetime.now().strftime('%Y-%m-%d'), help='date format YY-MM-DD')
    image_parser.set_defaults(func=manager.draw_card)

    """Parser for adding data for a range of dates to the database"""
    db_add_parser = subparsers.add_parser('add_to_database', help='adds forecast for selected period')
    db_add_parser.add_argument('-db', default=pg_db, help='date_base driver')
    db_add_parser.add_argument('-city', default='moscow', help='city name where parse weather')
    db_add_parser.add_argument('-date_start',
                               default=datetime.now().strftime('%Y-%m-%d'),
                               help='use today\'s date and a maximum of 10 days in advance'
                                    'date format YY-MM-DD')
    db_add_parser.add_argument('-date_end',
                               default=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                               help='if you want to get forecast for one day - enter the same date as "-date_start". '
                                    'date format YY-MM-DD')
    db_add_parser.set_defaults(func=manager.add_to_database)

    """Parser for getting data for a range of dates from the database"""
    db_get_parser = subparsers.add_parser('get_from_database', help='gets forecast for selected period')
    db_get_parser.add_argument('-db', default=pg_db, help='date_base driver')
    db_get_parser.add_argument('-date_start', default=datetime.now().strftime('%Y-%m-%d'),
                               help='use today\'s date and a maximum of 10 days in advance'
                                    'date format YY-MM-DD')
    db_get_parser.add_argument('-date_end',
                               default=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                               help='if you want to get forecast for one day - enter the same date as "-date_start". '
                                    'date format YY-MM-DD')
    db_get_parser.set_defaults(func=manager.get_from_database)

    args = parser.parse_args()
    args.func(args)
