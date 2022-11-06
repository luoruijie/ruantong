"""
#参考URL https://www.codenong.com/cs109725238/
1.pip install celery  gunicorn
2.安装redis
  2.1 进入终端 redis-cli
  2.2 输入config set stop-writes-on-bgsave-error no
3.终端启动命令
    # 运行flask服务
    gunicorn entry_ner_cpu:app -b 0.0.0.0:5001
    # 使用celery执行异步任务
    celery -A entry_ner_cpu.celery_ worker
    # 使用flower监督异步任务
    flower --basic_auth=admin:admin --broker=redis://127.0.0.1:6379/0 --address=0.0.0.0 --port=5556

"""


from flask import Flask
from celery import Celery
from celery.result import AsyncResult
import time

app = Flask(__name__)
# 用以储存消息队列
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
# 用以储存处理结果


app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

celery_ = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery_.conf.update(app.config)


@celery_.task
def my_background_task(arg1, arg2):
     # 两数相加
     time.sleep(10)
     return arg1+arg2


@app.route("/sum/<arg1>/<arg2>")
def sum_(arg1, arg2):
    # 发送任务到celery,并返回任务ID,后续可以根据此任务ID获取任务结果
    result = my_background_task.delay(int(arg1), int(arg2))
    return result.id


@app.route("/get_result/<result_id>")
def get_result(result_id):
    # 根据任务ID获取任务结果
    result = AsyncResult(id=result_id)
    return str(result.get())


if __name__ == '__main__':
    app.run(debug=True,port= 8081)