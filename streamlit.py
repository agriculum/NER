

# imports
import streamlit as st
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Token, Span
from spacy import displacy
from spacy.pipeline import EntityRuler
from spacy.kb import KnowledgeBase
from py2neo import Graph,Subgraph,Node,Relationship,cypher,data
import pandas as pd
from pandas import DataFrame
import numpy as np

# Dataframe load
dfrel = pd.read_csv("/home/luca/Workspace/classrel.csv")
dftok = pd.read_csv("/home/luca/Workspace/tokenclass.csv")

# Model load, NLP object init, vocab init
nlp = spacy.load("en_core_web_sm")
vocab = nlp.vocab

# Phrase matcher init
matcher = PhraseMatcher(nlp.vocab,attr="LOWER")
from spacy.pipeline import EntityRuler

# entity ruler creation
nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp)

# creates a dataframe containing all classes
#cursor = graph.run("match (class:Class) return class.name ")
#df = DataFrame()

# creates a list of class nodes
#classList = list(df[0])
patterns = []

# Creating a list of Tokens, calling it tokenlist, creo un pattern per ogni classe che trovo... oppure...
#for tokenClass in classList:
#    cursor = graph.run("match (t:Token)-[:INSTANCE_OF]->(c:Class {name:'"+tokenClass+"'}) return t.name")
#    df = DataFrame(cursor)
#    tokenList = list(df[0])
#    tokenList = [t.lower() for t in tokenList]

#tokenclass è una stringa rappresentante la classe
#tokenlist è un lista contenente i nomi di tutti i token appartenenti a una specifica classe

#add patterns to phrase matcher
for index, row in dftok.iterrows():
    patterns.append({"pattern":(row["token"].lower()),"label":row["class"]})
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)

#funzione che associa ad ogni token la sua classe
def toktoclass(token):
    result = ""
    for index, row in dftok.iterrows():
        if(row["token"].lower() == token.lower()):
            result = row["class"]
    return result


#funzione classe + relazione -> classe
def finder(entity,relation):
    result = ""
    entity = toktoclass(entity)
    for index, row in dfrel.iterrows():
        if(row["rel"] == (relation).replace(" ","_").upper()):
            if(row["start"].lower() == entity.lower()):
                return row["end"]
            else:
                return row["start"]
    return result;


 #entity finder function
def entFinder(doc, entity):
    
    root1 = entity.root
    deps = dict()
    deps.update({root1.dep_:root1})
    
    for root2 in doc:
        deps.update({root2.dep_:root2})
        
    nsubj = deps.get("nsubj")
    dobj = deps.get("dobj")
    root = deps.get("ROOT")
        
    if(nsubj != None and dobj != None and root != None):

        resultingClass = finder(entity.label_,root.lemma_);

        if(resultingClass!="notFound"):
            if(dobj.text == entity.text):
            	st.write(nsubj.text,":",resultingClass)
            	return {"pattern":nsubj.text.lower(),"label":resultingClass}
            else:
            	st.write(dobj.text,":",resultingClass)
            	return {"pattern":dobj.text.lower(),"label":resultingClass}




st.title("Entity Finder")

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; 
                margin-bottom: 2.5rem">{}</div>"""

# text input
phrase = st.text_area("Enter your sentence...")



if st.button("Find Entities"):
	hush = dict()
	doc = nlp(phrase)
	st.subheader("Known Entities in the text:")

	#matcher(doc)
	html = displacy.render(doc, style="ent")

	# Newlines seem to mess with the rendering
	html = html.replace("\n", " ")
	st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)


	st.subheader("New entities found:")
	toAdd = entFinder(doc,doc.ents[0])
	#new = []
	#new.append(toAdd)
	#ruler.add_patterns(new)

	#st.subheader("Update Matcher data?")	
	#st.checkbox("Update Matcher")

st.header("Matcher DataFrame")
if st.button("Show Recognized Input"):
	st.subheader("Valid relations")
	st.dataframe(dfrel)
	st.subheader("Valid tokens")
	st.dataframe(dftok)