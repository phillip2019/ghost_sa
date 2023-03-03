# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys

from flask import current_app

sys.path.append("./")
sys.setrecursionlimit(10000000)
from flask import _app_ctx_stack
from kafka import KafkaProducer, KafkaConsumer
import json
from app.configs import kafka
from app.configs import admin


class CreateKafkaProducer(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def create_producer(self, app):
        app.logger.info(f'创建kafka producer, bootstrap_server地址为{app.config["BOOTSTRAP_SERVERS"]}...')
        return KafkaProducer(bootstrap_servers=app.config['BOOTSTRAP_SERVERS'], compression_type='gzip')

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'kafka_producer'):
            # 超时50s关闭
            ctx.kafka_producer.close(timeout=50)
            current_app.logger.info('正常关闭kafka生产者实例...')

    @property
    def producer(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'kafka_producer'):
                ctx.kafka_producer = self.create_producer(current_app)
            return ctx.kafka_producer


def insert_message_to_kafka(msg, key=None):
    if isinstance(key, str):
        key = key.encode()
    kafka_topic = current_app.config['KAFKA_TOPIC']
    current_app.logger.debug(f'即将往broker={current_app.config["BOOTSTRAP_SERVERS"]}, topic={kafka_topic}发送消息...')
    # 初始化及重连kafka_producer，避免断开连接
    # TODO 验证如何重连机制not current_app.kafka_producer.bootstrap_connected()
    if not hasattr(current_app, 'kafka_producer') or not current_app.kafka_producer:
        current_app.kafka_producer = CreateKafkaProducer().create_producer(current_app)
    # TODO 将unicode编码格式数据，转换为中文编码
    msg_str = json.dumps(msg, ensure_ascii=False)
    future = current_app.kafka_producer.send(topic=kafka_topic, key=key, value=msg_str.encode('utf-8', 'ignore'))
    result = future.get(timeout=10)
    current_app.logger.debug(f'往topic={kafka_topic}发送消息完成, 结果为{result}')


def get_message_from_kafka():
    consumer=KafkaConsumer(kafka.kafka_topic, bootstrap_servers=kafka.bootstrap_servers, group_id=kafka.client_group_id,auto_offset_reset=kafka_offset_reset,client_id='get_message_from_kafka')
    return consumer


def get_message_from_kafka_independent_listener():
    consumer=KafkaConsumer(kafka.kafka_topic, bootstrap_servers=kafka.bootstrap_servers, group_id=admin.independent_listener_kafka_client_group_id,auto_offset_reset=kafka_offset_reset,client_id='get_message_from_kafka_independent_listener')
    return consumer


if __name__ == "__main__":
    insert_message_to_kafka(msg={'msg': 'test'}, key='123231231')
