import re
import pandas as pd
import spacy   
import operator
from spacy.matcher import Matcher
from fuzzywuzzy import fuzz
from spacy.matcher import Matcher,PhraseMatcher
from sklearn.feature_extraction.text import CountVectorizer

activeDebug=False

def filterTimes(dataFrame,s_y,s_m,s_d,e_y,e_m,e_d):
    dataFrame['date'] = pd.to_datetime(dataFrame[['year','month','day']])
    dataFrame['date'] = pd.to_datetime(dataFrame['date'])
    dateStart = pd.Timestamp(s_y,s_m,s_d)
    dateEnd = pd.Timestamp(e_y,e_m,e_d)
    #df_filtrado= dataFrame[]
    df_filtrado= dataFrame[(dataFrame['date'] <= dateStart) & (dataFrame['date'] >= dateEnd)]
    return df_filtrado

#nlp = pipeline("question-answering", model='pierreguillou/bert-base-cased-squad-v1.1-portuguese')
isValidSpacy=True

try:
    nlp_spacy = spacy.load("pt_core_news_lg")
    isValidSpacy = True
except:
    spacy.cli.download("pt_core_news_lg")
    nlp_spacy = spacy.load("pt_core_news_lg")
    isValidSpacy = True
    
    
def dbg(title,v):
    if activeDebug:
        print("\n================================================ {}\n {}".format(title.upper(),v))

def DistanceWords(s, word1, word2):
        
        s = s.lower()
        word1 = word1.lower()
        word2 = word2.lower()

        word_tok = nlp_spacy(s)
        word_tok1 = nlp_spacy(word1)
        word_tok2 = nlp_spacy(word2)

        word1_positions = []
        word2_positions = []
        
        for i, word_t in enumerate(word_tok):
            if word_t.lemma_ == word_tok1[0].lemma_:
                word1_positions.append(i)
            elif word_t.lemma_ == word_tok2[0].lemma_:
                word2_positions.append(i)
        min_dist = float('inf')
        for pos1 in word1_positions:
            for pos2 in word2_positions:
                curr_dist = abs(pos1 - pos2) - 1
                #print("Current curr_dist: {}, Current min_dist: {}".format(curr_dist,min_dist))
                if curr_dist < min_dist:
                    min_dist = curr_dist
                    #print("Updated min_dist: {}".format(min_dist))
                    
        if min_dist == float('inf'):
            return 1e6  # retorna 1e6 se não houver nenhuma palavra no texto
        else:
            return min_dist
        
class FraseExtractor:
    stopwords = ['?','nº','n.º','No.','nro.','nr.','número','número.','numero','numero.',"o", "a", "os", "as", "um", "uma", "e", "ou", "de", "do", "da", "em", "para", "com", "por", "se", "só", "mais", "menos", "não", "nunca", "jamais", "mas", "porém", "todavia", "entretanto", "no", "na", "nos", "nas", "ao", "à", "aos", "às", "como", "onde", "quando", "porque", "porquê", "que", "quem", "qual", "cujo", "cujos", "cuja", "cujas", "é", "ser", "são", "seja", "sejam", "foi", "foram", "for", "sobre", "sob", "pelo", "pela", "pelos", "pelas", "até", "até", "esta", "estas", "estou", "estamos", "está", "estão", "estive", "estivemos", "esteve", "estiveram", "estava", "estávamos", "estavam", "estivera", "estiveram", "estiver", "estiverem", "esteja", "estejam", "estejamos", "estejam", "estivesse", "estivessemos", "estivessem", "estivesse", "estivessem", "estivéssemos", "estivéramos", "estivessem", "estivéssemos", "também", "ali", "lá", "aqui", "acolá", "hoje", "ontem", "amanhã", "logo", "cedo", "tarde", "noite", "manhã", "dia", "mês", "ano", "pouco", "muito", "quanto", "quão", "algum", "alguns", "alguma", "algumas", "nenhum", "nenhuns", "nenhuma", "nenhumas", "todo", "todos", "toda", "todas", "vários", "várias", "cada", "certo", "certa", "certos", "certas", "outro", "outra", "outros", "outras", "mesmo", "mesma", "mesmos", "mesmas", "próprio", "própria", "próprios", "próprias", "seu", "sua", "seus", "suas", "dele", "dela", "deles", "delas", "isso", "isso", "isto", "aquilo", "aquilo", "aqui", "aí", "ali", "lá", "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas", "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas", "vosso", "vossa", "vossos", "vossas", "deles", "delas", "me", "mim", "comigo", "te", "ti", "contigo", "se", "si", "consigo", "nos", "nós", "conosco", "vos", "vós", "convosco", "se", "si", "consigo", "o", "a", "os", "as", "ele", "ela", "eles", "elas", "você", "vocês", "lhe", "lhes", "teu", "tua", "teus", "tuas", "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas", "vosso", "vossa", "vossos", "vossas", "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas", "seu", "sua", "seus", "suas", "seu", "sua", "seus", "suas", "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas", "teu", "tua", "teus", "tuas", "teu", "tua", "teus", "tuas", "nós", "nós", "vós", "vós", "eu", "eu", "mim", "mim", "ti", "ti", "contigo", "contigo", "si", "si", "consigo", "consigo", "lhe", "lhe", "lhes", "lhes", "meu", "meu", "minha", "minha", "meus", "meus", "minhas", "minhas", "seu", "seu", "sua", "sua", "seus", "seus", "suas", "suas", "seu", "seu", "sua", "sua", "seus", "seus", "suas", "suas", "seu", "seu", "sua", "sua", "seus", "seus", "suas", "suas", "meu", "meu", "minha", "minha", "meus", "meus", "minhas", "minhas", "teu", "teu", "tua", "tua", "teus", "teus", "tuas", "tuas", "teu", "teu", "tua", "tua", "teus", "teus", "tuas", "tuas", "nosso", "nosso", "nossa", "nossa", "nossos", "nossos", "nossas", "nossas", "vosso", "vosso", "vossa", "vossa", "vossos", "vossos", "vossas", "vossas", "dele", "dele", "dela", "dela", "deles", "deles", "delas", "delas", "isso", "isso", "isto", "isto", "aquilo", "aquilo", "aqui", "aqui", "aí", "aí", "ali", "ali", "lá", "lá", "meu", "meu", "minha", "minha", "meus", "meus", "minhas", "minhas", "teu", "teu", "tua", "tua", "teus", "teus", "tuas", "tuas", "seu", "seu", "sua", "sua", "seus", "seus", "suas", "suas", "nosso", "nosso", "nossa", "nossa", "nossos", "nossos", "nossas", "nossas", "vosso", "vosso", "vossa", "vossa", "vossos", "vossos", "vossas", "vossas", "dele", "dele", "dela", "dela", "deles", "deles", "delas", "delas", "me", "me", "mim", "mim", "comigo", "comigo", "te", "te", "ti", "ti", "contigo", "contigo", "se", "se", "si", "si", "consigo", "consigo", "nos", "nos", "nós", "nós", "conosco", "conosco", "vos", "vos", "vós", "vós", "convosco", "convosco", "se", "se", "si", "si", "consigo", "consigo", "nós", "nós", "vós", "vós", "eu", "eu", "mim", "mim", "ti", "ti", "contigo", "contigo", "si", "si", "consigo", "consigo", "lhe", "lhe", "lhes", "lhes"]


    def __init__(self):
        self.nlp = spacy.load("pt_core_news_lg")
        self.matcher = PhraseMatcher(self.nlp.vocab)
        #self.list_stopwords()
        self.frases_padrao_localizacao = [
            "onde está", "ond esta", "onde esta",
            "você sabe onde está", "vc sabe onde esta", "voce sabe onde esta",
            "você pode me dizer onde está", "vc pode me dizer onde esta", "voce pode me dizer onde esta",
            "pode me ajudar a encontrar", "pode me ajud encontrar", "pode ajudar encontrar",
            "você viu", "vc viu", "voce viu",
            "sabe onde posso encontrar", "sabe onde encontrar", "sabe posso encontrar",
            "onde posso encontrar", "onde p encontrar", "onde posso achar",
            "você tem ideia de onde está", "vc tem ideia onde esta", "voce tem ideia onde esta",
            "você tem alguma ideia de onde eu poderia encontrar", "vc tem ideia onde posso achar", "voce tem ideia onde posso achar",
            "estou procurando", "to procurando", "estou proc",
            "encontre", "achar", "procure",
            "você poderia encontrar", "vc poderia encontrar", "voce poderia encontrar",
            "preciso que você encontre", "preciso q vc encontre", "preciso q voce encontre",
            "tente encontrar", "tente achar", "tente encontrar",
            "onde eu posso encontrar", "onde eu p achar", "onde eu posso achar",
            "pode me ajudar a encontrar", "pode me ajudar a achar", "pode me ajudar encontrar",
            "você sabe onde posso encontrar", "vc sabe onde posso achar", "voce sabe onde posso achar",
            "onde eu poderia encontrar", "onde eu poderia achar", "onde eu poderia encontrar",
            "você tem ideia de onde encontrar", "vc tem ideia onde achar", "voce tem ideia onde achar",
            "Em qual diario esta", "Em q diario está", "Em q diário ta", "Em qual diário tá",
            "Em qual dom esta", "Em q dom está","Em q dom ta", "Em qual dom tá", "Em qual dom esta", "Em qual jornal esta",
            "Em q jornal está","Em q jornal ta","Em qual jornal tá","Em qual jornal esta"
        ]
        
        self.patterns = [self.nlp.make_doc(text) for text in self.frases_padrao_localizacao]
        self.matcher.add("FrasesPadrao", None, *self.patterns)
        
        # Determinar o comprimento máximo da frase padrão
        self.max_len_frase_padrao = max(len(frase.split()) for frase in self.frases_padrao_localizacao)

    def pre_processar(self, frase):
        frase = frase.lower()
        frase = ' '.join([word.lemma_ for word in self.nlp(frase)])  # lemmatização
        return frase

    def extrair(self, frase):
        frase = self.pre_processar(frase)
        for frase_padrao in self.frases_padrao_localizacao:
            frase_padrao = self.pre_processar(frase_padrao)
            if frase_padrao in frase:  # Verifica se a frase padrão está na frase de entrada
                tokens = self.nlp(frase.split(frase_padrao, 1)[1].strip())
                return ' '.join([word.lemma_ for word in tokens if word.text.lower() not in self.stopwords])
        return None

def detectar_frases(texto):
    frases_padrao_localizacao = [
            "onde está", "ond esta", "onde esta",
            "você sabe onde está", "vc sabe onde esta", "voce sabe onde esta",
            "você pode me dizer onde está", "vc pode me dizer onde esta", "voce pode me dizer onde esta",
            "pode me ajudar a encontrar", "pode me ajud encontrar", "pode ajudar encontrar",
            "você viu", "vc viu", "voce viu",
            "sabe onde posso encontrar", "sabe onde encontrar", "sabe posso encontrar",
            "onde posso encontrar", "onde p encontrar", "onde posso achar",
            "você tem ideia de onde está", "vc tem ideia onde esta", "voce tem ideia onde esta",
            "você tem alguma ideia de onde eu poderia encontrar", "vc tem ideia onde posso achar", "voce tem ideia onde posso achar",
            "estou procurando", "to procurando", "estou proc",
            "encontre", "achar", "procure",
            "você poderia encontrar", "vc poderia encontrar", "voce poderia encontrar",
            "preciso que você encontre", "preciso q vc encontre", "preciso q voce encontre",
            "tente encontrar", "tente achar", "tente encontrar",
            "onde eu posso encontrar", "onde eu p achar", "onde eu posso achar",
            "pode me ajudar a encontrar", "pode me ajudar a achar", "pode me ajudar encontrar",
            "você sabe onde posso encontrar", "vc sabe onde posso achar", "voce sabe onde posso achar",
            "onde eu poderia encontrar", "onde eu poderia achar", "onde eu poderia encontrar",
            "você tem ideia de onde encontrar", "vc tem ideia onde achar", "voce tem ideia onde achar",
        "Em qual diario esta", "Em q diario está", "Em q diário ta", "Em qual diário tá",
    "Em qual diario esta?", "Em ql diario esta", "Em ql diario ta", "Em ql diário está", 
    "E qual diario esta", "E q diario esta", "E q diário tá", "M qual diario esta",
    "M qual diario ta", "M q diario está", "M q diário tá", "Em qual dom esta", "Em q dom está",
    "Em q dom ta", "Em qual dom tá", "Em qual dom esta?", "Em ql dom esta", "Em ql dom ta",
    "Em ql dom está", "E qual dom esta", "E q dom esta", "E q dom tá", "M qual dom esta",
    "M qual dom ta", "M q dom está", "M q dom tá", 
    "Em qual jornal esta",
    "Em q jornal está",
    "Em q jornal ta",
    "Em qual jornal tá",
    "Em qual jornal esta?",
    "Em ql jornal esta",
    "Em ql jornal ta",
    "Em ql jornal está",
    "E qual jornal esta",
    "E q jornal esta",
    "E q jornal tá",
    "M qual jornal esta",
    "M qual jornal ta",
    "M q jornal está",
    "M q jornal tá"
        ]
    
    frases_padrao_similaridade = [
        "similar:",
        "compare:"
    ]
    
    frases_padrao_ID = [
        "id:",
        "sec:",
        "dom:",
        "num",
    ]

    # Mantém apenas as 10 primeiras palavras do texto
    palavras = texto.split()
    if len(palavras) > 10:
        texto = ' '.join(palavras[:10])
    texto = texto.lower()  # Convertendo para lower case
    
    resultado = 0  # Valor padrão se não encontrar correspondência

    listas_de_frases = [frases_padrao_localizacao, frases_padrao_similaridade, frases_padrao_ID]
    
    for idx, lista_de_frases in enumerate(listas_de_frases, 1):
        for frase in lista_de_frases:
            ratio = fuzz.partial_ratio(texto, frase.lower())
            if ratio >= 75:
                #print(f"Frase '{texto}' corresponde à estrutura de frase '{frase}' com precisão de {ratio}%")
                resultado = idx  # Atualiza o resultado com o número do conjunto de frases
                break  # Pára a iteração assim que encontra a primeira correspondência
        if resultado:
            break  # Se já encontrou uma correspondência, interrompe a iteração sobre as listas de frases

    return resultado  # Retorna o resultado

import re

class find_id():
    def __init__(self, nums_id, df):
        self.df_matched = self.find_id_func(nums_id, df)
    
    def find_id_func(self, nums_id, df):
        df_copy = df.copy(deep=True)
        matches = re.sub(r'id: ', '', nums_id).split()
        
        # Cria uma nova coluna 'match' com valores False
        df_copy['match'] = False
        
        # Para cada linha do dataframe
        for idx, row in df_copy.iterrows():
            # Se algum dos IDs desejados está contido na coluna 'ids' da linha
            if any(match in row['ids'] for match in matches):
                # Marca a linha como um 'match'
                df_copy.at[idx, 'match'] = True
                
        # Filtra as linhas onde 'match' é True
        df_matched = df_copy[df_copy['match'] == True]
        
        return df_matched

    def get_matched_rows(self):
        return self.matched_rows

class find_sec:
    def __init__(self, sec_name, query):
        self.sec_name = sec_name
        self.query = query
        self.results = self.check_sec_in_ids()

    def list_sec(self):
        sec_dict = {
            "PODER" :"00048",
            "SEMA" :"00042",
            "SEMF" :"00043",
            "SEMCASPI" :"00049",
            "SEMDEF" :"00052",
            "SEMP" :"00053",
            "SEMDUH" :"00030",
            "SEMPPM" :"00031",
            "SEMEST" :"00035",
            "SEMAM" :"00037",
            "SEMEC" :"00044",
            "SEMPLAN" :"00046",
            "PGM" :"00047",
            "SEMGOV" :"00048",
            "SEMJUV" :"00057",
            "SEMEL" :"00078",
            "SEMCOM" :"00086",
            "SEMDEC" :"00093",
            "ARSETE" :"00055",
            "ETURB" :"00081",
            "PRODATER" :"00021",
            "FMS" :"00045",
            "FCMC" :"00066",
            "FWF" :"00094",
            "IPMT" :"00041",
            "STRANS" :"00077",
            "SUL" :"00070",
            "NORTE" :"00050",
            "CENTRO" :"00051",
            "LESTE" :"00082",
            "SUDESTE" :"00097",
            "RURAL" :"00083",
            "LICITAÇÕES" :"00042",
            "LICITAÇÃO" :"00042",
            "CPL" :"00042",
            "CPL FMS" :"00045",
            "CÂMARA" :"00001",
        }
        
        return sec_dict.get(self.sec_name.upper(), None)

    def extract_ids(self,text):
        res = re.findall(r'id: (\d+)', text.lower())
        first_5_digits = [num[:5] for num in res]
        return first_5_digits

    def check_sec_in_ids(self):
        sec_number = self.list_sec()
        if sec_number == "Seção não encontrada":
            print(f"Seção '{self.sec_name}' não encontrada no dicionário")
            return []

        results = []
        for instance in self.query:
            ids = self.extract_ids(instance.text)
            if sec_number in ids:
                results.append(instance)

        return results

    def result(self):
        return self.results

class find_dom:
    def __init__(self, dom_name, DataDom):
        self.DataDom = DataDom
        self.dom_numbers = self.extract_ids(dom_name)
        self.dom_rows = self.find_dom_rows()

    def extract_ids(self, text):
        res = re.findall(r'\d+', text)
        numbers = [int(num) for num in res]
        return numbers

    def find_dom_rows(self):
        dom_rows = []
        for dom_number in self.dom_numbers:
            dom_rows.extend(self.DataDom.query.filter(self.DataDom.title.contains(f"DOM{dom_number}")).all())
        return dom_rows

    def result(self):
        dom_rows_dicts = [self.row_to_dict(row) for row in self.dom_rows]
        return pd.DataFrame(dom_rows_dicts)
    
    @staticmethod
    def row_to_dict(row):
        row_dict = row.__dict__
        if "_sa_instance_state" in row_dict:
            del row_dict["_sa_instance_state"]
        return row_dict

class find_dom_df:
    def __init__(self, dom_name, df):
        self.df = df.copy()
        self.dom_numbers = self.extract_ids(dom_name)
        self.dom_rows = self.find_dom_rows()

    def extract_ids(self,text):
        res = re.findall(r'\d+', text)
        numbers = [int(num) for num in res]
        return numbers

    def find_dom_rows(self):
        mask = [any(f"DOM{dom_number}" in title for dom_number in self.dom_numbers) for title in self.df["title"]]
        return self.df[mask]

    def result(self):
        return self.dom_rows

class find_num_doc():
    def __init__(self, sec_name, df):
        self.sec_name = sec_name
        self.df = self.check_sec_in_ids(df.copy())
    
    def extract_ids(self,text):
        # Atualizar a expressão regular para pegar os quatro dígitos antes dos últimos quatro
        res = re.findall(r'id:\s*\d*(\d{4})\d{4}', text.lower())
        return res

    def check_sec_in_ids(self, df):
        sec_number = self.sec_name
        if sec_number == "Seção não encontrada":
            return df

        df['ids'] = df['text'].apply(self.extract_ids)
        mask = []

        for index, row in df.iterrows():
            for ids in row['ids']:
                if sec_number == ids:
                    mask.append(True)
                    break                    
            else:
                mask.append(False)

        if not any(mask):  # Se a máscara não contém nenhum True
            return pd.DataFrame()  # Retorna um novo DataFrame vazio
        else:
            return df[mask]  # Retorna o DataFrame filtrado

    def result(self):
        return self.df

class OrdDocs:
    def __init__(self, data):
        self.data = data

    def organize_by_score(self):
        scores = [(title, min((item['score'] if item['score'] is not None else float('inf')) for item in items)) for title, items in self.data['titles'].items()]
        scores = sorted(scores, key=lambda x: x[1])
        self.data['titles'] = {title: self.data['titles'][title] for title, score in scores}

        return self.data

    def __dict__(self):
        return self.data

class TransformData:
    def __init__(self, df):
        self.df = df

    def transform(self):
        data_dict = {"titles": {}}

        for index, row in self.df.iterrows():
            title = row['title']
            page = row['page']
            # você pode ajustar a lógica de cálculo de score e total_words de acordo com sua necessidade
            #score = None  
            #score1 = len(row['nums'])
            #total_words = len(row['text'].split())
            if title not in data_dict:
                data_dict['titles'][title] = []
                
            data_dict['titles'][title].append({
                'page': page,
                'score': 0,
                'score1': 0,
                'total_words': 0
            })
        
        return data_dict

class ultrabs:
    res = ['','']
    termoSearch = ''
    
    def __init__(self, text,df, query, DataDom) -> None:
        ret = pd.DataFrame()
        num_func = detectar_frases(text)
        
        if num_func == 1:
            extractor = FraseExtractor()
            text = extractor.extrair(text)
            self.termoSearch = text    
            if ("dom :" in text.lower()) and "sec :" not in text.lower():
                dom_num = text.lower().split("dom : ")[1]
                dom_num = "dom: "+dom_num
                finder = find_dom(dom_num,DataDom)
                result = finder.result()
                fuzzDic = self.fuzzySearch(text,result, toplist=50)
                ret = self.stepMeterDistances(text.lower().split("dom : ")[0], fuzzDic)
                dbg("OUTPUT SEARCH WITH DOM", ret) 
                
            elif ("sec :" in text.lower()) and "dom :" not in text.lower():
                sec_name = text.lower().split("sec : ")[1]
                #print(text.lower().split("sec : ")[0])
                #print(sec_name)
                
                finder = find_sec(sec_name,query)
                result = finder.result()
                listToDf = pd.DataFrame([instance.__dict__ for instance in result])
                
                fuzzDic = self.fuzzySearch(text,listToDf, toplist=50)
                ret = self.stepMeterDistances(text.lower().split("sec : ")[0], fuzzDic)
                dbg("OUTPUT SEARCH WITH SEC", ret) 
            else:
                
                fuzzDic = self.fuzzySearch(text,df, toplist=50)
                ret = self.stepMeterDistances(text, fuzzDic)
                dbg("OUTPUT SEARCH",ret)    
            
        if num_func == 3:
            
            if ("id:" in text.lower()) and "sec:" not in text.lower() and "dom:" not in text.lower():
                
                self.termoSearch = 'por chave ID '+text.split('id: ')[1]
                res_id= find_id(text,df).df_matched
                data_to_dic = TransformData(res_id)
                transformed_data = data_to_dic.transform()
                ret = transformed_data
                
            if ("sec:" in text.lower()) and "dom:" not in text.lower() and "id:" not in text.lower():
                sec_name = text.lower().split(" ")[1]
                ret1 = find_sec(sec_name,query)
                finder = ret1.result()
                listToDf = pd.DataFrame([instance.__dict__ for instance in finder])
                self.termoSearch = 'por secretaria '+text.split('sec: ')[1]
                if ("num:" in text.lower()):
                    sec_name1 = text.lower().split("num: ")[1]
                    self.termoSearch = 'por secretaria '+sec_name + ' e numero do documento ' + sec_name1
                    result_fn = find_num_doc(sec_name1,listToDf).df
                    data_to_dic = TransformData(result_fn)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                else:
                    data_to_dic = TransformData(listToDf)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                    
                
            if ("dom:" in text.lower()) and "sec:" not in text.lower():
                dom_name = text.lower().split("num: ")[0]
                dom_name = dom_name.split('dom: ')[1]
                
                finder = find_dom(dom_name,DataDom)
                result = finder.result()
                self.termoSearch = 'por numero do DOM '+dom_name
                
                if ("num:" in text.lower()):
                    sec_name = text.lower().split("num: ")[1]
                    self.termoSearch = 'por DOM '+ dom_name + ' e numero do documento ' + sec_name
                    result_fn = find_num_doc(sec_name,result).df
                    data_to_dic = TransformData(result_fn)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                    
                else:
                    data_to_dic = TransformData(result)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                    
            if ("dom:" in text.lower()) and "sec:" in text.lower() and "num:" in text.lower():
                sec_name = ''
                if ("num:" in text.lower()):
                    sec_name1 = text.lower().split("num: ")
                    sec_name = sec_name1[0].lower().split("sec: ")
                    
                else:
                    sec_name1 = text.lower().split("sec: ")
                
                self.termoSearch = 'por DOM '+ sec_name[0].split('dom: ')[1] +', secretaria '+ sec_name[1].strip().upper() + ' e numero do documento ' + sec_name1[1]
                
                ret1 = find_sec(sec_name[1].strip(),query)
                finder1 = ret1.result()
                listToDf = pd.DataFrame([instance.__dict__ for instance in finder1])
                
                finder = find_dom_df(sec_name[0].split('dom: ')[1],listToDf)
                result = finder.result()
                
                if ("num:" in text.lower()):
                    result_fn = find_num_doc(sec_name1[1],result).df
                    data_to_dic = TransformData(result_fn)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                else:
                    data_to_dic = TransformData(result)
                    transformed_data = data_to_dic.transform()
                    ret = transformed_data
                    
            if ("dom:" in text.lower()) and "sec:" in text.lower() and "num:" not in text.lower():
                sec_name = text.lower().split("sec: ")
                self.termoSearch = 'por DOM '+ sec_name[0].split('dom: ')[1] +', secretaria '+ sec_name[1].strip().upper()
                ret1 = find_sec(sec_name[1].strip(),query)
                finder1 = ret1.result()
                listToDf = pd.DataFrame([instance.__dict__ for instance in finder1])
                
                finder = find_dom_df(sec_name[0].split('dom: ')[1],listToDf)
                result = finder.result()
                
                data_to_dic = TransformData(result)
                transformed_data = data_to_dic.transform()
                ret = transformed_data
                                
        if type(ret) == dict:
            self.res = ret
        else:
            try:            
                if ret.df.empty:
                    self.res = [] #Returna vazio
                else:
                    self.res = ret
            except:
                if ret.empty:
                    self.res = [] #Returna vazio
                else:
                    self.res = ret
        #try:
        #except:
        #    self.res = {'Error':'Error'}
    def removerStopWords(self,input_text):
        new_stop_words = ['ano','uso','diário','diario', 'oficial','DOM', 'dom','municipal', 'secretário', 'secretario', 'secretaria','orgânica',
                  'município', 'gabinete', 'prefeito','prefeitura', 'presidente', 'fundação','e','s', 'p', 't', 'c', 
                  'n', 'nº', 'n°','º', '°','diário oficial', "i", "ii", "iii", "iv", "v", "vi", 
                  "vii", "viii", "ix", "x","xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", 
                  "xix", "xx", "xxi", "xxii", "xxiii", "xxiv", "xxv", "xxvi", "xxvii", "xxviii", 
                  "xxix", "xxx","xxxi", "xxxii", "xxxiii", "xxxiv", "xxxv", "xxxvi", "xxxvii", 
                  "xxxviii", "xxxix", "xl","xli", "xlii", "xliii", "xliv", "xlv", "xlvi", "xlvii", 
                  "xlviii", "xlix", "l","li", "lii", "liii", "liv", "lv", "lvi", "lvii", "lviii", "lix", "lx"]
        for word in new_stop_words:
            nlp_spacy.vocab[word].is_stop = True
        
        input_text = input_text.lower()
        doc_text_clean = [word.lemma_ for word  in nlp_spacy(input_text) if not (word.is_stop or word.is_punct or (word.pos_ == 'VERB'))]
        doc_text_clean = ' '.join([str(element) for element in doc_text_clean])
        doc_text_clean = doc_text_clean.replace("\n ", "")
        doc_text_clean = doc_text_clean.replace("\n", "")
        doc_text_clean = nlp_spacy(doc_text_clean)
        return doc_text_clean
    
    def fuzzySearch(self,text,dataFrame, toplist=10):
    #text_seacher= 
        text_seacher_sentece = self.removerStopWords(text)
        dataset_doc = {}
        
        for index, row in dataFrame.iterrows():
            dataset_doc[index] = fuzz.token_set_ratio(row['text'], text_seacher_sentece)

        sorted_scores = sorted(dataset_doc.items(), key=operator.itemgetter(1), reverse = True)
        HTMLbox =''
        listDoc = {
                    "index":[],
                    "title":[],
                    "page":[],
                    "score":[],
                    "text":[]
                    }
        for i in sorted_scores[:toplist]:
            page = dataFrame['page'][i[0]]
            title = dataFrame['title'][i[0]]
            score = i[1]
            
            listDoc["index"].append(i[0])
            listDoc["title"].append(title)
            listDoc["page"].append(page)
            listDoc["score"].append(score)
            listDoc["text"].append(dataFrame['text'][i[0]])
            
            #print('Titulo:{} ; pagína:{}; Combinações:{}; \n'.format(title,page,score))
        return listDoc
    
    def ExtratTextToFindInDOM(self, Input_text):    
        matcher = Matcher(nlp_spacy.vocab)
        #pattern = [{"POS": "NOUN", "OP": "+"},{"POS":"NUM"}]
        if 'ano' in Input_text.text:
            pattern = [{"POS": {"IN":["ADJ","NOUN"]}, "OP": "{1,2}"},
                        {"POS":{"IN":["PROPN","NUM"]}},
                        {"TEXT": "ano"},
                        {"POS":"NUM"}
                    ]
        else:
            pattern = [{"POS": {"IN":["ADJ","NOUN"]}, "OP": "{1,2}"},
                        {"POS":{"IN":["PROPN","NUM"]},"OP": "{1,2}"}
                    ]
        matcher.add("SearchText", [pattern])

        matches = matcher(Input_text)
        span = []
        for match_id, start, end in matches:
            span_t = Input_text[start:end]
            span.append(str(span_t))
        return max(span, key=len)

    def ExtractTextDown(self, input_text):
        text_after_first_break = input_text.split('\n', 1)[1]
        return text_after_first_break
       
    def sumDistances(self, s_data):
        summ = 0

        for i in s_data:
            if i != 1e6:
                summ = summ + i

            if i == 1e6:
                return None
        return summ
        
    def stepMeterDistances(self,shared_s,sentences):
        shared_s_tok = nlp_spacy(shared_s)
        
        list_score = {"titles":{}}
        for j, s in enumerate(sentences['text']):
            list_score['titles'][sentences['title'][j], sentences['page'][j]] = []
            
        for key in list_score['titles']:
            title, page = key
            title_index = sentences['title'].index(title)  # Encontre o índice do título
            for j in range(1, len(shared_s_tok)):
                min_dist = DistanceWords(sentences['text'][title_index], shared_s_tok[j-1].lemma_, shared_s_tok[j].lemma_)  # Use o índice do título
                list_score['titles'][key].append(min_dist)
        
        dbg("LIST SCORE STAGE 1",list_score)
        for i in list_score['titles']:
            list_score['titles'][i]=self.sumDistances(list_score['titles'][i])
        dbg("LIST SCORE STAGE 2",list_score)
        filtered_result = {key: value for key, value in list_score['titles'].items() if value is not None}
        dbg("FILTER RESULT STAGE",filtered_result)
        
        words = [token.text for token in shared_s_tok]

        vectorizer = CountVectorizer(vocabulary=words)
        word_count_dict = {}
        for title in sentences['title']:
            word_count_dict[title] = 0  # cria um dicionário que retorna 0 se a chave não existe

        for i, title in enumerate(sentences['title']):
            X = vectorizer.transform([sentences['text'][i]])
            word_counts = X.toarray().sum(axis=0)  # soma as ocorrências de cada palavra
            word_count_dict[title] += sum(word_counts)  # soma o total de ocorrências para o título

        dbg("SCORE 1 STAGE",word_count_dict)
        
        #dbg("SCORES 1 STAGE ",scores)
        list_doc = {"titles": {}}

        for idx, (title, page, sentence, score3) in enumerate(zip(sentences['title'], sentences['page'], sentences['text'],sentences['score'])):
            
            score1 = word_count_dict[title]
            #print(f"score1 {score1}")
            # Check if the key exists in filtered_result
            if (title, page) in filtered_result:
                score = filtered_result[title, page]
            else:
                score = None
            
            # I= ADICIONAR UM RECURSO NA INFARCE PARA CONFIGURA O VALOR DE COMPARAÇÃO DO SCORE 3
            if (score != None or score3 >= 85) and ((score1 > 1)):
                # If the title is not in list_doc, add it
                if title not in list_doc["titles"]:
                    list_doc["titles"][title] = []
                # Add the page and score as a new dict to the list of titles
                list_doc["titles"][title].append({
                    'page': page,
                    'score': score,
                    'score1':score1,
                    'total_words': len(shared_s_tok)
                })
        dbg("LIST DOC",list_doc)
        return list_doc
        """
        list_doc = {"titles":{}}
        for key in filtered_result:
            title, page = key
            score = filtered_result[title, page]
            
            # Se o título ainda não existe no dicionário, adicione-o
            if title not in list_doc['titles']:
                list_doc['titles'][title] = []
            
            # Adicione a página e a pontuação como um novo dicionário à lista de títulos
            list_doc['titles'][title].append({'page': page, 'score': score})
        dbg("LIST DOC STAGE",list_doc)
        return list_doc
        """
    
    def reOrde(self, res, fuzzyDic):
        rows = []
        for i in res:
            for j, f in enumerate(fuzzyDic['title']):
                if i == f:
                    # create a row dictionary and append to list
                    rows.append({"title": fuzzyDic['title'][j], "page": fuzzyDic['page'][j]})

        # create DataFrame using concat
        df = pd.concat([pd.DataFrame([i], columns=["title", "page"]) for i in rows], ignore_index=True)
        return df
    
    
    
