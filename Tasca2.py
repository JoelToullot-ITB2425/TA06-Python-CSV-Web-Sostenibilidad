import os
import re

def verificar_fitxers_dat_personalitzats(directori):
    """
    Comprova fitxers .dat per a diferents normes segons el tipus de línia:
    - Nom del fitxer: "precip.PX.MIROC5.RCP60.2006-2100.REGRESION.dat", on PX ha de coincidir amb la columna inicial
      de totes les línies (excepte la primera).
    - Primera línia: Ha de coincidir exactament amb "precip MIROC5 RCP60 REGRESION decimas 1".
    - Segona línia: Ha de començar amb PX i complir el format especificat, i conté el rang d'anys que s'ha de respectar.
    - Altres línies: Cada fila ha de tenir exactament 31 dies, els valors han d'estar entre 0 i 1344 (excepte '-999'),
      i no han de contenir lletres. Els valors han d'estar separats per exactament un espai. Els anys han de respectar
      el rang especificat a la segona línia.
    - Les combinacions d'any i mes no poden repetir-se dins del mateix fitxer.
    """
    errors = []

    for arxiu in os.listdir(directori):
        if arxiu.endswith('.dat'):  # Comprova si és un fitxer .dat
            ruta_fitxer = os.path.join(directori, arxiu)

            # Obtenir el valor PX del nom del fitxer
            filename_regex = r"^precip\.(P\d+)\.MIROC5\.RCP60\.2006-2100\.REGRESION\.dat$"
            match = re.match(filename_regex, arxiu)
            if not match:
                errors.append(f"Nom de fitxer incorrecte: {arxiu}")
                continue

            px_expected = match.group(1)

            try:
                # Llegeix el fitxer línia per línia
                with open(ruta_fitxer, 'r') as f:
                    linies = f.readlines()

                if not linies:
                    errors.append(f"Fitxer buit: {ruta_fitxer}")
                    continue

                # Comprovar primera línia
                primera_linia_esperada = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
                if linies[0].strip() != primera_linia_esperada:
                    errors.append(f"Primera línia incorrecta al fitxer {ruta_fitxer}: {linies[0].strip()}")

                # Comprovar segona línia
                if len(linies) > 1:
                    segona_linia = linies[1].strip()
                    segona_regex = fr"^{px_expected}\t-?\d+\.\d+\t-?\d+\.\d+\t182\tgeo\t(\d+)\t(\d+)\t-1$"
                    match = re.match(segona_regex, segona_linia)
                    if not match:
                        errors.append(f"Segona línia incorrecta al fitxer {ruta_fitxer}: {segona_linia}")
                        continue

                    # Extreure el rang d'anys
                    any_inicial, any_final = int(match.group(1)), int(match.group(2))

                else:
                    errors.append(f"Segona línia no present al fitxer {ruta_fitxer}")
                    continue

                # Conjunt per registrar combinacions any-mes
                combinacions_any_mes = set()

                # Comprovar altres línies
                for i, linia in enumerate(linies[2:], start=3):  # Comença des de la línia 3
                    linia = linia.strip()

                    # Ignora la primera columna (P1, P2, etc.)
                    elements = linia.split()
                    if len(elements) < 4:
                        errors.append(f"Nombre insuficient de columnes al fitxer {ruta_fitxer}, línia {i}: {linia}")
                        continue

                    # Comprova si hi ha espais múltiples entre números
                    if "  " in linia:  # Cerca doble espai a la línia original
                        errors.append(f"Espais múltiples detectats al fitxer {ruta_fitxer}, línia {i}: {linia}")

                    # Comprova que la primera columna coincideix amb PX esperat
                    if elements[0] != px_expected:
                        errors.append(f"Identificador incorrecte al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperat: {px_expected}, Trobat: {elements[0]}")

                    # Comprova l'any (segona columna)
                    any_ = elements[1]
                    if not (any_.isdigit() and any_inicial <= int(any_) <= any_final):
                        errors.append(f"Any fora de rang al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperat: {any_inicial}-{any_final}, Trobat: {any_}")
                        continue

                    # Comprova el mes (tercera columna)
                    mes = elements[2]
                    if not (mes.isdigit() and 1 <= int(mes) <= 12):
                        errors.append(f"Mes invàlid (fora del rang 1-12) al fitxer {ruta_fitxer}, línia {i}: {mes}")
                        continue

                    # Comprova si la combinació any-mes ja existeix
                    combinacio_any_mes = (int(any_), int(mes))
                    if combinacio_any_mes in combinacions_any_mes:
                        errors.append(f"Duplicat any-mes detectat al fitxer {ruta_fitxer}, línia {i}: {linia}")
                        continue
                    else:
                        combinacions_any_mes.add(combinacio_any_mes)

                    # Extreu les dades després del mes
                    dies = elements[3:]

                    # Comprova que la línia té exactament 31 valors per als dies
                    if len(dies) != 31:
                        errors.append(f"Nombre incorrecte de dies al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperats: 31, Trobats: {len(dies)}")
                        continue

                    # Comprova que els valors estan entre 0 i 1344 o són '-999'
                    for j, dia in enumerate(dies, start=4):  # Columnes dels dies comencen des de la 4
                        if dia != "-999":
                            if not dia.isdigit():
                                errors.append(f"Valor invàlid detectat (no numèric) al fitxer {ruta_fitxer}, "
                                              f"línia {i}, columna {j}: {dia}")
                            elif not (0 <= int(dia) <= 1344):
                                errors.append(f"Valor fora de rang (0-1344) al fitxer {ruta_fitxer}, "
                                              f"línia {i}, columna {j}: {dia}")

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
verificar_fitxers_dat_personalitzats(directori)
