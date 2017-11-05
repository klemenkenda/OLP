# izračun OLP točkovanja

# Navodila:
#   rezultate zapiši v folder rezultati, v datoteke olpX.csv, kjer je X številka tekme.
#   rezultat se bo zapisal v datoteko OLP.csv

# globalne spremenljivke
leagueCategories = ['A', 'B', 'C']
csvName = 'olp_2017.csv'

# imports
import csv
import json
import os
import re
import math

# readRaceCSV
#   prebere CSV datotko in si jo zapomni v standardizirano Python strukturo
def readRaceCSV(fname):
    # struktura z rezultati
    results = []
    
    coding = 'utf-8'
    with open(fname, encoding = coding) as f:
        reader = csv.reader(f, delimiter=';')
        
        # številka vrstice
        n = 0;
        
        # branje vseh vrstic
        for row in reader:
            n = n + 1
            # prva vrstica je header
            if n == 1:
                header = row;                  
                # zapomniti si moramo: 
                #   - ime (First name)
                #   - priimek (Surname)
                #   - klub (Cl.name in City)
                #   - kategorijo (Short)
                #   - način uvrstitve (Classifier)
                #   - čas (Time)
                nameI = header.index('First name')
                try:
                    surnameI = header.index('Surname')
                except:
                    surnameI = header.index('\ufeffSurname')
                clubI = header.index('Cl.name')
                cityI = header.index('City')
                categoryI = header.index('Short')
                classifierI = header.index('Classifier')
                timeI = header.index('Time')
                
            # vsaka naslednja vrstica je tekmovalec
            elif len(row) > 0:
                # če je določeno ime kluba, vzamemo to, sicer vzamemo city (Kramer)
                if (row[clubI] != ""):
                    club = row[clubI]
                else:
                    club = row[cityI]
                    
                # pretvorimo čas v sekunde, predvidevamo format h:m:s
                timeSplits = row[timeI].split(':')
                length = len(timeSplits);
                # če čas ni določen, ga nastavimo na 0
                time = 0
                factor = 1
                if (len(timeSplits) > 1):
                    for i in range(length - 1, -1, -1):
                        time = time + factor * int(timeSplits[i])
                        factor = factor * 60
                
                if (row[classifierI] != "0"):
                    time = "-"
                
                # dodamo zapis na listo kar v JSON formatu
                # če ne gre za vacanta
                if (row[nameI] != "Vacant") & (row[surnameI] != "Vacant"):
                    results.append({
                        'name': row[nameI],
                        'surname': row[surnameI],
                        'club': club,
                        'category': row[categoryI],
                        'classifier': row[classifierI],
                        'timeStr': row[timeI],
                        'time': time
                    })
                
    return(results)
                
# FUNCTION: calculateRace
#   izračuna OLP rezultate po kategorijah za posamezno tekmo, uporabi staro OLP
#   formulo - čas_zmagovalca/čas * 100 + število slabših tekmovalcev
def calculateRace(results):
    # preglej, katere kategorije so v rezultatih
    categories = []
    bestTimes = []
    nums = []
    outResults = []
    for result in results:
        category = result['category']
        if not(category in categories):
            categories.append(category)
    
    # pojdi čez vse kategorije
    for category in categories:
        # poišči najboljši rezultat
        minT = 9999999;
        # preštej uvrščene
        num = 0;
        for result in results:
            if (result['category'] == category) and (result['classifier'] == '0') and (result['time'] != 0):
                num = num + 1
                if (result['time'] < minT):
                    minT = result['time']
        
        nums.append(num)            
        bestTimes.append(minT)
        print(bestTimes)
    
    # izračunaj ostale rezultate
    for idx, category in enumerate(categories, start = 0):
        if (category in leagueCategories):
            print('Kategorija: ' + category)
            place = 0;
            for result in results:
                if (result['category'] == category):
                    score = 0
                    if (result['classifier'] == '0') and (result['time'] > 0):
                        place = place + 1;
                        score = bestTimes[idx] / result['time'] * 100 + (nums[idx] - place);
                    result['score'] = score
                    result['place'] = str(place)

                    # dodaj nov zapis v obdelane rezultate
                    outResults.append(result)
      
    return(outResults)


# FUNCTION: addToResults
#   doda rezultat tekme v tabelo lige
def addToResults(league, result, ridx):
    # format
    # Surname;First name;City;Class;Time;Pl;Points;OLP1;...;OLPN;Sum;Average
    surname = result['surname']
    name = result['name']
    city = result['club']
    category = result['category']
    time = result['timeStr']
    points = result['score']
    place = result['place']
    
    idx = category + surname + name
    race = 'race' + str(ridx)
    
    found = 0
    
    for pidx,person in enumerate(league):
        if (person['id'] == idx):
            print('Updating ' + idx)
            found = 1
            # update person
            league[pidx]['points'] = "%.2f" % points
            league[pidx]['place'] = place
            league[pidx]['time'] = time
            league[pidx][race] = points
            
    if (found == 0):
        print('Adding new ' + idx)
        league.append({
            'id': idx,
            'name': name,
            'surname': surname,
            'city': city,
            'class': category,
            'time': time,
            'points': "%.2f" % points,
            'place': place,
            race: points
        })
    return league

# FUNCTION: mergeResults
#   združi rezultate vseh tekem in izračuna ligo
def mergeResults(resultsList, names):
    league = []
    
    for ridx, results in enumerate(resultsList):
        for result in results:
            league = addToResults(league, result, ridx)        
    
    # poračunaj vsoto
    n = len(names)
    c = math.floor(n/2 + 1)
    
    for pidx, person in enumerate(league):
        summa = 0
        average = 0
        count = 0
        
        for i in range(0, n):
            key = 'race' + str(i)
            if (key in person):
                count = count + 1
                summa = summa + person[key]
        
        average = summa / count
        league[pidx]['sum'] = summa
        league[pidx]['avg'] = average
        
        # briši zadnji rezultat, če ni bil na tekmi
        key = 'race' + str(n - 1)
        if not(key in person):
            league[pidx]['points'] = ""
            league[pidx]['place'] = ""
    
    # uredimo zapise
    leagueSorted = sorted(league, key = lambda x: (x['class'], 1000 - x['sum']))
    
    return(leagueSorted)


# FUNCTION: exportCSV
#   izvozi CSV datoteko lige
def exportCSV(csvName, league, names):
    f = open(csvName,'w')

    # konstruiraj header
    # Surname;First name;City;Class;Time;Pl;Points;OLP1;...;OLPN;Sum;Average
    races = ";".join(names)    
    header = "Surname;First name;City;Class;Time;Pl;Points;" + races + ";Sum;Average\n";
    f.write(header);
    
    for person in league:
        s = person['surname'] + ";" + person['name'] + ";" + person['city'] + ";" + person['class'] + ";" + person['time'] + ";" + person['place'] + ";" + person["points"] + ";"
        
        n = len(names)
        for i in range(0, n):
            key = 'race' + str(i)
            if (key in person):
                s = s + "%.2f" % person[key]
            s = s + ";"    
        
        s = s + "%.2f" % person['sum'] + ";" + "%.2f" % person['avg']
        
        s = s + "\n"
        f.write(s)
    
    f.close();
    
# FUNCTION: calculateLeague
#   preveri vse datoteke v results, jih prebere, izračuna točke in jih združi
def calculateLeague():   
    i = 0
    resultsList = []
    names = []
    for file in os.listdir("./rezultati"):
        if file.endswith(".csv"):
            fname = 'rezultati/' + file
            if (fname.find("olp") > -1):
                i = i + 1
                print("Obdelujem: " + fname)
                results = readRaceCSV(fname)
                resultsList.append(calculateRace(results))
                idx = re.search(r'\d+', fname).group(0)
                names.append('OLP ' + idx)

    league = mergeResults(resultsList, names)
    exportCSV(csvName, league, names)            
        
        
# tu se začne izvajanje vsega
calculateLeague();
