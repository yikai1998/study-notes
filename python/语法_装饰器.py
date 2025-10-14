# coding=gbk

# 简单版
def check(func):
    def inside(a, b):
        if b == 0:
            print('can not divide by 0')
            return 0
        print('Calculating...')
        return func(a, b)
    return inside


@check  # equals div = check(div)
def div(a, b):
    return a/b


print(div(5, 0))
print(div(1005001, 20))


# 增加难度
def check2(param=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in args:
                print(i)
            for k, v in kwargs.items():
                print(k, v)
            if param is not None:
                print(f'Applying {param} parameter to function {func.__name__}')
            # 在这里可以添加更多的逻辑，比如检查参数，或者根据param的值改变行为
            print(func(*args, **kwargs))
        return wrapper
    return decorator


# 使用装饰器，传入参数
@check2(param='special behavior')
def div(a, b, *args, **kwargs):
    return a / b if b != 0 else 'Cannot divide by zero'

div(490, 80, 'eggs', dinner='noodles')


# 使用装饰器，不传入参数
@check2()
def add(a, b):
    return a + b


# 使用装饰器，传入不同的参数
@check2(param='another behavior')
def multiply(a, b, c='test'):
    return a * b


multiply(10, 30, c='can you see')
add(100, 2000)
div(490, 80)
'''
10
30
c can you see
Applying another behavior parameter to function multiply
300
100
2000
2100
490
80
Applying special behavior parameter to function div
6.125
'''


# 实操场景1
def search_datacenter(accountid=None, legalentityid=None):
    url = 'https:xxxgraphql/kyc'
    config.awx_headers['x-data-center'] = 'HK'  # reset to be default
    if accountid is None:
        caseInfo = {
            'operationName': 'getLegalEntityList',
            'query': 'query xxxx',
            'variables': {
                'params': {
                    'client_legal_entity_id': legalentityid,
                    'from': 0,
                    'size': 10,
                }
            }
        }
    else:
        caseInfo = {
            'operationName': 'getLegalEntityList',
            'query': 'query xxxx',
            'variables': {
                'params': {
                    'account_id': accountid,
                    'from': 0,
                    'size': 10,
                }
            }
        }
    r = requests.post(url=url, data=json.dumps(caseInfo), headers=config.awx_headers).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return r['data']['getLegalEntityList']['total']

"""
def search_datacenter(accountid):
    awx_headers['x-data-center'] = 'HK'  # reset to be default
    url = f'https:xxxx?businessName%3D{accountid}%26pageSize%3D50'
    r = requests.get(url=url, headers=awx_headers).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    dc = 'hk' if len(r['data']) > 0 else 'sg'
    return dc
"""

def datacenter_decorator(func):
    def wrapper(*args, **kwargs):
        accountid = kwargs.get('accountid')
        legalentityid = kwargs.get('legalentityid')
        datacenter = 'HK' if search_datacenter(accountid=accountid, legalentityid=legalentityid) > 0 else 'SG'
        kwargs['datacenter'] = datacenter
        return func(*args, **kwargs)
    return wrapper

@datacenter_decorator
def get_LegalEntityId(datacenter, accountid):
    url = 'xxxx/kyc'
    info = {
        'operationName': 'getLegalEntityList',
        'query': 'query xxxx',
        'variables': {
            'params': {
                'account_id': accountid,
                'from': 0,
                'size': 10,
            }
        }
    }
    config.awx_headers['x-data-center'] = datacenter
    r = requests.post(url=url, data=json.dumps(info), headers=config.awx_headers).text
    r = r.replace('false', 'False').replace('null', 'None').replace('true', 'True')
    r = ast.literal_eval(r)
    return r['data']['getLegalEntityList']['data'][0]['client_legal_entity_id']

