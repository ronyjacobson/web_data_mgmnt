import requests 
import lxml.html 
import sys


def get_url_doc(url):
    res = requests.get(url) 
    return lxml.html.fromstring(res.content)


def get_data_from_player(file_handler, player_url, cities_d, player_name):
    doc = get_url_doc("http://en.wikipedia.org" + player_url)

    player_birthday = doc.xpath("//table[contains(@class, 'infobox')]//tr[contains(th/text(), 'Date of birth')]/td//span[contains(@class,'player_birthday')]/text()")
    if len(player_birthday) > 0:
        player_birthday = player_birthday[0].encode('utf-8').replace(" ", "_")
        file_handler.write("<http://example.org/"+ player_name +"> <http://example.org/birthDate> <http://example.org/"+ player_birthday +"> .\n")

    player_pos = doc.xpath("//table[contains(@class, 'infobox')]//tr[contains(th/text(), 'Playing position')]/td/a/text()")
    for position_raw in player_pos:
        position = position_raw.encode('utf-8').replace(" ", "_")
        file_handler.write("<http://example.org/"+ player_name +"> <http://example.org/position> <http://example.org/"+ position +"> .\n")

    formt_for_date = "//table[contains(@class, 'infobox')]//tr[contains(th/text(), 'Place of birth')]/td/a[{0}]"

    birth_city_raw_XPath = str.format(formt_for_date, 1)
    birth_contry_raw_XPath = str.format(formt_for_date, 2)

    birth_city_raw = doc.xpath(birth_city_raw_XPath)
    if len(birth_city_raw) > 0:
        birth_city = birth_city_raw[0].xpath("@title")[0].encode('utf-8').replace(" ", "_")
        file_handler.write("<http://example.org/" + player_name +"> <http://example.org/birthPlace> <http://example.org/" + birth_city + "> .\n")

        if birth_city not in cities_d.keys():
            birth_contry_raw = doc.xpath(birth_contry_raw_XPath)
            if len(birth_contry_raw) > 0:
                birth_country = birth_contry_raw[0].xpath("@title")[0].encode('utf-8').replace(" ", "_")
                file_handler.write("<http://example.org/" + birth_city +"> <http://example.org/located_in> <http://example.org/" + birth_country + "> .\n")
                cities_d[birth_city] = birth_contry_raw

            else:
                country_raw = birth_city_raw[0].xpath("../text()")
                if len(country_raw) > 0 :
                    country_raw_text = country_raw[0].split(", ")
                    if len(country_raw_text) > 1:
                        country = country_raw_text[1].encode('utf-8').replace(" ", "_")
                        file_handler.write("<http://example.org/" + birth_city + "> <http://example.org/located_in> <http://example.org/" + country + "> .\n")


def main(argv):
    base_url = "https://en.wikipedia.org/wiki/2016%E2%80%9317_Premier_League"
    
    file_handler = open('question3Aontology.txt', 'a+')
    doc = get_url_doc(base_url)
    league = doc.xpath("//table[contains(@class, 'infobox')]/caption/a/@title")[0].encode('utf-8').replace(' ', '_')
    country = "England"
    file_handler.write("<http://example.org/" + league +"> <http://example.org/country> <http://example.org/" + country + "> .\n")

    cities_d = {}
    doc = get_url_doc(base_url)
    formt_for_date = "//h2/span[contains(text(), 'Teams')]/following::table[1]/tr/td[{0}]/a"

    teams = doc.xpath(str.format(formt_for_date, 1))
    cities = doc.xpath(str.format(formt_for_date, 2))

    try:
        for i in range(0, len(teams)):
            try:
                teami = teams[i]
                team = teami.xpath("text()")[0].encode('utf-8').replace(' ', '_')
                cityi = cities[i]
                city = cityi.xpath("text()")[0].encode('utf-8').replace(' ', '_')
            except IndexError as err:
                print err

            file_handler.write("<http://example.org/"+ team +"> <http://example.org/homeCity> <http://example.org/"+ city +"> .\n")
            file_handler.write("<http://example.org/"+ team +"> <http://example.org/league> <http://example.org/"+ league +"> .\n")

            if city not in cities_d.keys():
                file_handler.write("<http://example.org/"+ city +"> <http://example.org/located_in> <http://example.org/England> .\n")
                cities_d[city] = "England"

            doc = get_url_doc("http://en.wikipedia.org" + teams[i].xpath("@href")[0])
            players = doc.xpath("//h2/span[text() = 'Players and professional staff' or text() = 'Current squad' or text() = 'First team' or text() = 'Players']/following::table[1]//table/tr[contains(@class, 'vcard agent')]/td[4]//a[1]")

            for player_row in players:
                player = player_row.xpath("text()")[0].encode('utf-8').replace(" ", "_")
                file_handler.write("<http://example.org/"+ player +"> <http://example.org/playsFor> <http://example.org/"+ team +"> .\n")
                get_data_from_player(file_handler, player_row.xpath("@href")[0], cities_d, player)
    except IndexError as err:
        print err

if __name__ == "__main__":
    sys.exit(main(sys.argv))
