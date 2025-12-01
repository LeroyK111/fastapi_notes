
# 协议转发工具


文档地址 https://deepsight.feishu.cn/docx/HCrsdMETToLFZbxNPc7cQWppnAd?302from=wiki
mqtt服务地址：172.29.10.42:21883

```sh
conda create -n secondaryAgency python=3.13
conda activate secondaryAgency
conda deactivate

pip freeze > requirements.txt
pip install -r requirements.txt

```
部署的时候记得删除.env

```sh
python3 ./src/main.py

# 使用框架自带工具，会导致env失效
fastapi dev ./src/main.py  --reload  --host 172.29.10.42  --port 11111
fastapi run ./src/main.py  --workers 4 --host 172.29.10.42  --port 9111
```


## 对接 AIMaster http转mqtt

usage
```
# 初始订阅地址，确保收发分离
AIMASTER_SUBSCRIBETOPIC=aimaster_send
# 初始发送地址，确保收发分离
AIMASTER_PUBLISHTOPIC=aimaster_recv

aimaster_send：
{
  "url": "http://172.29.10.42:11883/api/v1/http",
  "method": "POST",
  "data": {
    "a": "2"
  }
}


aimaster_recv:
{
  "source": {
  "url": "http://172.29.10.42:11883/api/v1/http",
  "method": "POST",
  "data": {"a": "2"}
  },
  "data": {
    "message": "测试接收",
    "data": {"a": "2"}
  }
}
```



```

SOLUTION_FLOW_INFORMATION_URl = os.getenv('SOLUTION_FLOW_INFORMATION_URl')
SOLUTION_SEND_TO = os.getenv('SOLUTION_SEND_TO')
VISION_BUILDER_TEMP_DETAIL_URL = os.getenv('VISION_BUILDER_TEMP_DETAIL_URL')

SOLUTION_FLOW_INFORMATION_URl = 'http://172.29.10.42:8856/test/solution'
SOLUTION_SEND_TO = 'http://172.29.10.42:8856/test/solution_infer'
SPOT_CHECK_SEND_TO = SOLUTION_SEND_TO
SORTING_SEND_TO = SOLUTION_SEND_TO
VISION_BUILDER_TEMP_DETAIL_URL = 'http://192.168.77.158:9905'

调用的第一个接口
response = requests.post(url=SOLUTION_FLOW_INFORMATION_URl, json=params, timeout=20).content.decode()

第二个接口
response = json.loads(requests.post(url=SPOT_CHECK_SEND_TO, json=msg, timeout=(10, 60)).content.decode())
 
第三个接口
response = json.loads(requests.post(url=SORTING_SEND_TO, json=msg, timeout=(30, 300)).content.decode())

第四个接口
response = requests.post(url=VISION_BUILDER_TEMP_DETAIL_URL, json=param)

第五个接口
response = requests.post(url=VISION_BUILDER_TEMP_DETAIL_URL, json=param)

第六个接口
response = requests.post(url=VISION_BUILDER_TEMP_DETAIL_URL, json=param)

```
