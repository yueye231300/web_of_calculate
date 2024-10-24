# import setting
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from io import StringIO
from matplotlib.font_manager import FontProperties  # 导入FontProperties
import math
from operator import itemgetter
import plotly.graph_objects as go

# font setting
font = FontProperties(fname="font/SimSun.ttf", size=10)
font_1 = FontProperties(fname="font/SimSun.ttf", size=8)


# 类定义
# 构建H—Q函数
class BaseSection(object):
    """断面基类"""
    def breadth(self, h: float):
        """水面宽"""
        raise NotImplementedError('breadth 方法必须被重写')

    def area(self, h: float):
        """过水断面面积"""
        raise NotImplementedError('area 方法必须被重写')

    def perimeter(self, h: float):
        """湿周"""
        raise NotImplementedError('perimeter 方法必须被重写')

    def radius(self, h: float):
        """水力半径"""
        return self.area(h) / self.perimeter(h)

    def element(self, h: float):
        """水力要素计算结果"""
        return {
            'h': h,
            'B': self.breadth(h),       # 水面宽
            'A': self.area(h),          # 过水断面面积
            'X': self.perimeter(h),     # 湿周
            'R': self.radius(h),        # 水力半径
        }

    def manning(self, h: float, n: float, j: float):
        """
        曼宁公式，计算过流能力
        :param h: float 水深（水位）
        :param n: float 糙率
        :param j: float 比降
        :return: {"C": 谢才系数, 'Q': 设计流量, 'V': 平均流速}
        """
        if not hasattr(self, 'element'):
            raise NotImplementedError('element 方法必须被定义')
        element = self.element(h)
        R = element.get("R")
        A = element.get("A")
        C = 1 / n * R ** (1 / 6)
        V = C * math.sqrt(R * j)
        Q = A * V
        return {
            **element,
            "C": C,
            "V": V,
            "Q": Q,
        }


class MeasuredSection(BaseSection):
    """实测断面"""
    def __init__(self, coords):
        """
        :param coords: list(list) 实测坐标点[(x1, y1), (x2, y2) ...]
        """
        self.coords = sorted(coords, key=itemgetter(0))

    def area(self, h: float):
        return self.element(h).get('A')

    def perimeter(self, h: float):
        return self.element(h).get('X')

    def breadth(self, h: float):
        return self.element(h).get('B')

    def element(self, h: float):
        x, y = list(zip(*self.coords))
        if h < min(y):
            print('水位低于河底！')
            raise ValueError
        if h > max(y):
            print('水位高于堤顶！')
            raise ValueError
        s = 0
        ka = 0
        b = 0
        for i in range(0, len(x) - 1):
            if y[i] != y[i + 1]:
                x0 = (h - y[i]) * (x[i + 1] - x[i]) / (y[i + 1] - y[i]) + x[i]
            else:
                x0 = x[i + 1]
            s1 = (h - y[i + 1]) * (x[i + 1] - x0) / 2
            s2 = (h - y[i]) * (x0 - x[i]) / 2
            s3 = (2 * h - y[i] - y[i + 1]) * (x[i + 1] - x[i]) / 2
            ka1 = ((x[i + 1] - x0) ** 2 + (y[i + 1] - h) ** 2) ** 0.5
            ka2 = ((x[i] - x0) ** 2 + (y[i] - h) ** 2) ** 0.5
            ka3 = ((x[i] - x[i + 1]) ** 2 + (y[i] - y[i + 1]) ** 2) ** 0.5
            b1 = x[i + 1] - x0
            b2 = x0 - x[i]
            b3 = x[i + 1] - x[i]
            if y[i] >= h > y[i + 1] or y[i] > h >= y[i + 1]:
                s += s1
                ka += ka1
                b += b1
            elif y[i] <= h < y[i + 1] or y[i] < h <= y[i + 1]:
                s += s2
                ka += + ka2
                b += b2
            elif h > y[i] and h > y[i + 1]:
                s += s3
                ka += ka3
                b += b3

        return {
            'h': h - min(y),
            'B': b,  # 水面宽
            'A': s,  # 过水断面面积
            'X': ka,  # 湿周
            'R': s / ka if ka != 0 else 0,  # 水力半径
        }


# 定义空白页面
def nl(num_of_lines):
    for i in range(num_of_lines):
        st.write(" ")


# def method
def calculate_length(y):
    #x,y is a list and x is used to calculate the length
    length = pd.DataFrame(columns=['len'])
    for i in range(len(y['NEAR_X'])):
        dis = ((y['NEAR_X'][i]-x_beginner)**2+(y['NEAR_Y'][i]-y_beginner)**2)**(0.5)
        length = length._append({'len':dis},ignore_index=True)
    return length


def hebing(x, y):
    x_len = pd.DataFrame()
    x_len.insert(x_len.shape[1],'z',x['z'])
    x_len.insert(x_len.shape[1],'len',y['len'])
    return x_len


def limit(x,y):
    len_dif = []
    for i in range(len(x['x'])):
        for j in range(len(y['x'])):
            if zdm['x'][i]==qiao['x'][j]:
                limitation = i+1
                return limitation


def max_i(x, y,t):
    list_z = []
    for i in range(len(x['z'])):
        if x['z'][i]> y['z'][t-1]:
            if x['len'][i]< y['len'][t-1]:
                list_z.append(i)
    return list_z


# 随距离流量计算
def calculate_len_Q(W,L):
    Q_1 = W/Q_m + L/(v*k)
    Q = W/Q_1
    return Q


# 已知流量得水位
def find_water_level(qiao_section, target_flow, n, j):
    h_1 = qiao # 初始水位
    increment = 0.0001  # 水位增量
    while True:
        flow = qiao_section.manning(h_1, n, j)['Q']
        if flow >= target_flow:
            return h_1
        h_1 += increment


# 深泓线距离计算
def shenhong_calculate(zdm, qiao_height):
    for i in range(len(zdm['z'])):
        if zdm['z'][i] > qiao_height:
            continue
        elif zdm['z'][i] == qiao_height:
            l_shenhong = zdm['len'][i]
            return l_shenhong
        elif zdm['z'][i] < qiao_height:
            # 线性插值计算
            z1 = zdm['z'][i-1]
            z2 = zdm['z'][i]
            l1 = zdm['len'][i-1]
            l2 = zdm['len'][i]
            # 计算斜率
            slope = (l2 - l1) / (z2 - z1)
            # 线性插值公式
            l_shenhong = l1 + slope * (qiao_height - z1)
            return l_shenhong


# ui_marking
st.set_page_config(
    page_title="雍水计算",
    page_icon="👋",
)

st.header('雍水计算')

st.subheader('流域选择')
# select the chapter
chapter = st.selectbox("选择你做的流域", (None, '陡沟', '漳腊河岷江北源段', '漳腊河流域漳腊河', '牟尼沟岷江北源段'))
if chapter is not None:
    if chapter == '陡沟':
        path = 'bridge/陡沟桥梁数据.csv'
    if chapter == '漳腊河岷江北源段':
        path = 'bridge/漳腊河岷江北源段桥梁数据.csv'
    if chapter == '漳腊河流域漳腊河':
        path = 'bridge/漳腊河流域漳腊河桥梁数据.csv'
    if chapter == '牟尼沟岷江北源段':
        path = 'bridge/牟尼沟岷江北源段桥梁数据.csv'
    bridge_path = pd.read_csv(path)
    bridge_path_1 = pd.DataFrame(columns=['name'])
    for i in range(len(bridge_path['名称'])):
        name_1 = bridge_path['名称'][i]
        name_2 = name_1[-2:]
        bridge_path_1 = bridge_path_1._append({'name': name_2}, ignore_index=True)
    bridge_path_1.insert(bridge_path_1.shape[1], 'bridge_length', bridge_path['桥面高'])
    bridge_path_1.insert(bridge_path_1.shape[1], 'B', bridge_path['桥宽'])
    bridge_path_1.insert(bridge_path_1.shape[1], 'H', bridge_path['高差'])
    st.write(bridge_path)

st.subheader("上传数据")
# date load
left_row, right_row = st.columns(2)

with left_row:
    zdm_path = st.file_uploader('纵断面文件', type='csv')

with right_row:
    qiao_path = st.file_uploader('桥梁所在断面文件', type='csv')

jmd_path = st.file_uploader('居民点（包含near_x与near_y）', type='txt')


st.subheader('对应雍水图像')
if zdm_path is not None:
    if jmd_path is not None:
        if qiao_path is not None:
            zdm = pd.read_csv(zdm_path)
            zdm_path_name = zdm_path.name
            # st.write(name)
            beginner = zdm.iloc[0, 0:2]
            x_beginner = beginner[0]
            y_beginner = beginner[1]
            near_file = pd.read_csv(jmd_path)
            len_1 = calculate_length(near_file)
            qiao = pd.read_csv(qiao_path)
            hdm = qiao
            jmd_z_len = hebing(near_file, len_1)
            zdm_z_len = hebing(zdm, zdm)
            qiao_lower = qiao['z'].min()
            zdm_yongshui = pd.DataFrame()
            limitation = limit(zdm, hdm)
            zdm_plot = zdm_z_len.iloc[:limitation]
            zdm_path_1 = zdm_path_name[-9:-7]

            if chapter is not None:
                for i in range(len(bridge_path_1['name'])):
                    if bridge_path_1['name'][i]==zdm_path_1:
                        height = bridge_path_1['bridge_length'][i]
            else:
                height = 0
            yongshui_dif =height-qiao_lower
            st.write('桥梁水面高程',height)
            st.write('桥梁横断面最低点',qiao_lower)
            zdm_yongshui.insert(zdm_yongshui.shape[1], 'z', zdm_z_len['z']+yongshui_dif)
            yongshui_z_len = hebing(zdm_yongshui, zdm)
            # reshape the date
            # get the limitation
            yongshui_plot = yongshui_z_len[:limitation]
            jmd_plot_i = max_i(jmd_z_len,zdm,limitation)
            jmd_plot = jmd_z_len.iloc[jmd_plot_i]

            save_path = zdm_path_name[:-7]
            # 创建图像和绘制数据
            fig, ax = plt.subplots()
            ax.scatter(jmd_plot['len'], jmd_plot['z'], marker="^", linewidths=0, color="#efba11", label='居民点')
            ax.plot(zdm_plot['len'], zdm_plot['z'], color='#5177bd', label='深泓线')
            ax.plot(yongshui_plot['len'], yongshui_plot['z'], color='#f3bf97', label='雍水线')

            # 设置图像标签和轴
            plt.xlabel("距离/m", fontproperties=font)
            plt.ylabel('高程/m', fontproperties=font)
            plt.xlim(0, zdm_plot['len'].max() * 1.1)

            # 设置图例位置，确保图例在图像下方
            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8, prop=font_1)

            # 在 Streamlit 中显示图像
            st.pyplot(fig)

            # 创建布局列
            st.write('下载数据')
            left_columns_2, right_columns_2 = st.columns(2)

            # 保存图像并包含图例
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', bbox_extra_artists=[legend])  # 确保图例包含在图像中
            buffer.seek(0)  # 重置缓冲区位置

            # 将数据框转换为 CSV 格式
            csv = zdm_z_len.to_csv(index=False)
            buffer_1 = StringIO(csv)

            # 生成下载按钮
            with left_columns_2:
                st.download_button(label="下载雍水图像", data=buffer, file_name=f"{save_path}.png", mime="image/png")
            with right_columns_2:
                st.download_button(label="下载数据(居民距离以及高度) CSV", data=buffer_1.getvalue(), file_name=f"{save_path}_jmd.csv", mime= "text/csv")
nl(5)

st.subheader('下游溃决计算')
left_columns_3, right_columns_3 = st.columns(2)
with left_columns_3:
    # zdm_zy是纵断面中游的数据
    hdm_zy_path = st.file_uploader('纵断面下游（中）', type='csv', help='指的是下游断面中这个文件，请不要搞错了')
with right_columns_3:
    # zdm_xy指的是纵断面下游的数据
    hdm_xy_path = st.file_uploader('纵断面下游', type='csv')

date_check = st.checkbox('查看数据是否全部上传')
if date_check:
    if not any(var is None for var in [jmd_path,qiao_path,jmd_path,hdm_xy_path,hdm_zy_path]):
        st.success('数据全部上传完全')
    else:
        st.error('请上传所有数据')

if not any(var is None for var in [jmd_path,qiao_path,jmd_path,hdm_xy_path,hdm_zy_path]):
    hdm_zy = pd.read_csv(hdm_zy_path)
    hdm_xy = pd.read_csv(hdm_xy_path)
    # 获得z_len数据
    hdm_zy_z_len = hebing(hdm_zy, hdm_zy)
    hdm_xy_z_len = hebing(hdm_xy, hdm_xy)
    # 寻找三横一纵节点,得到的结果是纵断面的索引号，需要注意
    qiao_jiedian = limit(zdm, qiao)
    hdm_zy_jiedian = limit(zdm, hdm_zy)
    hdm_xy_jiedian = limit(zdm, hdm_xy)

    # 用于计算三个节点到初始位置的距离，可以用来作为图像节点
    qiao_length = zdm['len'][qiao_jiedian]
    hdm_zy_length = zdm['len'][hdm_zy_jiedian]
    hdm_xy_length = zdm['len'][hdm_xy_jiedian]
    # 将横断面坐标制作为坐标形式
    hdm_xy_zb = list(zip(hdm_xy['len'], hdm_xy['z']))
    hdm_zy_zb = list(zip(hdm_zy['len'], hdm_zy['z']))
    qiao_zb = list(zip(qiao['len'], qiao['z']))
    # 水利计算尝试
    # 桥面高程一
    h_1 = height
    # to do 桥面高程.
    # 类型补充
    qiao_section = MeasuredSection(qiao_zb)
    element = qiao_section.element(h_1)
    A = element['A']
    # 使用曼宁公式计算过流能力
    n = 0.03  # 糙率
    j = 0.01  # 比降
    flow = qiao_section.manning(h_1, n, j)
    Q_origin = flow['Q']

    hdm_zy_section = MeasuredSection(hdm_zy_zb)
    hdm_xy_section = MeasuredSection(hdm_xy_zb)
    # 随距离变化的流量计算
    # 全局变量定义
    m = 1.5
    lamad = 0.172229748
    if chapter is not None:
        for i in range(len(bridge_path_1['name'])):
            if bridge_path_1['name'][i] == zdm_path_1:
                B = bridge_path_1['B'][i]
    if chapter is not None:
        for i in range(len(bridge_path_1['name'])):
            if bridge_path_1['name'][i] == zdm_path_1:
                H_change = bridge_path_1['H'][i]
    H_1 = H_change ** (3 / 2)
    S = B *  H_change
    g = 3.132091953
    Q_m = lamad * g * B * H_1
    v = 5
    k = 1.3
    hongxian = zdm['len'][qiao_jiedian] - shenhong_calculate(zdm, height)
    # 随距离变化计算,计算距离
    L_zy = zdm['len'][hdm_zy_jiedian] - zdm['len'][qiao_jiedian]
    L_xy = zdm['len'][hdm_xy_jiedian] - zdm['len'][qiao_jiedian]

    # 计算阻水库容
    W = 1 / 3 * A * hongxian

    # 流量计算
    Q_lm_zy = calculate_len_Q(W, L_zy)
    Q_lm_xy = calculate_len_Q(W, L_xy)

    # 绘制桥断面坐标
    st.subheader('桥梁横断面')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qiao['len'], y=qiao['z'], mode='lines+markers', name='z vs len'))

    # 设置图形标题和标签
    fig.update_layout(title='横断面图',
                      xaxis_title='距离',
                      yaxis_title='高程')

    # 在 Streamlit 中显示图形
    st.plotly_chart(fig)