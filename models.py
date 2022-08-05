from peewee import SqliteDatabase, Model, CharField, DateField, ForeignKeyField, BooleanField
from playhouse.migrate import *

db = SqliteDatabase("bot.sqlite3")
migrator = SqliteMigrator(db)


class User(Model):
    chat_id = CharField()
    first_name = CharField()
    username = CharField(null=True)
    is_authorized = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    class Meta:
        database = db


if __name__ == "__main__":
    db.create_tables([User, ])
    migrate(migrator.add_column("User", "is_superuser", User.is_superuser))
    # migrate(migrator.drop_not_null("User", User.username))
