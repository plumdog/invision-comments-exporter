import requests
from bs4 import BeautifulSoup
import json
import itertools
import csv
import io
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')

    args = parser.parse_args()

    url = args.url

    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html5lib')
    config_script = soup.find_all('script', id='config')[0]
    config_raw = config_script.contents[0].strip()
    config_raw = config_raw.lstrip('window.config = JSON.parse( "').rstrip('" );')
    config_ready = config_raw.encode('utf8').decode('unicode-escape')
    config = json.loads(config_ready)

    comments = config['comments']
    by_screen = {screen_id: list(comments) for screen_id, comments in itertools.groupby(sorted(comments, key=lambda c: c['screenID']), lambda c: c['screenID'])}

    screens = sorted(config['screens'], key=lambda s: s['sort'])

    rows = []

    for screen in screens:
        comments = by_screen.get(screen['id']) or []
        by_conv = {conv_id: list(comments) for conv_id, comments in itertools.groupby(sorted(comments, key=lambda c: (c['conversationID'], c['createdAt'])), key=lambda c: c['conversationID'])}
        for i, commentGroup in enumerate(by_conv.values(), start=1):
            for comment in commentGroup:
                row = {
                    'screen': screen['sort'],
                    'comment': i,
                    'user': comment['userName'],
                    'text': comment['comment'],
                    'link': f'{url}/{screen["id"]}/comments/{comment["conversationID"]}',
                }
                rows.append(row)

    f = io.StringIO()
    writer = csv.DictWriter(f, ['screen', 'comment', 'user', 'text', 'link'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    print(f.getvalue())

if __name__ == '__main__':
    main()
