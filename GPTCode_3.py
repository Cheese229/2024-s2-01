import json, csv, re, os
from bs4 import BeautifulSoup

def json_html_to_dom(json_key, html_content):
    """ Convert JSON key/value pair with HTML content to a DOM object using BeautifulSoup. """
    # Wrap the HTML content with the JSON key as the root tag
    dom = BeautifulSoup(f"<{json_key}>{html_content}</{json_key}>", 'lxml')
    return dom

def txt_html_to_dom(fname):
    dom = BeautifulSoup(fname)
    return dom

def main():
    # Example JSON key/value pair containing HTML content

    with open('C:\\VS Code\\Capstone\\response_1725867868418.json', 'r') as file:
        json_obj = json.load(file)
    
    # Load JSON data
    for key, value in json_obj.items():
        if key == "fullContent":
            dom = json_html_to_dom(key, value)
            main_content = dom.find('div', class_ = 'requirement-content')
            breadcrumbs = dom.find('div', class_ = 'breadCrumbs')
            try: 
                version_div = main_content.find('div', class_ = 'VersionNumber')
            except:
                print ("Section not found")
    
    locations = breadcrumbs.find_all('a')[1:]
    for i in range(0, 2):
        locations[i] = re.sub("<[^<>]+>",'', str(locations[i]))
        locations[i] = re.sub(" ",'_', str(locations[i]))


# Create folders for the pages/products if nonexistant
    path = f'{locations[1]}/{locations[0]}'
    if (os.path.exists(path) == False):
        os.makedirs(f'{path}/CSV')



    if (os.path.exists(f'{path}/previous_scrape.json')):
        with open(f'{path}/previous_scrape.json', 'r') as file:
            prev_obj = json.load(file)
        for k, v in prev_obj.items():
            if k == 'version':
                version = json_html_to_dom(k, v).find('div', class_= 'VersionNumber')


    
# Create JSON for version if it doesn't exist or needs to be updated
    if (version == version_div):
        exit()
    else:
        with open(f'{path}/previous_scrape.json', 'w') as f:
            dict = {'version':str(version_div), 'content':str(main_content)}
            json.dump(dict, f) # Store as JSON for version validation

        table_names = []
        tables = main_content.find_all('table')

        for table_index, table in enumerate(tables):
            with open(f'{path}/CSV/{locations[1]}_{table_index + 1}.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Extract table headers
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                if headers:
                    writer.writerow(headers)
                
                # Extract table rows
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        writer.writerow(row_data)
                
                table_names.append(f'{path}/CSV/{locations[1]}_{table_index + 1}.csv')

        count=0
        for table in tables:
            table_label = re.sub("<[^<>]+>",'', str(table.find('caption')))

            #print(table_label)
            new_div = dom.new_tag('div')

            new_label = dom.new_tag('p')
            if table_label != "None":
                new_label.string = table_label
            else: 
                new_label.string = "Unlabelled table"

            new_ref = dom.new_tag('p')
            new_ref.string = f'See {table_names[count]}'

            new_div.append(new_label)
            new_div.append(new_ref)

            table.replace_with(new_div)
            count+=1


        section_titles = main_content.find_all('h3')[1:]
        #print(len(section_titles))
        sections = main_content.find_all('div', class_ = 'collapsefaq-content')[1:]
        print(len(sections))
        
        
        with open(f'{path}/{locations[1]}_{locations[0]}.txt', 'w') as file:
            text = ''
            for i in range(len(sections)):
                text += f'{section_titles[i]}\n{sections[i]}\n'
                text = re.sub("&amp;",'&',text)
                text = re.sub("<[^<>]+>",'\n',text)
            file.write(text)




if __name__ == "__main__":
    main()