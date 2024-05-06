import env_configuration
import databases
import sqlalchemy

DATABASE_URL = "%s://%s:%s@%s:%s/%s" % (
    env_configuration.config.get("DBDRIVER"),
    env_configuration.config.get("DBUSERNAME"),
    env_configuration.config.get("DBPASSWORD"),
    env_configuration.config.get("DBHOST"),
    env_configuration.config.get("DBPORT"),
    env_configuration.config.get("DBNAME"),
)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)
