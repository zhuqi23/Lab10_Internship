from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import json
import re
import time

# -------------------------- 基础配置 --------------------------
list_url = "https://sztu.bysjy.com.cn/module/onlines?menu_id=40670"
detail_urls = []  # 存储所有岗位详情页链接
job_data = []     # 存储最终提取的岗位信息

# -------------------------- 1. 爬取所有详情页链接（自动翻页） --------------------------
def crawl_all_pages():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(list_url)
    time.sleep(3)  # 初始加载等待

    # 提取总页数
    try:
        page_info = driver.find_element(By.XPATH, "//div[contains(text(), '共') and contains(text(), '条记录')]").text
        total_pages = int(re.search(r'(\d+)/(\d+)', page_info).group(2))
        print(f"检测到总页数：{total_pages} 页")
    except:
        total_pages = 100
        print("无法提取总页数，默认最多爬取100页")

    page_num = 1
    while page_num <= total_pages:
        print(f"\n===== 开始爬取第 {page_num} 页链接 =====")
        
        # 解析当前页链接
        soup = BeautifulSoup(driver.page_source, "lxml")
        job_items = soup.find_all("li", class_="item")
        
        if not job_items:
            print(f"第 {page_num} 页未找到岗位数据，停止爬取")
            break
        
        for item in job_items:
            item_main = item.find("div", class_="item-main")
            if item_main:
                job_link = item_main.find("p", class_="item-tit").find("a", class_="item-link")
                if job_link:
                    detail_url = job_link.get("href")
                    if detail_url.startswith("/"):
                        detail_url = "https://sztu.bysjy.com.cn" + detail_url
                    if detail_url not in detail_urls:
                        detail_urls.append(detail_url)
                        print(f"已获取链接：{detail_url}")
        
        print(f"第 {page_num} 页链接爬取完成，累计 {len(detail_urls)} 个")

        # 翻页
        if page_num < total_pages:
            try:
                next_page_btn = driver.find_element(By.XPATH, "//a[contains(text(), '»')]")
                next_page_btn.click()
                time.sleep(2)
                page_num += 1
            except Exception as e:
                print(f"翻页失败：{str(e)}，停止爬取")
                break
        else:
            print("已到达最后一页，链接爬取完成")
            break

    driver.quit()


# -------------------------- 2. 爬取详情页信息（精准解析） --------------------------
def crawl_detail_pages():
    # 初始化浏览器（复用配置）
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    for i, url in enumerate(detail_urls, 1):
        try:
            print(f"\n===== 开始爬取第 {i}/{len(detail_urls)} 个详情页 =====")
            driver.get(url)
            time.sleep(3)  # 延长等待时间，确保动态内容加载完成
            soup = BeautifulSoup(driver.page_source, "lxml")
            
            # -------------------------- 1. 提取公司信息（1个/详情页） --------------------------
            # 公司名称
            company_name = "未知"
            try:
                company_name = soup.find("p", class_="ci-text").text.strip()
            except:
                print("警告：未提取到公司名称")
            
            # 公司地址（注册地址）
            company_address = "未知"
            try:
                # 从含"地址"关键词的段落提取
                addr_tag = soup.find("p", class_="ci-text", string=lambda x: x and "地址" in str(x))
                if addr_tag:
                    company_address = addr_tag.text.replace("地址：", "").strip()
            except:
                print("警告：未提取到公司地址")
            
            # -------------------------- 2. 提取所有岗位信息（n个/详情页） --------------------------
            # 定位所有岗位容器（每个岗位对应一个<div class="clearfix dm-text">）
            job_containers = soup.find_all("div", class_="clearfix dm-text")
            if not job_containers:
                print(f"警告：{url} 中未找到岗位容器")
                continue
            
            # 遍历每个岗位容器，提取独立信息
            for container in job_containers:
                # 招聘岗位名称
                job_title = "未知"
                try:
                    job_title = container.find("a", class_="item-link").text.strip()
                except:
                    pass
                
                # 薪资（通过红色高亮样式定位）
                salary = "未知"
                try:
                    salary = container.find("div", style="float:left;color:#ff9900;").text.strip()
                except:
                    pass
                
                # 招聘人数
                recruit_num = "未知"
                try:
                    # 人数在右侧第一个p标签
                    recruit_num = container.find("div", style="float:right;").find("p").text.strip()
                except:
                    pass
                
                # 工作地点（岗位具体地点，优先从岗位信息中提取）
                work_location = "未知"
                try:
                    # 岗位地点在右侧第二个p标签（格式：学历 | 地点）
                    loc_tag = container.find("div", style="float:right;").find_all("p")[1]
                    if loc_tag:
                        # 从"本科及以上 | 深圳市"中提取地点
                        work_location = loc_tag.text.split("|")[-1].strip()
                except:
                    # 若未找到，默认使用公司地址
                    work_location = company_address
                    print(f"警告：{job_title} 未提取到工作地点，使用公司地址替代")
                
                # 岗位要求
                job_require = "无"
                try:
                    # 1. 先定位到岗位详情的主容器（class="job-detail-main"）
                    detail_main = container.find("div", class_="job-detail-main")
                    if not detail_main:
                        print(f"警告：{job_title} 未找到岗位详情主容器")
                    else:
                        # 2. 找到"岗位要求："标题（h3标签）
                        require_head = detail_main.find("h3", string="岗位要求：")
                        if not require_head:
                                            # 备选：如果标题是"任职要求："
                            require_head = detail_main.find("h3", string=lambda x: x and "任职要求" in x)
                        
                        if require_head:
                            # 3. 提取标题后的第一个div（包含所有要求内容）
                            require_div = require_head.find_next("div")
                            if require_div:
                                # 4. 提取div内的所有文本，合并为字符串（处理换行和空格）
                                # 先获取所有p标签文本，再拼接
                                require_parts = [p.text.strip() for p in require_div.find_all("p") if p.text.strip()]
                                # 替换多余的空格和换行符
                                job_require = "\n".join(require_parts).replace("&nbsp;", " ").replace("\r", "")
                            else:
                                print(f"警告：{job_title} 未找到岗位要求内容容器")
                        else:
                            print(f"警告：{job_title} 未找到'岗位要求'标题")
                except Exception as e:
                    print(f"警告：{job_title} 岗位要求提取失败：{str(e)}")
                
                # -------------------------- 3. 存储当前岗位数据 --------------------------
                job_info = {
                    "公司名称": company_name,
                    "公司地址": company_address,
                    "招聘岗位": job_title,
                    "薪资": salary,
                    "招聘人数": recruit_num,
                    "工作地点": work_location,
                    "岗位要求": job_require,
                    "详情页链接": url
                }
                job_data.append(job_info)
                print(f"已提取岗位：{company_name} - {job_title}")
        
        except Exception as e:
            print(f"详情页整体爬取失败（{url}）：{str(e)}")
            continue
    
    driver.quit()
    print(f"\n===== 所有详情页爬取完成，共提取 {len(job_data)} 条岗位数据 =====")


# -------------------------- 3. 主程序执行 --------------------------
if __name__ == "__main__":
    crawl_all_pages()
    if detail_urls:
        crawl_detail_pages()
        # 导出JSON
        with open("深圳技术大学招聘详情.json", "w", encoding="utf-8") as f:
            json.dump(job_data, f, ensure_ascii=False, indent=2)
        print("\n数据已保存至：深圳技术大学招聘详情.json")
    else:
        print("未获取到详情页链接，任务终止")