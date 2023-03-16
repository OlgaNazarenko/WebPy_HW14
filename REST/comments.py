# async def get_contacts_birthdays(user: User, db: Session):
#     seven_days_from_now = datetime.now().date() + timedelta(days=7)
#     contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
#
#     contacts_with_birthdays = [
#         contact for contact in contacts if
#         datetime.now().date().day <= contact.date_of_birth.day < seven_days_from_now.day
#     ]
#
#     return contacts_with_birthdays
#
# contacts = db.query(Contact).filter(Contact.user_id == user.id).all()


# contacts_with_birthdays=[]

# for contact in contacts :
#     bday_month = contact.date_of_birth.month
#     bday_day = contact.date_of_birth.day
#
#     # Проверяем, что день рождения находится в интервале текущей даты до текущей даты + 7 дней
#     if today.month <= bday_month <= end_date.month:
#         if (today.month < bday_month or today.day <= bday_day) and (
#                 bday_month < end_date.month or bday_day <= end_date.day):
#             contacts_with_birthdays.append(contact)
#
# return contacts_with_birthdays


# file_config = pathlib.Path(__file__).parent.joinpath('config.ini')
# config = configparser.ConfigParser()
# config.read(file_config)

# username = config.get('DB', 'user')
# password = config.get('DB', 'password')
# db_name = config.get('DB', 'db_name')
# host = config.get('DB', 'host')
# port = config.get('DB', 'port')
