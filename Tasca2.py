import os
import re


def verificar_fitxers_dat_pandas(directori):
    """
    Comprova fitxers .dat en un directori per inconsistències, valors nuls, lletres no desitjades,
    i espais extres entre números, només aplicant les validacions a les línies del tipus 'P1 <any>'.
    """
    errors = []

    for arxiu in os.listdir(directori):
        if arxiu.endswith('.dat'):  # Comprova si és un fitxer .dat
            ruta_fitxer = os.path.join(directori, arxiu)

            try:
                # Llegeix el fitxer línia per línia
                with open(ruta_fitxer, 'r') as f:
                    linies = f.readlines()

                if not linies:
                    errors.append(f"Fitxer buit: {ruta_fitxer}")
                    continue

                for i, linia in enumerate(linies):
                    linia = linia.strip()

                    # Ignora línies que no comencen amb el format 'P1 <year>'
                    if not re.match(r'^P1 \d{4}', linia):
                        continue

                    # Comprova si hi ha més d'un espai entre números
                    if "  " in linia:
                        errors.append(f"Espais extres al fitxer {ruta_fitxer}, línia {i + 1}: {linia}")

                    # Comprova si hi ha lletres on no haurien d'haver-n'hi
                    elements = linia.split()
                    if len(elements) > 3:  # Ignora les primeres 3 columnes
                        for element in elements[3:]:
                            if not re.match(r"^-?\d+(\.\d+)?$", element):
                                errors.append(f"Lletres detectades al fitxer {ruta_fitxer}, línia {i + 1}: {linia}")
                                break

            except Exception as e:
                errors.append(f"Error al processar {ruta_fitxer}: {e}")

    # Resultats
    if errors:
        print("Errors detectats:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Tots els fitxers .dat són vàlids i no tenen errors.")


# Exemple d'ús
directori = './V2precip.MIROC5.RCP60.2006-2100.SDSM_REJ'
verificar_fitxers_dat_pandas(directori)
