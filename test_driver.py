'''
@Time    : 2019/11/23 12:50
@Author  : wmy
'''
import unittest
import networkx as nx

from graph.community_detection.corpaoml_am.driver import driver
from graph.community_detection.utils import overlapping_modularity


class TestDriver(unittest.TestCase):

    def test(self):
        res = []
        for i in range(1):
            app = driver()
            path = '../../multiparty/artificial/n/10/network0.4_1k.txt'
            path_0 = '../../multiparty/artificial/n/10/network0.4_1k_0.txt'
            path_1 = '../../multiparty/artificial/n/10/network0.4_1k_1.txt'
            path_2 = '../../multiparty/artificial/n/10/network0.4_1k_2.txt'
            path_3 = '../../multiparty/artificial/n/10/network0.4_1k_3.txt'
            path_4 = '../../multiparty/artificial/n/10/network0.4_1k_4.txt'
            path_5 = '../../multiparty/artificial/n/10/network0.4_1k_5.txt'
            path_6 = '../../multiparty/artificial/n/10/network0.4_1k_6.txt'
            path_7 = '../../multiparty/artificial/n/10/network0.4_1k_7.txt'
            path_8 = '../../multiparty/artificial/n/10/network0.4_1k_8.txt'
            path_9 = '../../multiparty/artificial/n/10/network0.4_1k_9.txt'
            save_path = '../../multiparty/artificial/n/corpaoml_am_real_community0.4_1k.txt'
            v = 10
            G = nx.read_edgelist(path)
            G1 = app.read_graph(path_0)
            G2 = app.read_graph(path_1)
            G3 = app.read_graph(path_2)
            G4 = app.read_graph(path_3)
            G5 = app.read_graph(path_4)
            G6 = app.read_graph(path_5)
            G7 = app.read_graph(path_6)
            G8 = app.read_graph(path_7)
            G9 = app.read_graph(path_8)
            G10 = app.read_graph(path_9)
            app.run(G1, G2,G3, G4,G5, G6,G7, G8,G9, G10, v, save_path)
            com = overlapping_modularity.load_corpa(save_path)
            mod = overlapping_modularity.cal_EQ(com, G)
            res.append(mod)
        print(res)
        print(sum(res) / len(res))


if __name__ == '__main__':
    unittest.main()
