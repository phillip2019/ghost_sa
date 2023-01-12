# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    鬼策埋点上报模块.
"""

from flask import Blueprint, Response, jsonify

from app.configs.code import ResponseCode
from app.flaskr.sa.bu import get_data
from app.utils.response import res

sa_bp = Blueprint('sa', __name__)


@sa_bp.route('/sa.gif', methods=('GET', 'POST'))
@sa_bp.route('/sa', methods=('GET', 'POST'))
@sa_bp.route('/ghost/sa.gif', methods=('GET', 'POST'))
@sa_bp.route('/ghost/sa', methods=('GET', 'POST'))
def register():
    return get_data()


@sa_bp.route('/favicon.ico')
@sa_bp.route('/')
def index():
    return res(ResponseCode.SUCCEED)


@sa_bp.route('/config/visualized/Web.conf')
@sa_bp.route('/ghost/config/visualized/Web.conf')
def visual_web():
    mime_type = 'application/javascript'
    content = '''saJSSDKVtrackCollectConfig(
205, {
    event: {
        unlimited_div: true
    }
});'''
    return Response(content, mimetype=mime_type)


@sa_bp.route('/config/Android.conf')
@sa_bp.route('/ghost/config/Android.conf')
def visual_android_web():
    content = {"v": "v3", "configs": {"disableSDK": False, "disableDebugMode": False}}
    return jsonify(content)


@sa_bp.route('/config/iOS.conf')
@sa_bp.route('/ghost/config/iOS.conf')
def visual_ios_web():
    content = {"v": "v2", "configs": {"disableSDK": False, "disableDebugMode": False}}
    return jsonify(content)
