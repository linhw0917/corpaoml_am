'''
@Time    : 2019/12/16 12:45
@Author  : wmy
'''
import operator
import time
import networkx as nx


from graph.community_detection.corpaoml_am.coordinator import Coordinator
from graph.community_detection.corpaoml_am.guest import Guest
from graph.community_detection.corpaoml_am.host import Host
from statistics.intersect.driver import Intersect
# from graph.community_detection.utils import overlapping_modularity


class driver:

    @staticmethod
    def read_graph(edge_path):
        """
       读取边集生成图,将顶点标签设置为顶点索引
       :param edge_path:
       :return: g
       """
        g = nx.read_edgelist(edge_path, nodetype=int)
        # 初始化使所有节点的标签为其本身，标签权重设为1.0
        for node, data in g.nodes(True):
            label_dict = dict()
            label_dict[node] = 1.0
            data['label'] = label_dict
        return g

    @staticmethod
    def get_intersect_ids(G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, j):
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
        map = [node1_list, node2_list, node3_list, node4_list, node5_list, node6_list, node7_list, node8_list,
               node9_list, node10_list]
        intersect = Intersect()
        intersect_ids = []
        for i in range(0, 10):
            if (i != j):
                intersect_ids0 = intersect.run(map[j], map[i])
                intersect_ids = list(set(intersect_ids0) | set(intersect_ids))
        intersect_ids = [int(x) for x in intersect_ids]  # 转成int
        return intersect_ids


    def run(self, G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, v, save_path):
        """
        执行入口
        :param save_path:
        :param G1:
        :param G2:
        :param v:
        :param save_path:
        """
        begin_time = time.time()
        intersect_ids = [x for x in range(0, 10)]
        for i in range(10):
            intersect_ids[i] = self.get_intersect_ids(G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, i)  # 交集顶点
        end_time = time.time()
        # print(intersect_ids)
        id_match_time = (end_time - begin_time)  # 获取交集顶点时间
        # g1_node_num = len(g1.nodes())
        # g2_node_num = len(g2.nodes())
        node_num = 1000  # 原图的顶点个数

        # 初始化 host, guest, coordinator对象
        host = Host(node_num)
        guest = Guest(node_num)
        coordinator = Coordinator(node_num)
        params = dict()
        poly_modulus_degree = 4096  # poly_modulus_degree of ckks
        power = 60  # power for scale of ckks
        params['poly_modulus_degree'] = poly_modulus_degree
        params['power'] = power
        host.params_init(params)  # host加密参数初始化
        # guest和coordinator加密参数初始化
        # if encrypted_scheme == 'paillier':  # paillier加密方案
        #     guest.set_public_key(host.get_public_key())
        #     guest.set_private_key(host.get_private_key())
        # elif encrypted_scheme == 'ckks':  # ckks加密方案
        #     guest.set_scale(host.get_scale())
        #     guest.set_public_key(host.get_public_key())
        #     guest.set_private_key(host.get_private_key())
        #     guest.set_encoder(host.get_encoder())
        #     guest.set_encryptor(host.get_encryptor())
        #     guest.set_decryptor(host.get_decryptor())
        #     coordinator.set_evaluator(host.get_evaluator())
        guest.set_scale(host.get_scale())
        guest.set_public_key(host.get_public_key())
        guest.set_private_key(host.get_private_key())
        guest.set_encoder(host.get_encoder())
        guest.set_encryptor(host.get_encryptor())
        guest.set_decryptor(host.get_decryptor())
        coordinator.set_evaluator(host.get_evaluator())

        forward = []  # 保存上一次迭代每个社区的节点数
        iterate_times = 0  # 迭代次数
        encrypt_time = 0  # 加密总时间
        decrypt_time = 0  # 解密总时间
        while True:  # 开始迭代
            print("iterate_times====",iterate_times)
            backward = []  # 保存本轮迭代每个社区的节点数
            iterate_times += 1  # 迭代次数加1
            # t = [x for x in range(0, 10)]
            map = [G1, G2, G3, G4, G5, G6, G7, G8, G9, G10]
            n_list = [intersect_ids[0], intersect_ids[1], intersect_ids[2], intersect_ids[3], intersect_ids[4],
                                    intersect_ids[5], intersect_ids[6], intersect_ids[7], intersect_ids[8], intersect_ids[9]]
            host_label_dict = host.get_label_dict(map[0])
            guest_label_dict=[x for x in range(9)]
            for i in range(9):
                guest_label_dict[i]=guest.get_label_dict(map[i+1])

            guest_intersect_dict = [x for x in range(0, 9)]
            host_intersect_dict = host.get_intersect_dict(host_label_dict, intersect_ids[0])
            for j in range(9):
                guest_intersect_dict[j] = guest.get_intersect_dict(guest_label_dict[j], n_list[j+1])

            # 加密相交顶点的标签权重并发送到coordinator
            host_intersect_dict, host_encrypt_time = host.send_intersect_dict(host_intersect_dict)
            for j in range(0, 9):
                guest_intersect_dict[j], guest_encrypt_time = guest.send_intersect_dict(guest_intersect_dict[j])
                # print(host_intersect_dict)
                # print(guest_intersect_dict)

            # coordinator对顶点加密标签字典求和并返回求和之后的加密标签字典
            intersect_dict0=[x for x in range(0, 10)]
            intersect_dict1=[x for x in range(0, 10)]
            intersect_dict0[0]=host_intersect_dict
            for i in range(1,10):
                intersect_dict0[i]=guest_intersect_dict[i-1]

            for i in range(10):
                for j in range(10):
                    if i != j:
                        intersect_dict1[i] = coordinator.send_intersect_dict(intersect_dict0[i],intersect_dict0[j])
                # print(encrypted_intersect_dict)

                # host,guest各自更新标签
            host_decrypt_time = host.label_propagate(map[0], intersect_dict1[0], host_label_dict,
                                                         intersect_ids[0], v)
            guest_decrypt_time=0
            for i in range(1,10):
                guest_decrypt_time += guest.label_propagate(map[i],intersect_dict1[i],guest_label_dict[i-1],intersect_ids[i],v)

            encrypt_time += host_encrypt_time  # 累加host，guest加密时间
            decrypt_time += host_decrypt_time +  guest_decrypt_time# 累加host，guest解密时间
            # t[i]=map1
            # for i in range(10):
            #
            #     # 分别获取host,guest各自顶点的标签权重字典
            #     map = [G1, G2, G3, G4, G5, G6, G7, G8, G9, G10]
            #     n_list = [intersect_ids[0], intersect_ids[1], intersect_ids[2], intersect_ids[3], intersect_ids[4],
            #               intersect_ids[5], intersect_ids[6], intersect_ids[7], intersect_ids[8], intersect_ids[9]]
            #     host_label_dict = host.get_label_dict(map[i])
            #     map1 = map[i]
            #     intersect_ids1 = n_list[i]
            #     del map[i]
            #     del n_list[i]
            #     v_label = [x for x in range(0, 9)]
            #     for j in range(0, 9):
            #         v_label[j] = guest.get_label_dict(map[j])
            #     # print(host_label_dict)
            #     # print(guest_label_dict)
            #
            #     # 分别获取host,guest各自相交顶点的标签权重字典
            #     guest_intersect_dict = [x for x in range(0, 9)]
            #     host_intersect_dict = host.get_intersect_dict(host_label_dict, intersect_ids1)
            #     for j in range(0, 9):
            #         guest_intersect_dict[j] = guest.get_intersect_dict(v_label[j], n_list[j])
            #     # print(host_intersect_dict)
            #     # print(guest_intersect_dict)
            #
            #     # 加密相交顶点的标签权重并发送到coordinator
            #     host_intersect_dict, host_encrypt_time = host.send_intersect_dict(host_intersect_dict)
            #     for j in range(0, 9):
            #         guest_intersect_dict[j], guest_encrypt_time = guest.send_intersect_dict(guest_intersect_dict[j])
            #     # print(host_intersect_dict)
            #     # print(guest_intersect_dict)
            #
            #     # coordinator对顶点加密标签字典求和并返回求和之后的加密标签字典
            #     for j in range(0, 9):
            #         # if i!=j:
            #         host_intersect_dict = coordinator.send_intersect_dict(host_intersect_dict,guest_intersect_dict[j])
            #     # print(encrypted_intersect_dict)
            #
            #     # host,guest各自更新标签
            #     host_decrypt_time = host.label_propagate(map1, host_intersect_dict, host_label_dict,
            #                                              intersect_ids1, v)
            #     t[i]=map1
            #     # guest_decrypt_time = guest.label_propagate(g2, encrypted_intersect_dict, guest_label_dict,
            #     #                                            intersect_nodes, v)
            #     # encrypt_time += (host_encrypt_time + guest_encrypt_time)  # 累加host，guest加密时间
            #     decrypt_time += host_decrypt_time   # 累加host，guest解密时间
            # G1 = t[0]
            # G2 = t[1]
            # G3 = t[2]
            # G4 = t[3]
            # G5 = t[4]
            # G6 = t[5]
            # G7 = t[6]
            # G8 = t[7]
            # G9 = t[8]
            # G10 = t[9]
            # 根据划分的社区合并两个子图顶点
            communities = coordinator.get_communities(map)
            for i in communities:
                backward.append(len(i))
            # 连续两次迭代社区内节点数目不变 或者迭代次数大于30此，则停止迭代
            if operator.eq(backward, forward) or iterate_times > 30:
                print('community_num ： ', len(backward))
                print('iterate_times ： ', iterate_times)
                print('id_match_time ：', id_match_time)
                print('encryption_time ：', encrypt_time)
                print('decryption_time ：', decrypt_time)
                break
            else:
                forward = backward.copy()
        # 保存划分的社区
        coordinator.save_communities(communities, save_path)

    # @staticmethod
    # def parse_args():
    #     """
    #     获取命令行参数
    #     :return:parser
    #     """
    #     parser = argparse.ArgumentParser(description='run corpaoml_am')  # 初始化parser
    #     parser.add_argument('-es', type=str, choices=['paillier', 'ckks'], default='paillier', nargs=1,
    #                         dest='encrypted_scheme', help='choose encryption scheme from paillier or ckks', )  # 加密方案
    #     parser.add_argument('-kl', type=int, choices=[128, 256, 512, 1024], default=1024, nargs='?',
    #                         dest='key_length', help='key length of paillier', )  # paillier秘钥长度
    #     parser.add_argument('-pmd', type=int, choices=[2048, 4096, 8192], default=4096, nargs='?',
    #                         dest='poly_modulus_degree',
    #                         help='poly_modulus_degree of ckks', )  # ckks poly_modulus_degree
    #     parser.add_argument('-power', type=int, default=60, nargs='?', dest='power',
    #                         help='power for scale of ckks', )  # ckks scale
    #     parser.add_argument('-files', type=str, nargs=2, help='path of subgraphs', )  # 子图路径
    #     return parser.parse_args()  # 返回parser


# if __name__ == '__main__':
#     begin_time = time.time()
#     app = driver()
#     v = 2
#     # args = app.parse_args()  # 获取命令行参数
#     params = dict()  # 存储加密参数
#     # if args.encrypted_scheme[0] == 'paillier':  # paillier加密方案
#     #     print('=============================paillier======================================')
#     #     key_length = args.key_length  # paillier秘钥长度
#     #     params['key_length'] = key_length
#     # elif args.encrypted_scheme[0] == 'ckks':  # ckks加密方案
#         print('=============================ckks======================================')
#         poly_modulus_degree = 2048  # poly_modulus_degree of ckks
#         power = 60  # power for scale of ckks
#         params['poly_modulus_degree'] = poly_modulus_degree
#         params['power'] = power
#     # files = args.files  # 子图路径集
#     # g1 = app.read_graph(files[0])
#     # g2 = app.read_graph(files[1])
#
#     # 划分的社区保存路径
#     # profix1 = os.path.dirname(files[0]) + '/'
#     # profix2 = str(os.path.basename(files[0]).split('.')[0])
#     # community_path = profix1 + 'corpaoml_am_' + profix2 + '_community.txt'
#     # edge_path = '../../../../../dataset/test/lesmis.txt'
#     # g = nx.read_edgelist(edge_path)
#     # app.run(args.encrypted_scheme[0], params, g1, g2, v, community_path)
#     # 计算重叠模块度
#     com = overlapping_modularity.load_corpa(community_path)
#     mod = overlapping_modularity.cal_EQ(com, g)
#     print('重叠模块度 : ', mod)
#     end_time = time.time()
#     print('执行总时长 : ', end_time - begin_time)
