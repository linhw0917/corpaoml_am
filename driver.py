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
    def get_intersect_ids(G1, G2, G3, G4, G5, G6, G7, G8, G9, G10):
        """
        获取顶点交集
        :param G1:
        :param G2:
        :return: 顶点交集
        """
        node1_list = G1.nodes()
        node2_list = G2.nodes()
        node3_list = G3.nodes()
        node4_list = G4.nodes()
        node5_list = G5.nodes()
        node6_list = G6.nodes()
        node7_list = G7.nodes()
        node8_list = G8.nodes()
        node9_list = G9.nodes()
        node10_list = G10.nodes()
        map=[node1_list,node2_list,node3_list,node4_list,node5_list,node6_list,node7_list,node8_list,node9_list,node10_list]
        intersect = Intersect()
        intersect_ids=intersect.run(node9_list,node10_list)
        for i in range(0,8):
            for j in range(i+1,10):
                intersect_ids0=intersect.run(map[i],map[j])
                # print("intersect_ids0=",intersect_ids0)1
                intersect_ids=list(set(intersect_ids0)|set(intersect_ids))#初步的全图交点集
                # print("intersect_ids=", intersect_ids)
        intersection = [[0] for x in range(0, 10)]
        for i in range(0,10):
            intersection[i]=intersect.run(intersect_ids,map[i])#取交得到各个数据集自己的交点集
            intersection[i]=[int(x) for x in intersection[i]]  # 转成int
            # print("intersect_id[i]=",intersection[i])
        # print("intersection===",intersection[1])
        return intersection

    def run(self, G1, G2, G3, G4,G5, G6,G7, G8,G9, G10, v, save_path):
        """
        执行入口
        :param save_path:
        :param G1:
        :param G2:
        :param v:
        :param save_path:
        """
        begin_time = time.time()
        intersect_ids = self.get_intersect_ids(G1, G2,G3, G4,G5, G6,G7, G8,G9, G10)  # 交集顶点
        end_time = time.time()
        # print(intersect_ids)
        id_match_time = (end_time - begin_time)  # 获取交集顶点时间
        g1_node_num = len(G1.nodes())
        g2_node_num = len(G2.nodes())
        g3_node_num = len(G3.nodes())
        g4_node_num = len(G4.nodes())
        g5_node_num = len(G5.nodes())
        g6_node_num = len(G6.nodes())
        g7_node_num = len(G7.nodes())
        g8_node_num = len(G8.nodes())
        g9_node_num = len(G9.nodes())
        g10_node_num = len(G10.nodes())
        node_num=1000
        # node_num = g1_node_num + g2_node_num + g3_node_num + g4_node_num + g5_node_num + g6_node_num + g7_node_num +\
        # g8_node_num + g9_node_num + g10_node_num - intersect_lenth  # 原图的顶点个数
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
            _guest_label_dict1 = _guest.get_label_dict(G2)
            _guest_label_dict2 = _guest.get_label_dict(G3)
            _guest_label_dict3 = _guest.get_label_dict(G4)
            _guest_label_dict4 = _guest.get_label_dict(G5)
            _guest_label_dict5 = _guest.get_label_dict(G6)
            _guest_label_dict6 = _guest.get_label_dict(G7)
            _guest_label_dict7 = _guest.get_label_dict(G8)
            _guest_label_dict8 = _guest.get_label_dict(G9)
            _guest_label_dict9 = _guest.get_label_dict(G10)
            # print("_host_label_dict===",_host_label_dict)
            # print("_guest_label_dict1====",_guest_label_dict1)

            # 分别获取host,guest各自相交顶点的标签数字典
            _host_intersect_dict = _host.get_intersect_dict(_host_label_dict, intersect_ids[0])
            _guest_intersect_dict1 = _guest.get_intersect_dict(_guest_label_dict1, intersect_ids[1])
            _guest_intersect_dict2 = _guest.get_intersect_dict(_guest_label_dict2, intersect_ids[2])
            _guest_intersect_dict3 = _guest.get_intersect_dict(_guest_label_dict3, intersect_ids[3])
            _guest_intersect_dict4 = _guest.get_intersect_dict(_guest_label_dict4, intersect_ids[4])
            _guest_intersect_dict5 = _guest.get_intersect_dict(_guest_label_dict5, intersect_ids[5])
            _guest_intersect_dict6 = _guest.get_intersect_dict(_guest_label_dict6, intersect_ids[6])
            _guest_intersect_dict7 = _guest.get_intersect_dict(_guest_label_dict7, intersect_ids[7])
            _guest_intersect_dict8 = _guest.get_intersect_dict(_guest_label_dict8, intersect_ids[8])
            _guest_intersect_dict9 = _guest.get_intersect_dict(_guest_label_dict9, intersect_ids[9])
            # print("_host_label_dict===", _host_intersect_dict)
            # print("_guest_label_dict1====", _guest_intersect_dict1)

            # 加密相交顶点的标签数并发送到coordinator
            _host_intersect_dict, _host_encrypt_time = _host.send_intersect_dict(_host_intersect_dict)
            _guest_intersect_dict1, _guest_encrypt_time1 = _guest.send_intersect_dict(_guest_intersect_dict1)
            _guest_intersect_dict2, _guest_encrypt_time2 = _guest.send_intersect_dict(_guest_intersect_dict2)
            _guest_intersect_dict3, _guest_encrypt_time3 = _guest.send_intersect_dict(_guest_intersect_dict3)
            _guest_intersect_dict4, _guest_encrypt_time4 = _guest.send_intersect_dict(_guest_intersect_dict4)
            _guest_intersect_dict5, _guest_encrypt_time5 = _guest.send_intersect_dict(_guest_intersect_dict5)
            _guest_intersect_dict6, _guest_encrypt_time6 = _guest.send_intersect_dict(_guest_intersect_dict6)
            _guest_intersect_dict7, _guest_encrypt_time7 = _guest.send_intersect_dict(_guest_intersect_dict7)
            _guest_intersect_dict8, _guest_encrypt_time8 = _guest.send_intersect_dict(_guest_intersect_dict8)
            _guest_intersect_dict9, _guest_encrypt_time9 = _guest.send_intersect_dict(_guest_intersect_dict9)
            # print(_host_intersect_dict)
            # print(_guest_intersect_dict1)

            # coordinator对顶点的加密标签数量字典求和并返回求和之后的加密标签数量字典
            intersect_dict =[_host_intersect_dict,_guest_intersect_dict1,_guest_intersect_dict2,_guest_intersect_dict3\
                              ,_guest_intersect_dict4,_guest_intersect_dict5,_guest_intersect_dict6,_guest_intersect_dict7\
                              ,_guest_intersect_dict8,_guest_intersect_dict9]

            for i in range(0,10):
                for j in range(0,10):
                    if i!=j:
                        intersect_dict[i]=_coordinator.send_intersect_dict(intersect_dict[i],intersect_dict[j])
                # if i==0:
                #     intersect_dict[i]=list(_host.get_intersect_dict(intersect_dict[i], intersect_ids[0]))
                # else:
                #     intersect_dict[i] = list(_guest.get_intersect_dict(intersect_dict[i], intersect_ids[i]))
                # print("intersect_dict[i]=", intersect_dict[i])
            # host,guest各自更新标签

            # print("intersect_dict[0]====",intersect_dict[0])
            _host_decrypt_time, _host_intersect_up_time, _host_intersect_up_num = \
                _host.update_intersect_nodes(G1, intersect_dict[0], v)
            _host_remain_up_time, _host_remain_up_num = \
                _host.update_remain_nodes(G1, _host_label_dict, intersect_ids[0], v)
            _host_up_time = (_host_intersect_up_time + _host_remain_up_time)  # 累加更新时间
            _host_up_num = (_host_intersect_up_num + _host_remain_up_num)  # 累加更新标签个数

            _guest_decrypt_time1, _guest_intersect_up_time1, _guest_intersect_up_num1 = _guest.update_intersect_nodes(G2, intersect_dict[1], v)
            _guest_decrypt_time2, _guest_intersect_up_time2, _guest_intersect_up_num2 =_guest.update_intersect_nodes(G3, intersect_dict[2], v)
            _guest_decrypt_time3, _guest_intersect_up_time3, _guest_intersect_up_num3 = _guest.update_intersect_nodes(G4, intersect_dict[3], v)
            _guest_decrypt_time4, _guest_intersect_up_time4, _guest_intersect_up_num4 =_guest.update_intersect_nodes(G5, intersect_dict[4], v)
            _guest_decrypt_time5, _guest_intersect_up_time5, _guest_intersect_up_num5 =_guest.update_intersect_nodes(G6, intersect_dict[5], v)
            _guest_decrypt_time6, _guest_intersect_up_time6, _guest_intersect_up_num6 =_guest.update_intersect_nodes(G7, intersect_dict[6], v)
            _guest_decrypt_time7, _guest_intersect_up_time7, _guest_intersect_up_num7 =_guest.update_intersect_nodes(G8, intersect_dict[7], v)
            _guest_decrypt_time8, _guest_intersect_up_time8, _guest_intersect_up_num8 =_guest.update_intersect_nodes(G9, intersect_dict[8], v)
            _guest_decrypt_time9, _guest_intersect_up_time9, _guest_intersect_up_num9 =_guest.update_intersect_nodes(G10, intersect_dict[9], v)
            _guest_decrypt_time, _guest_intersect_up_time, _guest_intersect_up_num= \
                _guest_decrypt_time1 + _guest_decrypt_time2 + _guest_decrypt_time3 + _guest_decrypt_time4 + _guest_decrypt_time5\
                + _guest_decrypt_time6 + _guest_decrypt_time7 + _guest_decrypt_time8 + _guest_decrypt_time9, \
                _guest_intersect_up_time1 + _guest_intersect_up_time2 + _guest_intersect_up_time3 + _guest_intersect_up_time4 + _guest_intersect_up_time5 + \
                _guest_intersect_up_time6 +_guest_intersect_up_time7 +_guest_intersect_up_time8 +_guest_intersect_up_time9, \
                _guest_intersect_up_num1 + _guest_intersect_up_num2 + _guest_intersect_up_num3 + _guest_intersect_up_num4 + _guest_intersect_up_num5 + \
                _guest_intersect_up_num6 +_guest_intersect_up_num7 + _guest_intersect_up_num8 + _guest_intersect_up_num9


            _guest_remain_up_time1, _guest_remain_up_num1 = _guest.update_remain_nodes(G2, _guest_label_dict1, intersect_ids[1], v)
            _guest_remain_up_time2, _guest_remain_up_num2 = _guest.update_remain_nodes(G3, _guest_label_dict2, intersect_ids[2], v)
            _guest_remain_up_time3, _guest_remain_up_num3 = _guest.update_remain_nodes(G4, _guest_label_dict3, intersect_ids[3], v)
            _guest_remain_up_time4, _guest_remain_up_num4 = _guest.update_remain_nodes(G5, _guest_label_dict4, intersect_ids[4], v)
            _guest_remain_up_time5, _guest_remain_up_num5 = _guest.update_remain_nodes(G6, _guest_label_dict5, intersect_ids[5], v)
            _guest_remain_up_time6, _guest_remain_up_num6 = _guest.update_remain_nodes(G7, _guest_label_dict6, intersect_ids[6], v)
            _guest_remain_up_time7, _guest_remain_up_num7 = _guest.update_remain_nodes(G8, _guest_label_dict7, intersect_ids[7], v)
            _guest_remain_up_time8, _guest_remain_up_num8 = _guest.update_remain_nodes(G9, _guest_label_dict8, intersect_ids[8], v)
            _guest_remain_up_time9, _guest_remain_up_num9 = _guest.update_remain_nodes(G10, _guest_label_dict9, intersect_ids[9], v)
            _guest_remain_up_time , _guest_remain_up_num = \
            _guest_remain_up_time1 + _guest_remain_up_time2 + _guest_remain_up_time3 + _guest_remain_up_time4 + \
            _guest_remain_up_time5 +_guest_remain_up_time6 + _guest_remain_up_time7 + _guest_remain_up_time8 + _guest_remain_up_time9, \
            _guest_remain_up_num1 + _guest_remain_up_num2 + _guest_remain_up_num3 + _guest_remain_up_num4 + \
            _guest_remain_up_num5 +_guest_remain_up_num6 + _guest_remain_up_num7 + _guest_remain_up_num8 + _guest_remain_up_num9
            _guest_up_time = (_guest_intersect_up_time + _guest_remain_up_time)  # 更新时间
            _guest_up_num = (_guest_intersect_up_num + _guest_remain_up_num)  # 更新标签个数

            encrypt_time += (_host_encrypt_time + _guest_encrypt_time1+\
                             _guest_encrypt_time2+ _guest_encrypt_time3+\
                             _guest_encrypt_time4+ _guest_encrypt_time5+\
                             _guest_encrypt_time6+ _guest_encrypt_time7+\
                             _guest_encrypt_time8+ _guest_encrypt_time9)  # 累加加密时间
            decrypt_time += (_host_decrypt_time + _guest_decrypt_time)  # 累加解密时间
            update_time += (_host_up_time + _guest_up_time)  # 累加标签更新时间
            update_num += (_host_up_num + _guest_up_num)  # 累加更新标签数量

            # 根据划分的社区合并两个子图顶点
            communities = _coordinator.get_communities(G1, G2 , G3, G4 , G5, G6 , G7, G8 , G9, G10)
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
