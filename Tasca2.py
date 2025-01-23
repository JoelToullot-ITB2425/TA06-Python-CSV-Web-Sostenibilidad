import os
import re
import logging

def configurar_logging():

    logging.basicConfig(
        filename='TA06.log',
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def verificar_fitxers_dat_personalitzats(directori):

    errors = []

    try:

        if not os.path.exists(directori):
            raise FileNotFoundError(f"Directori no trobat: {directori}")


        fitxers_dat = [arxiu for arxiu in os.listdir(directori) if arxiu.endswith('.dat')]


        if not fitxers_dat:
            errors.append("No s'han detectat fitxers amb l'extensió .dat al directori especificat.")
            raise FileNotFoundError("Directori buit o sense fitxers .dat")

        for arxiu in fitxers_dat:
            ruta_fitxer = os.path.join(directori, arxiu)


            filename_regex = r"^precip\.(P\d+)\.MIROC5\.RCP60\.2006-2100\.REGRESION\.dat$"
            match = re.match(filename_regex, arxiu)
            if not match:
                errors.append(f"Nom de fitxer incorrecte: {arxiu}")
                continue

            px_expected = match.group(1)

            try:

                with open(ruta_fitxer, 'r') as f:
                    linies = f.readlines()

                if not linies:
                    errors.append(f"Fitxer buit: {ruta_fitxer}")
                    continue

                primera_linia_esperada = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
                if linies[0].strip() != primera_linia_esperada:
                    errors.append(f"Primera línia incorrecta al fitxer {ruta_fitxer}: {linies[0].strip()}")

                if len(linies) > 1:
                    segona_linia = linies[1].strip()
                    segona_regex = fr"^{px_expected}\t-?\d+\.\d+\t-?\d+\.\d+\t182\tgeo\t(\d+)\t(\d+)\t-1$"
                    match = re.match(segona_regex, segona_linia)
                    if not match:
                        errors.append(f"Segona línia incorrecta al fitxer {ruta_fitxer}: {segona_linia}")
                        continue

                    any_inicial, any_final = int(match.group(1)), int(match.group(2))

                else:
                    errors.append(f"Segona línia no present al fitxer {ruta_fitxer}")
                    continue

                combinacions_any_mes = set()

                for i, linia in enumerate(linies[2:], start=3):
                    linia = linia.strip()

                    if "  " in linia:
                        errors.append(f"Espais extres al fitxer {ruta_fitxer}, línia {i + 1}: {linia}")

                    elements = linia.split()
                    if len(elements) < 4:
                        errors.append(f"Nombre insuficient de columnes al fitxer {ruta_fitxer}, línia {i}: {linia}")
                        continue

                    if elements[0] != px_expected:
                        errors.append(f"Identificador incorrecte al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperat: {px_expected}, Trobat: {elements[0]}")

                    any_ = elements[1]
                    if not (any_.isdigit() and any_inicial <= int(any_) <= any_final):
                        errors.append(f"Any fora de rang al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperat: {any_inicial}-{any_final}, Trobat: {any_}")
                        continue

                    mes = elements[2]
                    if not (mes.isdigit() and 1 <= int(mes) <= 12):
                        errors.append(f"Mes invàlid (fora del rang 1-12) al fitxer {ruta_fitxer}, línia {i}: {mes}")
                        continue

                    combinacio_any_mes = (int(any_), int(mes))
                    if combinacio_any_mes in combinacions_any_mes:
                        errors.append(f"Duplicat any-mes detectat al fitxer {ruta_fitxer}, línia {i}: {linia}")
                        continue
                    else:
                        combinacions_any_mes.add(combinacio_any_mes)

                    dies = elements[3:]

                    if len(dies) != 31:
                        errors.append(f"Nombre incorrecte de dies al fitxer {ruta_fitxer}, línia {i}. "
                                      f"Esperats: 31, Trobats: {len(dies)}")
                        continue

                for any_ in range(any_inicial, any_final + 1):
                    for mes in range(1, 13):
                        if (any_, mes) not in combinacions_any_mes:
                            errors.append(f"Falten dades per a l'any {any_}, mes {mes} al fitxer {ruta_fitxer}")

            except Exception as e:
                errors.append(f"Error al processar {ruta_fitxer}: {e}")

    except FileNotFoundError as e:
        errors.append(str(e))

    if errors:
        for error in errors:
            logging.error(error)
        print("Errors detectats. Revisa 'TA06.log' per detalls")
    else:
        print("Tots els arxius .dat són vàlids i sense errors")

configurar_logging()

directori = './precip.MIROC5.RCP60.2006-2100.SDSM_REJ'
verificar_fitxers_dat_personalitzats(directori)