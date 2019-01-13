import pandas as pd
import numpy as np
import scipy.stats as ss
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
import os
import pydotplus

os.environ["PATH"] += os.pathsep + "D:/graphviz/bin/"


def hr_preprocessing(sl=False, le=False, npr=False, amh=False, tsc=False, wa=False, pl=False, dep=False, sal=False,
                     lower_d=False, ld_n=1):
    """
    sl=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    le=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    npr=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    amh=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    tsc=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    wa=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    pl=False --> MinMaxScaler  归一化   sl=True --> StandardScaler  标准化
    dep=False --> LabelEncoder          dep=True --> OneHotEncoder
    sal=False --> LabelEncoder          dep=True --> OneHotEncoder
    lower_d=False --> 不降维    ld_n=1 默认1维
    :param sl:
    :return:
    """
    df = pd.read_csv("HR.csv.bak")
    # 清洗数据
    df = df.dropna(subset=["satisfaction_level", "last_evaluation"])
    df = df[df["satisfaction_level"] <= 1][df["salary"] != "nme"]
    # 得到标注
    label = df["left"]
    df = df.drop("left", axis=1)
    # 特征选择
    # 特征处理
    scaler_lst = [sl, le, npr, amh, tsc, wa, pl]
    column_lst = ["satisfaction_level", "last_evaluation", "number_project", "average_monthly_hours",
                  "time_spend_company", "Work_accident", "promotion_last_5years"]
    for i in range(len(scaler_lst)):
        if not scaler_lst[i]:
            df[column_lst[i]] = \
                MinMaxScaler().fit_transform(df[column_lst[i]].values.reshape(-1, 1)).reshape(1, -1)[0]
        else:
            df[column_lst[i]] = \
                StandardScaler().fit_transform(df[column_lst[i]].values.reshape(-1, 1)).reshape(1, -1)[0]

    scaler_lst2 = [sal, dep]
    column_lst2 = ["salary", "department"]
    # 对salary和department两列处理
    for i in range(len(scaler_lst2)):
        if not scaler_lst2[i]:
            if column_lst2[i] == "salary":
                df[column_lst2[i]] = [map_salary(s) for s in df["salary"].values]
            else:
                df[column_lst2[i]] = LabelEncoder().fit_transform(df[column_lst2[i]])
            # 归一化处理
            df[column_lst2[i]] = MinMaxScaler().fit_transform(df[column_lst2[i]].values.reshape(-1, 1))
        else:
            # OneHotEncoder
            df = pd.get_dummies(df, columns=[column_lst2[i]])
    if lower_d:
        # return LinearDiscriminantAnalysis(n_components=ld_n)  LDA降维
        return PCA(n_components=ld_n).fit_transform(df.values), label
    return df, label


d = dict([('low', 0), ("medium", 1), ("high", 2)])


def map_salary(s):
    return d.get(s, 0)


def hr_modeling(features, label):
    """建模"""
    from sklearn.model_selection import train_test_split
    f_v = features.values
    f_names = features.columns.values
    l_v = label.values
    # X_validation为验证集, Y_validation为验证集
    x_tt, x_validation, y_tt, y_validation = train_test_split(f_v, l_v, test_size=0.2)
    # X_train 为训练集，X_test为测试集，y_train为标注训练集，y_test为标注测试集
    x_train, x_test, y_train, y_test = train_test_split(x_tt, y_tt, test_size=0.25)

    from sklearn.metrics import accuracy_score, recall_score, f1_score
    # KNN
    from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier
    # 贝叶斯
    from sklearn.naive_bayes import GaussianNB, BernoulliNB
    # 决策树
    from sklearn.tree import DecisionTreeClassifier, export_graphviz
    from sklearn.externals.six import StringIO
    # 向量机
    from sklearn.svm import SVC
    # 随机森林 RandomForest
    from sklearn.ensemble import RandomForestClassifier
    # AdaBoost
    from sklearn.ensemble import AdaBoostClassifier
    # 逻辑斯特回归
    from sklearn.linear_model import LogisticRegression, LinearRegression

    models = list()
    models.append(("KNN", KNeighborsClassifier(n_neighbors=3)))
    models.append(("GaussianNB", GaussianNB()))
    models.append(("BernoulliNB", BernoulliNB()))
    models.append(("DecisionTreeGini", DecisionTreeClassifier()))  # 参数默认Gini系数
    models.append(("DecisionTreeEntropy", DecisionTreeClassifier(criterion="entropy")))  # 参数熵增益
    models.append(("SVM", SVC(kernel="rbf", C=100)))  # C为惩罚度，也就是要求度
    models.append(("RandomForest", RandomForestClassifier(n_estimators=20)))  # 默认为10
    models.append(("AdaBoost", AdaBoostClassifier(n_estimators=100)))  # 弱分类器个数
    models.append(("LogisticRegression", LogisticRegression()))  # 回归方程当做分类器
    for clf_name, clf in models:
        clf.fit(x_train, y_train)
        xy_lst = [(x_train, y_train), (x_validation, y_validation), (x_test, y_test)]
        for i in range(len(xy_lst)):
            x_part = xy_lst[i][0]
            y_part = xy_lst[i][1]
            y_pred = clf.predict(x_part)
            print(i)
            print(clf_name + " ACC:", accuracy_score(y_part, y_pred))
            print(clf_name + " REC:", recall_score(y_part, y_pred))
            print(clf_name + " F-Score:", f1_score(y_part, y_pred))
            # 绘制决策树
            dot_name = export_graphviz(clf, out_file=None,
                                       feature_names=f_names,
                                       class_names=["NL", "L"],
                                       filled=True,
                                       rounded=True,
                                       special_characters=True)
            graph = pydotplus.graph_from_dot_data(dot_name)
            graph.write_pdf("dt_tree.pdf")


def main():
    features, label = hr_preprocessing(sl=True, le=True, npr=True, amh=True, tsc=True, wa=True, pl=True,
                                       dep=False, sal=False)
    hr_modeling(features, label)
    # print(features, label)


if __name__ == "__main__":
    main()
