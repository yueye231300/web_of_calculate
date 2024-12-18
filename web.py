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
import numpy as np
import random


def generate_two_numbers(mean_value):
    # Generate the first number in the range of 0.5 to 0.7 times the mean_value
    first_number = random.uniform(0.5 * mean_value, 0.7 * mean_value)

    # Calculate the second number such that the mean of the two numbers is mean_value
    second_number = 2 * mean_value - first_number

    return first_number, second_number

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

def limit_1(x,y):
    for i in range(len(x['x'])):
        for j in range(len(y['x'])):
            if x['y'][i]==y['y'][j]:
                limitation = i
                return limitation

def hl_calculate(hl_z_len_1,zy_jiedian,xy_jiedian):
    zy_hl = []
    xy_hl = []
    for i in range(len(hl_z_len_1['z'])):
        if hl_z_len_1['z'][i]<zdm['z'][zy_jiedian] and hl_z_len_1['len'][i]<zdm['len'][zy_jiedian]:
            zy_hl.append(i)
        elif zdm['z'][zy_jiedian] < hl_z_len_1['z'][i] < zdm['z'][xy_jiedian] and zdm['len'][zy_jiedian] < \
                hl_z_len_1['len'][i] < zdm['len'][xy_jiedian]:
            xy_hl.append(i)
    return zy_hl,xy_hl



# def method
def calculate_length(y):
    #x,y is a list and x is used to calculate the length
    length = pd.DataFrame(columns=['len'])
    for i in range(len(y['NEAR_X'])):
        dis = ((y['NEAR_X'][i]-x_beginner)**2+(y['NEAR_Y'][i]-y_beginner)**2)**(0.5)
        length = length._append({'len':dis},ignore_index=True)
    return length


def calculate_length_x_y(x):
    length = pd.DataFrame(columns=['len'])
    for i in range(len(x['x'])):
        dis = ((x['x'][i] - x_beginner) ** 2 + (x['y'][i] - y_beginner) ** 2) ** (0.5)
        length = length._append({'len': dis}, ignore_index=True)
    return length





def hebing(x, y):
    x_len = pd.DataFrame()
    x_len.insert(x_len.shape[1],'z',x['z'])
    x_len.insert(x_len.shape[1],'len',y['len'])
    return x_len


def limit(x, y):
    for i in range(len(x['x'])):
        for j in range(len(y['x'])):
            if x['y'][i] == y['y'][j]:
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
    h_1 = qiao['z'].min() # 初始水位
    h_min = qiao['z'].min()
    increment = 0.0001  # 水位增量
    while True:
        flow = qiao_section.manning(h_1, n, j)['Q']
        if flow >= target_flow:
            return h_1-h_min
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



def generate_two_numbers(mean_value):
    # Generate the first number in the range of 0.5 to 0.7 times the mean_value
    first_number = random.uniform(0.5 * mean_value, 0.7 * mean_value)

    # Calculate the second number such that the mean of the two numbers is mean_value
    second_number = 2 * mean_value - first_number

    return first_number, second_number


def calculate_pojiang(x):
    '''
    :param x: 传入纵断面数据，注意纵断面行名应该命名好
    :return: 计算坡降
    '''
    df = x
    df['h_i'] = df['z'] - df['z'].min()
    # Calculate the horizontal distance l_i between consecutive points
    df['l_i'] = np.sqrt((df['x'].shift(-1) - df['x']) ** 2 + (df['y'].shift(-1) - df['y']) ** 2)
    # calculate the j
    L = df['l_i'].sum()
    df['weighted_hl'] = (df['h_i'] + df['h_i'].shift(-1)) * df['l_i']
    J = df['weighted_hl'].sum() / L ** 2
    return J







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
    bridge_path_1.insert(bridge_path_1.shape[1], 'B', bridge_path['桥长'])
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

radio = st.radio('是否有居民点数据',['1','2'],captions=['有居民点','无居民点'])
st.subheader('对应雍水图像')
if zdm_path is not None:
        if qiao_path is not None and jmd_path is not None:
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
            # 可视化图像
            st.subheader('查看居民点是否有问题并进行修改')
            # 创建图形对象
            fig = go.Figure()
            # 添加居民点散点图
            if radio == '1':
                fig.add_trace(go.Scatter(
                    x=jmd_plot['len'],
                    y=jmd_plot['z'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color="#efba11"),
                    name='居民点'
                    ))

            # 添加深泓线
            fig.add_trace(go.Scatter(
                x=zdm_plot['len'],
                y=zdm_plot['z'],
                mode='lines',
                line=dict(color='#5177bd'),
                name='深泓线'
            ))

            # 添加水面线
            fig.add_trace(go.Scatter(
                x=yongshui_plot['len'],
                y=yongshui_plot['z'],
                mode='lines',
                line=dict(color='#f3bf97'),
                name='水面线'
            ))

            # 设置图像标签和轴
            fig.update_layout(
                xaxis_title="距离/m",
                yaxis_title='高程/m',
                xaxis=dict(range=[0, zdm_plot['len'].max() * 1.1]),
                font=dict(family="Your Font Family"),  # 替换为你想要的字体
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)',
                )
            )

            # 在 Streamlit 中显示图形
            st.plotly_chart(fig)






            fig, ax = plt.subplots()
            if radio == '1':
                ax.scatter(jmd_plot['len'], jmd_plot['z'], marker="^", linewidths=0, color="#efba11", label='居民点')
            ax.plot(zdm_plot['len'], zdm_plot['z'], color='#5177bd', label='深泓线')
            ax.plot(yongshui_plot['len'], yongshui_plot['z'], color='#f3bf97', label='水面线')

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
            fig.savefig(buffer, format='png', bbox_inches='tight', bbox_extra_artists=[legend],dpi=600)  # 确保图例包含在图像中
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
    if not any(var is None for var in [jmd_path,qiao_path,hdm_xy_path,hdm_zy_path]):
        st.success('数据全部上传完全')
    else:
        st.error('请上传所有数据')

if not any(var is None for var in [zdm_path,qiao_path,jmd_path,hdm_xy_path,hdm_zy_path]):
    hdm_zy = pd.read_csv(hdm_zy_path)
    hdm_xy = pd.read_csv(hdm_xy_path)
    # 获得z_len数据
    hdm_zy_z_len = hebing(hdm_zy, hdm_zy)
    hdm_xy_z_len = hebing(hdm_xy, hdm_xy)
    # 寻找三横一纵节点,得到的结果是纵断面的索引号，需要注意
    qiao_jiedian = limit_1(zdm, qiao)
    hdm_zy_jiedian = limit_1(zdm, hdm_zy)
    hdm_xy_jiedian = limit_1(zdm, hdm_xy)

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
    # to do 桥面高程
    qiao_section = MeasuredSection(qiao_zb)
    element = qiao_section.element(h_1)
    A = element['A']
    A_zy,A_xy =generate_two_numbers(A)
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
    zdm_pojaing = zdm
    if height >zdm['z'].max():
        st.error('桥高高于纵断面最大值，先记录一下，可以继续做')
        J = calculate_pojiang(zdm_pojaing)
        st.write('坡降是')
        st.write(J)
        l_1 = zdm['len'][qiao_jiedian]-zdm['len'][0]
        l_2 = (height - zdm['z'][0])/J
        hongxian = l_1+l_2
        st.write('泓线长度')
        st.write(hongxian)
    else:
        hongxian = zdm['len'][qiao_jiedian] - shenhong_calculate(zdm, height)
    # 随距离变化计算,计算距离
    L_zy = zdm['len'][hdm_zy_jiedian] - zdm['len'][qiao_jiedian]
    L_xy = zdm['len'][hdm_xy_jiedian] - zdm['len'][qiao_jiedian]


    # 计算阻水库容
    W = 1 / 3 * A * hongxian

    # 流量计算
    Q_lm_zy = calculate_len_Q(W, L_zy)
    Q_lm_xy = calculate_len_Q(W, L_xy)
    nl(2)
    if height>qiao['z'].max():
        st.error('桥高于河堤')
    elif height<qiao['z'].min():
        st.error('桥低于河底')
    else:
        st.success('桥梁数据没有问题')
    # 绘制桥断面坐标
    st.subheader('桥梁横断面')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qiao['len'], y=qiao['z'], mode='lines+markers', name='桥梁横断面图'))

    # 设置图形标题和标签
    fig.update_layout(title='横断面图',
                      xaxis_title='距离',
                      yaxis_title='高程')

    # 在 Streamlit 中显示图形
    st.plotly_chart(fig)

    # 绘制水位流量表格
    # 假设你已经定义了 qiao_section 对象
    qiao_section = qiao_section  # 你的断面对象
    n = 0.03  # 糙率
    j = 0.01  # 比降
    # Streamlit 页面标题
    st.subheader('水位与流量关系图')
    # 输入起始水位和最终水位
    h_start = qiao['z'].min()
    h_end = qiao['z'].max()
    # 存储数据
    water_levels = []
    flows = []
    areas = []
    # 增加水位
    h_values = np.arange(h_start, h_end, 0.01)
    for h in h_values:
        # 计算水利要素
        element = qiao_section.manning(h, n, j)

        water_levels.append(h)
        flows.append(element['Q'])
        areas.append(element['A'])

    # 创 DataFrame 存储水位、流量和面积
    df_results = pd.DataFrame({
        '水位 (H)': water_levels,
        '流量 (Q)': flows,
        '断面面积 (A)': areas
    })

    # 创建折线图
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=water_levels, y=flows, mode='lines', name='流量(Q)'))

    # 设置图形标题和标签
    fig.update_layout(title='水位与流量关系图',
                      xaxis_title='水位 (H)',
                      yaxis_title='流量 (Q)',
                      showlegend=True)
    # 在 Streamlit 中显示图形
    st.plotly_chart(fig)
    # 显示结果表格
    st.subheader('水位与流量及断面面积表格')
    st.dataframe(df_results)
    st.subheader('多支汇流计算')
    hl_path = st.file_uploader('多支汇流数据', type='csv')
    if hl_path is not None:
        hl = pd.read_csv(hl_path)
        hl_length = calculate_length_x_y(hl)
        hl_z_len= hebing(hl,hl_length)
        zy_hl,xy_hl = hl_calculate(hl_z_len,hdm_zy_jiedian,hdm_xy_jiedian)
        st.write('中游断面汇流的有：')
        st.write(zy_hl)
        st.write('下游断面汇流的有：')
        st.write(xy_hl)
        # 绘制汇流图像
        # Create the plot
        fig = go.Figure()
        # Plot zdm_z_len as scatter and line
        fig.add_trace(go.Scatter(x=zdm_z_len['len'], y=zdm_z_len['z'], mode='markers', name='纵断面节点',
                                 marker=dict(color='blue')))
        fig.add_trace(go.Scatter(x=zdm_z_len['len'], y=zdm_z_len['z'], mode='lines', name='深弘线',
                                 line=dict(color='blue')))

        # Highlight hdm_zy_jiedian and hdm_xy_jiedian
        fig.add_trace(
            go.Scatter(x=[zdm_z_len['len'][hdm_zy_jiedian]], y=[zdm_z_len['z'][hdm_zy_jiedian]], mode='markers',
                       name='中游断面节点', marker=dict(color='red', size=10)))
        fig.add_trace(
            go.Scatter(x=[zdm_z_len['len'][hdm_xy_jiedian]], y=[zdm_z_len['z'][hdm_xy_jiedian]], mode='markers',
                       name='下游断面节点', marker=dict(color='green', size=10)))

        # Add hl data as scatter points
        fig.add_trace(
            go.Scatter(x=hl_z_len['len'], y=hl_z_len['z'], mode='markers', name='汇流节点', marker=dict(color='orange')))

        # Set labels and legend
        fig.update_layout(
            xaxis_title='距离/m',
            yaxis_title='高程/m',
            legend_title='图例'
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig)
        qiao_max = qiao['z'].max()
        Q_max = qiao_section.element(qiao_max)
        flow_1 = qiao_section.manning(qiao_max,0.03,0.01)
        Q_MAX = flow_1['Q']

        st.write("请给出对应的流量数据")
        st.write('汇流流量之和不能超过')
        st.write(Q_MAX-Q_m)
        left_columns_4, right_columns_4 = st.columns(2)
        with left_columns_4:
            zy_hl = st.number_input('输入中游支流数据')
        with right_columns_4:
            xy_hl = st.number_input('输入下游汇流数据')
        if not any(var is None for var in [zy_hl, xy_hl]):
            Q_lm_zy_hl = Q_lm_zy + zy_hl
            Q_lm_xy_hl = Q_lm_xy + zy_hl +xy_hl
            H_zy = find_water_level(qiao_section,Q_lm_zy_hl,0.03,0.01)
            H_zy_1 = H_zy+hdm_zy_z_len['z'].min()
            H_xy = find_water_level(qiao_section,Q_lm_xy_hl,0.03,0.01)
            H_xy_1 = H_xy+hdm_xy_z_len['z'].min()
            plot_H = {'height':[height,H_zy_1,H_xy_1],'len':[0,L_zy,L_xy]}
            plot_H = pd.DataFrame(plot_H)
            zdm_plot_2 = zdm.iloc[limitation-1:]
            jmd_plot_2 =jmd_z_len[~jmd_z_len.index.isin(jmd_plot_i)]
            jmd_plot_2['len'] = jmd_plot_2['len']-zdm['len'][qiao_jiedian]
            zdm_plot_2['len'] = zdm_plot_2['len']-zdm['len'][qiao_jiedian]
            # 创建图形对象
            fig1 = go.Figure()


            # 添加居民点散点图
            if radio =='1':
                fig1.add_trace(go.Scatter(
                    x=jmd_plot_2['len'],
                    y=jmd_plot_2['z'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color="#efba11"),
                    name='居民点'
                ))

            # 添加深泓线
            fig1.add_trace(go.Scatter(
                x=zdm_plot_2['len'],
                y=zdm_plot_2['z'],
                mode='lines',
                line=dict(color='#5177bd'),
                name='深泓线'
            ))

            # 添加水面线
            fig1.add_trace(go.Scatter(
                x=plot_H['len'],
                y=plot_H['height'],
                mode='lines',
                line=dict(color='#f3bf97'),
                name='水面线'
            ))

            # 设置图像标签和轴
            fig1.update_layout(
                xaxis_title="距离/m",
                yaxis_title='高程/m',
                xaxis=dict(range=[0, zdm_plot_2['len'].max() * 1.1]),
                font=dict(family="Your Font Family"),  # 替换为你想要的字体
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)',
                    font=dict(size=8)
                )
            )

            # 在 Streamlit 中显示图形
            st.plotly_chart(fig1)

            st.write(plot_H)
            # 绘制图像，包括深洪线，居民点和流量距离曲线
            fig2, ax = plt.subplots()
            if radio == '1':
                ax.scatter(jmd_plot_2['len'], jmd_plot_2['z'], marker="^", linewidths=0, color="#efba11", label='居民点')
            ax.plot(zdm_plot_2['len'], zdm_plot_2['z'], color='#5177bd', label='深泓线')
            ax.plot(plot_H['len'], plot_H['height'], color='#f3bf97', label='水面线')
            # 设置图像标签和轴
            plt.xlabel("距离/m", fontproperties=font)
            plt.ylabel('高程/m', fontproperties=font)
            plt.xlim(0, zdm_plot_2['len'].max() * 1.1)
            # 设置图例位置，确保图例在图像下方
            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8, prop=font_1)

            # 在 Streamlit 中显示图像
            st.pyplot(fig2)
            # 创建布局列
            st.write('溃决数据下载')
            left_columns_5, right_columns_5= st.columns(2)
            # 保存图像并包含图例
            buffer2 = BytesIO()
            fig2.savefig(buffer2, format='png', bbox_inches='tight', bbox_extra_artists=[legend],dpi=600)  # 确保图例包含在图像中
            buffer2.seek(0)  # 重置缓冲区位置
            save_result = {'S_shangyou':[A_zy],'S_xiayou':[A_xy],'S_duan': [A],'S_zu':[S],'R1':[S/A],'hongxian_l':[hongxian],'W':[W],'Q_m':[Q_m],'Q_m_zhongyou':[Q_lm_zy],'Q_mxaiyou':[Q_lm_xy],\
            'B':[B],'H_gaocha':[H_change],'L_xiayou':[L_xy],'yongshuidiangaocha':[height-qiao['z'].min()],'L_zy':[L_zy]}
            save_result =pd.DataFrame(save_result)

            # 将数据框转换为 CSV 格式
            csv = save_result.to_csv(index=False,encoding='utf-8')
            buffer_3 = StringIO(csv)
            # 生成下载按钮
            with left_columns_5:
                st.download_button(label="下载溃决图像", data=buffer2, file_name=f"{save_path}溃决.png", mime="image/png")
            with right_columns_5:
                st.download_button(label="下载溃决计算结果", data=buffer_3.getvalue(),
                                   file_name=f"{save_path}_溃决计算.csv", mime="text/csv")
