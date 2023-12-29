import base64
import json
from turtle import pd
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import ORM.models as models
import ORM.config as config
import pandas as pd
import subprocess
from datetime import datetime

backup_file_path = "files/backup.sql"


class Services:
    def __init__(self):
        self.data_base = models.DataBase()

    def service_check_user_login(self, login):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        query = (
            select(self.data_base.Users.id)
            .filter(self.data_base.Users.login == f'{login}')
        )

        try:
            result = session.execute(query)
            rows = result.fetchall()

        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
            return None

        session.commit()
        session.close()
        if len(rows) == 0:
            return None
        else:
            return rows[0][0]

    def service_check_user_password(self, user_id, password):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        query = (
            select(self.data_base.Users.password)
            .filter(self.data_base.Users.id == f'{user_id}')
        )

        try:
            result = session.execute(query)
            rows = result.fetchall()
            rows = rows[0][0]

            if rows == password:
                answer = True
            else:
                answer = False

        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
            return False

        session.commit()
        session.close()
        return answer

    def service_get_shops(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        query = (
            select(self.data_base.Shop.id,
                   self.data_base.Shop.name)
        )

        try:
            result = session.execute(query)
            rows = result.fetchall()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
            return None

        session.commit()
        session.close()
        return rows

    def service_get_devices(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.Device.id,
                       self.data_base.Device.name,
                       self.data_base.Image.image)
                .join(self.data_base.Image)
            )
            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_device_comments(self, device_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.DeviceRating.rating,
                       self.data_base.DeviceRating.comment,
                       self.data_base.Users.fsc)
                .join(self.data_base.Users, self.data_base.Users.id == self.data_base.DeviceRating.user_id)
                .filter(self.data_base.DeviceRating.device_id == f'{device_id}')
            )

            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_shops_of_this_device(self, device_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.WarehousePosition.shop_id,
                       self.data_base.WarehousePosition.price,
                       self.data_base.WarehousePosition.count,
                       self.data_base.Shop.name,
                       self.data_base.Shop.place)
                .filter(self.data_base.WarehousePosition.device_id == f'{device_id}')
                .join(self.data_base.Shop)
            )

            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_inf_about_device(self, device_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.Device.id,
                       self.data_base.Device.name,
                       self.data_base.DeviceType.name,
                       self.data_base.Device.description,
                       self.data_base.Image.image)
                .join(self.data_base.DeviceType)
                .join(self.data_base.Image)
                .filter(self.data_base.Device.id == f'{device_id}')
            )

            res = session.execute(query).first()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_buy_device(self, device_id, shop_id, price, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            new_order = self.data_base.Order(device_id=device_id,
                                             price=price,
                                             date=datetime.now().date(),
                                             status=False,
                                             shop_id=shop_id,
                                             user_id=user_id
                                             )
            session.add(new_order)


        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
            return False
        session.commit()
        session.close()

        return True

    def service_device_rating(self, device_id, rating, comment, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            new_device_rating = self.data_base.DeviceRating(device_id=device_id,
                                                            rating=rating,
                                                            comment=comment,
                                                            user_id=user_id)

            session.add(new_device_rating)
            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def service_get_inf_about_shops(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.Shop.id,
                       self.data_base.Shop.name,
                       self.data_base.Shop.place
                       )
            )

            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_is_seller(self, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            user = session.query(self.data_base.Users).get(user_id)
            role_id = user.role_id
            role = session.query(self.data_base.Role).get(role_id)
            res = role.name
            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        if res == 'seller':
            return True
        else:
            return False

    def service_is_admin(self, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            user = session.query(self.data_base.Users).get(user_id)
            role_id = user.role_id
            role = session.query(self.data_base.Role).get(role_id)
            res = role.name
            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        if res == 'admin':
            return True
        else:
            return False

    def service_get_shop_id_by_user_id(self, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            user = session.query(self.data_base.Users).get(user_id)
            res = user.representative_shop_id

            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return None
        finally:
            session.close()

        return res

    def service_get_warehouse_positions(self, shop_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(self.data_base.WarehousePosition.id,
                       self.data_base.Device.name,
                       self.data_base.WarehousePosition.price,
                       self.data_base.WarehousePosition.count)
                .filter(self.data_base.WarehousePosition.shop_id == f'{shop_id}')
                .join(self.data_base.Device)
            )

            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_shops_orders(self, shop_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(
                    self.data_base.Order.id,
                    self.data_base.Device.name,
                    self.data_base.Order.price,
                    self.data_base.Order.date,
                    self.data_base.Order.status,
                    self.data_base.Users.fsc,
                    self.data_base.Users.place
                )
                .join(self.data_base.Device, self.data_base.Order.device_id == self.data_base.Device.id)
                .join(self.data_base.Shop, self.data_base.Order.shop_id == self.data_base.Shop.id)
                .join(self.data_base.Users, self.data_base.Order.user_id == self.data_base.Users.id)
                .filter(self.data_base.Order.shop_id == f'{shop_id}')
            )
            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_warehouse_pos_by_id(self, id_):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            warehouse_pos = session.query(self.data_base.WarehousePosition).get(id_)
            res = [warehouse_pos.device_id, warehouse_pos.shop_id]
            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return None
        finally:
            session.close()

        return res

    def service_set_devices_in_warehouse(self, device_id, shop_id, added_count, added_price):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            warehouse_pos = (
                session.query(self.data_base.WarehousePosition)
                .filter(self.data_base.WarehousePosition.device_id == f'{device_id}')
                .filter(self.data_base.WarehousePosition.shop_id == f'{shop_id}')
                .first()
            )

            if warehouse_pos:
                warehouse_pos.count += int(added_count)
                warehouse_pos.price += int(added_price)

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def service_get_user_orders(self, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        res = None
        try:
            query = (
                select(
                    self.data_base.Order.id,
                    self.data_base.Device.name,
                    self.data_base.Order.price,
                    self.data_base.Order.date,
                    self.data_base.Order.status,
                    self.data_base.Users.place,
                    self.data_base.Shop.name
                )
                .join(self.data_base.Device, self.data_base.Order.device_id == self.data_base.Device.id)
                .join(self.data_base.Shop, self.data_base.Order.shop_id == self.data_base.Shop.id)
                .join(self.data_base.Users, self.data_base.Order.user_id == self.data_base.Users.id)
                .filter(self.data_base.Order.user_id == f'{user_id}')
            )
            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_add_image(self, image_path):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            with open(image_path, 'rb') as file:
                image_data = file.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            new_image = self.data_base.Image(image=image_base64)
            session.add(new_image)
            session.commit()
            res = new_image.id
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_user(self, user_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            user = session.query(self.data_base.Users).get(user_id)
            shop_name = None
            if user.representative_shop_id is not None:
                shop_name = session.query(self.data_base.Shop).get(user.representative_shop_id).name

            res = [user.id, user.fsc, user.login,
                   user.password, user.role_id,
                   shop_name, user.place]

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

        return res

    def service_set_user_place(self, user_id, place):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            user = session.query(self.data_base.Users).get(user_id)
            user.place = place

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

        return res

    def service_get_roles(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            query = (
                select(self.data_base.Role.id,
                       self.data_base.Role.name)
                .filter(self.data_base.Role.name != 'admin')
                .filter(self.data_base.Role.name != 'creator')
            )
            res = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

        return res

    def service_add_role(self, name):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            query = (
                select(self.data_base.Role.name)
                .filter(self.data_base.Role.name == name)
            )

            if session.execute(query).first() is None:
                role = self.data_base.Role(name=name)
                session.add(role)

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

    def service_delete_role(self, id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            row_to_delete = session.query(self.data_base.Role).get(id)
            session.delete(row_to_delete)

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

    def service_add_warehouse_pos(self, device_name, price, count, shop_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            query = (
                select(self.data_base.Device.id)
                .filter(self.data_base.Device.name == f'{device_name}')
            )
            res = session.execute(query).fetchall()
            print(res)
            if len(res) != 0:
                device_id = res[0][0]

                query = (
                    select(self.data_base.WarehousePosition.id)
                    .filter(self.data_base.WarehousePosition.device_id == f'{device_id}')
                    .filter(self.data_base.WarehousePosition.shop_id == f'{shop_id}')
                )
                res = session.execute(query).fetchall()
                print(res)
                if len(res) == 0:
                    new_warehouse_pos = self.data_base.WarehousePosition(device_id=device_id,
                                                                         price=price,
                                                                         count=count,
                                                                         shop_id=shop_id)

                    session.add(new_warehouse_pos)
                    session.commit()
                else:
                    session.commit()
                    session.rollback()
            else:
                session.commit()
                session.rollback()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
            return None
        finally:
            session.close()

        return res

    def service_register_user(self, fsc_, login_, password_, role_id_, shop_id_):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            if role_id_ is None:
                query = (
                    select(self.data_base.Role.id)
                    .filter(self.data_base.Role.name == 'customer')
                )
                result = session.execute(query)
                rows = result.fetchall()

                role_id_ = rows[0][0]

            if shop_id_ is not None:
                query = (
                    select(self.data_base.Role.id)
                    .filter(self.data_base.Role.name == 'seller')
                )
                result = session.execute(query)
                rows = result.fetchall()

                role_id_ = rows[0][0]

            new_user = self.data_base.Users(
                fsc=fsc_,
                login=login_,
                password=password_,
                role_id=role_id_,
                representative_shop_id=shop_id_
            )

            session.add(new_user)
            session.commit()

        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                # Handle the unique violation error here
                print(f"User with login '{login_}' already exists.")
            else:
                # Handle other IntegrityError cases
                print(f"IntegrityError: {e}")
            return False
            session.rollback()

        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def service_send_device(self, order_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            order = session.query(self.data_base.Order).get(order_id)

            if order and not order.status:
                order.status = True
                warehouse_pos = (session.query(self.data_base.WarehousePosition)
                                 .filter(self.data_base.WarehousePosition.device_id == f'{order.device_id}',
                                         self.data_base.WarehousePosition.shop_id == f'{order.shop_id}')
                                 .first())

                if warehouse_pos.count > 0:
                    # Измените значение атрибута
                    warehouse_pos.count -= 1
                else:
                    session.commit()
                    session.rollback()
                    return False
            else:
                session.commit()
                session.rollback()
                return False

        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.commit()
            session.rollback()
            return False
        finally:
            session.commit()
            session.close()

        return True

    def service_get_devices_for_admin_workbench(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        try:
            query = select(
                self.data_base.Device.id,
                self.data_base.Device.name,
                self.data_base.Device.device_type_id,
                self.data_base.Device.description,
                self.data_base.Device.image_id
            )
            rows = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return []
        finally:
            session.close()

        return rows

    def service_get_shops_for_admin_workbench(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            query = select(
                self.data_base.Shop.id,
                self.data_base.Shop.name,
                self.data_base.Shop.place
            )
            rows = session.execute(query).fetchall()

            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return []
        finally:
            session.close()

        return rows

    def service_delete_for_admin_workbench(self, data_structures, id):
        Session = sessionmaker(bind=config.engine)
        session = Session()
        try:
            row_to_delete = session.query(data_structures).get(id)
            session.delete(row_to_delete)
            session.commit()
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def service_delete_device_for_admin_workbench(self, device_id):
        return self.service_delete_for_admin_workbench(self.data_base.Device, device_id)

    def service_delete_shop_for_admin_workbench(self, shop_id):
        return self.service_delete_for_admin_workbench(self.data_base.Shop, shop_id)

    def service_set_shop(self, shop_id, shop_name, shop_place):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            shop = session.query(self.data_base.Shop).get(shop_id)

            if shop_name is not None:
                shop.name = shop_name

            if shop_place is not None:
                shop.place = shop_place

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

    def service_add_shop(self, shop_name, shop_place):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            shop = self.data_base.Shop(name=shop_name,
                                       place=shop_place)

            session.add(shop)
            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

    def service_add_device_type(self, name):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            query = (select(self.data_base.DeviceType.id)
                     .filter(self.data_base.DeviceType.name == f'{name}'))
            device_id = session.execute(query).fetchall()

            if len(device_id):
                res = device_id[0][0]
                session.commit()
            else:
                device_type = self.data_base.DeviceType(name=name)

                session.add(device_type)
                session.commit()
                res = device_type.id

        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

        return res

    def service_add_device(self, device_name, device_type_id, description, image_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        try:
            query = (
                select(self.data_base.Device.id)
                .filter(self.data_base.Device.name == f'{device_name}')
            )
            res = session.execute(query).fetchall()

            if len(res) == 0:
                device = self.data_base.Device(name=device_name,
                                               device_type_id=device_type_id,
                                               description=description,
                                               image_id=image_id)

                session.add(device)
                session.commit()

            else:
                session.commit()
                session.rollback()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()

    def service_set_device(self, edited_device_id, new_device_name, new_device_type_id, new_device_description,
                           new_device_image_id):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        res = None

        try:
            device = session.query(self.data_base.Device).get(edited_device_id)
            device.name = new_device_name
            device.device_type_id = new_device_type_id
            device.description = new_device_description
            device.image_id = new_device_image_id

            session.commit()
        except Exception as e:
            print("-----------------Ошибка-----------------")
            print(e)
            print("----------------------------------------")
            session.rollback()
        finally:
            session.close()

        return res

    def convert_to_tuple(self, obj, data_base_class):
        if data_base_class == self.data_base.Users:
            return [obj.id, obj.fsc, obj.login, obj.password, obj.role_id, obj.representative_shop_id, obj.place]
        elif data_base_class == self.data_base.Role:
            return [obj.id, obj.name]
        elif data_base_class == self.data_base.Device:
            return [obj.id, obj.name, obj.name, obj.device_type_id, obj.description, obj.image_id]
        elif data_base_class == self.data_base.DeviceRating:
            return [obj.id, obj.device_id, obj.rating, obj.comment, obj.user_id]
        elif data_base_class == self.data_base.DeviceType:
            return [obj.id, obj.name]
        elif data_base_class == self.data_base.Shop:
            return [obj.id, obj.name, obj.place]
        elif data_base_class == self.data_base.Order:
            return [obj.id, obj.device_id, obj.price, obj.date, obj.status, obj.shop_id, obj.user_id]
        elif data_base_class == self.data_base.WarehousePosition:
            return [obj.id, obj.device_id, obj.price, obj.count, obj.shop_id]
        elif data_base_class == self.data_base.Image:
            return [obj.id, obj.image]

        return []

    def table_to_json(self, data_base_class, filename='output'):
        # Создаем сессию SQLAlchemy
        Session = sessionmaker(bind=config.engine)
        session = Session()

        result = session.query(data_base_class)
        data_list = [[]]

        for i in result:
            data_list += self.convert_to_tuple(i, data_base_class)

        json_data = json.dumps(data_list, indent=2)

        output_file = f'files/{filename}.json'
        session.close()
        with open(output_file, 'w+') as f:
            f.write(json_data)
        f.close()
        config.upload_on_Yandex(output_file, f'{filename}.json', 'table_json')

    def table_to_xlsx(self, data_base_class, filename='output'):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        result = session.query(data_base_class).all()
        data_list = []

        for i in result:
            data_list += [self.convert_to_tuple(i, data_base_class)]
        print(data_list)
        df = pd.DataFrame(data_list)

        output_file = f'files/{filename}.xlsx'
        df.to_excel(output_file, index=False)
        session.close()

        config.upload_on_Yandex(output_file, f'{filename}.xlsx', 'table_xlsx')

    def service_backup(self):
        Session = sessionmaker(bind=config.engine)
        session = Session()

        pg_dump_command = f"pg_dump {config.database_url} > {backup_file_path}"

        try:
            subprocess.run(pg_dump_command, shell=True, check=True)
            print(f"Резервная копия создана успешно в файле: {backup_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при создании резервной копии: {e}")
        finally:
            session.close()

        # Получение текущей даты и времени
        current_datetime = datetime.now()

        # Преобразование в строку
        current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H:%M:%S")
        config.upload_on_Yandex(backup_file_path, 'backup_' + current_datetime_str + '.sql', 'backup')
