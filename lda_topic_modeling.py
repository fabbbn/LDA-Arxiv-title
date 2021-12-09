# -*- coding: utf-8 -*-
"""lda-topic-modeling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R-suMWXfXHjaf8SeY0APhcsjRApiPsuw

# Klustering Topik Dokumen Artikel Ilmiah pada Big Data Menggunakan Metode LDA

# *Research Paper Titles Topic Clustering on Big Data Using the LDA Method*
Oleh: Nabila Febriyanti (NIM 09021281823071)
## Dibuat Sebagai Tugas Besar Mata Kuliah Pengantar Big Data

### Deskripsi data
Data yang digunakan dalam pengujian ini adalah data judul artikel ilmiah berjulmah 50 ribu rows dari website https://arxiv.org/. 

Data diperoleh dari https://www.kaggle.com/tayorm/arxiv-papers-metadata.
### Deskripsi Program
Program ini membuat kluster dari data teks judul penelitian-penelitian. 


1.   **Persiapan data**: Dataframe dimuat kemudian dibersihka. Hasil proses ini adalah data frame dengan satu kolom judul artikel ilmiah.
2.   **Pra-pengolahan teks**: Proses ini mempersiapkan teks sebelum siap digunakan ke dalam model LDA. Hasil proses ini adalah korpus, kasus kata dan frekuensi
3. **Analisis data sederhana**: Dengan menggunakan data yang ada, dilakukan analisis sederhana menggunakan Pustaka cloudword untuk melihat sebaran kata kunci.
4. **Pembobotan/Vektorisasi dan Perbaikan Data**: Data diperbaiki dengan mencari frase berdasarkan frekuensi menggunakan alat bantu pustaka gensim. Deteksi frasa diperlukan untuk menangkap arti lebih baik terhadap teks. Data kemudian direpresentasikan menjadi bentuk vektor dengan metode TF-IDF. Kata dengan bobot rendah  diseleksi dan dibuang (reduksi fitur). Hasil proses ini adalah korpus dan kamus kata dan frekuensi siap pakai ke dalam model.
5. **Pelatihan Data ke dalam Model**: Memasukkan semua data yang diperlukan ke dalam model untuk dilakukan pemodelan clustering topik semantik dari judul artikel ilmiah
6. **Menghitung Coherence Score**

## Melakukan import pustaka yang diperlukan
"""

!pip install --upgrade numpy pandas gensim nltk wordcloud pyLDAvis

import nltk
nltk.download("stopwords")

# Commented out IPython magic to ensure Python compatibility.
# for data preparation
import numpy as np
import pandas as pd
import glob

# Gensim model and simple preprocess
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# Spacy for lemmatization
import spacy
from nltk.corpus import stopwords

# Matplotlib and seaborn for visualization
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

# LDA Visualizer
import pyLDAvis
import pyLDAvis.gensim_models

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

print(stopwords)

"""## 1. Persiapan Data
Menggunakan alat bantu pustaka pandas
"""

df = pd.read_csv('./arxiv-titles-250k.txt', header=None, names=['title'])
dataset = df['title'][0:50000]
dataset

"""## 2. Pra-Pengolahan Teks

### Lematisasi
Menggunakan alat bantu pustaka SpaCy
"""

def lemmatization(texts, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    texts_out = []
    for text in texts:
        doc = nlp(text)
        new_text = []
        for token in doc:
            if token.pos_ in allowed_postags:
                new_text.append(token.lemma_)
        final = " ".join(new_text)
        texts_out.append(final)
    return (texts_out)

lemmatized_text = lemmatization(dataset)

lemmatized_text[0:5]

"""### Pra-Pengolahan Teks
Menggunakan alat bantu pustaka Gensim. Terdiri dari tahap casefolding, mengubah teks menjadi token dan membuang token yang terlalu kecil dan terlalu besar.
"""

def gen_words(texts):
    final = []
    for text in texts:
        new = gensim.utils.simple_preprocess(text, deacc=True)
        final.append(new)
    return (final)

data_words = gen_words(lemmatized_text)
data_words[0:10]

long_str = ''
for row in data_words:
    long_str = long_str + (' '.join(row)) + " "
print(len(long_str))

"""## 3. Analisis Data Sederhana
Memetakan sebaran frekuensi kata dengan menggunakan alat bantu pustaka WordCloud
"""

from wordcloud import WordCloud
wordcloud = WordCloud(background_color="white", max_words=100000, contour_width=3, contour_color='steelblue')
wordcloud.generate(long_str)
wordcloud.to_image()

"""## 4. Pembobotan/Vektorisasi dan Perbaikan Data
Menggunakan alat bantu pustaka Gensim.
"""

# bigram and trigrams
bigram_phrases = gensim.models.Phrases(data_words, min_count=100, threshold=1000)
trigram_phrases = gensim.models.Phrases(bigram_phrases[data_words], threshold=1000)

bigram = gensim.models.phrases.Phraser(bigram_phrases)
trigram = gensim.models.phrases.Phraser(trigram_phrases)

def make_bigram(texts):
    return(bigram[doc] for doc in texts)

def make_trigrams(texts):
    return(trigram[bigram[doc]] for doc in texts)


data_bigram = make_bigram(data_words)
data_bigram = list(data_bigram)
data_bigram_trigram = make_trigrams(data_bigram)
data_bigram_trigram = list(data_bigram_trigram)

print(data_bigram_trigram[0:10])

# tf-idf removal using gensim
from gensim.models import TfidfModel

id2word = corpora.Dictionary(data_bigram_trigram)

texts = data_bigram_trigram

corpus = [id2word.doc2bow(text) for text in texts]

tfidf = TfidfModel(corpus=corpus, id2word=id2word)

low_value = 0.03
words = []
words_missing_in_tfidf = []
new_corpus = []

for i in range(0, len(corpus)):
    bow = corpus[i]
    low_value_words = []
    # new_bow = [b for b in bow if b[0] not in low_value_words]
    tfidf_ids = [id for id, value in tfidf[bow]]
    bow_ids = [id for id, value in bow]
    low_value_words = [id for id, value in tfidf[bow] if value < low_value]
    # print(low_value_words)
    drops = low_value_words + words_missing_in_tfidf
    # print(drops)
    for item in drops:
        words.append(id2word[item])
    words_missing_in_tfidf = [id for id in bow_ids if id not in tfidf_ids]

    new_bow = [b for b in bow if b[0] not in low_value_words and b[0] not in words_missing_in_tfidf]
    corpus[i] = new_bow
    new_corpus.append(new_bow)

print(corpus[0:5])
print(new_corpus[0:5])

"""## 5. Pelatihan Data ke dalam Model dan Perhitungan Coherence Score
Menggunakan alat bantu pustaka Gensim
"""

def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    """
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = gensim.models.ldamodel.LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary)
        path = './models/lda-{0}'.format(num_topics)
        model.save(path)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values

model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=texts, start=5, limit=101, step=5)

"""## Visualisasi Hasil clustering
Menggunakan alat bantu pustaka pyLDAvis
"""

# Show graph
limit=101; start=5; step=5;
x = range(start, limit, step)
plt.plot(x, coherence_values)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.show()# Print the coherence scores

# Print the coherence scores
for m, cv in zip(x, coherence_values):
    print("Num Topics =", m, " has Coherence Value of", round(cv, 4))

# Select the model and print the topics
optimal_model = model_list[12]
model_topics = optimal_model.show_topics(formatted=False)
optimal_model.print_topics(num_words=10)

pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim_models.prepare(optimal_model, corpus, id2word, mds="mds", R=10)
vis

"""### Menyimpan hasil 3 kata teratas setiap topik ke dalam bentuk .csv"""

top_words_per_topic = []
for t in range(optimal_model.num_topics):
    top_words_per_topic.extend([(t, ) + x for x in optimal_model.show_topic(t, topn = 3)])

top_words = pd.DataFrame(top_words_per_topic, columns=['Topic', 'Word', 'P'])
top_words.to_csv("top_words.csv")
top_words