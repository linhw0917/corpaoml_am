"""
@Time    : 2019/12/16 12:46
@Author  : wmy
"""
import random
import time
from seal import *
from collections import Counter


class Guest:

    def __init__(self, num):
        self.num = num

    def set_public_key(self, public_key):
        self.public_key = public_key

    def get_public_key(self):
        return self.public_key

    def set_private_key(self, private_key):
        self.private_key = private_key

    def get_private_key(self):
        return self.private_key

    def set_scale(self, scale):
        self.scale = scale

    def get_scale(self):
        return self.scale

    def set_encoder(self, encoder):
        self.encoder = encoder

    def get_encoder(self):
        return self.encoder

    def set_encryptor(self, encryptor):
        self.encryptor = encryptor

    def get_encryptor(self):
        return self.encryptor

    def set_decryptor(self, decryptor):
        self.decryptor = decryptor

    def get_decryptor(self):
        return self.decryptor

    def get_label_dict(self, g):
        """
       获取标签权重字典
       :param G:
       :return: label_dict
       """
        node_label_dict = dict()  # 顶点及其标签权重向量 eg:{1:[0.5,0.2],2:[0.1,0.0]}
        for node, data in g.nodes(True):  # eg:G.nodes[node]['label']:{1:0.5,2:0.2}
            union_dict = dict()  # 存储当前顶点所有邻居的标签及其权重
            for neighbor in g.neighbors(node):
                label_dict = g.nodes[neighbor]['label']
                union_dict = dict(Counter(union_dict) + Counter(label_dict))  # 字典合并,相同label的权重相加
            label_weight_vector = [0.0 for x in range(self.num)]  # 维度为原图顶点数的单个向量，初始为0.0
            for key, value in union_dict.items():
                label_weight_vector[key] = value  # 更新顶点对应标签及其权重
            node_label_dict[node] = label_weight_vector
        return node_label_dict

    @staticmethod
    def get_intersect_dict(node_label_dict, intersect_nodes):
        """
        获取交集点的标签权重字典
        :param node_label_dict:
        :param intersect_nodes:
        :return: 交集点的标签权重字典
        """
        intersect_dict = dict()
        for intersect_node in intersect_nodes:
            for key, value in node_label_dict.items():
                if intersect_node == key:
                    intersect_dict[key] = value
        return intersect_dict

    def send_intersect_dict(self, intersect_dict):
        """
        交集顶点的标签权重向量加密并发送给coordinator
        :param self:
        :param encrypted_scheme: 加密方案
        :param intersect_dict:
        :return: 加密的交集顶点标签权重向量

        """
        encrypt_time = 0  # 单次迭代加密时间
        encrypted_intersect_dict = dict()
        for key, value in intersect_dict.items():
            begin_time = time.time()
            encrypted_value = self.encrypt( value)  # 加密权重向量
            end_time = time.time()
            encrypted_intersect_dict[key] = encrypted_value
            encrypt_time += (end_time - begin_time)
        print("guest send message to coordinator ...")
        return encrypted_intersect_dict, encrypt_time

    def label_propagate(self, g, encrypted_intersect_dict, node_label_dict, intersect_nodes, v):
        """
        更新顶点标签及其权重
        :param self:
        :param encrypted_scheme: 加密方案
        :param g: 子图
        :param encrypted_intersect_dict: 加密状态的交集顶点标签字典
        :param node_label_dict: 顶点标签字典
        :param intersect_nodes: 交集顶点雷暴
        :param v:
        :return: decrypt_time

        """
        # 更新交集顶点标签及其权重
        decrypt_time = 0  # 单次迭代解密时间
        for key, value in encrypted_intersect_dict.items():
            dec_begin_time = time.time()  # 解密开始时间
            label_weight_vector = self.decrypt( value)  # 解密向量
            dec_end_time = time.time()  # 解密结束时间
            decrypt_time += (dec_end_time - dec_begin_time)
            label_weight_vector = self.update_label_weight(label_weight_vector, v)  # 更新标签权重向量
            # 更新子图顶点标签及其权重
            label_dict = dict()
            for i in range(len(label_weight_vector)):
                if label_weight_vector[i] != 0.0:
                    label_dict[i] = label_weight_vector[i]
            g.nodes[key]["label"] = label_dict  # 更新g的顶点的标签以及权重

        # 更新非交集顶点标签及其权重
        for key, value in node_label_dict.items():
            if key not in intersect_nodes:
                label_weight_vector = self.update_label_weight(value, v)  # 更新标签权重向量
                # 更新子图顶点标签及其权重
                label_dict = dict()
                for i in range(len(label_weight_vector)):
                    if label_weight_vector[i] != 0.0:
                        label_dict[i] = label_weight_vector[i]
                g.nodes[key]["label"] = label_dict  # 更新g的顶点的标签以及权重
        return decrypt_time

    def update_label_weight(self, item_label_weight, v):
        """
        根据corpa规则处理标签权重向量
        :param item_label_weight: 标签权重向量
        :param v:
        :return: 更新的标签权重向量
        """
        item_label_weight = self.normalize(item_label_weight)  # 对标签权重向量做归一化处理
        max_weight = max(item_label_weight)  # 找到最大权重值
        if max_weight < 1 / float(v):  # 如果所有标签的最大权重值权重小于1/v,则从值为max_weight的索引(标签)中随机选取一个值置1，其余值置0
            idx_list = []  # 值为max_weight的索引下标（即为标签）
            for i in range(len(item_label_weight)):
                if item_label_weight[i] == max_weight:
                    idx_list.append(i)
            choice_index = random.choice(idx_list)  # 值为max_weight的索引下标（即为标签）中随机选取一个，值置为1,其余置0
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
        return item_label_weight

    @staticmethod
    def normalize(item_label_weight):
        """
        向量的归一化处理
        :param item_label_weight:
        :return:
        """
        sum_num = sum(item_label_weight)  # 权重求和
        item_label_weight = [x / sum_num for x in item_label_weight]
        return item_label_weight

    def encrypt(self, item_label_weight):
        """
       无论是paillier还是ckks都封装成加密一个向量
        """
        # if encrypted_scheme == 'paillier':  # paillier向量加密
        #     item_label_weight = [self.get_public_key().encrypt(x) for x in item_label_weight]
        #     return item_label_weight
        # elif encrypted_scheme == 'ckks':  # ckks向量加密
        input_vector = DoubleVector(item_label_weight)
        # 编码
        x_plain = Plaintext()
        self.get_encoder().encode(input_vector, self.scale, x_plain)
        # 加密
        x_encrypted = Ciphertext()
        self.get_encryptor().encrypt(x_plain, x_encrypted)
        return x_encrypted

    def decrypt(self, item_label_weight):
        """
       无论是paillier还是ckks都封装成解密一个向量
        """
        # 解密
        plain_result = Plaintext()
        self.get_decryptor().decrypt(item_label_weight, plain_result)
        # 解码
        decoded_vector = DoubleVector()
        self.get_encoder().decode(plain_result, decoded_vector)
        return decoded_vector
        # if encrypted_scheme == 'paillier':  # paillier向量解密
        #     item_label_weight = [self.get_private_key().decrypt(x) for x in item_label_weight]
        #     return item_label_weight
        # elif encrypted_scheme == 'ckks':  # ckks向量解密
        #     # 解密
        #     plain_result = Plaintext()
        #     self.get_decryptor().decrypt(item_label_weight, plain_result)
        #     # 解码
        #     decoded_vector = DoubleVector()
        #     self.get_encoder().decode(plain_result, decoded_vector)
        #     return decoded_vector
