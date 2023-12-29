from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
import ORM.config as config


class DataBase:
    def __init__(self):
        # Создаем объект MetaData, чтобы получить метаданные из базы данных
        self.metadata_roles = MetaData(schema="roles")
        self.metadata_roles.reflect(config.engine)

        self.metadata_main = MetaData(schema="main")
        self.metadata_main.reflect(config.engine)

        self.Base_roles = automap_base(metadata=self.metadata_roles)
        self.Base_roles.prepare()

        self.Base_main = automap_base(metadata=self.metadata_main)
        self.Base_main.prepare()

        self.Role = self.Base_roles.classes.role
        self.Users = self.Base_roles.classes.users

        self.Device = self.Base_main.classes.device
        self.DeviceType = self.Base_main.classes.device_type
        self.Order = self.Base_main.classes.order
        self.Shop = self.Base_main.classes.shop
        self.WarehousePosition = self.Base_main.classes.warehouse_position
        self.Image = self.Base_main.classes.image
        self.DeviceRating = self.Base_main.classes.device_rating

