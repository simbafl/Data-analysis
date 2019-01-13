import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles, make_blobs, make_moons
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering

n_samples = 1000
circles = make_circles(n_samples=n_samples, factor=0.5, noise=0.05)
moons = make_moons(n_samples=n_samples, noise=0.05)
blobs = make_blobs(n_samples=n_samples, random_state=8, center_box=(-1, 1), cluster_std=0.1)
random_data = np.random.rand(n_samples, 2), None  # None指标注
colors = "bgrcmyk"
data = [circles, moons, blobs, random_data]  # 四个数据集
models = [("None", None),  # 不添加任何模型
          ("KMeans", KMeans(n_clusters=3)),]  # KMeans 分成3类
          # ("DBscan", DBSCAN(min_samples=3, eps=0.2)),  # 分成3类， E邻域
          # ("Agglomerative", AgglomerativeClustering(n_clusters=3, linkage="ward"))]  # 指定ward方法
f = plt.figure()
for inx, clt in enumerate(models):
    clt_name, clt_entry = clt
    for i, dataset in enumerate(data):
        X, Y = dataset
        if not clt_entry:
            clt_res = [0 for i in range(len(X))]
        else:
            clt_entry.fit(X)
            clt_res = clt_entry.labels_.astype(np.int)
        f.add_subplot(len(models), len(data), inx*len(data)+i+1)
        plt.title(clt_name)
        [plt.scatter(X[p, 0], X[p, 1], color=colors[clt_res[p]]) for p in range(len(X))]
plt.savefig("Kmeans.png")
plt.show()
