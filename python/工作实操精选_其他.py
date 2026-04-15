"""airboard api template
这一部分是在定义一套通用的 Airboard 接口调用方式：
先根据 legal_entity_id 或 account_id 试探该对象属于 HK 还是 SG datacenter，
再把这个 datacenter 自动注入后续业务函数里，避免每个接口函数都手动判断一次。
核心目的是把“路由到正确机房”和“真正业务查询”拆开，提高复用性。
"""
def set_headers(datacenter, token):
    return {
        'Content-Type': 'application/json',
        'authorization': token,
        'x-data-center': datacenter,
    }

def search_datacenter(legal_entity_id=None, account_id=None, token=None):
    if not token:
        raise ValueError("token is required")
    token = token[7:] if token.startswith("Bearer ") else token
    headers = set_headers(datacenter='HK', token=token)  # reset to be default
    url = 'xxx'
    data = {
        'operationName': 'getLegalEntityList',
        'query': 'xxx',  # GraphQL 主要是一种 API 查询语言，它允许客户端通常在单个请求中精确地请求他们需要的数据。这种查询灵活性减少了对多个 SQL 查询的需求，从而优化了数据获取和处理。
        'variables': {
            'params': {
                'from': 0,
                'size': 10,
            }
        }
    }
    if account_id is None:
        data['variables']['params']['client_legal_entity_id'] = legal_entity_id
    else:
        data['variables']['params']['account_id'] = account_id
    r = requests.post(url=url, headers=headers, json=data)  # requests帮你做了 dumps (dict -> JSON字符串)
    r.raise_for_status()  # 如果 HTTP 状态码是 4xx/5xx，直接报错；否则继续。用于尽早发现请求失败。
    r = r.json()  # requests帮你做了 loads (JSON字符串 -> dict)
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    return r['data']['getLegalEntityList']['total']

def datacenter_decorator(func):
    def wrapper(*args, **kwargs):
        account_id = kwargs.get('account_id')
        legal_entity_id = kwargs.get('legal_entity_id')
        token = kwargs.get('token')
        datacenter = 'HK' if search_datacenter(account_id=account_id, legal_entity_id=legal_entity_id, token=token) > 0 else 'SG'
        kwargs['datacenter'] = datacenter
        return func(*args, **kwargs)
    return wrapper

@datacenter_decorator
def get_tm_case(datacenter, token, case_id, account_id=None, legal_entity_id=None):
    ...


"""token transfer涉及上传文件
这一部分是在做附件上传的完整流程：
先向业务接口申请一个可上传的临时链接和表单参数，
再让用户本地选择文件，按 MIME 类型做白名单过滤，
然后把文件真正传到对象存储，
最后保留上传结果。
它本质上是一个带简单 GUI 的“选择文件 → 校验类型 → 上传附件”的工具链。
"""
# token transfer涉及上传文件
import requests
from config import *
import json
import mimetypes
import tkinter
from tkinter.filedialog import *
import tkinter.messagebox as messagebox
from bs4 import BeautifulSoup

# 先拿上传凭证，再真正传文件。
def generate_upload_link(mimetype):
    url = 'https://xxxx'
    data = {
        'operationName': 'generateUploadLink',
        'query': "xxxx",
        'variables': {'mimeTypes': mimetype},
    }
    r = requests.post(url=url, json=data, headers=awx_headers)
    r.raise_for_status()
    r = r.json()  # 不管你files叫啥名，OSS(Object Storage Service)主要根据你form-data里的key字段来存放文件
    return r['data']['generateUploadLink']['data'][0]['endpoint'], r['data']['generateUploadLink']['data'][0]['form_data']

# 真正执行文件上传。
def aliyun_enable(url, form_data, file_name, mimetype):
    # global uploaded_attachments (global 不太建议常用,修改的是函数外面的变量, 阅读时不直观, 容易产生副作用)
    with open(file=file_name, mode='rb') as f:
        file = {'file': (file_name, f, mimetype)}
        r = requests.post(url=url, data=form_data, files=file)
        if r.status_code != 204:
            raise Exception(r.text)
    return form_data

# 文件选择 + 类型过滤 + 批量上传。
def select_upload_files(app):
    uploaded_attachments = []
    fl = askopenfilenames(filetypes=[('全部文件', '*.*')], initialdir='.', parent=app)
    accept_list = [
        'image/apng',
        'image/heic',
        'image/heic-sequence',
        'image/heif',
        'image/heif-sequence',
        'image/bmp',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/tiff',
        'image/tiff-fx',
        'image/webp',
        'application/pdf',
        'text/csv',
        'text/html',
        'application/msword',
        'application/vnd.ms-excel',
        'application/x-x509-ca-cert',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/zip',
        'application/x-zip-compressed',
        'video/webm',
    ]
    pass_dic = []
    for i in fl:
        mimetype, encoding = mimetypes.guess_type(i)
        if mimetype not in accept_list:
            print(i, mimetype, 'A non supported MimeType was provided')
            return
        else:
            print(i, mimetype, 'Passed')
            pass_dic.append({'fileName': i, 'mimeType': mimetype})
    if len(pass_dic) > 0:
        for file in pass_dic:
            print(file)
            end_url, form_data = generate_upload_link(mimetype=file['mimeType'])
            result = aliyun_enable(url=end_url, form_data=form_data, file_name=file['fileName'], mimetype=file['mimeType'])
            uploaded_attachments.append(result)

        print('>> All Completed ...')
        messagebox.showinfo(title='上传成功', message='所有文件均已上传成功！', parent=app)
    else:
        messagebox.showwarning(title='结束', message='没有文件被上传！', parent=app)
    app.destroy()
    return uploaded_attachments

# 给上传逻辑加一个简单 GUI 入口。
def trigger_attachment():
    mac = tkinter.Tk()
    mac.attributes('-topmost', True)
    mac.after(5000, lambda: mac.attributes('-topmost', False))  # 5秒后允许被其它窗口覆盖
    tkinter.Button(mac, command=lambda: select_upload_files(app=mac), text='select and upload files').pack()
    mac.geometry('1200x400')
    mac.mainloop()

# 根据附件ID回查附件详情。
def find_attachment(file_id):
    url = 'https://xxxd'
    data = {
        'operationName': 'getFileById',
        'query': "xxxx",
        'variables': {'fileId': file_id}
    }
    r = requests.post(url=url, json=data, headers=awx_headers)
    r.raise_for_status()
    r = r.json()
    return r


"""decode token
这一部分是在不校验签名的前提下直接解析 JWT token 的 payload，用来快速读取 token 里的过期时间、用户信息等字段，
主要适合本地辅助分析或调试，不适合做安全判断。
"""
import jwt
def decode_token(token):
    pload = jwt.decode(token, options={'verify_signature': False})
    return pload


"""读取html
这一部分是在读取本地 HTML 文件后，用 BeautifulSoup 解析 DOM，再提取 <body> 内部的内容，适合把客户提供的网页材料、导出的 HTML 报告或邮件正文进一步处理成可分析文本。
"""
with open(html_path, encoding='utf-8') as f:
    # 默认先只考虑一个html文件，如果内容很多就先合并进一个文件中
    html = f.read()
soup = BeautifulSoup(html, 'html.parser')
body_content = soup.body.decode_contents() if soup.body else ''


"""bug经验
在Python中，空字符串 '' 被认为在任何字符串中，所以
'' in 'A29AD2EBC5VQHK'   # 等于 True
这一点逻辑上类似于：找“空子串”总会在任何串的开始、结束等地方。
if needle and needle in haystack:
先确保 needle 不是空字符串，再判断包含关系。
"""


"""local runtime
这一部分是在说明如何通过 Docker 在本地拉起一个运行环境，并通过本地端口访问它，
适合需要模拟 notebook/runtime 服务或做隔离运行测试的场景，本质上是一个本地开发环境启动说明。
"""
```txt
download docker https://rancherdesktop.io/
open the docker in backend
open terminal
    docker run -p 127.0.0.1:9000:8080 asia-docker.pkg.dev/colab-images/public/runtime
    copy: http://127.0.0.1:9000/?token=xxx

import socket; print(socket.gethostname())
```


"""自动刷新token，并并入自定义公式中
这一部分是在把 token 生命周期管理抽象成一个 TokenManager：
先初始化 access/refresh token，解析过期时间，请求前自动检查是否快过期，必要时自动刷新，
再由业务函数统一取最新 headers 使用。
目的是让批量任务在长时间运行时不需要手工重新贴 token。
"""
class TokenManager:
    def __init__(self):
        self.refresh_token = None
        self.access_token = None
        self.access_bearer_token = None
        self.token_expired_at = 0.0

    def init_token(self):
        self.refresh_token = input('>> Input Latest Airboard-Refresh-Token: ')
        self.access_token = input('>> Input Latest Airboard-Access-Token: ')
        self.access_bearer_token = self.access_token if self.access_token.startswith('Bearer ') else f'Bearer {self.access_token}'
        self.access_token = self.access_token[7:] if self.access_token.startswith('Bearer ') else self.access_token  # 去掉"Bearer "前缀
        decoded_jwt = jwt.decode(self.access_token, algorithms=['HS256'], options={'verify_signature': False})
        self.token_expired_at = decoded_jwt['exp']
        return self

    def check_and_refresh_token(self):
        current_time = time.time()
        if current_time >= self.token_expired_at - 15 * 60:
            print(f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Token expires: {datetime.datetime.fromtimestamp(self.token_expired_at).strftime('%Y-%m-%d %H:%M:%S')}")
            print('Token expired, refreshing...')
            self.refresh_access_token()
        else:
            pass
            # print('Token still valid...')

    def refresh_access_token(self):
        data = {
            'refreshToken': self.refresh_token,
            'email': 'ben.chen@airwallex.com',
        }
        headers = {
            'Content-Type': 'application/json',
            'authorization': self.access_bearer_token,
            'x-data-center': 'HK',
        }
        url = 'https://xxxx/refresh'
        try:
            r = requests.post(url=url, json=data, headers=headers)
            r.raise_for_status()
            r = r.json()
            self.access_token = r['data']['token']
            self.refresh_token = r['data']['refreshToken']
            decoded_jwt = jwt.decode(self.access_token, algorithms=['HS256'], options={'verify_signature': False})
            self.token_expired_at = decoded_jwt['exp']
            self.access_bearer_token = f"Bearer {self.access_token}"

            update_info = {
                'access_token': self.access_token,
                'access_bearer_token': self.access_bearer_token,
                'refresh_token': self.refresh_token,
                'token_expired_at': self.token_expired_at,
            }
            print(update_info)
        except Exception as e:
            raise RuntimeError(f"Error refreshing token: {e}") from e

    def get_headers(self):
        """返回带有当前有效token的请求头"""
        return {
            'Content-Type': 'application/json',
            'authorization': self.access_bearer_token,
            'x-data-center': 'HK',
        }

class AccountFunctionClub:
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def global_account_info(self, row):
        self.token_manager.check_and_refresh_token()
        headers = self.token_manager.get_headers()
        gaid = row['gaid']
        dc = row['dc']
        url = f'https://airboard-ng.airwallex.com/api/v1/accountList/ga?createTimeRangeByDay%3D2016-01-01%2C2028-05-31%26vbaId%3D{gaid}%26pageSize%3D100'
        headers['x-data-center'] = 'SG' if dc.lower() == 'sg' else 'HK'
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        r = r.json()
        return r

token_manager = airboard_func.TokenManager()
abFuncs = airboard_func.AccountFunctionClub(token_manager=token_manager)
...
token_manager.init_token()
    for row in tqdm(df_combine, desc='retrieving ga info'):
        data_return = abFuncs.global_account_info(row=row)
        ...


"""希望动态基于scenario执行一套函数时
这一部分是在把不同场景的执行逻辑配置化：
通过 request_config 定义每个 request_id 对应的函数名、参数、datacenter 范围和表格输出信息，再用 getattr 动态拿到函数执行。
这样你以后新增场景时更多是在改配置，而不是重复改主流程代码。

ab_func.xxx 只能访问到在 ab_func.py 里定义的变量/函数
从字符串变成真正的函数，要么：
用 getattr(ab_func, '函数名字符串')
要么在字典里直接存函数对象，而不是名字字符串
"""
request_config = {
    '001': {
        'func': 'get_case_business_kyc',
        'params': {
            'biz_type': 'BUSINESS_ONBOARDING',
            'case_status': ['IN_REVIEW'],
            'level': ['L1', 'L2'],
            'review_status': ['READY_FOR_REVIEW', 'ASSIGNED'],
            'triggered_by': [],
        },
        'dc_pool': ['hk', 'sg'],
        'sheet': {
            'sh_k': 'xxx',  # [kyc-onboarding-queue-python] [Daily Pending 2.0 - Business KYC non CA]
            'tab_k': xxx,
        }
    },
    ...
}
token = input('>> input token (please include Bearer at start): ')
request_id = input('>> input request id (001 / 002 / 003): ').strip()
cfg = request_config.get(request_id)
if not cfg:
    raise ValueError('未知的 request_id: ' + request_id)

func_name = cfg['func']
func = getattr(ab_func, func_name)  # 「反射」工具 等价于 ab_func.get_case_business_kyc
params = cfg['params']
dc_pool = cfg['dc_pool']
sheet_info = cfg['sheet']

all_dfs = []
for dc in dc_pool:
    df = func(token=token, dc=dc, **params)
    all_dfs.append(df)  # 用 list 收集多个 DataFrame，最后一次性拼接。（不要用的是 DataFrame.append()）

if len(all_dfs) == 0:
    com_df = pd.DataFrame()
else:
    com_df = pd.concat(all_dfs, ignore_index=True)


"""接口并发+进度展示
这一部分是在用线程池同时发多个接口请求，提高批量查询速度，并用 tqdm 实时展示完成进度；
成功结果和异常分别收集，方便后续统一处理。
它的核心目的是在大量 ID 批量拉取时兼顾速度、可视化进度和错误追踪。
"""
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    futures = [
        ex.submit(ab.get_cle_details, dc='', token=token, account_id=None, legal_entity_id=cid)
        for cid in cle_ids
    ]

    results, errors = [], []
    for fut in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Fetching CLE"):
        try:
            results.append(fut.result())
        except Exception as e:
            errors.append(str(e))
