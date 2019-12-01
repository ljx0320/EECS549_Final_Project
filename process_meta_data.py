import json
import re


def compile_regex(stopwords):
    regex = '|'.join(stopwords)
    return re.compile(regex)


def filter_save(filename, pattern, destination):
    data = []
    filtered_data = []
    with open(filename) as json_file:
        data = json.loads(json_file.read())
    
    for datum in data:
        if not pattern.search(datum['title'].lower()):
            filtered_data.append({'asin': datum['asin'], 'title': datum['title']})
    
    print(len(data))
    print(len(filtered_data))

    with open(destination, 'w') as f:
        json.dump(filtered_data, f)
                

def main():
    stopwords = [
        'logitech', 
        'mouse', 
        'keyboard', 
        'receiver', 
        'controller', 
        'charg',
        'microphone',
        'memory Card',
        'battery',
        'headset',
        'console',
        'cable',
        'replacement',
        'case',
        'pad',
        'adapter',
        'protect',
        'system',
        'membership',
        'joystick',
        'hard disk',
        'amiibo',
        'hard drive']
    pattern = compile_regex(stopwords)
    filename = 'data/processed_meta_data.json'
    destination = 'data/filtered_meta_data.json'
    filter_save(filename, pattern, destination)


if __name__ == "__main__":
    main()
