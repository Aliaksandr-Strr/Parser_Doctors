import json
import math

import pandas
import requests


class Parser:

    def __init__(self):
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=16116'  # Камянск
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=873'# Била церква
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=20347'  # Одеса
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page='  # Одеса
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=23977'  # львов
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page='  # львов
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=18172' # Чернивци
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=' # Чернивци
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=18589' Харьков
        self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=' # Харьков
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=9232' # Rivne
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=10259' # Poltava
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=21525'  # Zaporogie
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page='  # Zaporogie
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=12106'  # Sumi
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=15752'  # Dnipro
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page='  # Dnipro
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page=1&settlementId=1'  # Kiiv
        # self.url = 'https://helsi.me/api/healthy/organizations?level=0&limit=30&page='  # Kiiv
        self.url_doctors = 'https://helsi.me/api/healthy/doctors?limit=11&organizationId='
        self.url_phone = 'https://helsi.me/api/healthy/doctors/'
        self.json = 'offices.json'
        self.fio = []

    def processing_data(self):
        for i in range(1, 5):
            result = requests.get(f"{self.url}{i}&settlementId=18589")
            all_data = result.json()['data']
            for data in all_data:
                id = data['id']
                hospital_specialization = data['specialization']
                if hospital_specialization == 'PrimaryCare':
                    hospital_specialization = 'Сімейні лікарі'
                elif hospital_specialization == 'Outpatient':
                    hospital_specialization = 'Вузькі спеціалісти'
                elif hospital_specialization == 'Undefined':
                    hospital_specialization = 'Приватна клініка'
                result = requests.get(f"{self.url_doctors}{id}&page=1")
                paging = result.json()['paging']
                pages = (math.ceil(paging['length'] / paging['limit']))
                for i in range(1, pages + 1):
                    # for i in range(1,2):
                    result = requests.get(f"{self.url_doctors}{id}&page={i}")
                    all_data = result.json()['data']
                    for data in all_data:
                        resourceId = data['resourceId']
                        phone_url = requests.get(f"{self.url_phone}{resourceId}")
                        try:
                            phone = phone_url.json()['contactPhones'][0]
                        except Exception:
                            phone = '-'
                        last_name = data['lastName']
                        first_name = data['firstName']
                        try:
                            middle_name = data['middleName']
                        except KeyError:
                            middle_name = '---'
                        doc = ''
                        try:
                            speciality = data['speciality']
                            for i in speciality:
                                doc += f" {i['doctorSpeciality']}"
                        except KeyError:
                            doc += '---'
                        organization = data['organization']['name']
                        addresses = data['organization']['addresses']['address']['addressText']
                        self.fio.append(
                            {'ФИО': f"{last_name} {first_name} {middle_name}",
                             'Специальность': doc,
                             'Организация': organization,
                             'Адрес': addresses,
                             'Тип': hospital_specialization,
                             'Телефон': phone
                             }
                        )
            #     print(self.fio)
        print(len(self.fio))
        df_master = None
        for info in self.fio:
            df = pandas.DataFrame(info, index=[0])
            if df_master is None:
                df_master = df
            else:
                df_master = pandas.concat([df_master, df])
        with pandas.ExcelWriter("Харьков.xlsx", engine="openpyxl", mode="w") as writer:
            df_master.to_excel(writer)


if __name__ == '__main__':
    p = Parser()
    p.processing_data()
