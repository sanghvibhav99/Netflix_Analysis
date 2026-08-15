import numpy as mp
import pandas as pd

def process(df):
    df['cast_set'] = df['cast'].apply(lambda x: set(actor.strip() for actor in str(x).split(',')) if x != 'Unknown' else set())
    df['genre_set'] = df['listed_in'].apply(lambda x: set(genre.strip() for genre in str(x).split(',')))

    return df