import json, csv, re, os
from bs4 import BeautifulSoup

def json_html_to_dom(json_key, html_content):
    """ Convert JSON key/value pair with HTML content to a DOM object using BeautifulSoup. """
    # Wrap the HTML content with the JSON key as the root tag
    dom = BeautifulSoup(f"<{json_key}>{html_content}</{json_key}>", 'lxml')
    return dom

def main():
    # Ensure the program is running in the same file as expected
    os.chdir(os.path.dirname(__file__))
    validation = False
    attempts = 0
    # Load JSON data
    while not validation:
        try: # Try to open JSON file
            with open(input("enter file: "), 'r') as file:
                print("reading file")
                json_obj = json.load(file)
                validation = True
        except FileNotFoundError:
            if attempts == 4: # Loop breaker if file cannot be found after 5 attempts
                print("404 - File Not Found")
                exit()
            else:
                attempts+=1
    
    # Extract HTML data from JSON
    for key, value in json_obj.items():
        if key == "fullContent":
            dom = json_html_to_dom(key, value)
            main_content = dom.find('div', class_ = 'requirement-content')
            breadcrumbs = dom.find('div', class_ = 'breadCrumbs')
            try: 
                version_div = main_content.find('div', class_ = 'VersionNumber')
            except:
                print ("Section not found")
    
    # Use the page breadcrumbs to identify the country and product.
    path = f'MICOR_Data'
    locations = breadcrumbs.find_all('a')[1:]
    print(len(locations))
    for i in range(0, len(locations)):
        print(locations[i])
        locations[i] = re.sub("<[^<>]+>",'', str(locations[i]))
        locations[i] = re.sub(" ",'_', str(locations[i]))
        path += f'/{locations[i]}' # Generate file path of any produce... hopefully


# Create folders for the pages/products if nonexistant
    if (os.path.exists(path) == False):
        os.makedirs(f'{path}/CSV')


# Check if there is a previous record, get it if exists
    version = 'null'
    if (os.path.exists(f'{path}/previous_scrape.json')):
        with open(f'{path}/previous_scrape.json', 'r') as file:
            prev_obj = json.load(file)
        for k, v in prev_obj.items():
            if k == 'version':
                version = json_html_to_dom(k, v).find('div', class_= 'VersionNumber')
    
# Create JSON for version if it doesn't exist or needs to be updated
    if (version != 'null' and version == version_div):
        exit() # If no changes, nothing required so program ends
    else:
        with open(f'{path}/previous_scrape.json', 'w') as f:
            vers = {'version':str(version_div), 'content':str(main_content)}
            json.dump(vers, f) # Store as JSON for version validation

        with open(f'{path}/{locations[1]}_{locations[0]}_fullcontent.txt', 'w') as f:
            mainText = str(main_content)
            f.write(mainText) # Write full HTML for cross validation

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
        
        # Replace tables in HTML with references to the relevent files
        count=0
        for table in tables:
            table_label = re.sub("<[^<>]+>",'', str(table.find('caption')))

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

        # Print page content to text file
        section_titles = main_content.find_all('h3')[1:]
        sections = main_content.find_all('div', class_ = 'collapsefaq-content')[1:]
        print(len(sections))
        with open(f'{path}/{locations[1]}_{locations[0]}.txt', 'w') as file:
            text = ''
            for i in range(len(sections)):
                text += f'{section_titles[i]}\n{sections[i]}\n'
                text = re.sub("&amp;",'&',text)
                text = re.sub("<[^<>]+>",'\n',text)
            file.write(text)\
        
        # Legacy code for sending the HTML tables to a JSON 
        '''dictionary = dict() 
        text = ''
        for i in range(len(tables)):
            with open(f'{path}/{locations[1]}_{locations[0]}_htmltable.json', 'w') as file:
                text += str(tables[i])
                key = f'table{i}'
                dictionary.update({key:text})
                print(len(dictionary))
                json.dump(dictionary, file)'''




if __name__ == "__main__":
    main()