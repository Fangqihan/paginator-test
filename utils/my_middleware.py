from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse


class Md1(MiddlewareMixin):
    def process_request(self, reqeust):
        print('md1_process_request')
        return HttpResponse('<h1>你好</h1>')

    def process_response(self, requst, response):
        print('md1_process_response')
        return response  # 必须带返回值


class Md2(MiddlewareMixin):
    def process_request(self, request):
        print('md2_process_request')
        return 'asas'

    def process_response(self, request, response):
        print('md2_process_response')
        return response  # 必须带返回值
