from sqlalchemy.orm import sessionmaker
import subprocess

from config import engine, database_url


def backup():
    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Имя файла для резервной копии
    backup_file = "backup.sql"

    # Команда для создания резервной копии с использованием pg_dump
    pg_dump_command = f"pg_dump {database_url} > {backup_file}"

    try:
        # Выполнение команды
        subprocess.run(pg_dump_command, shell=True, check=True)
        print(f"Резервная копия создана успешно в файле: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании резервной копии: {e}")
