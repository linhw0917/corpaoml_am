'''
@Time    : 2019/12/16 12:43
@Author  : wmy
'''

import collections
import time


class coordinator:

    def __init__(self, num):
        self.num = num  # 原图顶点数量

    def send_intersect_dict(self, intersect_host_dict, intersect_guest_dict):
        """
         # 分组求和
        :param num:
        :param intersect_host_dict:
        :param intersect_guest_dict:
        :return: 求和之后的交集字典
        """
        # intersect_dict = []
        # print(intersect_host_dict)
        for host_item in intersect_host_dict[:]:
            host_item_node = host_item['node']
            host_item_label_weight = host_item['label_weight']
            # print("host_item_node======", host_item_label_weight)
            for guest_item in intersect_guest_dict[:]:
                guest_item_node = guest_item['node']
                guest_item_label_weight = guest_item['label_weight']
                # print("guest_item_node======", guest_item_label_weight)
                if host_item_node == guest_item_node:
                    # print("host_item_node=====",host_item_label_weight)
                    host_item['label_weight'] = [guest_item_label_weight[i] + host_item_label_weight[i] for i in
                                                   range(0, self.num)]  # 同类标签数量相加
                    # item_intersect_dict = {'node': host_item_node, 'label_weight': intersect_item_label_weight}
                    # intersect_dict.append(item_intersect_dict)
                    # print("intersect_dict====",intersect_dict)
                    break
        print("coordinator send message to host ...")
        print("coordinator send message to guest ...")
        # print("intersect_dict=====",intersect_dict[1])
        return intersect_host_dict

    @staticmethod
    def get_communities(t):
        ids = []
        # list2 = []
        communities = collections.defaultdict(lambda: list())
        for G in t:
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
            for node in G.nodes(True):
                label_dict = node[1]["label"]
                for item in label_dict:
                    community = item['community']
                    weight = item['weight']
                    communities[community].append(node[0])
                    print()
        for i in communities.values():
            id = list(set(i))
            if i not in ids:
                ids.append(id)
        #        print('communities.values()',communities.values())
        print('ids:', ids)
        return ids

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
                output_file.write(member + " ")
            output_file.write("\n")
        output_file.close()
        return
