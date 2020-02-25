from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
import requests
import re
import sys

class RLClient:
    def __init__(self, username=None, password=None):
        self.cookies = RequestsCookieJar()
        if username and password:
            self.login(username, password)

    def _handle_request(self, method, url, headers=None, body=None):
        headers = headers if headers else { 'Host': 'retaillink.wal-mart.com' }
        body = body if body else {}

        try:
            method = method.upper()
            if method == 'GET':
                response = requests.get(url, headers=headers, cookies=self.cookies)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, cookies=self.cookies)
            else:
                raise Exception(f"method '{method}' not supported")
        except requests.exceptions.RequestException as e:
            raise(e)
        else:
            return response

    def login(self, username, password):
        url = 'https://retaillink.login.wal-mart.com/api/login'
        headers = {
            'Host': 'retaillink.login.wal-mart.com',
            'Origin': 'https://retaillink.login.wal-mart.com',
            'Referer': 'https://retaillink.login.wal-mart.com/login',
        }
        body = {
            'username': username,
            'password': password,
            'language': 'en'
        }

        response = self._handle_request('POST', url, headers, body)

        self.cookies = response.cookies
        return response.content

    def get_reports(self, folder_name):
        url = f"https://retaillink.wal-mart.com/Decision_support/mySavedReports.aspx?ApplicationId=300"
        response = self._handle_request('GET', url)
        soup = BeautifulSoup(response.content, 'html.parser')
        folder_link = soup.find('span', string=folder_name)
        folder_id = re.search(r'\(\'(\w+)\'\)', folder_link['onclick']).group(1)
        folder = soup.find(parentfolderid=str(folder_id))
        report_elements = folder.find_all('span', reportinfostring=True)

        # Standardize reports
        reports = []
        for element in report_elements:
            reports.append({
                'id': re.search(r'(\d+)', element['reportinfostring']).group(1),
                'title': element.contents[1].strip()
            })
        return reports

    def get_jobs(self, status='Done'):
        url = f"https://retaillink.wal-mart.com/Decision_support/status_get_data.aspx?ApplicationId=300"
        response = self._handle_request('GET', url)
        soup = BeautifulSoup(response.content, 'html.parser')
        job_elements = soup.find_all('td', string=status)

        # Standardize jobs
        jobs = []
        for element in job_elements:
            jobs.append({
                'id': element.previous_sibling.string.strip(),
                'title': element.next_sibling.string.strip(),
                'ext': {
                    'text': 'txt',
                    'excel': 'xls'
                }.get(element.next_sibling.next_sibling.next_sibling.next_sibling.string.strip().lower(), 'txt')
            })
        return jobs

    def submit_report(self, report_id):
        url = f"https://retaillink.wal-mart.com/Decision_support/submit_request.aspx?submitlater=true&requestid={report_id}&applicationid=300"
        response = self._handle_request('GET', url)
        return response.content

    def download_report(self, job_id):
        url = f"https://retaillink.wal-mart.com/rl_home_services/home/DownloadReport?jobid={job_id}"
        response = self._handle_request('GET', url)
        return response.content

    def mark_retrieved(self, job_id):
        url = f"https://retaillink.wal-mart.com/Decision_support/Status_retrieve_request.aspx?applicationid=300&JobId={job_id}&status=D&Extension=None&filename=None&reqname=None"
        response = self._handle_request('GET', url)
        return response
