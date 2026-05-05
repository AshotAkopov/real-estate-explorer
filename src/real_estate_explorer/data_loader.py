import pandas as pd
from .config import APPARTEMENTS_FILE, MAISONS_FILE


def load_appartements():
    df = pd.read_csv(APPARTEMENTS_FILE)
    df["type_bien"] = "Appartement"
    return df


def load_maisons():
    df = pd.read_csv(MAISONS_FILE)
    df["type_bien"] = "Maison"
    return df


def load_all_data():
    df_appart = load_appartements()
    df_maisons = load_maisons()

    return pd.concat([df_appart, df_maisons], 
                     ignore_index=True)
