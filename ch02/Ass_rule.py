"""
关联规则/序列规则
"""
from itertools import combinations


def comb(lst):
    """
    得到一个列表里所有元素的组合
    ["a", "b", "c"]
    >>> [("a",), ("b",), ("c",), ("a","b"), ("a","c"), ("b","c"), ("a","b","c")]
    """
    ret = []
    for i in range(1, len(lst) + 1):
        ret += list(combinations(lst, i))
    return ret


class AprLayer(object):
    """存放项目数量相同的项集"""
    def __init__(self):
        self.d = dict()


class AprNode(object):
    """
    初始化每一个项集
    node = ("a", ) 或 ("b",) 或 ("a", "b")
    """
    def __init__(self, node):
        self.s = set(node)
        self.size = len(self.s)
        self.lnk_nodes = dict()
        self.num = 0

    def __hash__(self):
        return hash("__".join(sorted([str(itm) for itm in list(self.s)])))

    def __eq__(self, other):
        if "__".join(sorted([str(itm) for itm in list(self.s)])) == "__".join(
                sorted([str(itm) for itm in list(other.s)])):
            return True
        return False

    def isSubnode(self, node):
        return self.s.issubset(node.s)

    def incNum(self, num=1):
        self.num += num

    def addLnk(self, node):
        self.lnk_nodes[node] = node.s


class AprBlk(object):
    """使AprLayer和AprNode两个数据结构结合"""
    def __init__(self, data):
        cnt = 0  # 计数器
        self.apr_layers = dict()
        self.data_num = len(data)
        for datum in data:
            cnt += 1
            datum = comb(datum)
            # datum=[("a",), ("b",), ("a","b")]
            nodes = [AprNode(da) for da in datum]
            for node in nodes:
                # 根据项集的数目
                if node.size not in self.apr_layers:
                    # {1: {('a',): AprNode(('a',)), ('b',): AprNode(('b',))}, 2:{}, 3:{}}
                    self.apr_layers[node.size] = AprLayer()
                if node not in self.apr_layers[node.size].d:
                    self.apr_layers[node.size].d[node] = node
                # 调用数量加1
                self.apr_layers[node.size].d[node].incNum()
            for node in nodes:
                if node.size == 1:
                    continue
                for sn in node.s:
                    # 高阶项集减去一阶项集
                    # sn -> '毛巾', set([sn]) -> {'毛巾'}
                    sub_n = AprNode(node.s - set([sn]))
                    # 在低阶项集上建立和高阶项集的联系
                    self.apr_layers[node.size - 1].d[sub_n].addLnk(node)

    def getFreqItems(self, thd=1, hd=1):
        # thd=1 为阈值
        freq_items = []
        for layer in self.apr_layers:
            for node in self.apr_layers[layer].d:
                if self.apr_layers[layer].d[node].num < thd:
                    continue
                freq_items.append((self.apr_layers[layer].d[node].s, self.apr_layers[layer].d[node].num))
        # 根据num从高到低排序
        freq_items.sort(key=lambda x: x[1], reverse=True)
        return freq_items[:hd]

    def getConf(self, low=True, h_thd=10, l_thd=1, hd=1):
        # h_thd 高阈值
        confidence = []
        for layer in self.apr_layers:
            for node in self.apr_layers[layer].d:
                if self.apr_layers[layer].d[node].num < h_thd:
                    continue
                for lnk_node in node.lnk_nodes:
                    if lnk_node.num < l_thd:
                        continue
                    # 置信度=低阶频繁项集所连接的高阶频繁项集的数量/低阶频繁项集的数量
                    conf = float(lnk_node.num) / float(node.num)
                    confidence.append([node.s, node.num, lnk_node.s, lnk_node.num, conf])
        # 根据置信度排序
        confidence.sort(key=lambda x: x[4])
        if low:
            # 返回低置信度
            return confidence[:hd]
        else:
            # 返回高置信度
            return confidence[-hd::-1]


class AssctAnaClass():
    """关联规则"""
    def __init__(self):
        self.apr_blk = None

    def fit(self, data):
        # 拟合数据
        self.apr_blk = AprBlk(data)
        return self

    def get_freq(self, thd=1, hd=1):
        # 取出频繁项集
        return self.apr_blk.getFreqItems(thd=thd, hd=hd)

    def get_conf_high(self, thd, h_thd=10):
        # 取出高置信度项集组合
        return self.apr_blk.getConf(low=False, h_thd=h_thd, l_thd=thd)

    def get_conf_low(self, thd, hd, l_thd=1):
        # 取出低置信度项集组合
        return self.apr_blk.getConf(h_thd=thd, l_thd=l_thd, hd=hd)


def main():
    data = [
        ["牛奶", "啤酒", "尿布"],
        ["牛奶", "啤酒", "咖啡", "尿布"],
        ["香肠", "牛奶", "饼干"],
        ["尿布", "果汁", "啤酒"],
        ["钉子", "啤酒"],
        ["尿布", "毛巾", "香肠"],
        ["啤酒", "毛巾", "尿布", "饼干"]
    ]
    print("Freq", AssctAnaClass().fit(data).get_freq(thd=3, hd=10))
    print("Conf", AssctAnaClass().fit(data).get_conf_high(thd=3, h_thd=4))


if __name__ == "__main__":
    main()
