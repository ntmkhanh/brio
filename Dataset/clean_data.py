import pandas as pd
import regex as re

if __name__ == '__main__':
    
    df = pd.read_csv('./data/recipes_dataset_3col.csv', index_col=0)
    emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                u"\U00002500-\U00002BEF"  # chinese char
                                u"\U00002702-\U000027B0"
                                u"\U00002702-\U000027B0"
                                u"\U000024C2-\U0001F251"
                                u"\U0001f926-\U0001f937"
                                u"\U00010000-\U0010ffff"
                                u"\u2640-\u2642"
                                u"\u2600-\u2B55"
                                u"\u200d"
                                u"\u23cf"
                                u"\u23e9"
                                u"\u231a"
                                u"\ufe0f"  # dingbats
                                u"\u3030"
                                "]+", flags=re.UNICODE)

    

    df['Title'] = df['Title'].astype('string').str[:]
    df['Title'] = df['Title'].map(lambda x: emoji_pattern.sub(r'',x))
    df['Title'] = df['Title'].map(lambda x: re.sub('\(.*?\)','', x))
    df['Title'] = df['Title'].map(lambda x: x.replace('-', ','))
    df['Title'] = df['Title'].map(lambda x: x.strip())



    df['Instructions'] = df['Instructions'].astype('string').str[:]
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('.,', '.'))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('...', '.'))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace(':', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('?', '.'))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace(';', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('!', '.'))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('*', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('+', ','))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace(':)', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('^_^', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('^^', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: re.sub('\(.*?\)','', x))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('-', ' đến '))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('~', ' đến '))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('hiii', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('hihi', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('hii', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('mozzarella', ''))
    df['Instructions'] = df['Instructions'].map(lambda x: x.replace('tteokbokki', 'bánh gạo'))
    df['Instructions'] = df['Instructions'].map(lambda x: emoji_pattern.sub(r'',x))
    df['Instructions'] = df['Instructions'].map(lambda x: x.strip())


    df['Ingredients'] = df['Ingredients'].astype('string').str[:]
    df['Ingredients'] = df['Ingredients'].map(lambda x: x.replace('-', ' đến '))
    df['Ingredients'] = df['Ingredients'].map(lambda x: x.replace('~', ' đến '))
    df['Ingredients'] = df['Ingredients'].map(lambda x: x.replace(':', ''))
    df['Ingredients'] = df['Ingredients'].map(lambda x: re.sub('\(.*?\)','', x))
    df['Ingredients'] = df['Ingredients'].map(lambda x: x.strip())

    df['inputs'] = df['Ingredients']
    df['targets'] = df['Title'] + " | " + df['Instructions']
    
    df.to_csv('CookyVN-recipe-dataset-cleaned.csv', encoding='utf-8', index=False)
