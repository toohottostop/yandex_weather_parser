# Yandex Weather Parser  
**Parser can:**  
1. Parse and save weather forecast in database for a range of dates
2. Get weather forecast from database for a range of dates
3. Create weather forecast card for the selected date
# What used?
Pytnon:
[pytnon 3.8.5](https://www.python.org/downloads/release/python-385/)  

Libs:  
- requests
- BeautifulSoup
- OpenCV
- Pillow
- peewee ORM
- argparse
## Installation
1. Make dir and jump into it `$mkdir weather_parser && cd weather_parser`
2. Clone repository`git clone https://github.com/toohottostop/yandex_weather_parser.git`
3. Install virtual environment package `$sudo apt install python3-virtualenv`    
Set your virtual environment package `$python3 -m virtualenv <name_of_virtualenv>`  
Activate virtual environment `$source <name_of_virtualenv>/bin/activate`
4. Install requirements `pip install -r requirements.txt`
5. Set your data base in `database_config.py`(in project I used Postgres, but you can choose [another one](http://docs.peewee-orm.com/en/latest/peewee/database.html#initializing-a-database))  
`pg_db = PostgresqlExtDatabase('<database_name>', user='<your role in database>')`
## How to use  
**~NOTE_1:** You can get the weather from the current day and 10 days in advance  
**~NOTE_2:** If you want add or get weather data in 1 day you need to pass the same date in `-date_end` as in `-date_start`
1. First you need to parse and save to database. Use "add_to_database" subparser:   
`python python_console.py add_to_database -city <city_name> -date_start <date in format YYYY-MM-DD> -date_end <date in format YYYY-MM-DD>`
2. Than you can make a card with "draw_card" subparser. 
Follow command will show you weather card and make directory with this card in project folder:   
`python python_console.py draw_card -date <choose date in format YYYY-MM-DD>`
3. Also you can get weather data from your database with "get_from_database" subparser.
 This command will print in stdout your weather schedule for chosen dates:  
 `python python_console.py get_from_database -date_start <date in format YYYY-MM-DD> -date_end <date in format YYYY-MM-DD>`  
