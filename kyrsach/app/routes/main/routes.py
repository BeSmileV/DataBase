from app.app import *
from ORM.service.service import *

serv = Services()

global death_message


@app.route('/death_window')
def call_death_window():
    return death_message


# ==================================== Авторизация ====================================
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return f'вы уже вошли, ваш id = {current_user.id}'

    if request.method == 'POST':
        login_ = request.form.get('username')
        password_ = request.form.get('password')
        user_id = serv.service_check_user_login(login_)

        if user_id and serv.service_check_user_password(user_id, password_):
            login_user(User(user_id))
            return redirect(url_for('call_main'))
    return render_template('login/login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return f'Dashboard for User {current_user.id}'


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('call_main'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fsc_ = request.form.get('fsc')
        login_ = request.form.get('login')
        password_ = request.form.get('password')
        role_id_ = request.form.get('role_id')
        shop_id_ = request.form.get('shop_id')
        if role_id_ == 'None':
            role_id_ = None

        if shop_id_ == 'None':
            shop_id_ = None

        is_success = serv.service_register_user(
            fsc_,
            login_,
            password_,
            role_id_,
            shop_id_
        )

        if is_success:
            user_id = serv.service_check_user_login(login_)

            if user_id and serv.service_check_user_password(user_id, password_):
                login_user(User(user_id))
                return redirect(url_for('call_main'))
        else:
            return 'шо-то не так'

    roles = serv.service_get_roles()
    stores = serv.service_get_shops()

    return render_template('register/register.html',
                           roles=roles,
                           stores=stores)


# ==================================== Главная страница ====================================
@app.route('/')
def call_main():
    isLogin = current_user.is_authenticated

    data_list_of_devices = serv.service_get_devices()
    return render_template('main.html',
                           data_list_of_devices=data_list_of_devices,
                           isLogin=isLogin)


# ==================================== Девайсы ====================================
@app.route('/device', methods=['GET', 'POST'])
def call_device(device_id=None):
    isLogin = current_user.is_authenticated
    device_id = device_id or request.form.get('deviceId')
    comments_data = serv.service_get_device_comments(device_id)
    shops_data = serv.service_get_shops_of_this_device(device_id)
    device = serv.service_get_inf_about_device(device_id)

    return render_template('device.html',
                           device_id=device[0],
                           device_name=device[1],
                           device_type=device[2],
                           device_description=device[3],
                           device_img=device[4],
                           comments_data=comments_data,
                           shops_data=shops_data,
                           isLogin=isLogin)


@app.route('/buy_device', methods=['POST'])
def call_buy_device():
    if current_user.is_authenticated:
        shop_id_price_device_id = request.form.get('shop_id_price_device_id')
        if shop_id_price_device_id is not None:
            shop_id_price_device_id = shop_id_price_device_id.split('|')
            shop_id = shop_id_price_device_id[0]
            price = shop_id_price_device_id[1]
            device_id = shop_id_price_device_id[2]
            user_id = current_user.id
            serv.service_buy_device(device_id, shop_id, price, user_id)
            return redirect(url_for('call_profile'))

    global death_message
    death_message = 'Не получилось произвести покупку.'
    return redirect(url_for('call_death_window'))


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    device_id = request.form.get('deviceId')
    rating = request.form.get('rating')
    comment = request.form.get('commentText')
    serv.service_device_rating(device_id, rating, comment, current_user.id)
    return call_device(device_id=device_id)


# ==================================== Магазины ====================================
@app.route('/shops')
def call_shops():
    isLogin = current_user.is_authenticated
    shops_data = serv.service_get_inf_about_shops()
    return render_template('shops.html',
                           shops_data=shops_data,
                           isLogin=isLogin)


# ==================================== Специальные действия ====================================
@app.route('/special_actions')
def call_special_actions():
    if current_user.is_authenticated:
        if serv.service_is_seller(current_user.id):
            return redirect(url_for('call_seller_workbench'))
        elif serv.service_is_admin(current_user.id):
            return redirect(url_for('call_admin_workbench'))

    global death_message
    death_message = 'Пока здесь для вас ничего нет.'
    return redirect(url_for('call_death_window'))


# ==================================== Верстак для магазина ====================================
@app.route('/seller_workbench')
def call_seller_workbench():
    isLogin = current_user.is_authenticated
    if serv.service_is_seller(current_user.id):
        shop_id = serv.service_get_shop_id_by_user_id(current_user.id)
        if shop_id is not None:
            warehouse_data = serv.service_get_warehouse_positions(shop_id)
            orders_data = serv.service_get_shops_orders(shop_id)
            return render_template('seller_workbench.html',
                                   shop_id=shop_id,
                                   warehouse_data=warehouse_data,
                                   isLogin=isLogin,
                                   orders_data=orders_data)
    return redirect(url_for('call_main'))


@app.route('/edit_warehouse', methods=['POST'])
def call_edit_warehouse():
    edited_id = request.form.get('id')
    edited_price = request.form.get('price')
    edited_count = request.form.get('count')

    device_id_shop_id = serv.service_get_warehouse_pos_by_id(edited_id)
    serv.service_set_devices_in_warehouse(device_id_shop_id[0],
                                          device_id_shop_id[1],
                                          edited_count,
                                          edited_price)
    return redirect(url_for('call_seller_workbench'))


@app.route('/add_warehouse', methods=['POST'])
def call_add_warehouse():
    add_shop_id = request.form.get('add_shop_id')
    add_count = request.form.get('add_count')
    add_price = request.form.get('add_price')
    add_name = request.form.get('add_name')
    # print(add_shop_id)
    serv.service_add_warehouse_pos(add_name,
                                   add_price,
                                   add_count,
                                   add_shop_id)
    return redirect(url_for('call_seller_workbench'))


@app.route('/send_order', methods=['POST'])
def send_order():
    order_id = request.form.get('order_id')

    if not serv.service_send_device(order_id):
        global death_message
        death_message = 'Не получилось отправить заказ.'
        return redirect(url_for('call_death_window'))

    return redirect(url_for('call_seller_workbench'))


# ==================================== Верстак для админа ====================================
@app.route('/admin_workbench')
def call_admin_workbench():
    isLogin = current_user.is_authenticated
    if serv.service_is_admin(current_user.id):
        shops_data = serv.service_get_shops_for_admin_workbench()
        devices_data = serv.service_get_devices_for_admin_workbench()
        roles_data = serv.service_get_roles()
        return render_template('admin_workbench.html',
                               isLogin=isLogin,
                               shops_data=shops_data,
                               devices_data=devices_data,
                               roles_data=roles_data)
    return redirect(url_for('call_main'))


@app.route('/edit_shop', methods=['POST'])
def edit_shop():
    edited_shop_id = request.form.get('edited_shop_id')
    edited_shop_name = request.form.get('edited_shop_name')
    edited_shop_place = request.form.get('edited_shop_place')
    serv.service_set_shop(edited_shop_id, edited_shop_name, edited_shop_place)
    return redirect(url_for('call_admin_workbench'))


@app.route('/create_shop', methods=['POST'])
def create_shop():
    new_shop_name = request.form.get('new_shop_name')
    new_shop_place = request.form.get('new_shop_place')
    serv.service_add_shop(new_shop_name, new_shop_place)
    return redirect(url_for('call_admin_workbench'))


@app.route('/edit_device', methods=['POST'])
def edit_device():
    edited_device_name = request.form.get('edited_device_name')
    edited_device_type = request.form.get('edited_device_type')
    edited_device_description = request.form.get('edited_device_description')
    image_data = request.files['edited_device_image']
    edited_device_id = request.form.get('edited_device_id')

    edited_device_type_id = serv.service_add_device_type(edited_device_type)

    edited_device_image_id = None
    if image_data:
        path = 'data/' + image_data.filename
        image_data.save(path)

        edited_device_image_id = serv.service_add_image(path)
    print(edited_device_name, edited_device_type_id, edited_device_description, edited_device_image_id)
    serv.service_set_device(edited_device_id, edited_device_name, edited_device_type_id, edited_device_description,
                            edited_device_image_id)
    return redirect(url_for('call_admin_workbench'))


@app.route('/create_device', methods=['POST'])
def create_device():
    new_device_name = request.form.get('new_device_name')
    new_device_device_type = request.form.get('new_device_device_type')
    new_device_description = request.form.get('new_device_description')
    image_data = request.files['new_device_image']
    new_device_device_id = serv.service_add_device_type(new_device_device_type)

    new_device_image_id = None
    if image_data:
        path = 'data/' + image_data.filename
        image_data.save(path)

        new_device_image_id = serv.service_add_image(path)

    serv.service_add_device(new_device_name, new_device_device_id, new_device_description, new_device_image_id)
    return redirect(url_for('call_admin_workbench'))


@app.route('/delete_shop', methods=['POST'])
def delete_shop():
    shop_id = request.form.get('shop_id')
    serv.service_delete_shop_for_admin_workbench(shop_id)
    return redirect(url_for('call_admin_workbench'))


@app.route('/delete_device', methods=['POST'])
def delete_device():
    device_id = request.form.get('device_id')
    serv.service_delete_device_for_admin_workbench(device_id)
    return redirect(url_for('call_admin_workbench'))


@app.route('/delete_role', methods=['POST'])
def delete_role():
    role_id = request.form.get('role_id')
    serv.service_delete_role(role_id)
    return redirect(url_for('call_admin_workbench'))


@app.route('/add_role', methods=['POST'])
def add_role():
    role_name = request.form.get('role_name')
    serv.service_add_role(role_name)
    return redirect(url_for('call_admin_workbench'))


@app.route('/get_selection', methods=['POST'])
def get_selection():
    print('yes')
    choose_option_file_type = request.form.get('chooseOptionFileType')
    choose_option_class = request.form.get('chooseOptionClass')
    file_name = None
    data_base_class = None
    if choose_option_class == '0':
        data_base_class = serv.data_base.Users
        file_name = 'user_table'
    elif choose_option_class == '1':
        data_base_class = serv.data_base.Role
        file_name = 'role_table'
    elif choose_option_class == '2':
        data_base_class = serv.data_base.Device
        file_name = 'device_table'
    elif choose_option_class == '3':
        data_base_class = serv.data_base.DeviceType
        file_name = 'device_type_table'
    elif choose_option_class == '4':
        data_base_class = serv.data_base.Order
        file_name = 'order_table'
    elif choose_option_class == '5':
        data_base_class = serv.data_base.Shop
        file_name = 'shop_table'
    elif choose_option_class == '6':
        data_base_class = serv.data_base.Image
        file_name = 'image_table'
    elif choose_option_class == '7':
        data_base_class = serv.data_base.DeviceRating
        file_name = 'device_rating_table'

    print(file_name)
    print(choose_option_file_type)
    if choose_option_file_type == '0':
        serv.table_to_json(data_base_class, file_name)
    elif choose_option_file_type == '1':
        serv.table_to_xlsx(data_base_class, file_name)

    return redirect(url_for('call_admin_workbench'))


@app.route('/do_backup', methods=['POST'])
def do_backup():
    serv.service_backup()
    return redirect(url_for('call_admin_workbench'))


# ==================================== Профиль ====================================
@app.route('/profile')
def call_profile():
    isLogin = current_user.is_authenticated
    print(isLogin)
    if isLogin:
        user_data = serv.service_get_user(current_user.id)
        orders_data = serv.service_get_user_orders(current_user.id)
        return render_template('profile.html',
                               isLogin=isLogin,
                               user_data=user_data,
                               orders_data=orders_data)
    return redirect(url_for('login'))


@app.route('/add_place', methods=['POST'])
def add_place():
    new_place = request.form.get('new_place')
    serv.service_set_user_place(current_user.id, new_place)
    return redirect(url_for('call_profile'))
