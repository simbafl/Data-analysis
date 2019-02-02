## 监督式学习
#### 分类
 [随机森林](RandomForest.ipynb) `KNN` `朴素贝叶斯`  [决策树](RandomForest.ipynb)  [SVM](SVM.ipynb)  `GDBT`  `Adaboost` ...
#### 回归
 `线性回归`  [逻辑回归](logistic_regression.ipynb)
 
## 非监督式学习
#### 聚类
 [Kmeans](K-means.py)  `DBSCAN`  `层次聚类`  [关联规则](Ass_rule.py)  `序列规则` ...

## 半监督学习
 `标签传播`
 
### 机器学习一般流程： 问题建模， 特征工程， 模型选择， 模型融合， 模型应用
#### 1. 问题建模
解决机器学习问题都是从建模开始。首先需要收集问题的资料，深入理解问题，然后将问题抽象成机器可预测的问题。
在这个过程中要明确业务指标和模型预测目标，根据预测目标选择适当的评估指标用于模型评估。接着从原始数据中选择
最相关的样本子集用于模型训练，并对样本子集划分训练集和测试集，应用交叉验证的方法对模型进行选择和评估。
![1-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/1.jpg)
#### 2. 特征工程
完成问题建模，对数据进行筛选和清洗之后的步骤，就是对数据抽取特征，即特征工程。此时就要对模型的算法有深入的理解。
![2-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/2.jpg)
#### 3. 常用模型(更多模型选择往下看)
特征工程的目的是为了将特征输入给模型，让模型从数据中学习规律。但模型有很多，不同的模型差别很大，使用场景不同，
能够处理的特征也会不同。
![3-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/3.jpg)
#### 4. 模型融合
充分利用不同模型的差异，采用模型融合的方法，以进一步优化目标。
![4-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/4.jpg)
#### 5. 用户画像
![5-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/5.jpg)
#### 机器学习实现了太多模型，具体如何选择，sklearn官网提供了大概思路
![sklearn-view](https://github.com/fenglei110/Data-analysis/blob/master/ch02/images/sklearn.png)
