import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin

def get_all_brawlers():
    """Récupère la liste de tous les Brawlers depuis la page principale"""
    url = "https://brawlstars.fandom.com/wiki/Brawlers"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        brawlers = []
        # Chercher dans les liens de la page principale
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            title = link.get('title') or link.get_text().strip()
            
            if href and '/wiki/' in href and title:
                # Nettoyer le nom du Brawler
                clean_name = title.strip()
                # Filtrer les pages non-Brawler
                if (clean_name and len(clean_name) < 25 and 
                    not any(x in clean_name.lower() for x in 
                    ['category', 'file', 'template', 'user', 'talk', 'special', 
                     'help', 'gadget', 'star power', 'skin', 'pin', 'guide', 
                     'list', 'page', 'wiki', ':', 'brawl stars'])):
                    if clean_name not in brawlers and len(clean_name) > 2:
                        brawlers.append(clean_name)
        
        # Liste complète des Brawlers connus (mise à jour 2024)
        known_brawlers = [
            '8-BIT', 'Amber', 'Angelo', 'Ash', 'Barley', 'Bea', 'Belle', 'Berry',
            'Bibi', 'Bo', 'Bonnie', 'Brock', 'Bull', 'Buster', 'Buzz', 
            'Byron', 'Carl', 'Charlie', 'Chester', 'Chuck',
            'Clancy', 'Colette', 'Colt', 'Cordelius', 'Crow', 'Darryl', 'Doug',
            'Draco', 'Dynamike', 'Edgar', 'El Primo', 'Emz', 'Eve', 'Fang',
            'Finx', 'Frank', 'Gale', 'Gene', 'Gray', 'Griff', 'Grom', 'Gus',
            'Hank', 'Jacky', 'Janet', 'Jessie', 'Juju', 'Kenji',
            'Kit', 'Larry & Lawrie', 'Leon', 'Lily', 'Lola', 'Lou', 'Lumi',
            'Maisie', 'Mandy', 'Max', 'Meeple', 'Meg', 'Melodie', 'Mico', 'Moe',
            'Mortis', 'Mr. P', 'Nani', 'Nita', 'Ollie', 'Otis', 'Pam', 'Pearl',
            'Penny', 'Piper', 'Poco', 'R-T', 'Rico', 'Rosa', 'Ruffs', 'Sam',
            'Sandy', 'Shade', 'Shelly', 'Spike', 'Sprout', 'Squeak', 'Stu',
            'Surge', 'Tara', 'Tick', 'Willow','Kaze','Alli','Jae-yong'
        ]
        
        return known_brawlers
        
    except Exception as e:
        print(f"Erreur lors de la récupération des Brawlers: {e}")
        return known_brawlers

def extract_data_from_pi_items(soup, data_source_name):
    """Extrait les données depuis les éléments pi-item avec data-source spécifique"""
    try:
        # Chercher l'élément avec le data-source spécifique
        pi_item = soup.find('div', {'data-source': data_source_name})
        if pi_item:
            # Chercher la valeur dans pi-data-value
            data_value = pi_item.find('div', class_='pi-data-value')
            if data_value:
                text = data_value.get_text().strip()
                return text
        
        # Méthode alternative : chercher dans les pi-item avec class spécifique
        pi_items = soup.find_all('div', class_='pi-item')
        for item in pi_items:
            if item.get('data-source') == data_source_name:
                value_div = item.find('div', class_='pi-data-value')
                if value_div:
                    return value_div.get_text().strip()
                    
    except Exception as e:
        print(f"Erreur extraction {data_source_name}: {e}")
    
    return "N/A"

def extract_gadget_cooldowns(soup):
    """Extrait les cooldowns des gadgets avec méthodes améliorées"""
    gadget_cooldowns = []
    
    try:
        # Méthode 1 : Chercher avec data-source patterns étendus
        gadget_patterns = [
            'Gadget1cooldown', 'Gadget2cooldown', 'GadgetCooldown', 
            'Gadget1Cooldown', 'Gadget2Cooldown', 'gadget1cooldown', 
            'gadget2cooldown', 'Gadget1CD', 'Gadget2CD', 'gadget1CD', 'gadget2CD',
            'firstgadgetcooldown', 'secondgadgetcooldown', 'FirstGadgetCooldown',
            'SecondGadgetCooldown', 'Gadget1_cooldown', 'Gadget2_cooldown'
        ]
        
        for pattern in gadget_patterns:
            cooldown = extract_data_from_pi_items(soup, pattern)
            if cooldown != "N/A" and cooldown not in gadget_cooldowns:
                gadget_cooldowns.append(cooldown)
        
        # Méthode 2 : Chercher dans les sections avec "Cooldown" dans le label
        pi_items = soup.find_all('div', class_='pi-item')
        for item in pi_items:
            # Chercher les labels contenant "cooldown"
            labels = item.find_all(['h3', 'div'], class_='pi-data-label')
            for label in labels:
                label_text = label.get_text().lower()
                if 'cooldown' in label_text:
                    # Chercher la valeur correspondante
                    value_div = item.find('div', class_='pi-data-value')
                    if value_div:
                        cooldown_text = value_div.get_text().strip()
                        if cooldown_text and cooldown_text not in gadget_cooldowns:
                            gadget_cooldowns.append(cooldown_text)
        
        # Méthode 3 : Chercher dans les sections pi-collapse (comme pour Spike)
        pi_collapse_sections = soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open')
        for section in pi_collapse_sections:
            # Chercher les éléments avec "cooldown" dans le texte
            section_text = section.get_text().lower()
            if 'cooldown' in section_text:
                # Extraire les valeurs de cooldown de cette section
                cooldown_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:second|sec|s)', section_text)
                for match in cooldown_matches:
                    formatted_cooldown = match + "s"
                    if formatted_cooldown not in gadget_cooldowns:
                        gadget_cooldowns.append(formatted_cooldown)
        
        # Méthode 4 : Chercher "Cooldown" dans tout le texte de la page avec regex amélioré
        if len(gadget_cooldowns) < 2:
            page_text = soup.get_text()
            # Pattern pour trouver "Cooldown: X seconds" ou "Cooldown X s"
            cooldown_pattern = r'cooldown[:\s]*(\d+(?:\.\d+)?)\s*(?:second|sec|s)'
            matches = re.findall(cooldown_pattern, page_text, re.IGNORECASE)
            for match in matches:
                formatted_cooldown = match + "s"
                if formatted_cooldown not in gadget_cooldowns:
                    gadget_cooldowns.append(formatted_cooldown)
        
        # Méthode 5 : Chercher dans les divs avec des patterns spécifiques pour Spike
        if len(gadget_cooldowns) < 2:
            # Chercher tous les éléments contenant "second" ou "sec"
            all_elements = soup.find_all(string=re.compile(r'\d+\s*(?:second|sec|s)', re.IGNORECASE))
            for element in all_elements:
                # Vérifier si l'élément parent contient "cooldown" ou "gadget"
                parent = element.parent
                if parent:
                    parent_text = parent.get_text().lower()
                    if any(keyword in parent_text for keyword in ['cooldown', 'gadget', 'ability']):
                        cooldown_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:second|sec|s)', element, re.IGNORECASE)
                        if cooldown_match:
                            formatted_cooldown = cooldown_match.group(1) + "s"
                            if formatted_cooldown not in gadget_cooldowns:
                                gadget_cooldowns.append(formatted_cooldown)
        
    except Exception as e:
        print(f"Erreur extraction gadgets: {e}")
    
    return gadget_cooldowns[:2]  # Limiter à 2 gadgets maximum

def extract_simple_data(soup, data_source_name):
    """Extrait une valeur simple depuis un data-source donné (ex: Rarity, Class, VoiceActor, Image)"""
    try:
        pi_item = soup.find('div', {'data-source': data_source_name})
        if pi_item:
            data_value = pi_item.find('div', class_='pi-data-value')
            if data_value:
                return data_value.get_text().strip()
        # Pour l'image
        if data_source_name == 'Image' and pi_item:
            img = pi_item.find('img')
            if img and img.get('src'):
                return img['src']
    except Exception as e:
        print(f"Erreur extraction {data_source_name}: {e}")
    return "N/A"

def extract_health_table(soup):
    """Extrait la table de santé par niveau (Health)"""
    health_dict = {}
    try:
        health_section = None
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2 and 'health' in h2.get_text().lower():
                health_section = section
                break
        if health_section:
            tables = health_section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        try:
                            level = int(cells[0].get_text().strip())
                            value = int(cells[1].get_text().strip())
                            health_dict[level] = value
                        except:
                            continue
    except Exception as e:
        print(f"Erreur extraction Health table: {e}")
    return health_dict

def extract_attack_table(soup):
    """Extrait la table de dégâts d'attaque par niveau (Dash/Slash)"""
    attack_dict = {}
    try:
        attack_section = None
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2 and 'attack' in h2.get_text().lower():
                attack_section = section
                break
        if attack_section:
            tables = attack_section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 3:
                        try:
                            level = int(cells[0].get_text().strip())
                            dash = int(cells[1].get_text().strip())
                            slash = int(cells[2].get_text().strip())
                            attack_dict[level] = {'dash': dash, 'slash': slash}
                        except:
                            continue
    except Exception as e:
        print(f"Erreur extraction Attack table: {e}")
    return attack_dict

def extract_super_table(soup):
    """Extrait la table de dégâts du Super par niveau"""
    super_dict = {}
    try:
        super_section = None
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2 and 'super' in h2.get_text().lower():
                super_section = section
                break
        if super_section:
            tables = super_section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        try:
                            level = int(cells[0].get_text().strip())
                            value = int(cells[1].get_text().strip())
                            super_dict[level] = value
                        except:
                            continue
    except Exception as e:
        print(f"Erreur extraction Super table: {e}")
    return super_dict

def extract_hypercharge_bonuses(soup):
    """Extrait les bonus Hypercharge (multiplier, speed, damage, shield)"""
    bonuses = {}
    try:
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2 and 'hypercharge' in h2.get_text().lower():
                for div in section.find_all('div', class_='pi-item pi-data'):
                    label = div.find('h3', class_='pi-data-label')
                    value = div.find('div', class_='pi-data-value')
                    if label and value:
                        key = label.get_text().strip()
                        val = value.get_text().strip()
                        bonuses[key] = val
    except Exception as e:
        print(f"Erreur extraction Hypercharge bonuses: {e}")
    return bonuses

def extract_prev_next_brawlers(soup):
    """Extrait les liens vers le brawler précédent et suivant"""
    prev, next_ = "N/A", "N/A"
    try:
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color'):
            h2 = section.find('h2')
            if h2 and 'links' in h2.get_text().lower():
                for table in section.find_all('table'):
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        for cell in cells:
                            if 'previous' in cell.get_text().lower():
                                a = cell.find('a')
                                if a:
                                    prev = a.get_text().strip()
                            if 'next' in cell.get_text().lower():
                                a = cell.find('a')
                                if a:
                                    next_ = a.get_text().strip()
    except Exception as e:
        print(f"Erreur extraction prev/next brawlers: {e}")
    return prev, next_

def extract_all_tables_by_section(soup, section_title):
    """Extrait tous les tableaux de stats par niveau pour une section donnée (ex: Attack, Super, Gadget, Star Power)"""
    results = []
    try:
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2 and section_title.lower() in h2.get_text().lower():
                tables = section.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if not rows:
                        continue
                    headers = [cell.get_text().strip() for cell in rows[0].find_all('td')]
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if len(cells) == len(headers):
                            entry = {}
                            for i, cell in enumerate(cells):
                                entry[headers[i]] = cell.get_text().strip()
                            results.append(entry)
    except Exception as e:
        print(f"Erreur extraction tables section {section_title}: {e}")
    return results

def extract_gadgets_and_star_powers(soup):
    """Extrait les gadgets et star powers (nom, cooldown, stats par niveau)"""
    gadgets = []
    star_powers = []
    try:
        for section in soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open'):
            h2 = section.find('h2')
            if h2:
                title = h2.get_text().strip()
                # Gadget
                if title.lower().startswith('gadget:'):
                    gadget = {'name': title.replace('Gadget:', '').strip()}
                    # Cooldown
                    cooldown_div = section.find('div', {'data-source': 'Gadget1Cooldown'}) or section.find('div', {'data-source': 'Gadget2Cooldown'})
                    if cooldown_div:
                        value = cooldown_div.find('div', class_='pi-data-value')
                        if value:
                            gadget['cooldown'] = value.get_text().strip()
                    # Tableaux
                    tables = section.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        if not rows:
                            continue
                        headers = [cell.get_text().strip() for cell in rows[0].find_all('td')]
                        for row in rows[1:]:
                            cells = row.find_all('td')
                            if len(cells) == len(headers):
                                entry = {}
                                for i, cell in enumerate(cells):
                                    entry[headers[i]] = cell.get_text().strip()
                                gadget.setdefault('stats', []).append(entry)
                    gadgets.append(gadget)
                # Star Power
                elif title.lower().startswith('star power:'):
                    sp = {'name': title.replace('Star Power:', '').strip()}
                    tables = section.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        if not rows:
                            continue
                        headers = [cell.get_text().strip() for cell in rows[0].find_all('td')]
                        for row in rows[1:]:
                            cells = row.find_all('td')
                            if len(cells) == len(headers):
                                entry = {}
                                for i, cell in enumerate(cells):
                                    entry[headers[i]] = cell.get_text().strip()
                                sp.setdefault('stats', []).append(entry)
                    star_powers.append(sp)
    except Exception as e:
        print(f"Erreur extraction gadgets/star powers: {e}")
    return gadgets, star_powers

def extract_additional_simple_stats(soup):
    """Extrait des stats simples additionnelles (projectiles per attack, attack width, attack speed, etc.)"""
    fields = [
        ('AttackBullets', 'Projectiles per attack'),
        ('AttackWidth', 'Attack width'),
        ('AttackSpeed', 'Attack projectile speed'),
        ('SuperDuration', 'Super duration'),
        ('SuperMinionRange', 'Thorny grenade range'),
    ]
    result = {}
    for data_source, label in fields:
        val = extract_simple_data(soup, data_source)
        if val != 'N/A':
            result[label] = val
    return result

def clean_numeric_value(value):
    """Extrait SEULEMENT la première valeur numérique d'une chaîne de caractères"""
    if value is None or value == "N/A" or value == "Erreur" or value == "Erreur réseau":
        return None
    
    # Convertir en string si ce n'est pas déjà le cas
    value_str = str(value)
    
    # Extraire SEULEMENT le premier nombre trouvé (entier ou décimal)
    match = re.search(r'(\d+(?:\.\d+)?)', value_str)
    if match:
        num_str = match.group(1)
        # Retourner int si c'est un entier, float sinon
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    return None

def clean_percentage_value(value):
    """Extrait SEULEMENT la première valeur numérique d'un pourcentage"""
    if value is None or value == "N/A" or value == "Erreur" or value == "Erreur réseau":
        return None
    
    value_str = str(value)
    # Chercher SEULEMENT le premier nombre suivi de %
    match = re.search(r'(\d+(?:\.\d+)?)%', value_str)
    if match:
        return float(match.group(1))
    
    # Si pas de %, essayer d'extraire juste le premier nombre
    return clean_numeric_value(value_str)

def clean_speed_value(value):
    """Extrait SEULEMENT la première valeur de vitesse (sans les parenthèses descriptives)"""
    if value is None or value == "N/A" or value == "Erreur" or value == "Erreur réseau":
        return None
    
    value_str = str(value)
    # Extraire SEULEMENT le premier nombre trouvé
    match = re.search(r'(\d+)', value_str)
    if match:
        return int(match.group(1))
    
    return None

def clean_range_value(value):
    """Extrait SEULEMENT la première valeur de portée"""
    if value is None or value == "N/A" or value == "Erreur" or value == "Erreur réseau":
        return None
    
    value_str = str(value)
    # Extraire SEULEMENT le premier nombre (peut être décimal)
    match = re.search(r'(\d+(?:\.\d+)?)', value_str)
    if match:
        num_str = match.group(1)
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    return None

def clean_cooldown_value(value):
    """Extrait SEULEMENT la première valeur de cooldown en secondes"""
    if value is None or value == "N/A" or value == "Erreur" or value == "Erreur réseau":
        return None
    
    value_str = str(value)
    # Chercher SEULEMENT le premier nombre suivi de 's' ou 'second'
    match = re.search(r'(\d+(?:\.\d+)?)', value_str)
    if match:
        num_str = match.group(1)
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    return None

def scrape_brawler_data(brawler_name):
    """Scrape les données d'un Brawler en utilisant la structure HTML observée"""
    base_url = 'https://brawlstars.fandom.com/wiki/'
    url = base_url + brawler_name.replace(' ', '_').replace('&', '%26')
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialiser les données (sans Image)
        data = {
            'Brawler': brawler_name,
            'Rarity': extract_simple_data(soup, 'Rarity'),
            'Class': extract_simple_data(soup, 'Class'),
            'Voice actor': extract_simple_data(soup, 'VoiceActor'),
            'Movement speed': extract_simple_data(soup, 'MovementSpeed'),
            'Attack Range': extract_simple_data(soup, 'AttackRange'),
            'Reload': extract_simple_data(soup, 'Reload'),
            'Attack spread': extract_simple_data(soup, 'AttackSpread'),
            'Super Range': extract_simple_data(soup, 'SuperRange'),
            'Projectiles per Super': extract_simple_data(soup, 'SuperBullets'),
            'Projectile speed': extract_simple_data(soup, 'SuperSpeed'),
        }
        # Ajouter les stats simples additionnelles
        data.update(extract_additional_simple_stats(soup))
        # Santé niveau 11 uniquement
        health_dict = extract_health_table(soup)
        if 11 in health_dict:
            data['Health_11'] = health_dict[11]
        # Dégâts attaque par niveau (générique, niveau 11 uniquement)
        attack_tables = extract_all_tables_by_section(soup, 'Attack')
        for entry in attack_tables:
            if entry.get('Level') == '11' or entry.get('Level') == 11:
                for k, v in entry.items():
                    if k != 'Level':
                        data[f'Attack_{k}_11'] = v
        # Dégâts super par niveau (générique, niveau 11 uniquement)
        super_tables = extract_all_tables_by_section(soup, 'Super')
        for entry in super_tables:
            if entry.get('Level') == '11' or entry.get('Level') == 11:
                for k, v in entry.items():
                    if k != 'Level':
                        data[f'Super_{k}_11'] = v
        # Bonus Hypercharge
        hyper_bonuses = extract_hypercharge_bonuses(soup)
        for k, v in hyper_bonuses.items():
            data[f'Hypercharge {k}'] = v
        # Liens brawler précédent/suivant
        prev, next_ = extract_prev_next_brawlers(soup)
        data['Previous Brawler'] = prev
        data['Next Brawler'] = next_
        # Gadgets et star powers (niveau 11 uniquement)
        gadgets, star_powers = extract_gadgets_and_star_powers(soup)
        for i, gadget in enumerate(gadgets, 1):
            data[f'Gadget_{i}_Name'] = gadget.get('name', '')
            data[f'Gadget_{i}_Cooldown'] = gadget.get('cooldown', '')
            if 'stats' in gadget:
                for stat in gadget['stats']:
                    lvl = stat.get('Level')
                    if lvl == '11' or lvl == 11:
                        for k, v in stat.items():
                            if k != 'Level':
                                data[f'Gadget_{i}_{k}_11'] = v
        for i, sp in enumerate(star_powers, 1):
            data[f'StarPower_{i}_Name'] = sp.get('name', '')
            if 'stats' in sp:
                for stat in sp['stats']:
                    lvl = stat.get('Level')
                    if lvl == '11' or lvl == 11:
                        for k, v in stat.items():
                            if k != 'Level':
                                data[f'StarPower_{i}_{k}_11'] = v
        # Extraction existante (super/hypercharge/gadgets)
        # 1. Extraire Super charge per hit - basé sur la structure HTML observée
        super_charge_patterns = [
            'SuperChargeperHit', 'SuperchargeperHit', 'Superchargeperattack',
            'SuperCharge', 'supercharge', 'SuperChargePerHit', 'SuperChargePerAttack',
            'SuperChargePerHit', 'SuperChargeperAttack', 'superchargeperHit'
        ]
        super_charge = "N/A"
        for pattern in super_charge_patterns:
            super_charge = extract_data_from_pi_items(soup, pattern)
            if super_charge != "N/A":
                break
        if super_charge == "N/A":
            all_text = soup.find_all(string=True)
            for i, text in enumerate(all_text):
                if 'super charge per hit' in text.lower():
                    for j in range(i+1, min(i+5, len(all_text))):
                        next_text = all_text[j].strip()
                        if '%' in next_text:
                            super_charge = next_text
                            break
                    if super_charge != "N/A":
                        break
        if super_charge != "N/A":
            data['Super Charge per Hit (%)'] = super_charge
        else:
            data['Super Charge per Hit (%)'] = "N/A"
        # 2. Extraire Hypercharge per hit - basé sur la structure HTML observée
        hypercharge_patterns = [
            'HyperchargechargeperHit', 'Hyperchargecharge', 'HyperChargeperHit', 
            'hyperchargeperHit', 'AttackHyperchargecharge', 'HyperchargeChargeperHit',
            'HyperchargePerHit', 'HyperchargePerAttack', 'HyperChargePerHit',
            'HyperChargePerAttack', 'hyperchargePerHit', 'hyperchargePerAttack'
        ]
        hypercharge = "N/A"
        for pattern in hypercharge_patterns:
            hypercharge = extract_data_from_pi_items(soup, pattern)
            if hypercharge != "N/A":
                break
        if hypercharge == "N/A":
            all_text = soup.find_all(string=True)
            for i, text in enumerate(all_text):
                if 'hypercharge charge per hit' in text.lower():
                    for j in range(i+1, min(i+5, len(all_text))):
                        next_text = all_text[j].strip()
                        if '%' in next_text:
                            hypercharge = next_text
                            break
                    if hypercharge != "N/A":
                        break
        if hypercharge != "N/A":
            data['Hypercharge per Hit (%)'] = hypercharge
        else:
            data['Hypercharge per Hit (%)'] = "N/A"
        # 3. Extraire les cooldowns des gadgets avec méthodes améliorées
        gadget_cooldowns = extract_gadget_cooldowns(soup)
        if len(gadget_cooldowns) >= 1:
            data['Gadget 1 Cooldown'] = gadget_cooldowns[0]
        else:
            data['Gadget 1 Cooldown'] = "N/A"
        if len(gadget_cooldowns) >= 2:
            data['Gadget 2 Cooldown'] = gadget_cooldowns[1]
        else:
            data['Gadget 2 Cooldown'] = "N/A"
        # 4. Méthode de fallback pour Super charge et Hypercharge si toujours N/A
        if data['Super Charge per Hit (%)'] == "N/A":
            page_text = soup.get_text().lower()
            super_match = re.search(r'super charge.*?(\d+(?:\.\d+)?)%', page_text)
            if super_match:
                data['Super Charge per Hit (%)'] = super_match.group(1) + "%"
        if data['Hypercharge per Hit (%)'] == "N/A":
            page_text = soup.get_text().lower()
            hyper_match = re.search(r'hypercharge.*?charge.*?(\d+(?:\.\d+)?)%', page_text)
            if hyper_match:
                data['Hypercharge per Hit (%)'] = hyper_match.group(1) + "%"
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {brawler_name}: {e}")
        return {
            'Brawler': brawler_name,
            'Rarity': "Erreur réseau",
            'Class': "Erreur réseau",
            'Voice actor': "Erreur réseau",
            'Movement speed': "Erreur réseau",
            'Attack Range': "Erreur réseau",
            'Reload': "Erreur réseau",
            'Attack spread': "Erreur réseau",
            'Super Range': "Erreur réseau",
            'Projectiles per Super': "Erreur réseau",
            'Projectile speed': "Erreur réseau",
            'Super Charge per Hit (%)': "Erreur réseau",
            'Hypercharge per Hit (%)': "Erreur réseau",
            'Gadget 1 Cooldown': "Erreur réseau",
            'Gadget 2 Cooldown': "Erreur réseau"
        }
    except Exception as e:
        print(f"Erreur lors du scraping de {brawler_name}: {e}")
        return {
            'Brawler': brawler_name,
            'Rarity': "Erreur",
            'Class': "Erreur",
            'Voice actor': "Erreur",
            'Movement speed': "Erreur",
            'Attack Range': "Erreur",
            'Reload': "Erreur",
            'Attack spread': "Erreur",
            'Super Range': "Erreur",
            'Projectiles per Super': "Erreur",
            'Projectile speed': "Erreur",
            'Super Charge per Hit (%)': "Erreur",
            'Hypercharge per Hit (%)': "Erreur",
            'Gadget 1 Cooldown': "Erreur",
            'Gadget 2 Cooldown': "Erreur"
        }

def clean_dataframe_for_calculations(df):
    """Nettoie le DataFrame pour ne garder que des valeurs numériques exploitables"""
    df_clean = df.copy()
    
    # Colonnes à nettoyer avec leurs fonctions de nettoyage spécifiques
    numeric_columns = {
        'Movement speed': clean_speed_value,
        'Attack Range': clean_range_value,
        'Reload': clean_cooldown_value,
        'Super Range': clean_range_value,
        'Projectiles per Super': clean_numeric_value,
        'Projectile speed': clean_numeric_value,
        'Projectiles per attack': clean_numeric_value,
        'Attack width': clean_numeric_value,
        'Attack projectile speed': clean_numeric_value,
        'Thorny grenade range': clean_numeric_value,
        'Health_11': clean_numeric_value,
        'Super Charge per Hit (%)': clean_percentage_value,
        'Hypercharge per Hit (%)': clean_percentage_value,
        'Gadget 1 Cooldown': clean_cooldown_value,
        'Gadget 2 Cooldown': clean_cooldown_value,
        'Super duration': clean_cooldown_value,
    }
    
    # Nettoyer les colonnes numériques
    for col, clean_func in numeric_columns.items():
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(clean_func)
    
    # Colonnes à garder en texte (seulement les noms et identifiants)
    text_columns = ['Brawler', 'Rarity', 'Class', 'Voice actor']
    
    # Créer un nouveau DataFrame avec seulement les colonnes importantes
    important_columns = ['Brawler', 'Rarity', 'Class', 'Movement speed', 'Health_11', 
                        'Attack Range', 'Reload', 'Super Range', 'Projectiles per attack',
                        'Projectiles per Super', 'Attack projectile speed', 'Projectile speed',
                        'Super Charge per Hit (%)', 'Hypercharge per Hit (%)', 
                        'Gadget 1 Cooldown', 'Gadget 2 Cooldown', 'Super duration']
    
    # Filtrer les colonnes qui existent dans le DataFrame
    available_columns = [col for col in important_columns if col in df_clean.columns]
    df_final = df_clean[available_columns].copy()
    
    # Renommer les colonnes pour plus de clarté
    column_rename = {
        'Movement speed': 'Movement_Speed',
        'Attack Range': 'Attack_Range', 
        'Super Range': 'Super_Range',
        'Projectiles per attack': 'Projectiles_per_Attack',
        'Projectiles per Super': 'Projectiles_per_Super',
        'Attack projectile speed': 'Attack_Projectile_Speed',
        'Projectile speed': 'Super_Projectile_Speed',
        'Super Charge per Hit (%)': 'Super_Charge_per_Hit_Percent',
        'Hypercharge per Hit (%)': 'Hypercharge_per_Hit_Percent',
        'Gadget 1 Cooldown': 'Gadget_1_Cooldown_Seconds',
        'Gadget 2 Cooldown': 'Gadget_2_Cooldown_Seconds',
        'Super duration': 'Super_Duration_Seconds',
        'Health_11': 'Health_Level_11'
    }
    
    df_final = df_final.rename(columns=column_rename)
    
    return df_final

def main():
    print("🎯 Scraper Brawl Stars Wiki - Version Améliorée v2.0")
    print("="*60)
    
    print("📋 Récupération de la liste des Brawlers...")
    brawlers = get_all_brawlers()
    print(f"✅ {len(brawlers)} Brawlers trouvés")
    
    # Option pour tester sur des Brawlers spécifiques
    test_specific = input("\n🎯 Tester des Brawlers spécifiques (ex: Spike,Colt) ? (laissez vide pour tous): ").strip()
    if test_specific:
        specific_brawlers = [b.strip() for b in test_specific.split(',')]
        # Rechercher les brawlers correspondants (insensible à la casse) dans la liste complète
        matched_brawlers = []
        for specific in specific_brawlers:
            for brawler in brawlers:
                if specific.lower() == brawler.lower():
                    matched_brawlers.append(brawler)
                    break
        brawlers = matched_brawlers
        print(f"🔍 Test spécifique - {len(brawlers)} Brawlers: {', '.join(brawlers)}")
    else:
        # Option pour tester sur quelques Brawlers d'abord
        test_mode = input("\n🧪 Mode test (5 premiers Brawlers) ? (y/N): ").lower() == 'y'
        if test_mode:
            brawlers = brawlers[:5]
            print(f"🔬 Mode test activé - {len(brawlers)} Brawlers")
    
    all_data = []
    successful = 0
    
    print(f"\n🚀 Début du scraping...")
    print("-" * 60)
    
    for i, brawler in enumerate(brawlers, 1):
        print(f"📊 [{i:2d}/{len(brawlers)}] Scraping: {brawler:<15}", end=" ")
        
        data = scrape_brawler_data(brawler)
        all_data.append(data)
        
        # Vérifier si on a récupéré des données
        has_data = any(v not in ["N/A", "Erreur", "Erreur réseau"] 
                      for k, v in data.items() if k != 'Brawler')
        
        if has_data:
            successful += 1
            print("✅")
        else:
            print("❌")
        
        # Afficher les données récupérées pour le debug
        if test_specific or (len(brawlers) <= 5):
            print(f"    Super: {data['Super Charge per Hit (%)']}")
            print(f"    Hyper: {data['Hypercharge per Hit (%)']}")
            print(f"    Gadget 1: {data['Gadget 1 Cooldown']}")
            print(f"    Gadget 2: {data['Gadget 2 Cooldown']}")
            print()
        
        # Pause pour éviter de surcharger le serveur
        time.sleep(1.5)
        
        # Affichage du progrès tous les 10 Brawlers
        if i % 10 == 0 and len(brawlers) > 10:
            success_rate = (successful / i) * 100
            print(f"   📈 Progression: {i}/{len(brawlers)} | Succès: {success_rate:.1f}%")
    
    # Créer le DataFrame
    df = pd.DataFrame(all_data)
    
    # Nettoyer les données pour avoir seulement des valeurs numériques
    df_clean = clean_dataframe_for_calculations(df)
    
    # Afficher les résultats
    print("\n" + "="*80)
    print("📊 RÉSULTATS DU SCRAPING")
    print("="*80)
    
    # Afficher un échantillon du CSV original
    print(f"\n🔍 Aperçu des données originales (premiers {min(5, len(df))} résultats):")
    print(df.head(5).to_string(index=False))
    
    # Afficher un échantillon du CSV nettoyé
    print(f"\n🧹 Aperçu des données nettoyées (premiers {min(10, len(df_clean))} résultats):")
    print(df_clean.head(10).to_string(index=False))
    
    if len(df) > 10:
        print(f"\n... et {len(df) - 10} autres Brawlers")
    
    # Sauvegarder les deux versions
    filename_original = 'brawler_complete_stats_v2.csv'
    filename_clean = 'brawler_stats_clean.csv'
    
    df.to_csv(filename_original, index=False, encoding='utf-8')
    df_clean.to_csv(filename_clean, index=False, encoding='utf-8')
    
    print(f"\n💾 Données originales sauvegardées dans '{filename_original}'")
    print(f"💾 Données nettoyées sauvegardées dans '{filename_clean}'")
    
    # Statistiques détaillées
    print(f"\n📈 STATISTIQUES:")
    print(f"   • Total Brawlers scrapés: {len(df)}")
    
    # Statistiques sur les données nettoyées
    print(f"\n📊 STATISTIQUES DES DONNÉES NETTOYÉES:")
    numeric_cols = ['Movement_Speed', 'Health_Level_11', 'Attack_Range', 'Super_Range', 
                   'Super_Charge_per_Hit_Percent', 'Hypercharge_per_Hit_Percent']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            non_null_count = df_clean[col].notna().sum()
            print(f"   • {col}: {non_null_count}/{len(df_clean)} valeurs numériques")
    
    if len(df) > 0:
        success_rate = (successful / len(df)) * 100
        print(f"   • Taux de succès global: {success_rate:.1f}%")
    else:
        print(f"   • Aucune donnée à traiter")
    
    # Afficher les Brawlers avec le plus de données numériques
    if len(df_clean) > 0:
        print(f"\n🏆 TOP 5 des Brawlers avec le plus de données numériques:")
        df_clean['numeric_data_count'] = df_clean.select_dtypes(include=['int64', 'float64']).notna().sum(axis=1)
        top_brawlers = df_clean.nlargest(5, 'numeric_data_count')[['Brawler', 'numeric_data_count']]
        for idx, row in top_brawlers.iterrows():
            print(f"   {row['Brawler']}: {row['numeric_data_count']} données numériques")

if __name__ == "__main__":
    main()