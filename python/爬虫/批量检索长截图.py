import json
import base64
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


COOKIE_FILE = 'temp_cookies.json'

# 获取程序所在目录，并作为工作目录使用。
def get_workdir():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe，目录取可执行文件所在位置
        return os.path.dirname(sys.executable)
    # 普通 .py 脚本则取脚本文件所在目录
    return os.path.dirname(os.path.abspath(__file__))

# 人工打开一次 Google，手动完成搜索 / 验证，然后把当前浏览器 cookie 保存到本地。
def create_cookie():
    opts = Options()
    driver = webdriver.Chrome(options=opts)
    driver.get('https://www.google.com')
    time.sleep(2)

    input('\n'.join([
        '>> 1. Search anything in Google',
        '>> 2. If verification/challenge appears, finish it',
        '>> 3. Do not close the browser',
        '>> 4. Press Enter to continue: ',
    ]))

    cookies = driver.get_cookies()
    with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)

    print(f'>> Cookies saved to {COOKIE_FILE}')
    driver.quit()

# 从本地读取 cookie，并注入到当前浏览器会话中。这里只保留 Selenium 常见支持的字段，避免 add_cookie 报错。
def load_cookies(driver, cookie_file=COOKIE_FILE):
    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookies = json.load(f)

    for c in cookies:
        cookie = {
            'name': c['name'],
            'value': c['value'],
        }
        for k in ('domain', 'path', 'expiry', 'secure', 'httpOnly', 'sameSite'):
            if k in c:
                cookie[k] = c[k]

        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f'⚠️ Skip cookie {cookie.get("name")}: {e}')

# 用 Chrome DevTools Protocol 进行整页截图。比 driver.save_screenshot() 更适合长页面。
def save_fullpage_png(driver, save_path):
    result = driver.execute_cdp_cmd('Page.captureScreenshot', {
        'format': 'png',
        'captureBeyondViewport': True,
    })
    with open(save_path, 'wb') as f:
        f.write(base64.b64decode(result['data']))

# 搜索关键词，并按页保存 Google 搜索结果截图。
def browser_screenshots(keyword: str, pages: int):
    if not keyword.strip():
        print('⚠️ Empty keyword')
        return

    opts = Options()
    opts.add_argument('--headless=new')  # 新版无头模式
    opts.add_argument('--window-size=1440,900')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get('https://www.google.com')  # 先打开目标域名，Selenium 才允许往这个域注入 cookie
        load_cookies(driver)  # 注入 cookie
        driver.refresh()  # 关键：加完 cookie 后刷新, 这样当前页面才会真正带着这些 cookie 生效
        q_box = wait.until(EC.element_to_be_clickable((By.NAME, 'q')))  # 等搜索框可点击，再输入关键词并回车
        q_box.clear()
        q_box.send_keys(keyword, Keys.ENTER)

        for page in range(1, pages + 1):
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')  # 等页面加载完成
            time.sleep(2)  # 给懒加载一点额外时间
            save_path = f'capture_{page}.png'
            save_fullpage_png(driver, save_path)
            print(f'✅ Saved: {save_path}')
            # 最后一页就不翻了
            if page < pages:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((By.ID, 'pnnext')))
                    driver.execute_script("arguments[0].click();", next_btn)
                except Exception:
                    print('⚠️ Next page not found, stop here')
                    break

    finally:
        driver.quit()
        print('>> Completed')


if __name__ == '__main__':
    os.chdir(get_workdir())
    print(f'>> Current path: {os.getcwd()}')
    # 如果本地还没有 cookie 文件，先手动创建一次
    if not os.path.exists(COOKIE_FILE):
        create_cookie()

    kw = input('>> Input keyword: ').strip()
    pages_text = input('>> Input page count (default 5): ').strip()

    try:
        pages = int(pages_text) if pages_text else 5
    except ValueError:
        pages = 5

    browser_screenshots(keyword=kw, pages=pages)
