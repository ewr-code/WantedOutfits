import xml.etree.ElementTree as ET
import translator
from googletrans import Translator
import urllib.request
import os
import shutil
import datetime
import pandas as pd


def myFunc(e):
    return e['stok kodu']


def addProducts(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    products = []
    options = []
    products = []
    att1_name = ""
    att1_val = []
    att2_name = ""
    att2_val = []
    # print(*products, sep='\n')
    for variants in root.findall('item'):
        skuMain = variants.find('stockCode').text
        isVariant = False
        for variant in variants.findall('variants'):
            for subbranks in variant.findall("variant"):
                isVariant = True
                sku = subbranks.find('vStockCode').text
                stok = subbranks.find('vStockAmount').text
                price = subbranks.find('vPrice1').text
                for opts in subbranks.findall("options"):
                    for opttions in opts.findall("option"):
                        options.append(
                            (opttions.find("variantName").text, opttions.find("variantValue").text))
                    if len(options) == 1:
                        products.append({"stok kodu": sku,
                                         "ürün adı": variants[1].text,
                                         "stok": int(stok),
                                         "status": variants[2].text,
                                         "fiyat": round(float(price)+float(price)*int(variants[15].text)/100, 2),
                                         "vergi": variants[27].text,
                                         "indirim": "",
                                         "indirimli fiyat": "",
                                         "product type": "variation",
                                         "parent": variants[0].text,
                                         "att1 name": options[0][0],
                                         "att1 val": options[0][1]})
                        att1_name = options[0][0]
                        att1_val.append(options[0][1])
                    else:
                        products.append({"stok kodu": sku,
                                         "ürün adı": variants[1].text,
                                         "stok": int(stok),
                                         "status": variants[2].text,
                                         "fiyat": round(float(price)+float(price)*int(variants[15].text)/100, 2),
                                         "vergi": "",
                                         "indirim": variants[27].text,
                                         "indirimli fiyat": "",
                                         "product type": "variation",
                                         "parent": variants[0].text,
                                         "att1 name": options[0][0],
                                         "att1 val": options[0][1],
                                         "att2 name": options[1][0],
                                         "att2 val": options[1][1]})
                        att1_name = options[0][0]
                        if len(att1_val) != 0:
                            if att1_val.count(options[0][1]) == 0:
                                att1_val.append(options[0][1])
                        else:
                            att1_val.append(options[0][1])
                        att2_name = options[1][0]
                        if len(att2_val) != 0:
                            if att2_val.count(options[1][1]) == 0:
                                att2_val.append(options[1][1])
                        else:
                            att2_val.append(options[1][1])
                    options = []
            else:
                if isVariant == True:
                    products.append({"stok kodu": skuMain,
                                     "ürün adı": variants[1].text,
                                     "stok": variants[17].text,
                                     "status": variants[2].text,
                                     "fiyat": float(variants[10].text),
                                     "vergi": float(variants[15].text),
                                     "indirim": variants[27].text,
                                     "indirimli fiyat": float(variants[26].text),
                                     "product type": "variable",
                                     "att1 name": att1_name,
                                     "att1 val": att1_val,
                                     "att2 name": att2_name,
                                     "att2 val": att2_val,
                                     "pic1": variants[20].text,
                                     "pic2": variants[21].text,
                                     "pic3": variants[22].text,
                                     "pic4": variants[23].text})
                    att1_val.clear()
                    att2_val.clear()
                    att1_name = ""
                    att2_name = ""
        if isVariant == False:
            products.append({"stok kodu": variants[0].text,
                             "ürün adı": variants[1].text,
                             "stok": variants[17].text,
                             "status": variants[2].text,
                             "fiyat": float(variants[10].text),
                             "vergi": float(variants[15].text),
                             "indirim": variants[27].text,
                             "indirimli fiyat": float(variants[26].text),
                             "product type": "simple",
                             "pic1": variants[20].text,
                             "pic2": variants[21].text,
                             "pic3": variants[22].text,
                             "pic4": variants[23].text})
    return products


def removeProducs(products):
    contents = pd.read_csv('products.csv', delimiter=',',
                           encoding='ISO-8859-1', index_col=2)
    for product in products:
        print(product['stok kodu'])
    contents.to_csv(r'products.csv')
# dosya adı için bugünün stringini oluştur
# today= str(datetime.datetime.now().day) + str(datetime.datetime.now().month) + str(datetime.datetime.now().year)

# bugünkü xmli indir
# url = 'http://www.modacelikler.com/index.php?do=catalog/output&pCode=2134241870'
# urllib.request.urlretrieve(url, 'index.xml')


productsOld = addProducts('index_old.xml')
productsNew = addProducts('index.xml')
productsOld.sort(key=myFunc)
productsNew.sort(key=myFunc)
i = 0
cikarilacaklarList = []
indirimegirenlerList = []
indirimibitenlerList = []
fiyatidegisenlerList = []
stoguazalanlarList = []
stoguartanlarList = []

for product in productsOld:
    kont = False
    kont1 = False
    kont2 = False
    kont3 = False
    i += 1
    for productNew in productsNew:
        if product["stok kodu"] == productNew["stok kodu"]:
            kont = True
            if product['product type'] != 'variable':
                if product["indirimli fiyat"] == productNew["indirimli fiyat"]:
                    kont1 = True
                if kont1 == False:
                    if product["indirimli fiyat"] > productNew["indirimli fiyat"] or product["indirimli fiyat"] == 0.0:
                        indirimegirenlerList.append({"stok kodu": product["stok kodu"],
                                                     "eski fiyat": product["indirimli fiyat"],
                                                     "yeni fiyat": round(float(productNew["indirimli fiyat"])+float(productNew["indirimli fiyat"])*float(productNew["vergi"]/100), 2)})
                    else:
                        indirimibitenlerList.append({"stok kodu": product["stok kodu"],
                                                     "eski fiyat": product["indirimli fiyat"],
                                                     "yeni fiyat": round(float(productNew["indirimli fiyat"])+float(productNew["indirimli fiyat"])*float(productNew["vergi"])/100, 2)})
                if product["fiyat"] == productNew["fiyat"]:
                    kont2 = True
                if kont2 == False:
                    fiyatidegisenlerList.append({"stok kodu": product["stok kodu"],
                                                 "Eski fiyat": product["fiyat"],
                                                 "Yeni fiyat": productNew["fiyat"]})
            if product["stok"] == productNew["stok"]:
                kont3 = True
            if kont3 == False:
                if product["stok"] > productNew["stok"]:
                    stoguazalanlarList.append({"stok kodu": product["stok kodu"],
                                               "eski stok": product["stok"],
                                               "yeni stok": productNew["stok"]})
                else:
                    stoguartanlarList.append({"stok kodu": product["stok kodu"],
                                              "eski stok": product["stok"],
                                              "yeni stok": productNew["stok"]})
            break
    if kont == False:
        cikarilacaklarList.append({"stok kodu": product["stok kodu"]})

i = 0
ekleneceklerList = []
for productNew in productsNew:
    kont = False
    i += 1
    for product in productsOld:
        if product["stok kodu"] == productNew["stok kodu"]:
            kont = True
#            print("ok " + str(i))
            break
    if kont == False:
        ekleneceklerList.append({"stok kodu": productNew["stok kodu"]})
print('\033[1m' + "Çıkarılacak ürünler:" + '\033[0m')
print(*cikarilacaklarList, sep='\n')
print('\033[1m' + "Eklenecek ürünler:" + '\033[0m')
print(*ekleneceklerList, sep='\n')
print('\033[1m' + "indirime girenler:" + '\033[0m')
print(*indirimegirenlerList, sep='\n')
print('\033[1m' + "indirimi bitenler:" + '\033[0m')
print(*indirimibitenlerList, sep='\n')
print('\033[1m' + "fiyatı değişenler:" + '\033[0m')
print(*fiyatidegisenlerList, sep='\n')
print('\033[1m' + "stogu azalanlar:" + '\033[0m')
print(*stoguazalanlarList, sep='\n')
print('\033[1m' + "stogu artanlar:" + '\033[0m')
print(*stoguartanlarList, sep='\n')
# dünkü xmli archive taşı
# shutil.move('index_old.xml', 'xml_archive/stock_' + today + '.xml')
# bugünkü xmli işlenmiş xml dosyası yap
# os.rename('index.xml', 'index_old.xml')