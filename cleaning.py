import numpy as np
import pandas as pd
    
def clean(df):
    df.drop_duplicates(inplace=True)
    df['release_year'] = df['release_year'].astype('Int16')

    for col in ['director' , 'cast' , 'country']:
        df[col] = df[col].fillna('Unknown')

    df['date_added'] = df['date_added'].str.strip()
    df['date_added'] = pd.to_datetime(df['date_added'])

    df['date_added'] = df['date_added'].fillna(pd.to_datetime(df['release_year'].astype(str) + '-12-31'))
    df['date_added'] = df['date_added'].dt.normalize()

    m = df[df['type'] == 'Movie']['duration'].str.extract(r'(\d+)').astype(float).mean().item()
    df['duration'] = df['duration'].fillna(f"{int(round(m))} min")

    df = df.dropna(subset = ['rating'])

    genre_mapping = {
            "International Movies": "Intl Movies",
            "Action & Adventure": "Action",
            "Children & Family Movies": "Kids/Family",
            "Independent Movies": "Indie",
            "Stand-Up Comedy & Talk Shows": "Stand-Up/Talk",
            "Stand-Up Comedy": "Stand-Up",
            "Romantic Movies": "Romance",
            "Sci-Fi & Fantasy": "Sci-Fi/Fantasy",
            "Documentaries": "Docs",
            "International TV Shows": "Intl TV",
            "TV Action & Adventure": "Action TV",
            "TV Sci-Fi & Fantasy": "Sci-Fi TV",
            "Spanish-Language TV Shows": "Spanish TV",
            "Korean TV Shows": "Korean TV",
            "Science & Nature TV": "Sci/Nature TV",
            "Docuseries": "Docs TV"
    }

    def map_genres(genre_string):
            if pd.isna(genre_string):
                return genre_string
            genres = [g.strip() for g in genre_string.split(',')]
            mapped_genres = [genre_mapping.get(g,g) for g in genres]
            return ', '.join(mapped_genres)

    df['listed_in'] = df['listed_in'].apply(map_genres)

    df.reset_index(inplace=True,drop=True)
    df.index = df.index+1
    
    return df