# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import base64
import gzip

try:
    import simplejson as json
except ImportError as _:
    import json
import urllib

from flask import request, current_app
import sys

sys.path.append("./")
sys.setrecursionlimit(10000000)


def get_post_datas():
    """获取上报数据，若获取为data，则拼装成数组；若原始为data_list,则直接返回
        单条上报的时候是data, 批量上报是data_list
        get方式我只遇到过data, post方式两种都有
        但是data_list和data在一个请求里不会同时出现
        获取参数信息，JSON 》 FORM 》 ARGS的顺序
    :return:
    """
    request_data = request.args.get('data')
    gzip_flag = request.args.get('gzip', 0)
    request_datas = None

    if request.method == 'POST' and hasattr(request, 'form'):
        request_data = request.form.get('data')
        request_datas = request.form.get('data_list')
        if not gzip_flag:
            gzip_flag = request.form.get('gzip', 0)

    # 兼容content-type为application/json，但是数据内容为datas=xxx&crc=xxx，避免报错，抛出bad request
    json_data = None
    err_msg = None
    try:
        if hasattr(request, 'json'):
            json_data = request.json
    except Exception as e:
        err_msg = f'解析json格式错误， content_type: application/json，但是获取json异常， 错误为{e}'

    if json_data:
        if hasattr(json_data, 'get'):
            request_data = json_data.get('data')
            request_datas = json_data.get('data_list')
            if not gzip_flag:
                gzip_flag = json_data.get('gzip', 0)
        elif json_data.startswith('data_list='):
            current_app.logger.debug(f'请求原始内容为{json_data}')
            request_datas = json_data[10:]
        else:
            current_app.logger.error(f'json内容类型错误，json值为: {json_data}')

    # 处理信标
    if 'text/plain' in request.headers.get('CONTENT-TYPE', ''):
        play_load = request.data
        play_load_str = play_load.decode('utf-8')
        params = dict(urllib.parse.parse_qsl(play_load_str))
        request_data = params.get('data')
        request_datas = params.get('data_list')
        err_msg = None

        if not gzip_flag:
            gzip_flag = params.get('gzip', 0)

    # 处理异常数据，content_type: application/json，但是数据内容为datas=xxx&crc=xxx
    if not request_data and not request_datas:
        play_load = request.data
        play_load_str = play_load.decode('utf-8')
        params = dict(urllib.parse.parse_qsl(play_load_str))
        request_data = params.get('data')
        request_datas = params.get('datas') or params.get('data_list')
        err_msg = None

    if err_msg:
        current_app.logger.error(err_msg)
        err_msg = None

    request_source_data = request_data if request_data else request_datas
    current_app.logger.debug(f'请求数据为{request_source_data}')

    request_target_data = None
    if request_source_data:
        de64 = None
        try:
            de64 = base64.b64decode(urllib.parse.unquote(request_source_data).encode('utf-8'))
            # request_target_data = json.loads(gzip.decompress(de64))
            if gzip_flag:
                de64 = gzip.decompress(de64)
            request_target_data = json.loads(de64)
        except Exception as e:
            current_app.logger.debug(f'请求参数为{request.url}, args: {request.args}, [form: {request.form}], body: {request.data}, json: {request.json}')
            current_app.logger.error(f'解码失败，原始数据为{request_source_data}, 使用base64.b64decode解码失败，开始异常为：{e}')
            current_app.logger.error(f'解码失败，原始数据为{de64}, 使用json.loads(de64)解码失败，开始异常为：{e}')
            try:
                request_target_data = json.loads(gzip.decompress(de64))
            except Exception as e:
                current_app.logger.error(f'第二次尝试解码失败，原始数据为{de64}, 使用json.loads(gzip.decompress(de64))解码失败，开始异常为：{e}')
                raise e
    else:
        request_body = None
        request_json = None
        if hasattr(request, 'body'):
            request_body = request.body
        if hasattr(request, 'json'):
            request_json = request.json
        current_app.logger.error(f'待解码数据为None，原始请求为{request}, args: [{request.args}], form: [{request.form}], body: [{request_body}], json: [{request_json}]')
        raise Exception(f'待解码数据为None，请检查原始数据解析功能，修复此问题')

    # 结果封装成列表
    datas = []
    if request_data:
        datas = [request_target_data]
    elif request_target_data:
        datas = request_target_data
    return datas


def get_url_params(param):
    # 获取参数信息，JSON 》 FORM 》 ARGS的顺序
    v = request.args.get(param)
    if request.method == 'POST' and hasattr(request, 'form'):
        v = request.form.get(param)

    if hasattr(request, 'json'):
        json_data = request.json
        v = json_data.get(param)

    return v


def get_ip():
    if request.headers.get('X-Forwarded-For') is None:
        ip = request.remote_addr  # 服务器直接暴露
    else:
        ip = request.headers.get('X-Forwarded-For')  # 获取SLB真实地址
    return ip
