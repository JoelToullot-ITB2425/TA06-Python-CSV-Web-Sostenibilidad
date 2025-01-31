import os
import re
import logging
from tqdm import tqdm
from colorama import Fore, Style

def configurar_logging():
    logging.basicConfig(
        filename='TA06.log',
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def calculate_percentage(change, original):
    if original == 0:
        return 0
    return (change / original) * 100

def verificar_fitxers_dat_personalitzats(directori):
    print(f"\n{Fore.BLUE}{'=' * 50}")
    print(f"{'VALIDANT FITXERS .DAT':^50}")
    print(f"{'=' * 50}{Style.RESET_ALL}\n")

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
        print(f"{Fore.RED}Errors detectats. Revisa 'TA06.log' per detalls{Style.RESET_ALL}")
        for error in errors:
            logging.error(error)
        return False
    else:
        print(f"{Fore.GREEN}Tots els arxius .dat són vàlids i sense errors{Style.RESET_ALL}")
        return True

def process_dat_files(directory):
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"""{"INICIANT PROCÉS D'ANÀLISI DE DADES":^50}""")
    print(f"{'=' * 50}{Style.RESET_ALL}\n")

    total_files = 0
    total_negative_999 = 0
    total_other_numbers = 0
    yearly_data = {}

    files = [f for f in os.listdir(directory) if f.endswith('.dat')]
    total_files = len(files)
    print(f"{Fore.YELLOW}Total de fitxers trobats: {total_files}{Style.RESET_ALL}\n")

    adjustment_factor = 2.00

    with tqdm(total=total_files, desc="Processant Valors", ncols=80, colour="green") as pbar:
        for file in files:
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                for line in lines[2:]:
                    values = line.split()
                    if len(values) < 4:
                        continue

                    year = int(values[1])
                    daily_values = [float(v) if v != "-999" else None for v in values[3:]]

                    valid_values = [v for v in daily_values if v is not None]
                    monthly_avg = sum(valid_values) / len(valid_values) if valid_values else 0

                    daily_values = [v * adjustment_factor if v is not None else max(monthly_avg * 0.8, 0.1) * adjustment_factor for v in daily_values]

                    monthly_sum = sum(daily_values)

                    if year not in yearly_data:
                        yearly_data[year] = []

                    yearly_data[year].append(monthly_sum)

                    total_negative_999 += values[3:].count("-999")
                    total_other_numbers += len(values[3:]) - values[3:].count("-999")

            except Exception as e:
                print(f"Error al processar {file_path}: {e}")

            pbar.update(1)

    yearly_totals = {}
    yearly_averages = {}

    for year, monthly_sums in yearly_data.items():
        total_anual = sum(monthly_sums)
        media_anual = total_anual / len(monthly_sums) if monthly_sums else 0

        yearly_totals[year] = total_anual
        yearly_averages[year] = media_anual

    print(f"{Fore.CYAN}\n=== Resultats de l'Anàlisi ==={Style.RESET_ALL}")
    total_values = total_negative_999 + total_other_numbers
    percentage_negative_999 = (total_negative_999 / total_values * 100) if total_values > 0 else 0

    print(f"{Fore.GREEN}Total de fitxers processats:{Style.RESET_ALL} {total_files:,}".replace(",", "."))
    print(f"{Fore.GREEN}Total de valors analitzats:{Style.RESET_ALL} {total_values:,}".replace(",", "."))
    print(f"{Fore.GREEN}Total de valors '-999':{Style.RESET_ALL} {total_negative_999:,}".replace(",", ".") + f" ({percentage_negative_999:.2f}%)")
    print(f"{Fore.GREEN}Total d'altres valors:{Style.RESET_ALL} {total_other_numbers:,}".replace(",", ".") + "\n")

    print(f"{Fore.CYAN}Mitjanes i totals anuals:{Style.RESET_ALL}")
    for year in sorted(yearly_totals):
        print(
            f"{Fore.YELLOW}Any {year}:{Style.RESET_ALL} Total: {yearly_totals[year]:,.2f} l/m², Mitjana: {yearly_averages[year]:.2f} l/m²")

    print(f"\n{Fore.CYAN}Tendència de canvi:{Style.RESET_ALL}")
    sorted_years = sorted(yearly_totals.keys())
    for i in range(1, len(sorted_years)):
        year1 = sorted_years[i - 1]
        year2 = sorted_years[i]
        change = calculate_percentage(yearly_totals[year2] - yearly_totals[year1], yearly_totals[year1])
        print(f"De {year1} a {year2}: {change:.2f}%")

    max_year = max(yearly_totals, key=yearly_totals.get)
    min_year = min(yearly_totals, key=yearly_totals.get)
    print(f"\n{Fore.CYAN}Extrems:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Any més plujós:{Style.RESET_ALL} {max_year} ({yearly_totals[max_year]:,.2f} l/m²)")
    print(f"{Fore.YELLOW}Any més sec:{Style.RESET_ALL} {min_year} ({yearly_totals[min_year]:,.2f} l/m²)")

    print(f"\n{Fore.CYAN}Informació adicional:{Style.RESET_ALL}")
    max_avg_year = max(yearly_averages, key=yearly_averages.get)
    print(
        f"{Fore.YELLOW}Any amb la mitjana anual més alta:{Style.RESET_ALL} {max_avg_year} ({yearly_averages[max_avg_year]:.2f} l/m²)"
    )
    total_precipitation = sum(yearly_totals.values())
    print(
        f"{Fore.YELLOW}Total de precipitacions en tots els anys analitzats:{Style.RESET_ALL} "
        f"{total_precipitation:,.2f} l/m²".replace(",", "."))

configurar_logging()
directori = './precip.MIROC5.RCP60.2006-2100.SDSM_REJ'

if verificar_fitxers_dat_personalitzats(directori):
    process_dat_files(directori)
