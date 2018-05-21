## Introduction
A manager (backend) for ss-libev. Aims to manage user accounts and traffics based on database.

## Installation
1. Install python3.5+
2. Install requirements using the following commands
    ```bash
    cd ssman-libev
    pip install -r requirement.txt
    ```
3. Setup database. Execute following commands in mysql
    ```sql
    create database ssman;
    grant all privileges on ssman.* to 'yourdbusername'@'%' identified by 'yourpassword';
    quit
    ```
    then in bash execute
    ```bash
    cd ssman-libev
    mysql -uyourdbusername -pyourpassword ssman < ssman.sql
    ```

## Usage
1. Prepare your data in database
2. Set up your configurations in `config.py`
3. Add `_cron_user_manager.py` and `_cron_reminder_mail.py` *(optional)* to your crontab on Database Server

    `_cron_user_manager.py` should run every a few minutes, but `_cron_reminder_mail.py` should only 
    run once per day, or the users may get several reminder mails in one day.


4. Start ss-libev(ss-manager mode) program on ss server. You can run it from docker using:
    ```bash
    docker run -itd --net=host --restart=always --name=ss-libev dylanchu/ss-libev ss-manager -u -m aes-128-cfb -u --manager-address 127.0.0.1:6001 -s :: -s 0.0.0.0
    ```
5. Run `client_server.py` on ss server


## Notice
_cron_user_manager.py is **necessary** and should be executed every a few minutes;

_cron_reminder_mail.py is **optional** and can be executed once a day;

_cron_reset_traffic.py is **necessary** and should be executed at the first day of every month.

