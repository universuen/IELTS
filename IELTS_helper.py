import re
import os
import random
import time
import http.client
import hashlib
import json
import urllib


def baidu_translate(content):
    appid = ''
    secretKey = ''
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content
    fromLang = 'auto'  # 源语言
    toLang = 'zh'  # 翻译后的语言
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
        dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst
    except Exception as e:
        pass
    finally:
        if httpClient:
            httpClient.close()


class IELTS:
    def __init__(self, n: int = 10, username: str = ''):
        # 每次测n个单词，count用来记录本次待测单词数
        self.username = username
        self.count = n
        # 读取本地词库lexicon
        fo = open('lexicon.txt', 'r')
        self.lexicon = fo.read().splitlines()
        # "word_翻译" -> "(word, 翻译)"
        for i in range(len(self.lexicon)):
            word = re.search(r'(.*)~', self.lexicon[i])
            translation = re.search(r'~(.*)', self.lexicon[i])
            self.lexicon[i] = word.groups('1') + translation.groups('1')
        # 获取新的词库new_words
        new_lists = self.get_new_list()
        self.new_words = self.get_new_words(new_lists)
        if len(self.new_words) > 0:
            # 更新本地词库
            self.lexicon = self.lexicon + self.new_words
            print('本次共新增'+str(len(self.new_words))+'个单词! 继续加油哦~')
        else:
            self.new_words = []
        fo.close()
        # 获取错题本
        self.relearn = self.get_relearn()
        # 获取待学本
        self.ready_to_learn = self.get_ready_to_learn()
        # 测试单词
        self.test_words()
        # 测完之后统一保存
        fo = open('lexicon.txt', 'w+')
        for i in self.lexicon:
            fo.write(i[0] + '~' + i[1] + '\n')
        fo.close()
        fo = open('need_to_relearn.txt', 'w+')
        for i in self.relearn:
            fo.write(i[0] + '~' + i[1] + '\n')
        fo.close()
        fo = open('ready_to_learn.txt', 'w+')
        for i in self.ready_to_learn:
            fo.write(i[0] + '~' + i[1] + '\n')
        fo.close()


    def get_ready_to_learn(self):
        fo = open('ready_to_learn.txt', 'r')
        data = fo.read().splitlines()
        for i in range(len(data)):
            word = re.search(r'(.*)~', data[i])
            translation = re.search(r'~(.*)', data[i])
            data[i] = word.groups('1') + translation.groups('1')
        fo.close()
        return data

    def get_relearn(self):
        fo = open('need_to_relearn.txt', 'r')
        data = fo.read().splitlines()
        for i in range(len(data)):
            word = re.search(r'(.*)~', data[i])
            translation = re.search(r'~(.*)', data[i])
            data[i] = word.groups('1') + translation.groups('1')
        fo.close()
        return data

    def get_new_list(self):
        file_names = os.listdir('./word_lists')
        fo = open('list_names.txt', 'r')
        current_names = fo.read().splitlines()
        for i in current_names:
            i = i.strip('\n')
        new_names = []
        fo.close()
        for i in file_names:
            if i not in current_names:
                new_names.append(i)
                current_names.append(i)
        # 有新词汇表，重写词汇表清单
        if len(new_names) > 0:
            fo = open('list_names.txt', 'w+')
            for i in current_names:
                fo.write(i + '\n')
        fo.close()
        return new_names

    def get_new_words(self, new_lists: list):
        result = []
        if len(new_lists) == 0:
            return result
        print("发现新单词！正在导入中......")
        # 获取新单词，存到data中
        for i in new_lists:
            fo = open('./word_lists/' + i, 'r', encoding='utf-8')
            content = fo.read()
            data = re.findall(r'([a-zA-Z].*)', content)
            # 删除没用的词汇
            for j in data:
                if ('.' in j) or ('XMind' in j):
                    data.remove(j)
            # 把data中的单词翻译一下得到最终结果
            for j in data:
                result.append(tuple([j, baidu_translate(j)]))
            fo.close()
        os.system('cls')
        return result

    def test_words(self):
        # 首先对用户进行亲切的问候
        print('Hey ' + self.username + '! Have a nice day!\nHere is today\'s test (●\'◡\'●)')
        while self.count >= 0:
            # 如果错题本里边有单词，优先测试错题本中的单词
            if len(self.relearn) > 0:
                for i in self.relearn:
                    print(i[0] + '的意思是?\n')
                    # 生成正确选项的序号
                    right_order = random.randint(0, 3)
                    right_answer = i[1]
                    for j in range(4):
                        if j < right_order:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                        elif j == right_order:
                            print(str(right_order + 1) + '.' + right_answer)
                        else:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                    choice = input('请输入序号')
                    if (int(choice) == right_order + 1):
                        print('Nice choice!')
                        self.relearn.remove(i)
                    else:
                        print("不太对哦，正确答案应该是:" + right_answer)
                        print("再认真记一遍，下次还考你哦！")
                    self.count -= 1
                    if self.count < 0:
                        break
                    time.sleep(1)
                    os.system('cls')
            # 错题本中没单词就看看有没有新单词可以测
            elif len(self.ready_to_learn) > 0:
                for i in self.ready_to_learn:
                    print(i[0] + '的意思是?\n')
                    # 生成正确选项的序号
                    right_order = random.randint(0, 3)
                    right_answer = i[1]
                    for j in range(4):
                        if j < right_order:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                        elif j == right_order:
                            print(str(right_order + 1) + '.' + right_answer)
                        else:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                    choice = input('请输入序号')
                    if (int(choice) == right_order + 1):
                        print('Nice choice!')
                    else:
                        print("不太对哦，正确答案应该是:" + right_answer)
                        print("再认真记一遍，下次还考你哦！")
                        self.relearn.append(i)
                    self.ready_to_learn.remove(i)
                    self.count -= 1
                    if self.count < 0:
                        break
                    time.sleep(1)
                    os.system('cls')
            # emm,再测就只能测背过的单词了
            else:
                temp_list = self.lexicon
                random.shuffle(temp_list)
                for i in temp_list:
                    print(i[0] + '的意思是?\n')
                    # 生成正确选项的序号
                    right_order = random.randint(0, 3)
                    right_answer = i[1]
                    for j in range(4):
                        if j < right_order:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                        elif j == right_order:
                            print(str(right_order + 1) + '.' + right_answer)
                        else:
                            temp = random.randint(0, len(self.lexicon) - 1)
                            while self.lexicon[temp][1] == right_answer:
                                temp = random.randint(0, len(self.lexicon) - 1)
                            print(str(j + 1) + '.' + self.lexicon[temp][1])
                    choice = input('请输入序号')
                    if (int(choice) == right_order + 1):
                        print('Nice choice!')
                    else:
                        print("不太对哦，正确答案应该是:" + right_answer)
                        print("再认真记一遍，下次还考你哦！")
                        self.relearn.append(i)
                    self.count -= 1
                    if self.count < 0:
                        break
                    time.sleep(1)
                    os.system('cls')
        print('恭喜你完成了今天的测试！再接再厉喔！')
        os.system('pause')
