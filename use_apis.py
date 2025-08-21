from pprint import pp
import requests
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time 
import pandas as pd


def start_browser():
    service = Service('./chromedriver.exe')
    option = webdriver.ChromeOptions()
    browser = webdriver.Chrome(service=service, options=option)
    return browser

def address_to_code(app_key: str,
                    address: str, 
                    city: str=None) -> list:
    """
    使用该函数可以获取地址的基本信息, 包括有:
    
    [地址, 国家, 省份, 城市, 城市编码, 区, 区域编码, 经纬度, 匹配级别]

    Args:
        app_key (str): 调用API的app_key
        address (str): 地址
        city (str): 地址所在的城市, 可以帮助减小搜索范围, 获取结果更准确
    Returns:
        对应地址的信息列表
    """
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"
    params = {"key": app_key,
              "address": re.sub("(\s\S)", "", address.replace("集团", "")).replace(")", "").replace("(", "")}
    if city is not None:
        params.update({"city": city})
    print(params)
    result = requests.get(url=url, params=params)
    result_json = result.json()
    pp(result_json)
    result_list = []
    if isinstance(result_json, dict) and result_json.get("status") == "1":
        geocodes = result_json.get("geocodes")
        for code in geocodes:
            info = [address, code["country"], code["province"], code["city"], code["citycode"], 
                    code["district"], code["adcode"], code["location"], code["level"]]
            result_list.append(info)
    return result_list
        
def update_html(longitude: float,
                latitude: float) -> None:
    """更新map.html中的坐标值

    Args:
        longitude (float): 经度
        latitude (float): 纬度
    Returns:
        None
    """
    with open("map.txt", encoding="utf-8") as fp:
        html_txt = fp.read()
        html_txt = re.sub("longitude", longitude, html_txt)
        html_txt = re.sub("latitude", latitude, html_txt)
    
    with open("map.html", "w", encoding="utf-8") as fp:
        fp.write(html_txt)

def main(address_list: list,
         province_list: list,
         city_list: list,
         district: list):
    """_summary_

    Args:
        address_list (list): 地址
        province_list (list): 省份
        city_list (list): 城市
        district (list): 区县
    """
    app_key = "0de3e8970a8681ac6352b420d0bee244"
    result_list = []
    for address, province, city, district in zip(address_list,
                                                 province_list,
                                                 city_list,
                                                 district):
        add = "".join([province, city, district, address])
        result = address_to_code(app_key=app_key, address=add, city=province)
        for res in result:
            result_list.append(res)
        time.sleep(0.5)
    # # 获取截图
    deriver = start_browser()
    for i, result in enumerate(result_list):
        path = f"image_pages/{i}_{result[0]}.png"
        longitude = result[7].split(",")[0]
        latitude = result[7].split(",")[1]
        print(i, result[0], longitude, latitude)
        update_html(longitude, latitude)
        deriver.get("file:///D:/PyCode/GitHubPages/FXDL-BPYW-MAP/map.html")
        deriver.maximize_window()
        deriver.save_screenshot(path)
        print(path, "保存完毕")
        time.sleep(0.5)
    deriver.close()
        

if __name__ == "__main__":
    address_infor = pd.read_excel("10.1.3.1.xlsx", usecols=["企业名称", "所属省份", "所属城市", "所属区县"])
    infors = address_infor.head(10)
    main(infors["企业名称"].tolist(), infors["所属省份"].tolist(), infors["所属城市"].tolist(), infors["所属区县"].tolist())
    
    # result_list = address_to_code(app_key=app_key, address="石狮黎祥食品有限公司", city="福建省")
    # if result_list:
    #     for result in result_list:
    #         longitude = result[7].split(",")[0]
    #         latitude = result[7].split(",")[1]
    #         update_html(longitude, latitude)