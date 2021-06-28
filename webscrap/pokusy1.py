import requests
from bs4 import BeautifulSoup as BS
import csv
import sys

def vyber_zoznam_dat(soup_obj):
	seznam_cisel = vyber_cisla_obce(soup)
	seznam_obci = vyber_nazvu_obce(soup)
	seznam_X = vyber_X_obce(soup)

	return list(zip(seznam_cisel, seznam_obci, seznam_X))


def zapis_do_csv(zoznam_dat):
	soubor = input('Nazov suboru (bez suffix): ').strip()
	link = 'https://www.volby.cz/pls/ps2017nss/' + zoznam_dat[0][2]
	resp = requests.get(link)
	hl_soup = BS(resp.text, 'html.parser')
	hlavicka = csv_hlavicka(hl_soup)
	with open(f'{soubor}.csv', 'w', newline='') as file:
		zapis = csv.writer(file)
		zapis.writerow(hlavicka)
		for data in zoznam_dat:
			link = 'https://www.volby.cz/pls/ps2017nss/' + data[2]
			resp = requests.get(link)
			soup = BS(resp.text, 'html.parser')
			vysledky = vyber_vysledky(soup)
			zapis.writerow([data[0], data[1]] + vysledky)


def vyber_cisla_obce(soup_obj):
	td_elements = vyber_elementov(soup_obj, 't1sa1 t1sb1', 't2sa1 t2sb1', 't3sa1 t3sb1')
	td_cisla = []
	for td in td_elements:
		if td.find('a'):
			td_cisla.append(td.find('a').text)
	return td_cisla


def vyber_nazvu_obce(soup_obj):
	td_elements = vyber_elementov(soup_obj, 't1sa1 t1sb2', 't2sa1 t2sb2', 't3sa1 t3sb2')
	nazev_obce = []
	for td in td_elements:
		nazev_obce.append(td.text)
	return nazev_obce

def vyber_X_obce(soup_obj):
	td_elements = vyber_elementov(soup_obj, 't1sa1 t1sb1', 't2sa1 t2sb1', 't3sa1 t3sb1')
	td_links = []
	for td in td_elements:
		if td.find('a'):
			td_links.append(td.find('a').get('href'))
	return td_links


def vyber_elementov(soup_obj, *args):
	td_elementy = []
	for arg in args:
		td_elementy += soup_obj.select(f'td[headers="{arg}"]')
	return td_elementy


def csv_hlavicka(soup_obj):
	hlavicka = ['Kód obce', 'Názov obce', 'Registrovaný voliči', 'Vydané obálky', 'Platné hlasy']
	nazvy_stran = vyber_volebnych_stran(soup_obj)
	return hlavicka + nazvy_stran


def vyber_volebnych_stran(soup_obj):
	td_elements = vyber_elementov(soup_obj, 't1sa1 t1sb2', 't2sa1 t2sb2')
	nazvy_stran = []
	for td in td_elements:
		nazvy_stran.append(td.text)
	return nazvy_stran


def vyber_vysledky(soup_obj):
	return vyber_volici_obalky_hlasy(soup_obj) + vyber_platnych_hlasov(soup_obj)


def vyber_volici_obalky_hlasy(soup_obj):
	info_headers = ['sa2', 'sa3', 'sa6']
	info_values = []
	for info_header in info_headers:
		value_element = soup_obj.find('td', {'headers':f'{info_header}'})
		info_values.append(value_element.text)
	return info_values


def vyber_platnych_hlasov(soup_obj):
	td_elements = vyber_elementov(soup_obj, 't1sa2 t1sb3', 't2sa2 t2sb3')
	platne_hlasy = []
	for td in td_elements:
			platne_hlasy.append(td.text)
	return platne_hlasy


if __name__ == '__main__':
	link = input('Link pre pozadovany okres: ')
	resp = requests.get(link)
	soup = BS(resp.text, 'html.parser')


	data = vyber_zoznam_dat(soup)
	zapis_do_csv(data)
