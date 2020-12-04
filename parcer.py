from bs4 import BeautifulSoup
import requests
import csv
from multiprocessing import Process
import time

class MyParcer(Process):
    def __init__(self,url,domain="https://hollyshop.ru",direct='photos/',field_names=['name','url','price','descr','composition','manufacturer','sort_leather','age','bar_code','photo0',
             'photo1','photo2','photo3','photo4']):
        Process.__init__(self)
        self.url = url
        self.domain = domain
        self.direct=direct
        self.pages = set()
        self.field_names = field_names
    def run(self):
        result={'url':self.url}
        request = requests.get(self.url)
        soup = BeautifulSoup(request.text,'html.parser')
        data = soup.find('div', {'class': 'card__right-wrapper'})
        result['name'] = data.find('div',{'class':'page-title'}).find('h1').text
        result['price'] = data.find('div',{'class':'card__prices-price'}).text.strip(' \n')
        main_data = data.find_all('div',{'class':'card__accordion-item__body js-accordion-content'})
        result['descr'] = main_data[0].find('div',{'class':'float-block'}).text
        result['composition'] = main_data[1].text.strip(' \n')
        characters_i = main_data[2].find_all('div',{'class':'card__props-item__label'})
        characters_v = main_data[2].find_all('div',{'class':'card__props-item__value'})
        for i in range(len(characters_i)):
            if characters_i[i].text.strip(' \n')=="Производитель":
                result['manufacturer']=characters_v[i].text.strip(' \n')
            elif characters_i[i].text.strip(' \n')=="Тип кожи":
                result['sort_leather']=characters_v[i].text.strip(' \n')
            elif characters_i[i].text.strip(' \n')=="Возраст":
                result['age']=characters_v[i].text.strip(' \n')
            elif characters_i[i].text.strip(' \n')=="Штрихкод":
                result['bar_code']=characters_v[i].text.strip(' \n')
        photos = soup.find('div',{'class':'card__gallery-wrapper'}).find_all("img")
        ph=[None]*5
        for i in range(5):
            try:
                ph[i]=photos[i]['src']
            except:
                pass
            result['photo{}'.format(i)]=ph[i]
        self.downl_img(ph,result['name'])
        self.csv_writer(result)
        
    def downl_img(self,photos,name):
        for i in range(len(photos)):
            if photos[i]:
                try:
                    with open(self.direct+name+str(i)+'.png', 'wb') as ph:
                        ph.write(requests.get(self.url+photos[i]).content)
                except:
                    name=name[:10]
                    with open(self.direct+name+str(i)+'.png', 'wb') as ph:
                        ph.write(requests.get(self.url+photos[i]).content)
    def csv_writer(self,data):
        with open('data/data1.csv','a',newline='',errors='ignore') as csvfile:
            writer = csv.DictWriter(csvfile,delimiter = ';',fieldnames=self.field_names)
            writer.writerow(data)
            
class SmParcer():
    
    def __init__(self,url):
        self.sm_url=url
        self.set_of_urls = set()

    def get_urls(self):
        request = requests.get(self.sm_url)
        soup = BeautifulSoup(request.text,'html.parser')
        catal = soup.find('nav',{'class':'header-menu'}).find_all('a',{'class':'header-menu__item-link'})
        for x in catal:
            self.get_items_url(x['href'])

    def get_items_url(self,url):
        request = requests.get(self.sm_url+url)
        soup = BeautifulSoup(request.text,'html.parser')
        pages = soup.find('div',{'class':'pagination'}).find_all('a')[-1].text
        for i in range(2,int(pages)+1):
            addr = self.sm_url+url+'?PAGEN_1={}'.format(i)
            req = requests.get(addr)
            soup = BeautifulSoup(req.text,'html.parser')
            proc_arr=[]
            items = soup.find('div',{'class':'catalog__products'}).find_all('a',{'class':'product-item__body'})
            for item in items:
                if item['href'] not in self.set_of_urls:
                    self.set_of_urls.add(item['href'])
                    proc = MyParcer(self.sm_url+item['href'])
                    proc.start()
                    proc_arr.append(proc)
            for pr in proc_arr:
                pr.join()
            
Sm = 'https://hollyshop.ru'
if __name__ == '__main__':
    Test = SmParcer(Sm)
    start_time = time.time()
    Test.get_urls()
    print(time.time()-start_time)
