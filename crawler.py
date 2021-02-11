import requests
from bs4 import BeautifulSoup
import pprint


def get_links_to_crawl(base_url, limit):
    '''
    Obtains the links needed to make the crawl.
    Input:
        base_url(str): Main url to start the search of the urls to crawl. 
        E.g: "https://inmuebles.metroscubicos.com/"

        limit(int): Number of items to be crawled.
        E.g: 10
    Output: 
        links_list(list): List of links needed to crawl.
    '''
    page = requests.get(base_url)
    soup = BeautifulSoup(page.text, "html.parser")
    list_of_properties = soup.find(id="searchResults").find_all(
    "li", class_=False, limit=limit
    )
    links_per_page = len(list_of_properties)   
    property_links = []
    for property_ in list_of_properties:
        property_links.append(property_.a.get("href"))
    
    while len(property_links) < limit:
        limit_remained = limit - len(property_links)
        next_page = soup.find('a', class_="andes-pagination__link prefetch").get('href')
        page = requests.get(next_page)
        soup = BeautifulSoup(page.text, "html.parser")
        list_of_properties = soup.find(id="searchResults").find_all(
        "li", class_=False, limit=limit_remained
        )
        for property_ in list_of_properties:
            property_links.append(property_.a.get("href"))

    print(f"All {len(property_links)} links obtained!")
    return property_links


def normalize_li_tags(tags):
    normalized_list = []
    for tag in tags:
        normalized_list.append(tag.text)
    return normalized_list

def write_file(content):
    f = open("homes.txt", "w")
    f.write(content)
    f.close()

def crawl_info(links_to_crawl):
    collected_data = []
    for iterator, property_url in enumerate(links_to_crawl):
        property_page = requests.get(property_url)
        property_soup = BeautifulSoup(property_page.text, "html.parser")
        property_name = property_soup.find(
            "div", class_="vip-product-info__development__info"
        ).h1.text
        property_full_address = property_soup.find("h2", class_="map-location").text
        property_first_image = (
            property_soup.find("div", id="short-description-gallery")
            .ul.find("li")
            .img.get("src")
        )
        property_price = (
            property_soup.find("div", class_="vip-product-info__development__info")
            .find("strong")
            .text
        )
        property_size = (
            property_soup.find("section", class_="vip-product-info__attributes")
            .ul.find("li")
            .find("span")
            .text
        )
        amenities_tag = property_soup.find("ul", class_="boolean-attribute-list")
        
        if amenities_tag: 
            amenities =  amenities_tag.find_all("li")
            property_amenities = normalize_li_tags(amenities)
        else:
            property_amenities = ''
        
        property_description = property_soup.find("pre", class_="preformated-text").text

        property_dict = {
            'id': iterator,
            'name': property_name,
            'price': property_price,
            'address': property_full_address,
            'size': property_size,
            'amenities': property_amenities,
            'image': property_first_image,
            'description': property_description
        }
        collected_data.append(property_dict)
    # Write content
    write_file(str(collected_data))


if __name__ == "__main__":
    links_to_crawl = get_links_to_crawl('https://inmuebles.metroscubicos.com/propiedades-individuales/', 150)
    crawl_info(links_to_crawl)
