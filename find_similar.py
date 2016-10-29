import csv
import jieba

CAMPANY_NAME = '客户名称'
CONFIDENCE_THRESHOLD = 0.2
MAX_MATCH = 5


class Campany():

    def __init__(self, info_dict):
        self.name = info_dict[CAMPANY_NAME]
        self.info = info_dict
        self.words = jieba.lcut_for_search(self.name)


class Find_similar():

    def __init__(self):
        self.words_freq = {}
        self.truth = []
        self.input = []

    def calc_confidence(self, list_a, list_b):
        result = 0
        for word in set(list_a).intersection(set(list_b)):
            result += self.words_freq[word]
        return result

    def init_truth(self, file_path):
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
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                campany = Campany(row)
                self.input.append(campany)

    def do_find(self):
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
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in result:
                input_campany_name = row['campany'].name
                for match in row['match']:
                    writer.writerow([input_campany_name, match[
                                    'campany'].name, match['confidence']])
if __name__ == '__main__':
    f = Find_similar()
    f.init_truth('target.csv')
    f.init_input('originSheet1.csv')
    result = f.do_find()
    f.write_to_file(result, 'out.csv')
