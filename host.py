'''
@Time    : 2019/12/16 12:48
@Author  : wmy
'''
import copy
import random
import time
import pandas as pd
from phe import paillier


class host:
    def __init__(self, num):
        self.num = num  # 原图图顶点数量
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=128)  # 同态加密公钥，秘钥

    def get_paillier_public_key(self):
        return self.public_key

    def get_paillier_private_key(self):
        return self.private_key

    def get_label_dict(self, G):
        """
       获取标签数字典
       :param G:
       :return: label_dict
       """
        label_dict = []
        for node, data in G.nodes(True):
            dict_list = []
            for neighbor in G.neighbors(node):  # 对顶点的所有邻居标签分组求和
                sub_dict_list = G.nodes[neighbor]['label']
                for item in sub_dict_list:
                    dict_list.append(item)  # 所有邻居的label
            dict_list_df = pd.DataFrame(dict_list)
            dict_list_df = dict_list_df.groupby('community').sum()
            dict_list_df.reset_index(inplace=True)  # 分组求和
            dict_list_df = pd.DataFrame(dict_list_df.values.T, index=dict_list_df.columns, columns=dict_list_df.index)
            dict_list = dict_list_df.to_dict()
            neighbor_label_dict_list = []
            for i in dict_list:  # 转成列表
                neighbor_label_dict_list.append(dict_list[i])
            new_array = [0.0 for x in range(self.num)]  # 维度为原图顶点数的单个向量，初始为0
            for item_dict in neighbor_label_dict_list:
                item_community = item_dict['community']
                item_weight = item_dict['weight']
                new_array[int(item_community)] = item_weight  # 更新顶点对应标签及其权重
            sub_dict = {'node': node, 'label_weight': new_array}
            label_dict.append(sub_dict)
        return label_dict

    @staticmethod
    def get_intersect_dict(label_dict, intersect_ids):
        """
        获取相交顶点的标签数字典
        :param label_dict:
        :param intersect_ids:
        :return: intersect_dict
        """
        intersect_dict = []
        for node in intersect_ids:
            # print(node)
            for item in label_dict:
                item_node = int(item['node'])
                if int(node) == item_node:
                    intersect_dict.append(item)
        return intersect_dict

    def send_intersect_dict(self, intersect_dict):
        """
        交集顶点和标签数加密并发送给coordinator
        :param self:
        :param intersect_dict:
        :return: intersect_dict
        """
        encrypt_time = 0  # 单次迭代加密时间
        intersect_dict = copy.deepcopy(intersect_dict)
        for item in intersect_dict[:]:
            item_label_weight = item['label_weight']
            begin_time = time.time()
            item_label_weight = [self.public_key.encrypt(x) for x in item_label_weight]
            end_time = time.time()
            encrypt_time += (end_time - begin_time)
            item['label_weight'] = item_label_weight
        print("host send message to coordinator ...")
        return intersect_dict, encrypt_time

    def update_intersect_nodes(self, G, intersect_dict, v):
        """
        更新交集顶点标签
        :param self:
        :param G:
        :param intersect_dict:
        :param v:
        """
        begin_time = time.time()
        intersect_dict = copy.deepcopy(intersect_dict)
        decrypt_time = 0  # 单次迭代解密时间
        intersect_up_num = 0  # 更新标签数量
        # 解密交集顶点标签权重
        for item in intersect_dict:
            item_node = item['node']
            item_label_weight = item['label_weight']
            dec_begin_time = time.time()
            item_label_weight = [self.private_key.decrypt(x) for x in item_label_weight]
            dec_end_time = time.time()
            decrypt_time += (dec_end_time - dec_begin_time)
            item_label_weight = self.normalize(item_label_weight)  # 对标签权权重向量做归一化处理
            max_weight = max(item_label_weight)  # 找到最大权重值
            if max_weight < 1 / float(v):  # 如果最大标签权重小于1/v,则从值为max_weight的索引中随机选取一个标签置1，其余全部置0,
                idx_list = []  # 值为max_weight的索引下标（即为标签）
                for i in range(len(item_label_weight)):
                    if item_label_weight[i] == max_weight:
                        idx_list.append(i)
                choice_index = random.choice(idx_list)  # 值为max_weight的索引下标（即为标签）中随机选取一个，数量置为1,其余置0
                for i in range(len(item_label_weight)):
                    if i == choice_index:
                        item_label_weight[i] = 1.0
                    else:
                        item_label_weight[i] = 0.0
            else:  # 如果最大标签权重大于 1/v,则将小于1/v的标签权重置0, 其余归一化处理
                for i in range(len(item_label_weight)):
                    if item_label_weight[i] < 1 / float(v):
                        item_label_weight[i] = 0.0
                item_label_weight = self.normalize(item_label_weight)  # 归一化处理
            item['label_weight'] = item_label_weight
            dict_list = []
            for i in range(len(item_label_weight)):
                if item_label_weight[i] != 0.0:
                    sub_dict = {'community': i, 'weight': item_label_weight[i]}
                    dict_list.append(sub_dict)
            G.nodes[item_node]["label"] = dict_list  # 更新G的顶点的标签以及权重
            intersect_up_num += 1
        end_time = time.time()
        intersect_up_time = (end_time - begin_time - decrypt_time)  # 单次迭代标签更新时间
        return decrypt_time, intersect_up_time, intersect_up_num

    def update_remain_nodes(self, G, label_dict, intersect_ids, v):
        """
        更新非交集顶点标签
        :param self:
        :param G:
         :param label_dict:
        :param intersect_ids:
        :param v:
        """
        remain_up_num = 0
        begin_time = time.time()
        for item in label_dict:
            item_node = item['node']
            item_label_weight = item['label_weight']
            if int(item_node) not in intersect_ids:
                item_label_weight = self.normalize(item_label_weight)  # 对标签权权重向量做归一化处理
                max_weight = max(item_label_weight)  # 找到最大权重值
                if max_weight < 1 / float(v):  # 如果最大标签权重小于1/v,则从值为max_weight的索引中随机选取一个标签置1，其余全部置0,
                    idx_list = []  # 值为max_weight的索引下标（即为标签）
                    for i in range(len(item_label_weight)):
                        if item_label_weight[i] == max_weight:
                            idx_list.append(i)
                    choice_index = random.choice(idx_list)  # 值为max_weight的索引下标（即为标签）中随机选取一个，数量置为1,其余置0
                    for i in range(len(item_label_weight)):
                        if i == choice_index:
                            item_label_weight[i] = 1.0
                        else:
                            item_label_weight[i] = 0.0
                else:  # 如果最大标签权重大于 1/v,则将小于1/v的标签权重置0, 其余归一化处理
                    for i in range(len(item_label_weight)):
                        if item_label_weight[i] < 1 / float(v):
                            item_label_weight[i] = 0.0
                    item_label_weight = self.normalize(item_label_weight)  # 归一化处理
                item['label_weight'] = item_label_weight
                dict_list = []
                for i in range(len(item_label_weight)):
                    if item_label_weight[i] != 0.0:
                        sub_dict = {'community': i, 'weight': item_label_weight[i]}
                        dict_list.append(sub_dict)
                G.nodes[item_node]["label"] = dict_list  # 更新G的顶点的标签以及权重
                remain_up_num += 1
        end_time = time.time()
        remain_up_time = (end_time - begin_time)  # 其余节点更新时间
        return remain_up_time, remain_up_num

    @staticmethod
    def normalize(item_label_weight):
        """
        标签数量的归一化处理
        :param item_label_weight:
        :return:
        """
        sum_num = sum(item_label_weight)
        item_label_weight = [x / sum_num for x in item_label_weight]
        return item_label_weight
