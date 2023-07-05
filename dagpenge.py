import pandas as pd
import numpy as np
import calendar
import locale
import datetime as dt
from datetime import date, time, datetime, timedelta
import holidays
import jsontest
import json

### Funktioner til at finde bankdage frem og tilbage i tid
def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))

def next_business_day(date):
    while date in dk_holidays:
        date = date + timedelta(days=1)
    return pd.bdate_range(date, date + timedelta(days=7))[0]

def last_business_day(date):
    while date in dk_holidays:
        date = date - timedelta(days=1)
    return pd.bdate_range(date - timedelta(days=7), date)[-1]

### Funktion til at håndtere genindsendte dagpengekort - brug det seneste
def get_indices(df):
    indices_a = [i for i, index_value in enumerate(df.index) if index_value == "Teknisk belægning"]
    row_a = indices_a[-1]
    indices_b = [i for i, index_value in enumerate(df.index) if index_value == "Fradrag pr. dag"]
    row_b = indices_b[-1] + 1
    indices_md = [i for i, index_value in enumerate(df.index) if index_value == "Modtagedato"]
    modtagedato = df.iloc[indices_md[-1], 0]
    return row_a, row_b, modtagedato


input_file = "C:/Users/KOM/Documents/Dagpenge/dp_kort.xlsx"
files_path = "C:/Users/KOM/Documents/Dagpenge"

# Fuldtids- eller deltidsforsikret?
fuldtid = True
if fuldtid:
    timetal = 160.33
    mindsteudbetaling = 14.8
else:
    timetal = 130
    mindsteudbetaling = 12

# Håndtering af danske månedsnavne
locale.setlocale(locale.LC_TIME, 'da_DK')
# Håndtering af danske helligdage
dk_holidays = holidays.DK()

# Read sheets
with pd.ExcelFile(input_file) as xls:
    sheets = xls.sheet_names
    for sht in sheets:
        df = xls.parse(sht, index_col=0)

        # Håndtering af danske månedsnavne
        locale.setlocale(locale.LC_TIME, 'da_DK')

        # Udtræk månedens nummer
        maaned = df.columns[0].lower()
        md_nr = list(calendar.month_name).index(maaned)


        # Behandling af dagpengekort


        row_a, row_b, modtagedato = get_indices(df)
        # Create a new df to calculate sum for only a few rows
        mini_df = df.iloc[row_a:row_b]
        new_df = mini_df.copy() # Omvej for at slippe for "SettingWithCopyWarning"
        new_df['Total'] = new_df.sum(axis=1)

        ### Generel

        # Modtagedato, kort modtaget før sidste udbetalingsdag (= sidste bankdag)?
        # Get month and year
        modtageyear = modtagedato.year
        modtagemonth = modtagedato.month
        modtagedate = modtagedato.date
        # Antal dage i måneden
        days_in_month = calendar.monthrange(modtageyear, md_nr)[1]
        # Find last business day (= not weekend) of month
        last_bankday = last_business_day(date(modtageyear, md_nr, days_in_month))
        disp_date = last_bankday
        if modtagedato >= datetime.combine(last_bankday, time.min):
            # Hvis ej modtaget før sidste bankdag - udbetal førstkommende bankdag
            disp_date = next_business_day(modtagedato + timedelta(days=1))
        dk_holidays = holidays.DK()


        ### Different cases
        # Samlet fradrag per måned
        total_hours = new_df.loc['Fradrag pr. dag', 'Total']

        # Simpel udbetaling
        # (ferie og sygdom giver ikke fraddrag i udbetaling)
        udbetal = timetal - (total_hours - new_df.loc['Ferie', 'Total'] - new_df.loc['Sygdom', 'Total'])
        if udbetal < mindsteudbetaling:
            udbetal = 0

        # Modtagedato - modtaget rettidigt (februar modtaget senest 10. april)
        if md_nr + 2 > 12:
            senest_modtaget = date(modtageyear + 1, (md_nr + 2) % 12, 10)
        else:
            senest_modtaget = date(modtageyear, md_nr + 2, 10)
        #print("Senest accepterede modtagelsesdato: ", senest_modtaget)
        if modtagedato.date() > senest_modtaget:
            udbetal = 0         # For sent modtaget --> Ingen penge!!!



        ### Generer input til JSON
        timesats = 150          #tilfældigt valg
        atp_sats = 1            #tilfældigt valg
        traekprocent = 40       #tilfældigt valg
        md_fradrag = 3000       #tilfældigt valg

        jsontest.Header["Udskrivningsdato"] = str(datetime.now().date())

        jsontest.Dagpengespecifikationer["Periode"]["Startdato"] = str(dt.date(modtageyear, md_nr, 1))
        jsontest.Dagpengespecifikationer["Periode"]["Slutdato"] = str(dt.date(modtageyear, md_nr, days_in_month))

        jsontest.Dagpengespecifikationer["Timer"] = round(udbetal, 2)
        jsontest.Dagpengespecifikationer["Timesats"] = round(timesats, 2)
        jsontest.Dagpengespecifikationer["Dagpengebeløb"] = round(udbetal * timesats, 2)
        jsontest.Dagpengespecifikationer["Atp"] = round(udbetal * atp_sats, 2)
        brutto_ud = udbetal * (timesats - atp_sats)
        jsontest.Dagpengespecifikationer["Brutto udbetaling"] = round(brutto_ud, 2)
        skat = max((brutto_ud - md_fradrag) * 0.37, 0)
        jsontest.Dagpengespecifikationer["Skat"] = round(skat, 2)
        jsontest.Dagpengespecifikationer["Netto udbetaling"] = round(brutto_ud - skat, 2)

        jsontest.Footer["Dispositionsdato"] = str(disp_date.date())
        jsontest.Footer["Til udbetaling"] = round(brutto_ud - skat, 2)

        # sammensæt dict
        # dict-navn = udfil_år_måned
        dict_name = "udfil_" + str(modtageyear) + "_" + str(md_nr) + ".json"

        ud_dict = {
            "Medlem" : jsontest.Medlem,
            "Arbejdsgaiver" : jsontest.Arbejdsgiver,
            "Akasse" : jsontest.Akasse,
            "Header" : jsontest.Header,
            "Dagpengespecifikationer" : jsontest.Dagpengespecifikationer,
            "Footer" : jsontest.Footer
        }

        # Skriv til JSON
        json_filename = files_path + "/Udbetalingsfiler/" + dict_name
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(ud_dict, f, ensure_ascii=False, indent=4)