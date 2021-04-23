#### Для старта в командной строке: locust -f load_test.py --host=https://regions-test.2gis.com


from locust import HttpUser, task, between
import time


class UserBehavior(HttpUser):
    wait_time = between(1, 6)
    @task(4)
    def task1(self):
        self.client.get('/1.0/regions', params={'q': 'рск'})

    @task(2)
    def task2(self):
        self.client.get('/1.0/regions', params={'country_code': 'ru'})

    @task(1)
    def task3(self):
        self.client.get('/1.0/regions', params={'page_size': '15'})





