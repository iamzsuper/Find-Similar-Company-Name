"""查找相似公司名
公司名可能会不规范，如“格力电器公司”；当归档录入时需要将公司名规范化，如前例需要修正为
“珠海格力电器股份有限公司”。

此程序旨在自动化此查找过程，提供需要修正的公司名（不规范）集合，以及规范的公司名集合，此
程序会在规范的公司名集合中寻找与需要修正的公司名最为匹配的值。由于计算机并不能绝对确定两公司名
对应同一公司，因此程序运行输出结果还需要手动核对，但工作量相对非常小。

程序采用了倒排索引的思想。对规范的公司名集合逐个分词后，以词出现的频率的倒数作为权重；对每个
不规范的公司名，分词后逐个与规范公司名分词比较，词相同则权重增加；最终得到一系列匹配度，排序
后即得到最匹配的公司名。
"""
"""
输入：规范的公司名集合csv文件，需要修正的公司名集合csv文件。
输出：需要修正的公司名集合及可能的匹配公司名csv文件。
"""
"""
用到的第三方库：jieba （https://github.com/fxsjy/jieba）

在Python 3.5.2 x64下测试通过。
"""
import csv
import jieba

CAMPANY_NAME = '客户名称'  # csv文件公司名列名
CONFIDENCE_THRESHOLD = 0.2  # confidence最小值，通常为0.2
MAX_MATCH = 5  # 最多显示可能公司名


class Campany():
"""公司类
"""

    def __init__(self, info_dict):
        """
        name：公司名
        info：公司相关信息
        words：公司名分词结果
        """
        self.name = info_dict[CAMPANY_NAME]
        self.info = info_dict
        self.words = jieba.lcut_for_search(self.name)


class Find_similar():
"""主类
读取文件，查找公司名等
"""

    def __init__(self):
        """
        words_freq：词频
        truth：规范的公司list
        input：需要修正的公司list
        """
        self.words_freq = {}
        self.truth = []
        self.input = []

    def calc_confidence(self, list_a, list_b):
        """计算匹配度
        """
        result = 0
        for word in set(list_a).intersection(set(list_b)):
            result += self.words_freq[word]
        return result

    def init_truth(self, file_path):
        """读取规范的公司名集合csv文件
        将公司实例化为Campany，保存至truth
        同时计算词频，即权重
        """
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                campany = Campany(row)
                self.truth.append(campany)
                for word in campany.words:
                    if not word in self.words_freq:
                        self.words_freq[word] = 0
                    self.words_freq[word] += 1
        for (key, value) in self.words_freq.items():
            self.words_freq[key] = 1 / value

    def init_input(self, file_path):
        """读取需要修正的公司名集合csv文件
        将公司实例化为Campany，保存至input
        """
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                campany = Campany(row)
                self.input.append(campany)

    def do_find(self):
        """查找匹配相似公司名
        对每个input中需要修正的公司名，遍历规范的公司名集合
        计算匹配度
        返回：
        [
            {
                'campany':input_Campany_0,
                'match':[
                    {
                        'campany':truth_Campany_a,
                        'confidence':d.dd
                    },
                    {
                        'campany':truth_Campany_b,
                        'confidence':d.dd
                    },
                    ...
                ]
            },
            {
                'campany':input_Campany_1,
                'match':[
                    {
                        'campany':truth_Campany_c,
                        'confidence':d.dd
                    },
                    {
                        'campany':truth_Campany_d,
                        'confidence':d.dd
                    },
                    ...
                ]
            },
            ...
        ]
        """
        result = []
        for input_campany in self.input:
            row = {
                'campany': input_campany,
                'match': []
            }
            confs = {}
            for index, truth_campany in enumerate(self.truth):
                conf = self.calc_confidence(
                    input_campany.words, truth_campany.words)
                confs[index] = conf
            confs_sort = sorted(confs, key=lambda k: confs[k], reverse=True)
            for index in confs_sort[:MAX_MATCH]:
                confidence = confs[index]
                if confidence > CONFIDENCE_THRESHOLD:
                    row['match'].append({
                        'campany': self.truth[index],
                        'confidence': confidence
                    })
            result.append(row)
        return result

    def write_to_file(self, result, output_file_path):
        """输出结果到文件
        将do_find()的结果输出到文件
        此处可以自定义格式
        """
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in result:
                input_campany_name = row['campany'].name
                if row['match']:
                    first_match = row['match'][0]
                    writer.writerow([input_campany_name, first_match[
                                    'campany'].name, first_match['confidence']])
                for match in row['match'][1:]:
                    writer.writerow(['', match[
                                    'campany'].name, match['confidence']])
if __name__ == '__main__':
    f = Find_similar()
    f.init_truth('target.csv')
    f.init_input('originSheet1.csv')
    result = f.do_find()
    f.write_to_file(result, 'out.csv')
