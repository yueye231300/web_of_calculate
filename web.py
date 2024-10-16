# import setting
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from io import StringIO
from matplotlib.font_manager import FontProperties  # 导入FontProperties

# font setting
font = FontProperties(fname="font/SimSun.ttf", size=10)
font_1 = FontProperties(fname="font/SimSun.ttf", size=8)


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


def max_i(x, y):
    list_z = []
    for i in range(len(x['z'])):
        if x['z'][i]> y:
            list_z.append(i)
    return list_z


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
            max_z = zdm['z'][limitation-1]

            jmd_plot_i = max_i(jmd_z_len,max_z)
            jmd_plot = jmd_z_len.iloc[jmd_plot_i]

            save_path = zdm_path_name[:-7]
            fig, ax = plt.subplots()
            ax.scatter(jmd_plot['len'], jmd_plot['z'], marker="^", linewidths=0, color="#efba11", label='居民点')
            ax.plot(zdm_plot['len'], zdm_plot['z'], color='#5177bd', label='深泓线')
            ax.plot(yongshui_plot['len'], yongshui_plot['z'], color='#f3bf97', label='雍水线')
            plt.xlabel("距离/m", fontproperties=font)
            plt.ylabel('高程/m', fontproperties=font)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8, prop=font_1)
            st.pyplot(fig)
            st.write('下载数据')
            # 数据下载
            left_columns_2,right_columns_2 = st.columns(2)
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)  # 重置缓冲区位置

            # 将数据框转换为 CSV 格式
            csv = zdm_z_len.to_csv(index=False)
            # 使用 StringIO 将 CSV 字符串转换为字节流
            buffer_1 = StringIO(csv)
            with left_columns_2:
                st.download_button(label="下载雍水图像", data=buffer, file_name=f"{save_path}.png", mime="image/png")

            with right_columns_2:
                st.download_button(label='居民点距上游距离以及高程数据', data=buffer_1.getvalue(), file_name=f'{save_path}_jmd.csv', mime='text/csv')