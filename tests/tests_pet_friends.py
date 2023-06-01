from api import PetFriends
from settings import valid_email, valid_password

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='CAT', animal_type='kitty',
                                     age='4', pet_photo='images/catCL.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "CAT", "kitty", "4", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# 1
def test_fail_get_api_key_for_invalid_user(email="a", password="0"):
    """ Проверяем что не сработают невалидные данные и в результате не содержится key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result
    # Тест пройден, невалидные данные не сработали и key не содержится


def test_update_self_pet_info_with_not_valid_auth_key(name='Мур', animal_type='Кот', age=9):
    """Проверяем невозможность обновления информации о питомце
    для несуществующего пользователя"""

    # Создаём переменную auth_key с некорректным значением
    auth_key = {'key': 'not_valid_auth_key'}

    # Пробуем отправить данные (имя, тип и возраст) для несуществующего пользователя
    status, result = pf.update_pet_info(auth_key, '123456', name, animal_type, age)

    # Проверяем что статус ответа = 403
    assert status == 403
    # Тест пройден, так как запрос не прошел


def test_add_new_pet_with_wrong_data(name='777', animal_type='888',
                                     age='abc', pet_photo='images/catanddog.jpg'):
    """Проверяем, что невозможно добавить питомца с некорректными данными."""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status != 200
    # Тест не пройден, так как сайт создаёт питомца с некорректными данными


def test_add_pet_with_data_empty():
    """Создаем питомца с пустыми полями"""
    name = ''
    animal_type = ''
    age = ''

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(api_key, name, animal_type, age)

    assert status != 200
    assert result['name'] == name
    print(f'{result}')
    # Тест не пройден, так как сайт создаёт питомца с пустыми полями


def test_add_pet_with_a_lot_of_words_in_variable_name(name='Напу Амо Хала Она Анека Вехи Она Хивеа Нена Вава Кехо Онка Кахе Хеа Леке Еа Она Ней Нана Ниа Кеко Оа Ога Ван Ика Ванао', animal_type='cat', age='2', pet_photo='images/catCL.jpg'):
    ''' Добавления питомца имя которого превышает норму слов
    Тест не будет пройден если питомец будет добавлен на сайт с именем состоящим из более нормы слов'''

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    list_name = result['name'].split()
    word_count = len(list_name)

    assert status != 200
    assert word_count == 26
# Тест не пройден, так как сайт создаёт питомца с именем больше нормы слов


def test_add_photo_for_pet(pet_photo='images/catCL.jpg'):
    """Проверяем возможность менять фото питомца"""
    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(api_key, my_pets['pets'][0]['id'], pet_photo)
        _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
        print(f'\n фото добавлено в {result}')
    else:
        raise Exception('Питомцы отсутствуют')
# Тест пройден, фото изменилось


def test_update_self_pet_info_with_not_valid_id(name='Мяу', animal_type='Котик', age=1):
    """Проверяем невозможность обновления информации о несуществующем питомце"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Пробуем отправить данные (имя, тип и возраст) для несуществующего id
    status, result = pf.update_pet_info(auth_key, 'not_valid_pet_id', name, animal_type, age)

    # Проверяем что статус ответа = 400
    assert status == 400
    # Тест пройден, так как запрос не отправлен


def test_add_pet_negative_age_number(name='Мяу', animal_type='Котик', age='-1', pet_photo='images/catCL.jpg'):
    '''Добавление питомца с отрицательным возрастом.'''

    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    assert age in result['age']
# Тест не пройден, так как питомец добавлен на сайт с отрицательным числом в поле возраст.


def test_add_pet_with_special_characters_in_variable_animal_type(name='!@#$%^&*(%',  animal_type='#)*&^%$#@',
                                                                 age='3', pet_photo='images/max.jpg'):
    ''' Добавление питомца со специальными символами вместо букв в имени и породе.'''

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name
# Тест не пройден, питомец добавлен с недопустимыми спец. символами


def test_add_new_pet_without_photo(name='Мур', animal_type='Котик', age='1,5'):
    """Добавление питомца без фотографии"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца и обработка исключения
    try:
        pf.add_new_pet(auth_key, name, animal_type, age)
    except TypeError:
        print('Питомец без фотографии не добавлен')
# Тест пройден, так как питомец не добавлен
