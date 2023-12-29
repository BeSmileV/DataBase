from flask import render_template, request

from app.app import *
from ORM.service.service import *

serv = Services()


@app.route('/device', methods=['POST'])
def call_main():
    input_data = request.form.get('device_id')
    print(data_list_of_popular_devices)
    data_array = ["das", "dasd", "asdads"]
    return render_template('main/main.html', data_list_of_popular_devices=data_list_of_popular_devices,
                           data_array=data_array)
