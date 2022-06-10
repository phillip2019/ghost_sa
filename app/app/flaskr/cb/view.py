# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    鬼策埋点上报模块.
"""

from flask import Blueprint

from app.flaskr.cb.bu import get_data

cb_bp = Blueprint('cb', __name__)


@cb_bp.route('/ghost/api/cb/adv_track', methods=('GET', 'POST'))
@cb_bp.route('/api/cb/adv_track', methods=('GET', 'POST'))
def ad_track():
    return get_data()
