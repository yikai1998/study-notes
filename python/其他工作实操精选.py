# 接口调用模版1
# headers
HEADER = {
    'Content-Type': 'application/json',
    'authorization': 'TOKEN WITHOUT BEARER',
    'x-data-center': 'HK'  # default
}
HEADER2 = {
    'Content-Type': 'application/json',
    'authorization': 'TOKEN',
    'x-data-center': 'HK'  # default
}
def search_datacenter(self, accountid=None, legalentityid=None):
    url = 'https://airboard-ng.airwallex.com/graphql/kyc/getLegalEntityList'
    HEADER['x-data-center'] = 'HK'  # reset to be default
    if accountid is None:
        data = {
            'operationName': 'getLegalEntityList',
            'query': 'query getLegalEntityList($params: GetLegalEntityListParam) {\n  getLegalEntityList(params: $params) {\n    data {\n      account_id\n      account_open_id\n      agreed_to_terms_and_conditions\n      business_structure\n      client_legal_entity_id\n      country\n      customer_name_english\n      customer_name_local\n      industry_category\n      kyc_created_time\n      kyc_passed_time\n      kyc_process_status\n      risk_rating\n      __typename\n    }\n    total\n    __typename\n  }\n}\n',
            'variables': {
                'params': {
                    'client_legal_entity_id': legalentityid,
                    'from': 0,
                    'size': 10,
                }
            }
        }
    else:
        data = {
            'operationName': 'getLegalEntityList',
            'query': 'query getLegalEntityList($params: GetLegalEntityListParam) {\n  getLegalEntityList(params: $params) {\n    data {\n      account_id\n      account_open_id\n      agreed_to_terms_and_conditions\n      business_structure\n      client_legal_entity_id\n      country\n      customer_name_english\n      customer_name_local\n      industry_category\n      kyc_created_time\n      kyc_passed_time\n      kyc_process_status\n      risk_rating\n      __typename\n    }\n    total\n    __typename\n  }\n}\n',
            'variables': {
                'params': {
                    'account_id': accountid,
                    'from': 0,
                    'size': 10,
                }
            }
        }
    r = requests.post(url=url, data=json.dumps(data), headers=HEADER).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return r['data']['getLegalEntityList']['total']
dc = 'HK' if func_repo.search_datacenter(accountid=accountid) > 0 else 'SG'
HEADER['x-data-center'] = dc
HEADER2['x-data-center'] = dc
def get_risk_common_info(legal_entity_id):
    url = 'https://airboard-ng.airwallex.com/graphql/risk-common'
    data = {
        'operationName': 'getAccountLinkageInformationV2',
        'query': 'query getAccountLinkageInformationV2($accStatuses: [String], $accountId: String, $beforeKycReceived: Boolean, $includeAnonymousIP: Boolean, $kycFailedReasons: [String], $kycRecordId: String, $kycStatuses: [String], $legalEntityId: String, $offboardReasons: [String], $orderByHits: Order, $pageNumber: Int, $pageSize: Int, $types: [String], $watchListCategories: [String], $watchListHits: Boolean) {\n  getAccountLinkageInformationV2(\n    accStatuses: $accStatuses\n    accountId: $accountId\n    beforeKycReceived: $beforeKycReceived\n    includeAnonymousIP: $includeAnonymousIP\n    kycFailedReasons: $kycFailedReasons\n    kycRecordId: $kycRecordId\n    kycStatuses: $kycStatuses\n    legalEntityId: $legalEntityId\n    offboardReasons: $offboardReasons\n    orderByHits: $orderByHits\n    pageNumber: $pageNumber\n    pageSize: $pageSize\n    types: $types\n    watchListCategories: $watchListCategories\n    watchListHits: $watchListHits\n  ) {\n    accountGroupId\n    accountLinkageCounts\n    accountLinkageDetails {\n      accountClosureReason\n      accountStatus\n      customerSegment\n      idHitsOfReasons\n      kycFailedReason\n      kycStatus\n      linkageInformation\n      linkageType\n      linkedAccountId\n      linkedCleId\n      linkedName\n      links {\n        detail\n        reason\n        __typename\n      }\n      offboardReason\n      ownerOrgLevelTwo\n      owningEntity\n      platformAccountId\n      spaceId\n      watchlistCategories\n      watchlistHit\n      __typename\n    }\n    kycFailedReasons\n    linkTypes\n    offboardReasons\n    ownedAccountGroups {\n      id\n      name\n      ownerId\n      __typename\n    }\n    resCount\n    statsOfAccount {\n      ACTIVE\n      CLOSED\n      DORMANT\n      FROZEN\n      INITIAL\n      PENDING_CLOSE\n      __typename\n    }\n    statsOfKycStats {\n      FAILURE\n      INIT\n      SUBMITTED\n      SUCCESS\n      __typename\n    }\n    statsOfLinkType {\n      email\n      phone\n      __typename\n    }\n    submissionIp {\n      geoInfo {\n        city\n        country\n        riskRating\n        __typename\n      }\n      ip\n      __typename\n    }\n    total\n    watchListCategories\n    watchListHitsCount\n    __typename\n  }\n}\n',
        'variables': {
            'accStatuses': ['CLOSED'],
            'beforeKycReceived': True,
            'legalEntityId': legal_entity_id,
            'pageNumber': 1,
            'pageSize': 10000,
            'types': ['director'],
        }
    }
    r = requests.post(url=url, data=json.dumps(data), headers=HEADER).text
    time.sleep(0.1)
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return r
---
# 接口调用模版2
def search_datacenter(legal_entity_id=None, account_id=None, token=None):
    headers = set_headers(datacenter='HK', token=token[7:])  # reset to be default
    url = 'https://airboard-ng.airwallex.com/graphql/kyc/getLegalEntityList'
    data = {
        'operationName': 'getLegalEntityList',
        'query': 'query getLegalEntityList($params: GetLegalEntityListParam) {\n  getLegalEntityList(params: $params) {\n    data {\n      account_id\n      account_open_id\n      agreed_to_terms_and_conditions\n      business_structure\n      client_legal_entity_id\n      country\n      customer_name_english\n      customer_name_local\n      industry_category\n      kyc_created_time\n      kyc_passed_time\n      kyc_process_status\n      risk_rating\n      __typename\n    }\n    total\n    __typename\n  }\n}\n',
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
    r = requests.post(url=url, headers=headers, data=json.dumps(data)).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
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


def set_headers(datacenter, token):
    return {
        'Content-Type': 'application/json',
        'authorization': token,
        'x-data-center': datacenter,
    }


@datacenter_decorator
def get_tm_case(datacenter, token, case_id, account_id=None, legal_entity_id=None):
    url = 'https://airboard-ng.airwallex.com/graphql/postmonitoring/uar'
    data = {
        'operationName': 'getCaseById',
        'query': 'query getCaseById($caseUuid: ID!) {\n  getCaseById(caseUuid: $caseUuid) {\n    accountId\n    businessName\n    cardNumber\n    caseHandlingTeam\n    channelRfiTag\n    clientRole\n    comment\n    createdAt\n    createdBy\n    customerExternalBankAccountNumber\n    customerSegment\n    emailSubject\n    files {\n      fileId\n      fileName\n      __typename\n    }\n    isMigration\n    legalEntityId\n    level\n    merchantId\n    migration\n    orgLevel2\n    owningEntity\n    recallStatus\n    receivedAt\n    reviewer\n    rfiEmailTitle\n    rfiSentDate\n    rfiSessionId\n    rfiSessionStatus\n    riskTypes\n    sla\n    sourceChannel\n    sourceSubType {\n      cardScheme {\n        cardSchemeValue\n        __typename\n      }\n      channelFraud {\n        accountStatus\n        indemnity\n        indemnityEta\n        indemnityRequestDate\n        internalClientEscalation\n        isNewFraud\n        recallStatus\n        returnedAmount\n        returnedDate\n        ticketStatus\n        __typename\n      }\n      channelRfi {\n        accountBlockByChannel\n        internalClientEscalation\n        tag\n        __typename\n      }\n      value\n      __typename\n    }\n    sourceType\n    status\n    transactionIds\n    uuid\n    zendeskTicketNumber\n    __typename\n  }\n}',
        'variables': {
            'caseUuid': case_id,
        }
    }
    headers = set_headers(datacenter=datacenter, token=token[7:])
    r = requests.post(url=url, headers=headers, data=json.dumps(data)).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return {
        'accountId': r['data']['getCaseById']['accountId'],
        'businessName': r['data']['getCaseById']['businessName'],
        'legalEntityId': r['data']['getCaseById']['legalEntityId'],
        'orgLevel2': r['data']['getCaseById']['orgLevel2'],
        'owningEntity': r['data']['getCaseById']['owningEntity'],
        'transactionId': r['data']['getCaseById']['transactionIds'][0],
        'zendeskTicketNumber': r['data']['getCaseById']['zendeskTicketNumber'],
    }
---
# token transfer涉及上传文件
import requests
from config import *
import json
import ast
import mimetypes
import tkinter
from tkinter.filedialog import *
import tkinter.messagebox as messagebox
from bs4 import BeautifulSoup

# variables
uploaded_attachments = []


def generate_upload_link(mimetype):
    url = 'https://airboard-ng.airwallex.com/graphql/account/generateUploadLink'
    data = {
        'operationName': 'generateUploadLink',
        'query': "mutation generateUploadLink($mimeTypes: String) {\n  generateUploadLink(mimeTypes: $mimeTypes) {\n    data {\n      endpoint\n      id\n      form_data {\n        OSSAccessKeyId\n        Signature\n        key\n        policy\n        googAlgorithm\n        googCredential\n        googDate\n        googSignature\n        contentType\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        'variables': {'mimeTypes': mimetype},
    }
    r = requests.post(url=url, data=json.dumps(data), headers=awx_headers).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)  # 不管你files叫啥名，OSS(Object Storage Service)主要根据你form-data里的key字段来存放文件
    return r['data']['generateUploadLink']['data'][0]['endpoint'], r['data']['generateUploadLink']['data'][0]['form_data']


def aliyun_enable(url, form_data, file_name, mimetype):
    global uploaded_attachments
    with open(file=file_name, mode='rb') as f:
        file = {'file': (file_name, f, mimetype)}
        r = requests.post(url=url, data=form_data, files=file)
        if r.status_code == 204:
            print('>> Uploaded successfully...')
            uploaded_attachments.append(form_data)
        else:
            raise f'>> {r.text}'


def select_upload_files(app):
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
            aliyun_enable(url=end_url, form_data=form_data, file_name=file['fileName'], mimetype=file['mimeType'])

        print('>> All Completed ...')
        messagebox.showinfo(title='上传成功', message='所有文件均已上传成功！', parent=app)
    else:
        messagebox.showwarning(title='结束', message='没有文件被上传！', parent=app)
    app.destroy()
    return


def trigger_attachment():
    mac = tkinter.Tk()
    mac.attributes('-topmost', True)
    mac.after(5000, lambda: mac.attributes('-topmost', False))  # 5秒后允许被其它窗口覆盖
    tkinter.Button(mac, command=lambda: select_upload_files(app=mac), text='select and upload files').pack()
    mac.geometry('1200x400')
    mac.mainloop()


def find_attachment(file_id):
    url = 'https://airboard-ng.airwallex.com/graphql/account/getFileById'
    data = {
        'operationName': 'getFileById',
        'query': "query getFileById($fileId: String) {\n  getFileById(fileId: $fileId) {\n    url\n    content_type\n    filename\n    size\n    __typename\n  }\n}\n",
        'variables': {'fileId': file_id}
    }
    r = requests.post(url=url, data=json.dumps(data), headers=awx_headers).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return r
---
# decode token
import jwt
def decode_token(self, token):
    pload = jwt.decode(token, options={'verify_signature': False})
    return pload
---
# map btw two list (“黑名单过滤”)
def black_map(black, iterable):
    black = set(black)
    for x in iterable:
        if x not in black:
            yield x

g = black_map(['a', 'b'], ['b', 'c', 'd'])
print(list(g))               # ['c', 'd']
---
# 读取html
with open(html_path, encoding='utf-8') as f:
    # 默认先只考虑一个html文件，如果内容很多就先合并进一个文件中
    html = f.read()
soup = BeautifulSoup(html, 'html.parser')
body_content = soup.body.decode_contents()
---
# bug经验
"""
在Python中，空字符串 '' 被认为在任何字符串中，所以
'' in 'A29AD2EBC5VQHK'   # 等于 True
这一点逻辑上类似于：找“空子串”总会在任何串的开始、结束等地方。
"""

---
# local runtime
```txt
download docker https://rancherdesktop.io/ 
open the docker in backend
open terminal
    docker run -p 127.0.0.1:9000:8080 asia-docker.pkg.dev/colab-images/public/runtime
    copy: http://127.0.0.1:9000/?token=xxx

import socket; print(socket.gethostname())
```
---
# 自动刷新token，并并入自定义公式中
```py
class TokenManager:
    def __init__(self):
        self.refresh_token = None
        self.access_token = None
        self.access_bearer_token = None
        self.token_expired_at = 0.0

    def init_token(self):
        self.refresh_token = input('>> Input Airboard-Refresh-Token: ')
        self.access_token = input('>> Input Airboard-Access-Token: ')
        self.access_bearer_token = self.access_token[:]
        self.access_token = self.access_token[7:]  # 去掉"Bearer "前缀
        decoded_jwt = jwt.decode(self.access_token, algorithms=['HS256'], options={'verify_signature': False})
        self.token_expired_at = decoded_jwt['exp'] - 15 * 60
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
        url = 'https://airboard-ng.airwallex.com/api/v1/security/refresh'
        try:
            r = requests.post(url=url, data=json.dumps(data), headers=headers).text
            r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
            r = ast.literal_eval(r)
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
            raise f"Error refreshing token: {e}"

    def get_headers(self):
        """返回带有当前有效token的请求头"""
        return {
            'Content-Type': 'application/json',
            'authorization': self.access_bearer_token,
            'x-data-center': 'HK',
        }

class AccountFunctionClub:
    def __init__(self, token_manager):
        # airboard token
        self.token = 'xxxx-xxxx-xxxx'
        self.awx_headers = {
            'Content-Type': 'application/json',
            'authorization': 'TOKEN',
            'x-data-center': 'HK'  # default
        }
        self.token_manager = token_manager

    def global_account_info(self, row):
        self.token_manager.check_and_refresh_token()
        headers = self.token_manager.get_headers()
        gaid = row['gaid']
        dc = row['dc']
        url = f'https://airboard-ng.airwallex.com/api/v1/accountList/ga?createTimeRangeByDay%3D2016-01-01%2C2028-05-31%26vbaId%3D{gaid}%26pageSize%3D100'
        headers['x-data-center'] = 'SG' if dc.lower() == 'sg' else 'HK'
        r = requests.get(url=url, headers=headers).text
        r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
        r = ast.literal_eval(r)
        return r

# working
token_manager = airboard_func.TokenManager()
abFuncs = airboard_func.AccountFunctionClub(token_manager=token_manager)
...
token_manager.init_token()
    for row in tqdm(df_combine, desc='retrieving ga info'):
        data_return = abFuncs.global_account_info(row=row)
        ...
```

---
# 如何存储密钥
"""
你的密钥（如 KEY_TEMP=xxxxx）应该写在 .env 文件（无扩展名，纯文本文件）里。
.env 文件里内容格式应该是KEY=VALUE，每行一个变量。不能写KEY_TEMP="abcd"、KEY_TEMP='abcd'那种 Python 代码，也不能有空格。
pip install python-dotenv
```import os
from dotenv import load_dotenv
load_dotenv()
print(os.environ.get('KEY_TEMP'))```
load_dotenv(dotenv_path='路径/到/你的.env')  # 如果你的.env不在同一目录下
"""
