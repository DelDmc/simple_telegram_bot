from peewee import SqliteDatabase, Model, CharField, DateField, ForeignKeyField

db = SqliteDatabase("bot.sqlite3")


class User(Model):
    chat_id = CharField()
    first_name = CharField()
    username = CharField()

    class Meta:
        database = db


if __name__ == "__main__":
    db.create_tables([User, ])
