import json
import requests
import pytest



test_data = [(requests.get('https://regions-test.2gis.com/1.0/regions'), 200),
             (requests.post('https://regions-test.2gis.com/1.0/regions'), 405),
             (requests.put('https://regions-test.2gis.com/1.0/regions'), 405),
             (requests.delete('https://regions-test.2gis.com/1.0/regions'), 405)]

@pytest.mark.parametrize("operation, response_status", test_data)
def test_using_crud_operation(operation, response_status):
    response = operation
    assert response.status_code == response_status, f'Код ответа {response.status_code}'


@pytest.mark.parametrize("protocol", ['http', 'https'])
def test_using_invalid_valid_protocol(protocol):
    response = requests.get(f'{protocol}://regions-test.2gis.com/1.0/regions')
    if protocol == 'http':
        assert response.status_code != 200, 'Недействительный протокол'
    else:
        assert response.status_code == 200, 'Код ответа != 200 '


def test_to_define_content_type():
    response = requests.get('https://regions-test.2gis.com/1.0/regions')
    assert response.headers['Content-Type'] == 'application/json; charset=utf-8', 'Недопустимый MIME тип'


def test_count_total_value():
    response = requests.get('https://regions-test.2gis.com/1.0/regions')
    body = json.loads(response.text)
    assert body['total'] == 22


def test_q_param_reset_other():
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'q': 'Новосибирск', 'country_code': 'kz',
                                    'page': '3', 'page_size': '4'})
    body = json.loads(response.text)
    assert body['items'][0]['name'] == 'Новосибирск' and len(body['items']) == 1, "Параметр 'q' не игнорирует остальные"


@pytest.mark.parametrize('q_param', ['новосибирск', 'НОВОСИБИРСК', 'НоВоСиБиРсК'])
def test_using_q_param_with_different_reg(q_param):
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'q': {q_param}})
    body = json.loads(response.text)
    assert body['items'][0]['name'] == 'Новосибирск', "Параметр 'q' регистрозависим"


@pytest.mark.parametrize('q_param', ['но', 'нов', 'ново'])
def test_sub_str_search(q_param):
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'q': {q_param}})
    body = json.loads(response.text)
    try:
        assert len(body['items']) >= 1
    except KeyError:
        assert body['error']['message'] == "Параметр 'q' должен быть не менее 3 символов"

@pytest.mark.parametrize('code', ['ru', 'kz', 'kg', 'cz'])
def test_verify_code_country_param(code):
    code_count = []
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'country_code': {code}, 'page_size': 15})
    body = json.loads(response.text)
    for item in body['items']:
        code_count.append(item['country']['code'])
    assert len(set(code_count)) == 1 , f"Значение кода страны более одного:{code_count}"


@pytest.mark.parametrize('code', ['us', 'fr', 'gb', 'ua', 1234, 'фр#145^:Hk'])
def test_verify_code_country_negative_value(code):
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'country_code': {code}})
    body = json.loads(response.text)
    try:
       assert body['error']['message'] == "Параметр 'country_code' может быть одним из следующих значений:" \
                                           " ru, kg, kz, cz"
    except KeyError:
        assert len(body['items']) == 0 , f"{code} Недопустимое значение"


def test_available_all_country():
    country_count = []
    response1 = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'page_size': '15'})
    body1 = json.loads(response1.text)
    response2 = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'page': '2', 'page_size': '15'})
    body2 = json.loads(response2.text)
    for item1 in body1['items']:
        country_count.append(item1['country']['code'])
    for item2 in body2['items']:
        country_count.append(item2['country']['code'])
    assert len(set(country_count)) == 5, "Отображаются не все страны"


@pytest.mark.parametrize("page_param", [0, 1, 2, 45, 1.5, "фр#145^:Hk"])
def test_verify_page_num(page_param):
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'page': page_param})
    assert response.status_code == 200, 'Недопустимый код ответа'
    body = json.loads(response.text)
    try:
        assert len(body['items']) >= 0
    except KeyError:
        assert body['error']['message'] == "Параметр 'page' длжен быть целым числом"


def test_verify_default_value_page():
    count1 = []
    count2 = []
    response1 = requests.get('https://regions-test.2gis.com/1.0/regions')
    body1 = json.loads(response1.text)
    response2 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '1'})
    body2 = json.loads(response2.text)
    def count_name(count,body):
        for item in body['items']:
            count.append(item['name'])
    count_name(count1, body1)
    count_name(count2, body2)
    assert count1 == count2, "Значение параметра 'page' по умолчанию не 1"


@pytest.mark.parametrize("page_size_param", [4, 5, 6, 9 ,10, 11, 14, 15, 16, "фр#145^:Hk"])
def test_verify_page_size_param(page_size_param):
    response = requests.get('https://regions-test.2gis.com/1.0/regions',
                            params={'page_size': page_size_param})
    body = json.loads(response.text)
    try:
        assert len(body['items']) == page_size_param
    except KeyError:
        assert body['error']['message'] == "Параметр 'page_size' может быть одним из следующих значений: 5, 10, 15"\
               or "Параметр 'page_size' длжен быть целым числом"


def test_verify_element_one_page_default_value():
    response = requests.get('https://regions-test.2gis.com/1.0/regions')
    body = json.loads(response.text)
    assert len(body['items']) == 15, 'Количество элементов на одной странице по умолчанию не 15'


def test_compare_sum_elements_all_pages_with_page_size_param_15():
    count = []
    response1 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '1', 'page_size': '15'})
    body1 = json.loads(response1.text)
    response2 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '2', 'page_size': '15'})
    body2 = json.loads(response2.text)
    def sort_id(body):
        for item in body['items']:
            count.append(item['id'])
    sort_id(body1)
    sort_id(body2)
    assert len(set(count)) == 22, f"{count}"


def test_compare_sum_elements_all_pages_with_page_size_param_10():
    count = []
    response1 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '1', 'page_size': '10'})
    body1 = json.loads(response1.text)
    response2 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '2', 'page_size': '10'})
    body2 = json.loads(response2.text)
    response3 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '3', 'page_size': '10'})
    body3 = json.loads(response3.text)
    def sort_id(body):
        for item in body['items']:
            count.append(item['id'])
    sort_id(body1)
    sort_id(body2)
    sort_id(body3)
    assert len(count) == 22, f"{count}"


def test_test_compare_sum_elements_all_pages_with_page_size_param_5():
    count = []
    response1 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '1', 'page_size': '5'})
    body1 = json.loads(response1.text)
    response2 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '2', 'page_size': '5'})
    body2 = json.loads(response2.text)
    response3 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '3', 'page_size': '5'})
    body3 = json.loads(response3.text)
    response4 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '4', 'page_size': '5'})
    body4 = json.loads(response4.text)
    response5 = requests.get('https://regions-test.2gis.com/1.0/regions',
                             params={'page': '5', 'page_size': '5'})
    body5 = json.loads(response5.text)
    def sort_id(body):
        for item in body['items']:
            count.append(item['id'])
    sort_id(body1)
    sort_id(body2)
    sort_id(body3)
    sort_id(body4)
    sort_id(body5)
    assert len(count) == 22, f"{count}"
