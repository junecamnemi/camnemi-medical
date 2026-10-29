#!/usr/bin/env python3
"""Refresh feed/amc-feed.json from AMC's own public sources.

Sources (public, no keys):
  * AMC English newsroom list   https://news-en.amc.seoul.kr/news/eng/list.do
  * AMC YouTube channel RSS     https://www.youtube.com/feeds/videos.xml?channel_id=UC08tP3KIyCK9vYNZm5qQuiw

Safety rules (Camnemi legal constraint: no patient stories / testimonials):
  * Headlines/videos matching DENY patterns are dropped and listed in `excluded`.
  * If a source fails or returns nothing, the previous items for that source are kept.
Run:  python tools/update_feed.py [path/to/amc-feed.json]
"""
import html, json, re, sys, urllib.request, datetime, pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'feed' / 'amc-feed.json'
UA = {'User-Agent': 'Mozilla/5.0 (CamnemiFeedBot; +https://medical.camnemi.com)'}
NEWS_LIST = 'https://news-en.amc.seoul.kr/news/eng/list.do'
NEWS_BASE = 'https://news-en.amc.seoul.kr'
YT_CHANNEL = 'UC08tP3KIyCK9vYNZm5qQuiw'
YT_RSS = f'https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL}'
MAX_NEWS, MAX_VIDEOS = 6, 6

DENY = re.compile(
    r'(travels? .* to korea|receives?|undergo|patient from|patient story|saved|survivor|recovers?|'
    r'life.?saving|\brates?\b|survival|mortality|success|\bcure[ds]?\b|\d+\s?%|child (attacked|from)|\bboy\b|\bgirl\b|real ?story|testimonial|'
    r'리얼스토리|후기|사연|완치|환자 이야기|치료 후|수술 후)', re.I)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


def parse_news(page):
    items = []
    for m in re.finditer(r'<li>\s*<a href="(/news/eng/detail\.do\?cntId=(\d+))"[^>]*>(.*?)</a>\s*</li>', page, re.S):
        body = m.group(3)
        d = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', body)
        t = re.search(r'<strong>(.*?)</strong>', body, re.S)
        if not (d and t):
            continue
        title = html.unescape(re.sub(r'<[^>]+>', '', t.group(1)).replace('&nbsp;', ' '))
        title = re.sub(r'\s+', ' ', title).strip()
        items.append({'id': int(m.group(2)), 'date': f'{d.group(1)}-{d.group(2)}-{d.group(3)}',
                      'title': title, 'url': NEWS_BASE + m.group(1)})
    return items


def parse_videos(xml):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    out = []
    for e in ET.fromstring(xml).findall('a:entry', ns):
        vid = e.find('yt:videoId', ns).text
        out.append({'id': vid, 'title': e.find('a:title', ns).text.strip(),
                    'published': e.find('a:published', ns).text[:10],
                    'url': f'https://www.youtube.com/watch?v={vid}'})
    return out


def split(items):
    keep, drop = [], []
    for it in items:
        (drop if DENY.search(it['title']) else keep).append(it)
    return keep, drop


def main():
    prev = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    feed = {'news': prev.get('news', []), 'videos': prev.get('videos', [])}
    excluded, errors = [], []
    try:
        keep, drop = split(parse_news(get(NEWS_LIST)))
        if keep:
            feed['news'] = keep[:MAX_NEWS]
        excluded += [{'src': 'news', 'title': x['title']} for x in drop]
    except Exception as e:
        errors.append(f'news: {e!r}')
    try:
        keep, drop = split(parse_videos(get(YT_RSS)))
        if keep:
            feed['videos'] = keep[:MAX_VIDEOS]
        excluded += [{'src': 'video', 'title': x['title']} for x in drop]
    except Exception as e:
        errors.append(f'video: {e!r}')
    feed['updated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    feed['channel'] = {'youtube': f'https://www.youtube.com/channel/{YT_CHANNEL}', 'newsroom': 'https://news-en.amc.seoul.kr/news/eng/main.do'}
    feed['excluded'] = excluded
    feed['errors'] = errors
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(feed, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'news={len(feed["news"])} videos={len(feed["videos"])} excluded={len(excluded)} errors={errors}')
    for x in excluded:
        print('  excluded:', x['src'], '|', x['title'][:90])


if __name__ == '__main__':
    main()
