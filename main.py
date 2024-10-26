import zeyrek
import re
import nltk
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unicodedata import numeric
import pandas as pd

# Gerekli nltk paketlerini indir
nltk.download('punkt')
nltk.download('universal_tagset')

analyzer = zeyrek.MorphAnalyzer()


def find_stem(word):
    if word != 'None':
        root = analyzer.lemmatize(word)
        result= root[0][-1][-1] if root else None
        print(f'{word} kelimesinin kökü : {result}')
        return  result # Eğer kök bulunamazsa None döner
    return 'Nothing'


def translate(word):

    if not word:
        return "Kelimenin kökü bulunamadı"

    # Chrome WebDriver'ı başlat
    driver = webdriver.Chrome()
    try:
        # TDK sözlük sayfasına git
        driver.get("https://sozluk.gov.tr/")
        # Arama çubuğunu bul
        arama_cubugu = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "tdk-srch-input"))
        )

        # Parametre olarak gelen kelimenin kökünü arama çubuğuna gir
        arama_cubugu.send_keys(word)

        # Enter tuşuna basarak arama yap
        arama_cubugu.send_keys(Keys.RETURN)

        # Arama sonuçlarının yüklenmesini bekle ve sonucu bul
        try:
            # İlk anlamı al
            anlam_elemani = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='anlamlar-gts0']"))
            )
            # Sonucu al
            sonuc = anlam_elemani.text
        except:
            sonuc = "Sonuç bulunamadı"
    finally:
        # Tarayıcıyı kapat
        driver.quit()

    # Sonucu döndür
    return sonuc


def remove_uppercase_words(wrd_list):
    return [word for word in wrd_list if not word.isupper()]


def remove_numeric(wrd_list):
    return [word for word in wrd_list if not word.isdigit()]


def remove_punctuation(word_list):
    # Noktalama işaretlerini içermeyen kelimeleri döndüren bir liste oluştur
    translator = str.maketrans('', '', string.punctuation)
    return [word.translate(translator) for word in word_list]


def remove_punctuation_only_elements(word_list):
    # Sadece noktalama işareti içeren öğeleri çıkaran bir liste oluştur
    return [word for word in word_list if not all(char in string.punctuation for char in word)]


with open("txtFile.txt", encoding='utf-8') as file:
    content = file.read()

word_list = content.split()
word_list = remove_uppercase_words(word_list)
word_list = remove_numeric(word_list)
word_list = remove_punctuation_only_elements(word_list)
word_list = remove_punctuation(word_list)
sorted_list = sorted(set(word_list))  # Set ile benzersiz elemanlar ve sorted ile sıralı liste elde edilir

print(sorted_list)

my_dict = {}
new_list=[]
for word in sorted_list:
    root_word=find_stem(word)
    if not root_word in new_list:
        new_list.append(root_word)


for word in new_list:
    my_dict[word] = translate(word)


# my_dict listesini bir pandas DataFrame'e dönüştür
df = pd.DataFrame(list(my_dict.items()), columns=['Kelime', 'Anlam'])

# DataFrame'i bir Excel dosyasına kaydet
df.to_excel('kelimeler.xlsx', index=False)

print("Excel dosyasına kaydedildi.")