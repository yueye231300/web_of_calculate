# import setting
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from matplotlib.font_manager import FontProperties  # 导入FontProperties

# font setting
font = FontProperties(fname="font/SimSun.ttf", size=14)


# def method
def calculate_length(y):
    #x,y is a list and x is used to calculate the length
    length = pd.DataFrame(columns=['len'])
    for i in range(len(y['NEAR_X'])):
        dis = ((y['NEAR_X'][i]-x_beginner)**2+(y['NEAR_Y'][i]-y_beginner)**2)**(0.5)
        length = length._append({'len':dis},ignore_index=True)
    return length


def hebing(x,y):
    x_len = pd.DataFrame()
    x_len.insert(x_len.shape[1],'z',x['z'])
    x_len.insert(x_len.shape[1],'len',y['len'])
    return x_len


# ui_marking

st.set_page_config(
    page_title="雍水计算",
    page_icon="👋",
)

st.header('雍水计算')
st.subheader("上传数据")

# date load
left_row, right_row = st.columns(2)

with left_row:
    zdm = st.file_uploader('纵断面文件', type='csv')

with right_row:
    qiao= st.file_uploader('桥梁所在断面文件', type='csv')

left_row_1, right_row_1 = st.columns(2)

with left_row_1:
    jmd = st.file_uploader('居民点（包含near_x与near_y）', type='txt')

with right_row_1:
    qiao_height = st.number_input('输入桥的高度')


st.subheader('对应雍水图像')
if zdm is not None:
    if jmd is not None:
        if qiao is not None:
            # name = zdm.name()
            zdm = pd.read_csv(zdm)
            # st.write(name)
            beginner = zdm.iloc[0, 0:2]
            x_beginner = beginner[0]
            y_beginner = beginner[1]

            near_file = pd.read_csv(jmd)
            len_1 = calculate_length(near_file)
# get the data

            qiao = pd.read_csv(qiao)
            jmd_z_len = hebing(near_file, len_1)
            zdm_z_len = hebing(zdm, zdm)
            qiao.sort_values(by='z', inplace=True)
            qiao_lower = qiao['z'][0]
            yongshui_dif =qiao_height-qiao_lower
            zdm_yongshui = pd.DataFrame()
            zdm_yongshui.insert(zdm_yongshui.shape[1],'z',zdm['z']+yongshui_dif)
            yongshui_z_len = hebing(zdm_yongshui,zdm)
        # plot the jmd and zdm
            fig,ax = plt.subplots()
            ax.scatter(jmd_z_len['len'], jmd_z_len['z'], marker="^", linewidths=0, color="#efba11",label='居民点')
            ax.plot(zdm_z_len['len'], zdm_z_len['z'], color='#5177bd',label='深泓线')
            ax.plot(yongshui_z_len['len'], yongshui_z_len['z'], color='#f3bf97',label='雍水线')
            plt.xlabel("距离/m", fontproperties=font)
            plt.ylabel('高程/m', fontproperties=font)
            plt.legend(fontsize=14, prop=font)
            st.pyplot(fig)
            st.write('下载数据')
            # 数据下载
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)  # 重置缓冲区位置
            st.download_button(
                label="下载雍水图像",
                data=buffer,
                file_name="雍水图像.png",
                mime="image/png"
            )

