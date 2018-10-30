from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import time
import pymysql

'''创建一个数据库连接,用来保存数据'''
con = pymysql.connect(host="127.0.0.1",user="root",password="123456",database="test",charset="utf8")
'''获取数据库游标，用来把数据保存到指定位置'''
cursor = con.cursor()
'''获取lagou主页上的所有连接'''
def getAllLinks():
    url = "https://www.lagou.com/"
    request = Request(url)
    request.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
    response = urlopen(request)
    soup = BeautifulSoup(response,"html.parser")
    main = soup.select("div.menu_sub a")
    '''for item in main:
        print(item.text)'''
    main = [item.get("href") for item in main]
   # print(main)
    sub = soup.select("div.menu_main a")
    '''for ite in sub:
        print(ite.text)'''
    sub = [item.get("href") for item in sub]
   # print(sub)
    main = set(main)
    sub = set(sub)
    #print(len(main))
    #print(len(sub))
    '''把去重后的连接合并'''
    allLinks = main.union(sub)
  #  print(len(allLinks))
    return list(allLinks)
'''抓取每个网页的数据，保存到mysql数据'''
def crawl(link):
 
    for page in range(1,30):
        print("准备爬去第%d页数据"%page)
        url = link+str(page)+"/" 
        request = Request(url)
        request.add_header(
             "Cookie","JSESSIONID=ABAAABAAAFCAAEG61EBA791F86DD48A8B9BE010CCB887AB; user_trace_token=20180602145450-d83b2d33-6631-11e8-8f48"+
                  "-525400f775ce; LGUID=20180602145450-d83b2fe6-6631-11e8-8f48-525400f775ce; index_location_city=%E5%8C%97%E4%BA%AC; TG-TRACK-CO"+
                  "DE=index_search; SEARCH_ID=f02a30fb86994246adc84d924a65c380; _gid=GA1.2.1467769841.1527922490; Hm_lvt_4233e74dff0ae5bd0a3d81c"+
                  "6ccf756e6=1527922490; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527924401; _ga=GA1.2.1635322740.1527922490; LGSID=20180602145"+
                  "450-d83b2e3c-6631-11e8-8f48-525400f775ce; LGRID=20180602152641-4b55bb14-6636-11e8-8f66-525400f775ce")
        request.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
        response = urlopen(request)
        if url != (response.geturl()):
            time.sleep(1)
            #print("该页没有数据，返回，准备爬去下一个分类")
            break
        soup = BeautifulSoup(response,"html.parser")
        title = soup.select("a.position_link h3")
        #for item in title:
        #   print(item.text)
        pos = soup.select("a.position_link em")
        #for ite in pos:
        #    print(ite.text)
        money = soup.select("div.p_bot")
        #for it in money:
        #    print(it.text)
        company = soup.select("div.company_name a")
        # for item in company:
        #    print(item[1].text)
        tags = soup.select("div.list_item_bot")
        domain = soup.select("div.industry")
        adv = soup.select("div.li_b_r")
        
        
        for i in range(len(title)):
            _title = title[i].text
            _pos = pos[i].text
            temp = list(money[i].stripped_strings)
            _money = temp[0]
            '''将字符串指定参数用split进行分割，返回分割之后的结果'''
            temp = temp[1].split(" / ")
            _exp = temp[0]
            _edu = temp[1]
            _company = company[i].text
            _tags = ",".join(list(tags[i].stripped_strings))
            temp = domain[i].text.strip().split(" / ")
            if len(temp)==2:
                _domain = temp[0]
                _phase = temp[1]
            else:
                _domian = "无"
                _phase = "无" 
            
            _adv = adv[i].text.strip("“”")
            print([_title,_pos,_money,_exp,_edu,_company,_tags,_domain,_phase,_adv])
            cursor.execute("insert into lagou(title,pos,money,exprience,edu,company,tags,domain,phase,adv)"
                           +"values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           [_title,_pos,_money,_exp,_edu,_company,_tags,_domain,_phase,_adv])
        con.commit()
        '''休眠时间，暂停抓取，给目标服务器减压，同时也防止因为访问太快而被目标服务器禁止访问，
                      所以要模仿人类访问的速度，停顿适当的时间'''
        time.sleep(3)
    
'''主函数程序运行的开始'''
def main():
    #cursor.close()
    #con.close()
    links = getAllLinks()
    for link in links:
        crawl(link)
main()
