"""
@Time    : 2019/12/16 12:43
@Author  : wmy
"""

import collections
from seal import *


class Coordinator:

    def __init__(self, num):
        self.num = num  # 原图顶点数量

    def set_evaluator(self, evaluator):
        self.evaluator = evaluator

    def get_evaluator(self):
        return self.evaluator

    def send_intersect_dict(self,  host_intersect_dict, guest_intersect_dict):
        """
         # 分组求和
        :param encrypted_scheme:
        :param host_intersect_dict:
        :param guest_intersect_dict:
        :return: encrypted_intersect_dict-对应顶点标签权重相加之后的加密状态交集字典
        """
        for host_key, host_value in host_intersect_dict.items():
            for guest_key, guest_value in guest_intersect_dict.items():
                if host_key == guest_key:
                    encrypted_label_weight_vector = Ciphertext()
                    self.evaluator.add(host_value, guest_value, encrypted_label_weight_vector)  # 密文相加
                    host_intersect_dict[host_key] = encrypted_label_weight_vector
                    break
        print("coordinator send message to host ...")
        print("coordinator send message to guest ...")
        return host_intersect_dict

    @staticmethod
    def get_communities(t):
        ids = []
        # list2 = []
        communities = collections.defaultdict(lambda: list())
        for G in t:
            for node, data in G.nodes(True):
                label_dict = data["label"]
                for key, value in label_dict.items():
                    communities[key].append(node)
                    # print()
        for i in communities.values():
            id = list(set(i))
            ids.append(id)
        #        print('communities.values()',communities.values())
        print('ids:', ids)
        return ids

    #     for node in G.nodes(True):
    #         label_dict = node[1]["label"]
    #         for item in label_dict:
    #             community = item['community']
    #             weight = item['weight']
    #             communities[community].append(node[0])
    # list1 = list(communities.values())
    # for x in range(len(list1)):
    #     for y in range(len(list1)):
    #         if (y > x):
    #             if (set(list1[x]).issubset(list1[y])):
    #                 list2.append(list1[x])
    #                 break
    #             elif (set(list1[y]).issubset(list1[x])):
    #                 list2.append(list1[y])
    #                 break
    # for m in list2:
    #     if (m in list1):
    #         list1.remove(m)
    #
    # for i in list1:
    #     id = list(set(i))
    #     ids.append(id)
    #     end_time = time.time()
    # print("ids=====",ids)
    # return ids

    @staticmethod
    def save_communities(communities, save_path):
        """
        保存社区
        :param communities:
        :param save_path:
        :return:
        """
        output_file = open(save_path, 'w')
        for cmu in communities:
            for member in cmu:
                output_file.write(str(member) + " ")
            output_file.write("\n")
        output_file.close()
        return
