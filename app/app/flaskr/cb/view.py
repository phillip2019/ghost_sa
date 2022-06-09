# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    鬼策埋点上报模块.
"""

from flask import Blueprint

from app.flaskr.cb.bu import get_data

cb_bp = Blueprint('cb', __name__)


@cb_bp.route('/adv_track', methods='GET')
def ad_track():
    return get_data()