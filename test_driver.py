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
            path = '../../corpa/n/2/network0.4_1k.txt'
            path_0 = '../../corpa/n/2/network0.4_1k_0.txt'
            path_1 = '../../corpa/n/2/network0.4_1k_1.txt'
            save_path = '../../corpa/n/2/corpaoml_am_network0.4_1k.txt'
            v = 2
            G = nx.read_edgelist(path)
            G1 = app.read_graph(path_0)
            G2 = app.read_graph(path_1)
            app.run(G1, G2, v, save_path)
            com = overlapping_modularity.load_corpa(save_path)
            mod = overlapping_modularity.cal_EQ(com, G)
            res.append(mod)
        print(res)
        print(sum(res) / len(res))


if __name__ == '__main__':
    unittest.main()
