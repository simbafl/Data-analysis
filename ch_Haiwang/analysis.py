import json
from collections import Counter
import pandas as pd
import numpy as np
import seaborn as sns
import jieba.analyse
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from pyecharts import WordCloud, Style, Geo


def get_data():
    df = pd.read_csv("haiwang.csv", sep=",", header=None, names=["nickName","cityName","content","approve","reply","startTime","avatarurl","score"],encoding="utf-8")
    print(df.columns)
    return df


# 清洗数据
def clean_data():
    df = get_data()
    has_copy = any(df.duplicated())
    print(has_copy)
    data_duplicated = df.duplicated().value_counts()
    print(data_duplicated)  # 查看有多少数据是重复的
    """
    >>>False    59900
       True      4450
       dtype: int64
    """
    data = df.drop_duplicates(keep="first")  # 删掉重复值, first保留最先的
    data = data.reset_index(drop=True)  # 删除部分行后重置索引
    data["startTime"] = pd.to_datetime(data["startTime"])  # dtype: object -->  dtype: datetime64[ns]
    data["content_length"] = data["content"].apply(len)  # 增加一列
    data = data[~data['nickName'].isin(["."])]
    return data


# 查看数据基本情况
def analysis1():
    data = clean_data()
    print(data.describe())
    print(data.isnull().any())  # 判断空值  cityName中存在空值
    print(len(data[data.nickName == "."]))  # 38个nickName是 '.'
    # 删除.
    # data = data[~(data['nickName'] == ".")]
    # 和上面等价
    data = data[~data['nickName'].isin(["."])]
    print(data.head())
    print(data['nickName'].describe())
    print(data['cityName'].describe())
    return data


def analysis2():
    """
    分析打分score情况
    饼状图基本参数都凑齐了
    """
    data = clean_data()
    grouped = data.groupby(by="score")["nickName"].size().tail(8)
    grouped = grouped.sort_values(ascending=False)
    index = grouped.index
    values = grouped.values

    # 将横、纵坐标轴标准化处理，保证饼图是一个正圆，否则为椭圆
    plt.axes(aspect='equal')
    plt.subplots(figsize=(10, 7))  # 设置绘图区域大小
    # 控制x轴和y轴的范围
    plt.xlim(0, 4)
    plt.ylim(0, 4)
    # 绘制饼图
    patches, texts, autotexts = plt.pie(x=index,   # 绘图数据
            labels=values,  # 添加label
            explode=[0.1, 0, 0, 0, 0, 0, 0, 0],
            autopct='%.1f%%',  # 设置百分比的格式，这里保留一位小数
            pctdistance=1.2,  # 设置百分比标签与圆心的距离
            labeldistance=0.8,  # 设置value与圆心的距离
            startangle=90,  # 设置饼图的初始角度
            radius=1.5,  # 设置饼图的半径
            shadow=True,  # 添加阴影
            counterclock=True,  # 是否逆时针，这里设置为顺时针方向
            wedgeprops={'linewidth': 1.5, 'edgecolor': 'green'},  # 设置饼图内外边界的属性值
            textprops={'fontsize': 12, 'color': 'k'},  # 设置文本标签的属性值
            center=(1.8, 1.8),  # 设置饼图的原点
            frame=0)  # 是否显示饼图的图框，这里设置显示
    # 重新设置字体大小
    proptease = fm.FontProperties()
    proptease.set_size('small')
    plt.setp(autotexts, fontproperties=proptease)
    plt.setp(texts, fontproperties=proptease)

    # 删除x轴和y轴的刻度
    plt.xticks(())
    plt.yticks(())
    plt.legend()
    # 显示图形
    plt.savefig('pie2.png')
    plt.show()


def analysis3():
    """分析评论时间"""
    data = clean_data()
    data["hour"] = data["startTime"].dt.hour  # 提取小时
    data["startTime"] = data["startTime"].dt.date  # 提取日期
    need_date = data[["startTime", "hour"]]

    def get_hour_size(data):
        hour_data = data.groupby(by="hour")["hour"].size().reset_index(name="count")
        return hour_data

    data = need_date.groupby(by="startTime").apply(get_hour_size)
    # print(data)
    data_reshape = data.pivot_table(index="startTime", columns="hour", values="count")[1:-2]
    data = data_reshape.describe()
    print(data)
    data_mean = data.loc["mean"]  # 均值
    data_std = data.loc["std"]  # 方差
    data_min = data.loc["min"]  # min
    data_max = data.loc["max"]  # max

    # 坐标轴负号的处理
    plt.rcParams['axes.unicode_minus'] = False

    plt.title("24h count")
    plt.plot(data_mean.index, data_mean, color="green", label="mean")
    plt.plot(data_std.index, data_std, color="red", label="std")
    plt.plot(data_min.index, data_min, color="blue", label="min")
    plt.plot(data_max.index, data_max, color="yellow", label="max")
    plt.legend()
    plt.xlabel("one day time")
    plt.ylabel("pub sum")
    plt.savefig('chart_line.png')
    plt.show()


def analysis4():
    data = clean_data()
    contents = list(data["content"].values)
    try:
        jieba.analyse.set_stop_words('stop_words.txt')
        tags = jieba.analyse.extract_tags(str(contents), topK=100, withWeight=True)
        name = []
        value = []
        for v, n in tags:
            # [('好看', 0.5783566110162118), ('特效', 0.2966753295335903), ('不错', 0.22288265823188907),...]
            name.append(v)
            value.append(int(n * 10000))
        wordcloud = WordCloud(width=1300, height=620)
        wordcloud.add("", name, value, word_size_range=[20, 100])
        wordcloud.render()
    except Exception as e:
        print(e)


def handle(cities):
    """处理地名数据，解决坐标文件中找不到地名的问题"""
    with open(
            'city_coordinates.json',
            mode='r', encoding='utf-8') as f:
        data = json.loads(f.read())  # 将str转换为json

    # 循环判断处理
    data_new = data.copy()  # 拷贝所有地名数据
    for city in set(cities):  # 使用set去重
        # 处理地名为空的数据
        if city == '':
            while city in cities:
                cities.remove(city)
        count = 0
        for k in data.keys():
            count += 1
            if k == city:
                break
            if k.startswith(city):
                # print(k, city)
                data_new[city] = data[k]
                break
            if k.startswith(city[0:-1]) and len(city) >= 3:
                data_new[city] = data[k]
                break
        # 处理不存在的地名
        if count == len(data):
            while city in cities:
                cities.remove(city)

    # 写入覆盖坐标文件
    with open(
            'city_coordinates.json',
            mode='w', encoding='utf-8') as f:
        f.write(json.dumps(data_new, ensure_ascii=False))  # 将json转换为str


def analysis5():
    data = clean_data()
    cities = list(data[~data["cityName"].isnull()]["cityName"].values)
    handle(cities)

    style = Style(
        title_color='#fff',
        title_pos='center right',
        width=1200,
        height=600,
        background_color='#404a59'
    )

    new_cities = Counter(cities).most_common(100)
    geo = Geo("《海王》粉丝分布", "数据来源：Github-fenglei110", **style.init_style)
    attr, value = geo.cast(new_cities)
    geo.add('', attr, value, visual_range=[0, 3000], visual_text_color='#fff', symbol_size=15,is_visualmap=True, is_piecewise=True, visual_split_number=10)
    geo.render('粉丝位置分布-GEO.html')


if __name__ == '__main__':
    analysis3()

