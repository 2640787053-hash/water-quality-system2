import warnings
warnings.filterwarnings("ignore")
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import platform

# =========【字体只保留一份，修复线上Linux找不到宋体】=========
if platform.system() == "Windows":
    # Windows本机使用宋体
    my_font = FontProperties(fname=r"C:\Windows\Fonts\simsun.ttc")
    plt.rcParams['axes.unicode_minus'] = False
else:
    # Streamlit云端Linux用文泉驿字体，不读取本地磁盘文件
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
    plt.rcParams['axes.unicode_minus'] = False
    my_font = FontProperties()


st.set_page_config(page_title="城市河道水质检测可视化系统", layout="wide")

st.title("城市河道水质检测可视化系统")
st.info("""
本系统模拟城市多个河道监测点水质数据，可查看pH、溶解氧、氨氮、浊度时序变化，
自动划分地表水Ⅰ~Ⅴ水质等级，支持数据筛选、超标预警、异常检测、相关性分析等功能。
""")

st.sidebar.header("参数设置")
# 图表主题切换
theme_mode = st.sidebar.radio("图表主题风格",["亮色主题","暗色主题"])
if theme_mode == "暗色主题":
    plt.style.use('dark_background')
else:
    plt.style.use('default')

sites = ["监测点A", "监测点B", "监测点C", "监测点D", "监测点E"]
time_list = pd.date_range(start="2026-01-01", periods=30, freq="D")

def generate_data():
    data = []
    for site in sites:
        for t in time_list:
            # 模拟水质指标
            ph = np.clip(np.random.normal(7.2, 0.6), 6, 9)
            do = np.clip(np.random.normal(6.5, 1.2), 2, 10)   # 溶解氧 mg/L
            nh3_n = np.clip(np.random.normal(0.8, 0.5), 0, 3) # 氨氮 mg/L
            turbidity = np.clip(np.random.normal(15, 8), 0, 50) # 浊度 NTU
            data.append([t, site, ph, do, nh3_n, turbidity])
    df = pd.DataFrame(data, columns=["时间", "监测点", "pH", "溶解氧DO", "氨氮", "浊度"])
    return df

df = generate_data()

def get_water_level(do, nh3):
    """
    简化地表水水质分类：Ⅰ~Ⅴ类
    DO：Ⅰ≥7.5；Ⅱ≥6；Ⅲ≥5；Ⅳ≥3；Ⅴ≥2
    氨氮：Ⅰ≤0.15；Ⅱ≤0.5；Ⅲ≤1.0；Ⅳ≤1.5；Ⅴ≤2.0
    """
    if do >=7.5 and nh3 <=0.15:
        return "Ⅰ"
    elif do >=6 and nh3 <=0.5:
        return "Ⅱ"
    elif do >=5 and nh3 <=1.0:
        return "Ⅲ"
    elif do >=3 and nh3 <=1.5:
        return "Ⅳ"
    else:
        return "Ⅴ"

df["水质等级"] = df.apply(lambda row: get_water_level(row["溶解氧DO"], row["氨氮"]), axis=1)

selected_site = st.sidebar.selectbox("选择监测站点", sites)
start_date = st.sidebar.date_input("起始日期", value=time_list.min())
end_date = st.sidebar.date_input("结束日期", value=time_list.max())

level_options = st.sidebar.multiselect("筛选水质等级", ["Ⅰ","Ⅱ","Ⅲ","Ⅳ","Ⅴ"], default=["Ⅰ","Ⅱ","Ⅲ","Ⅳ","Ⅴ"])

# 筛选数据
filter_df = df[
    (df["监测点"] == selected_site) &
    (df["时间"] >= pd.to_datetime(start_date)) &
    (df["时间"] <= pd.to_datetime(end_date)) &
    (df["水质等级"].isin(level_options))
].copy()

col1, col2 = st.columns([1,2])
with col1:
    st.subheader(f"{selected_site} 监测数据表")
    st.dataframe(filter_df, width="stretch")
    # 数据下载按钮
    csv = filter_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("下载当前筛选数据(CSV)", csv, file_name="水质监测数据.csv", mime="text/csv")

with col2:
    st.subheader("水质指标趋势图")
    fig, axes = plt.subplots(2,2, figsize=(14,8))
    axes = axes.flatten()

    # pH
    axes[0].plot(filter_df["时间"], filter_df["pH"], color="#1f77b4")
    axes[0].set_title("pH值变化", fontproperties=my_font)
    axes[0].set_ylabel("pH", fontproperties=my_font)
    axes[0].grid(alpha=0.3)

    # 溶解氧
    axes[1].plot(filter_df["时间"], filter_df["溶解氧DO"], color="#2ca02c")
    axes[1].set_title("溶解氧DO变化 mg/L", fontproperties=my_font)
    axes[1].set_ylabel("DO", fontproperties=my_font)
    axes[1].grid(alpha=0.3)

    # 氨氮
    axes[2].plot(filter_df["时间"], filter_df["氨氮"], color="#d62728")
    axes[2].set_title("氨氮变化 mg/L", fontproperties=my_font)
    axes[2].set_ylabel("氨氮", fontproperties=my_font)
    axes[2].grid(alpha=0.3)

    # 浊度
    axes[3].plot(filter_df["时间"], filter_df["浊度"], color="#ff7f0e")
    axes[3].set_title("浊度变化 NTU", fontproperties=my_font)
    axes[3].set_ylabel("浊度", fontproperties=my_font)
    axes[3].grid(alpha=0.3)

    try:
        plt.tight_layout(pad=1.5)
    except Exception:
        pass
    st.pyplot(fig)
    plt.close("all")


st.divider()
st.subheader("水质统计汇总 & 超标预警")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("平均pH", round(filter_df["pH"].mean(),2))
c2.metric("平均DO", round(filter_df["溶解氧DO"].mean(),2))
c3.metric("平均氨氮", round(filter_df["氨氮"].mean(),2))
c4.metric("平均浊度", round(filter_df["浊度"].mean(),2))
if len(filter_df)>0:
    c5.metric("当前主要水质类别", filter_df["水质等级"].value_counts().idxmax())
else:
    c5.metric("当前主要水质类别", "无数据")

# 超标预警
if len(filter_df)>0:
    over_nh3 = len(filter_df[filter_df["氨氮"]>1.0])
    over_do = len(filter_df[filter_df["溶解氧DO"]<5])
    warn_col1, warn_col2 = st.columns(2)
    with warn_col1:
        if over_nh3>0:
            st.warning(f"氨氮超标样本数：{over_nh3}条（Ⅲ类标准限值1.0mg/L）")
        else:
            st.success("氨氮全部达标")
    with warn_col2:
        if over_do>0:
            st.warning(f"溶解氧不足样本数：{over_do}条（Ⅲ类标准≥5mg/L）")
        else:
            st.success("溶解氧全部达标")

st.divider()
st.subheader("全部监测点水质等级分布")
level_count = df["水质等级"].value_counts()
fig2, ax2 = plt.subplots(figsize=(8,5))
bars = ax2.bar(level_count.index, level_count.values, color=["#9467bd","#2ca02c","#1f77b4","#ff7f0e","#d62728"])
# 在柱子上方显示百分比
total = level_count.sum()
for bar in bars:
    height = bar.get_height()
    pct = height / total * 100
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{pct:.1f}%', ha="center", va="bottom", fontproperties=my_font, fontsize=11)
ax2.set_xlabel("水质等级", fontproperties=my_font)
ax2.set_ylabel("样本数量", fontproperties=my_font)
ax2.set_title("各水质等级样本数量分布", fontproperties=my_font)
ax2.grid(axis="y", alpha=0.3)
try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig2)
plt.close("all")


# 多站点溶解氧对比折线图
st.divider()
st.subheader("多监测点溶解氧DO对比")
fig_multi, ax_multi = plt.subplots(figsize=(10,5))
for site in sites:
    site_data = df[df["监测点"] == site]
    ax_multi.plot(site_data["时间"], site_data["溶解氧DO"], label=site)
ax_multi.set_title("各监测点溶解氧时序对比", fontproperties=my_font)
ax_multi.set_xlabel("时间", fontproperties=my_font)
ax_multi.set_ylabel("溶解氧DO mg/L", fontproperties=my_font)
ax_multi.legend(prop=my_font)
ax_multi.grid(alpha=0.3)
plt.xticks(rotation=30)
try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig_multi)
plt.close("all")


# pH直方图分布
st.divider()
st.subheader("pH值分布直方图")
fig_hist, ax_hist = plt.subplots(figsize=(8,4))
ax_hist.hist(filter_df["pH"], bins=12, color="#1f77b4", alpha=0.7, edgecolor="black")
ax_hist.set_title("pH值频数分布", fontproperties=my_font)
ax_hist.set_xlabel("pH", fontproperties=my_font)
ax_hist.set_ylabel("频数", fontproperties=my_font)
ax_hist.grid(axis="y", alpha=0.3)
try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig_hist)
plt.close("all")


# ============水质指标相关性热力图============
st.divider()
st.subheader("水质指标相关性分析")
corr_df = df[["pH","溶解氧DO","氨氮","浊度"]].corr()
fig_corr, ax_corr = plt.subplots(figsize=(7,5))
im = ax_corr.imshow(corr_df.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax_corr.set_xticks(np.arange(len(corr_df.columns)))
ax_corr.set_yticks(np.arange(len(corr_df.columns)))
ax_corr.set_xticklabels(corr_df.columns, fontproperties=my_font)
ax_corr.set_yticklabels(corr_df.columns, fontproperties=my_font)
for i in range(len(corr_df.columns)):
    for j in range(len(corr_df.columns)):
        ax_corr.text(j,i,f"{corr_df.iloc[i,j]:.2f}",ha="center",va="center", fontproperties=my_font)
fig_corr.colorbar(im,ax=ax_corr)
ax_corr.set_title("指标相关系数热力图", fontproperties=my_font)
try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig_corr)
plt.close("all")


# ============当前筛选站点指标箱线图============
st.divider()
st.subheader(f"{selected_site} 各水质指标箱线图")
fig_box, axes_box = plt.subplots(2,2,figsize=(12,7))
axes_box = axes_box.flatten()

bp1 = axes_box[0].boxplot(filter_df["pH"])
axes_box[0].set_xticklabels(["pH"], fontproperties=my_font)
axes_box[0].set_title("pH分布箱线", fontproperties=my_font)
axes_box[0].grid(alpha=0.2)

bp2 = axes_box[1].boxplot(filter_df["溶解氧DO"])
axes_box[1].set_xticklabels(["溶解氧DO"], fontproperties=my_font)
axes_box[1].set_title("溶解氧DO分布箱线", fontproperties=my_font)
axes_box[1].grid(alpha=0.2)

bp3 = axes_box[2].boxplot(filter_df["氨氮"])
axes_box[2].set_xticklabels(["氨氮"], fontproperties=my_font)
axes_box[2].set_title("氨氮分布箱线", fontproperties=my_font)
axes_box[2].grid(alpha=0.2)

bp4 = axes_box[3].boxplot(filter_df["浊度"])
axes_box[3].set_xticklabels(["浊度"], fontproperties=my_font)
axes_box[3].set_title("浊度分布箱线", fontproperties=my_font)
axes_box[3].grid(alpha=0.2)

try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig_box)
plt.close("all")


# ============全部数据水质等级饼图============
st.divider()
st.subheader("全部监测点水质等级占比饼图")
fig_pie, ax_pie = plt.subplots(figsize=(6,6))
level_count_all = df["水质等级"].value_counts()
ax_pie.pie(level_count_all.values, labels=level_count_all.index, autopct="%.1f%%",
           startangle=90, textprops={"fontproperties":my_font})
ax_pie.set_title("地表水各等级占比", fontproperties=my_font)
try:
    plt.tight_layout(pad=1.5)
except Exception:
    pass
st.pyplot(fig_pie)
plt.close("all")


# ============异常数据检测模块============
st.divider()
st.subheader("⚠️水质异常记录检测")
abnormal_df = filter_df[
    (filter_df["pH"]<6.5) | (filter_df["pH"]>8.5) |
    (filter_df["氨氮"]>1.5) | (filter_df["溶解氧DO"]<3)
].copy()

if len(abnormal_df)>0:
    st.error(f"检测到 {len(abnormal_df)} 条异常水质记录！")
    st.dataframe(abnormal_df, width="stretch")
    csv_abnormal = abnormal_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("下载异常数据CSV",csv_abnormal,file_name="水质异常数据.csv")
else:
    st.success("当前筛选范围内无异常水质记录")


# ============地表水标准参考说明面板============
st.divider()
with st.expander("📖 地表水水质标准参考说明（简化版）", expanded=False):
    st.markdown("""
    |水质等级|溶解氧DO ≥|氨氮 ≤|说明|
    |--------|----------|------|----|
    |Ⅰ类|7.5|0.15|源头水、国家自然保护区|
    |Ⅱ类|6.0|0.50|集中式生活饮用水地表水源地一级保护区|
    |Ⅲ类|5.0|1.00|饮用水二级保护区，适合水产养殖|
    |Ⅳ类|3.0|1.50|工业用水，人体非直接接触|
    |Ⅴ类|2.0|2.00|农业用水，一般景观用水|

    pH正常范围：6‑9；数值偏离代表水体酸碱污染。
    浊度：代表水体悬浮物，数值越高水体越浑浊。
    """)


# ============各监测点水质等级统计对比表格============
st.divider()
st.subheader("各监测点水质等级统计")
site_level_stats = pd.crosstab(df["监测点"], df["水质等级"])
st.dataframe(site_level_stats)
