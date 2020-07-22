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
            path = '../../multiparty/genuine/jazz.txt'
            path_0 = '../../multiparty/genuine/jazz_0.txt'
            path_1 = '../../multiparty/genuine/jazz_1.txt'
            path_2 = '../../multiparty/genuine/jazz_2.txt'
            path_3 = '../../multiparty/genuine/jazz_3.txt'
            path_4 = '../../multiparty/genuine/jazz_4.txt'
            path_5 = '../../multiparty/genuine/jazz_5.txt'
            path_6 = '../../multiparty/genuine/jazz_6.txt'
            path_7 = '../../multiparty/genuine/jazz_7.txt'
            path_8 = '../../multiparty/genuine/jazz_8.txt'
            path_9 = '../../multiparty/genuine/jazz_9.txt'
            save_path = '../../multiparty/genuine/jazz_am.txt'
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
