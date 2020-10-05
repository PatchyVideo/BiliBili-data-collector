main_tags = {
    '东方MMD': 'MMD.3D',
    '剧情MMD': 'MMD.3D',
    '舞蹈MMD': 'MMD.3D',
    '东方3D': 'MMD.3D',
    '游戏': '游戏',
    '东方FTG': '游戏',
    '东方STG': '游戏',
    '音乐游戏': '游戏',
    'mugen': '游戏',
    '我的世界': '游戏',
    '实况': '游戏',
    '攻略': '游戏',
    '跑团': '游戏',
    '音乐': '音乐',
    '东方Arrange': '音乐',
    '东方风Arrange': '音乐',
    '东方PV': '音乐',
    'XFD': '音乐',
    '音乐短片': '音乐',
    '演奏': '音乐',
    '东方手书': '手书',
    '漫画': '手书',
    '动画': '手书',
    '有配音': '手书',
    'Walfas': '手书',
    'MAD': 'MAD/AMV',
    'AMV': 'MAD/AMV',
    '音MAD': '音MAD',
    '鬼畜': '音MAD',
    '东方杂谈': '科普/杂谈/考据',
    '东方科普': '科普/杂谈/考据',
    '东方考据': '科普/杂谈/考据',
    '访谈': '科普/杂谈/考据',
    '电台': '科普/杂谈/考据',
    '排行': '科普/杂谈/考据',
    '线下活动': '线下活动相关',
    '角色扮演': '线下活动相关',
    '绘画过程': '绘画/手工艺',
    '手工艺': '绘画/手工艺',
    '虚拟主播': 'VTuber',
    '图集': '绘画/手工艺'
}

import requests
import re
from bson.json_util import loads, dumps
from datetime import datetime, timedelta
# excel读写模块
import xlrd
from xlutils.copy import copy


def post_raw(url, payload):
    headers = {'content-type': 'text/plain; charset=utf-8'}
    return requests.post(url, data=payload, headers=headers)


def post_json(url, json_obj_or_string):
    if not isinstance(json_obj_or_string, str):
        payload = dumps(json_obj_or_string)
    else:
        payload = json_obj_or_string
    headers = {'content-type': 'application/json; charset=utf-8'}
    cookies = {'session': 'ffef4674%2C1616122597%2C09dfa*91'}
    return requests.post(url, data=payload, headers=headers, cookies=cookies)


cur_time = datetime.now()
week_time = (cur_time - timedelta(days=7)).strftime("%Y-%m-%d")
cur_time = cur_time.strftime("%Y-%m-%d")

query = f"site:bilibili date:>={week_time} date:<{cur_time}"
print(f"Bilibili videos from {week_time}UTC to {cur_time}UTC")

video_list = post_json('https://thvideo.tv/be/queryvideo.do', {
    'query': query,
    'page': 1,
    'page_size': 10000,
    'human_readable_tag': True,
    'language': 'CHS'
}).json()['data']

count = video_list["count"]
videos = video_list["videos"]

VIDEO_URL_MATCHERS = {
    r"((https:\/\/|http:\/\/)?(www\.)?bilibili\.com\/video\/av[\d]+|b23.tv/[\w\d]+)": 'bilibili',
    r"(https:\/\/|http:\/\/)?(www\.)?acfun\.cn\/v\/ac[\d]+": 'acfun',
    r"(https:\/\/|http:\/\/)?(www\.)?nicovideo\.jp\/watch\/(s|n)m[\d]+": 'nicovideo',
    r"((https:\/\/)?(www\.|m\.)?youtube\.com\/watch\?v=[-\w]+|https:\/\/youtu\.be\/(watch\?v=[-\w]+|[-\w]+)|youtu\.be\/[-\w]+)": 'youtube',
    r"(https:\/\/)?(www\.|mobile\.)?twitter\.com\/[\w]+\/status\/[\d]+": 'twitter',
    r"(https:\/\/|http:\/\/)?music\.163\.com\/song\?id=\d+": 'wangyiyun',
    r"ac[\d]+": 'acfun',
    r"av[\d]+": 'bilibili',
    r"th\d{3,}": 'thv',
    r"(s|n)m[\d]+": 'nicovideo',
    r"youtube-[-\w]+": 'youtube'
}
URL_MATCHER = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def replace_urls(txt):
    for vid_url_matcher, site in VIDEO_URL_MATCHERS.items():
        txt = re.sub(vid_url_matcher, f'VIDURLSITEfsghjugfasduAA{site}', txt)
    txt = re.sub(URL_MATCHER, '', txt)
    return txt


def cut_for_search(txt):
    resp = post_raw('http://127.0.0.1:5005/s/', txt.encode('utf-8'))
    txt = resp.content.decode('utf-8')
    words = loads(txt)['Words']
    return words


from collections import defaultdict

class_count_map = defaultdict(int)
repost_count_map = defaultdict(int)

for vid in videos:
    """
    视频分类
    """
    tags = vid['tags_readable']
    video_class = set()
    for tag in tags:
        if tag in main_tags:
            video_class.add(main_tags[tag])
    video_class = list(video_class)
    for tag in video_class:
        class_count_map[tag] += 1
    if len(video_class) == 0:
        class_count_map['其他'] += 1
    """
    视频转载
    """
    desc = vid['item']['desc']
    desc_words = cut_for_search(replace_urls(desc))
    first_words = desc_words[:5]
    vid_site = ''
    for w in first_words:
        if 'vidurlsitefsghjugfasduaa' in w:
            vid_site = w[len('vidurlsitefsghjugfasduaa'):]
            break
    if not vid_site:
        for idx, word in enumerate(desc_words):
            if 'vidurlsitefsghjugfasduaa' in word:
                word_prior = desc_words[idx - 3] + desc_words[idx - 2] + desc_words[idx - 1]
                if ('原' in word_prior or '源' in word_prior) and '原创' not in word_prior:
                    vid_site = word[len('vidurlsitefsghjugfasduaa'):]
                    break
    if vid_site not in ['nicovideo', 'youtube', 'twitter', 'wangyiyun', 'acfun', 'thv']:
        vid_site = '原创'
    repost_count_map[vid_site] += 1
    # print(f'{vid["item"]["title"]} => {video_class}')

print(f'总视频数: {count}')

print("\n视频分类分析")
for (k, v) in class_count_map.items():
    print(f'{k} => {v}')

print("\n转载视频分析")
for (k, v) in repost_count_map.items():
    print(f'{k} => {v}')

def editExcelFile():
    file = r'input.xls'
    # 读文件
    readFile = xlrd.open_workbook(file)
    DataSheet = readFile.sheet_by_index(0)
    Dataname = DataSheet.name
    startRow = DataSheet.nrows

    # 写文件
    writeFile = copy(readFile)
    DataSheet = writeFile.get_sheet(Dataname)
    DataSheet.write(startRow, 0, cur_time)
    DataSheet.write(startRow, 1, count)
    index = 2
    for (k, v) in class_count_map.items():
        DataSheet.write(startRow, index, v)
        index += 1
    for (k, v) in repost_count_map.items():
        DataSheet.write(startRow, index, v)
        index += 1

    # 存文件
    writeFile.save(file)

editExcelFile()
