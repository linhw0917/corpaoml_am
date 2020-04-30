'''
@Time    : 2019/12/16 12:45
@Author  : wmy
'''
import operator
import time

import networkx as nx

from graph.community_detection.corpaoml_am.coordinator import coordinator
from graph.community_detection.corpaoml_am.guest import guest
from graph.community_detection.corpaoml_am.host import host
from statistics.intersect.driver import Intersect


class driver:

    @staticmethod
    def read_graph(edge_path):
        """
       根据边集读图,将顶点标签设置为顶点序号
       :param edge_path:
       :return: 图
       """
        G = nx.read_edgelist(edge_path)
        # 初始化使所有节点的标签为其本身，社区权重设为1
        for node, data in G.nodes(True):
            dict_list = []
            sub_dict = {'community': node, 'weight': 1.0}
            dict_list.append(sub_dict)
            data['label'] = dict_list
        return G

    @staticmethod
    def get_intersect_ids(G1, G2):
        """
        获取顶点交集
        :param G1:
        :param G2:
        :return: 顶点交集
        """
        node1_list = G1.nodes()
        node2_list = G2.nodes()
        intersect = Intersect()
        intersect_ids = intersect.run(node1_list, node2_list)
        # print("intersect_ids=", intersect_ids)
        intersect_ids = [int(x) for x in intersect_ids]  # 转成int
        # print("intersect_ids0=",intersect_ids)
        return intersect_ids

    def run(self, G1, G2, v, save_path):
        """
        执行入口
        :param save_path:
        :param G1:
        :param G2:
        :param v:
        :param save_path:
        """
        begin_time = time.time()
        intersect_ids = self.get_intersect_ids(G1, G2)  # 交集顶点
        end_time = time.time()
        id_match_time = (end_time - begin_time)  # 获取交集顶点时间
        g1_node_num = len(G1.nodes())
        g2_node_num = len(G2.nodes())
        node_num = g1_node_num + g2_node_num - len(intersect_ids)  # 原图的顶点个数
        # print("node_num=",node_num)
        # 初始化 host, guest, coordinator
        _host = host(node_num)
        _guest = guest(_host.get_paillier_public_key(), _host.get_paillier_private_key(), node_num)
        _coordinator = coordinator(node_num)

        forward = []  # 保存前向每个社区的节点数
        iterate_times = 0  # 迭代次数
        encrypt_time = 0  # 加密时间
        decrypt_time = 0  # 解密时间
        update_time = 0  # 标签更新时间
        update_num = 0  # 更新标签数量
        while True:  # 迭代更新标签
            backward = []  # 保存后向每个社区的节点数
            iterate_times += 1  # 迭代次数加1

            # 分别获取host,guest各自顶点的标签数量字典
            _host_label_dict = _host.get_label_dict(G1)
            _guest_label_dict = _guest.get_label_dict(G2)
            # print("1=",_host_label_dict)
            # print(_guest_label_dict)

            # 分别获取host,guest各自相交顶点的标签数字典
            print(type(intersect_ids))
            _host_intersect_dict = _host.get_intersect_dict(_host_label_dict, intersect_ids)
            _guest_intersect_dict = _guest.get_intersect_dict(_guest_label_dict, intersect_ids)
            # print("2=",_host_intersect_dict)
            # print(_guest_intersect_dict)

            # 加密相交顶点的标签数并发送到coordinator
            _host_intersect_dict, _host_encrypt_time = _host.send_intersect_dict(_host_intersect_dict)
            _guest_intersect_dict, _guest_encrypt_time = _guest.send_intersect_dict(_guest_intersect_dict)
            # print(_host_intersect_dict)
            # print(_guest_intersect_dict)

            # coordinator对顶点的加密标签数量字典求和并返回求和之后的加密标签数量字典
            intersect_dict = _coordinator.send_intersect_dict(_host_intersect_dict, _guest_intersect_dict)
            # print(intersect_dict)

            # host,guest各自更新标签

            _host_decrypt_time, _host_intersect_up_time, _host_intersect_up_num = \
                _host.update_intersect_nodes(G1, intersect_dict, v)
            _host_remain_up_time, _host_remain_up_num = \
                _host.update_remain_nodes(G1, _host_label_dict, intersect_ids, v)
            _host_up_time = (_host_intersect_up_time + _host_remain_up_time)  # 累加更新时间
            _host_up_num = (_host_intersect_up_num + _host_remain_up_num)  # 累加更新标签个数

            _guest_decrypt_time, _guest_intersect_up_time, _guest_intersect_up_num = \
                _guest.update_intersect_nodes(G2, intersect_dict, v)
            _guest_remain_up_time, _guest_remain_up_num = \
                _guest.update_remain_nodes(G2, _guest_label_dict, intersect_ids, v)
            _guest_up_time = (_guest_intersect_up_time + _guest_remain_up_time)  # 更新时间
            _guest_up_num = (_guest_intersect_up_num + _guest_remain_up_num)  # 更新标签个数

            encrypt_time += (_host_encrypt_time + _guest_encrypt_time)  # 累加加密时间
            decrypt_time += (_host_decrypt_time + _guest_decrypt_time)  # 累加解密时间
            update_time += (_host_up_time + _guest_up_time)  # 累加标签更新时间
            update_num += (_host_up_num + _guest_up_num)  # 累加更新标签数量

            # 根据划分的社区合并两个子图顶点
            communities = _coordinator.get_communities(G1, G2)
            for i in communities:
                backward.append(len(i))
            # 连续两次迭代社区内节点数目不变
            if operator.eq(backward, forward) or iterate_times > 30:
                print('community_num ： ', len(backward))
                print('iterate_times ： ', iterate_times)
                print('id_match_time ：', id_match_time)
                print('encryption_time ：', encrypt_time)
                print('decryption_time ：', decrypt_time)
                print('update_time:', update_time)
                print('update_num:', update_num)
                break
            else:
                forward = backward.copy()
        # 保存划分的社区
        _coordinator.save_communities(communities, save_path)
