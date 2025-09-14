import spacy
import pandas as pd
import ast

# Load the trained model
nlp = spacy.load("./skill_ner_model")

# Load test data from the new location
df = pd.read_csv("app/test_data/test_data.csv")
TEST_DATA = []
for _, row in df.iterrows():
    text = str(row['text']).strip()
    entities = ast.literal_eval(str(row['entities']).strip())
    TEST_DATA.append((text, {"entities": entities}))

correct = 0
total = 0

for text, annotations in TEST_DATA:
    doc = nlp(text)
    predicted = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    actual = annotations["entities"]
    if predicted == actual:
        correct += 1
    total += 1

print(f"Accuracy: {correct/total:.2f}")