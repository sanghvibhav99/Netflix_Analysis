import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from cleaning import clean
from processing import process

st.set_page_config(page_title='Netflix Analysis',page_icon="🎬",layout='wide')
st.title("Netflix Analysis")

@st.cache_data
def load_and_prepare_data():
    df = pd.read_csv('netflix_titles.csv')
    df = clean(df)
    df = process(df)
    return df

df = load_and_prepare_data()

genres = sorted(list(set().union(*df['genre_set'])))
actors = sorted(list(set().union(*df['cast_set'])))

mode = st.segmented_control("Select View",["📈 Genre Trends", "🎭 Actor Portfolio"],default="📈 Genre Trends",label_visibility="collapsed")

if mode == "📈 Genre Trends":
    st.title("Genre Trends Over Time")
    col1 , col2 = st.columns(2)

    with col1:
        genre = st.selectbox("Select a Genre to track:",genres)
        genre_df = df[df['genre_set'].apply(lambda x: genre in x)]
        trend_df = genre_df.groupby('release_year').size().reset_index(name='count')

        fig , ax = plt.subplots(figsize=[6,3])

        ax.set_alpha(0)
        fig.set_facecolor('none')

        ax.plot(trend_df['release_year'],trend_df['count'],marker='o',linestyle='-',color='#E50914')
        ax.set_xlabel('Year',color='#E50914')
        ax.set_ylabel('No. of Releases',color='#E50914')
        ax.set_title(f'{genre} Movies released over years.',color='#E50914')
        ax.tick_params('both',colors='#E50914')
        ax.grid(True,linestyle='--',alpha=1)
        for spine in ax.spines.values():
            spine.set_color("#E50914")

        st.pyplot(fig,transparent=True)

    with col2:
        yr = st.slider("Select Release Year : " , int(df['release_year'].min()),int(df['release_year'].max()),2019)
        yr_df = df[df['release_year'] == yr]
        all_genres = [g for genres in yr_df['genre_set'] for g in genres]
        genre_counts = pd.Series(all_genres).value_counts().reset_index()
        genre_counts.columns = ['genre','count']
        top_15_genres = genre_counts.head(15)
        
        fig , ax = plt.subplots(figsize=[6,3])

        fig.set_facecolor('none')
        ax.set_alpha(0)

        ax.bar(top_15_genres['genre'],top_15_genres['count'],color='#E50914')
        ax.set_title(f"Top 15 Genres in {yr}", color='#E50914')
        ax.set_xlabel('Genre', color='#E50914')
        ax.set_ylabel('Count', color='#E50914')
        ax.tick_params(axis='x', rotation=90, colors='#E50914')
        ax.tick_params(axis='y', colors='#E50914')
        for spine in ax.spines.values():
            spine.set_color("#E50914")

        st.pyplot(fig,transparent=True)

    st.divider()
    a,b = st.columns([1,2])
    with a:
        comp_genres = st.multiselect("Select Two Genres to Compare : ",genres,default=genres[:2],max_selections=2)

        if len(comp_genres) >= 1:
            g1 = comp_genres[0]
            g1_df = df[df['genre_set'].apply(lambda x:g1 in x)].groupby('release_year').size().reset_index(name='count1')

        if len(comp_genres) == 2:
            g2 = comp_genres[1]
            g2_df = df[df['genre_set'].apply(lambda x:g2 in x)].groupby('release_year').size().reset_index(name='count2')

        x,y = st.columns(2)

        with x:
            if len(comp_genres) >= 1 and not g1_df.empty:
                g1_total = int(g1_df['count1'].sum())
                g1_peak_year = int(g1_df.loc[g1_df['count1'].idxmax(), 'release_year'])
                g1_peak_count = int(g1_df['count1'].max())
                st.metric(label=f"{g1} (Total)", value=g1_total)
                st.metric(label=f"Peak Year: {g1_peak_year}", value=g1_peak_count)

        with y:
            if len(comp_genres) == 2 and not g2_df.empty and not g1_df.empty:
                g2_total = int(g2_df['count2'].sum())
                g2_peak_year = int(g2_df.loc[g2_df['count2'].idxmax(), 'release_year'])
                g2_peak_count = int(g2_df['count2'].max())
                st.metric(label=f"{g2} (Total)", value=g2_total)
                st.metric(label=f"Peak Year: {g2_peak_year}", value=g2_peak_count)

    with b:
        if len(comp_genres) == 2:
            merged = pd.merge(g1_df,g2_df,on='release_year',how='outer').fillna(0).sort_values('release_year')
            merged['rolling1'] = merged['count1'].rolling(window=3,min_periods=1).mean()
            merged['rolling2'] = merged['count2'].rolling(window=3,min_periods=1).mean()

            x = np.arange(len(merged['release_year']))
            width = 0.35

            fig,ax = plt.subplots(figsize=[6,3])
            fig.set_facecolor('none')
            ax.set_alpha(0)
            ax.bar(x - width/2,merged['rolling1'],width,label=g1,color="#E50914")
            ax.bar(x + width/2, merged['rolling2'], width, label=g2, color="#E50914")

            ax.set_xlabel('Year',color='#E50914')
            ax.set_ylabel('No. of releases',color='#E50914')
            ax.set_title(f'Comparison : {g1} vs {g2}',color='#E50914')
            ax.set_xticks(x[::5])
            ax.set_xticklabels(merged['release_year'].iloc[::5].astype(int), rotation=45, color='#E50914')
            ax.tick_params(axis='y', colors='#E50914')

            ax.grid(True, linestyle='--', alpha=0.8)
            ax.legend(frameon=False, labelcolor='#E50914')
            for spine in ax.spines.values():
                spine.set_color("#E50914")

            st.pyplot(fig,transparent=True)

        elif len(comp_genres) < 2:
            st.info("Please select a second genre to see the comparison chart.")

    st.divider()

if mode == "🎭 Actor Portfolio":
    st.title("Actor Portfolio Explorer")

    actor = st.selectbox("Search for an Actor:", actors)
    actor_df = df[df['cast_set'].apply(lambda x:actor in x)].sort_values('release_year')
    actor_genres = [g for genre_list in actor_df['genre_set'] for g in genre_list]
    actor_genres = set(actor_genres)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Titles Featuring : {actor}")

        st.metric("Total Movies & Shows : ", len(actor_df))
        st.dataframe(actor_df[['type','title','director','release_year','duration','rating']])

    with col2:
        st.subheader("Genre Distribution")
        actor_genre_count = pd.Series(list(actor_genres)).value_counts().reset_index()
        actor_genre_count.columns = ['genre','count']
        
        fig , ax = plt.subplots(figsize=[6,3])

        ax.set_alpha(0)
        fig.set_facecolor('none')

        wedges,text,autotexts = ax.pie(actor_genre_count['count'],autopct='%1.0f%%',startangle=90,pctdistance=1.2,wedgeprops=dict(width=0.5, edgecolor='black'), textprops={'color': '#E50914', 'fontsize': 6} )
        legend = ax.legend(wedges,actor_genre_count['genre'],title="Genres",loc="center left",bbox_to_anchor=(1, 0, 0.5, 1),frameon=False,labelcolor='#E50914')
        plt.setp(legend.get_title(), color='#E50914') 
        st.pyplot(fig,transparent=True)

    choice = st.selectbox('Select Genre : ',list(actor_genres))
    genre_actor_df = actor_df[actor_df['genre_set'].apply(lambda x: choice in x)][['title','director','release_year','duration','rating']]
    genre_actor_df.reset_index(drop=True)
    st.dataframe(genre_actor_df)