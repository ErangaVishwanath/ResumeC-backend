import spacy
from spacy.training import Example
import pandas as pd

TRAIN_DATA = pd.read_csv("app/train_data.csv").values.tolist()

def train_ner(output_dir="./skill_ner_model", n_iter=30):
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")
    ner.add_label("SKILL") # type: ignore
    optimizer = nlp.begin_training()

    for itn in range(n_iter):
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, drop=0.3, losses=losses)
        print(f"Iteration {itn}: {losses}")

    nlp.to_disk(output_dir)
    print("Model saved to", output_dir)

if __name__ == "__main__":
    train_ner()
