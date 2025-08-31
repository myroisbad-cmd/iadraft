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
    """Extrait la table de dégâts d'attaque par niveau avec support pour différents formats"""
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
                    if len(cells) >= 2:
                        try:
                            level = int(cells[0].get_text().strip())
                            # Support pour différents formats de colonnes
                            if len(cells) == 2:
                                # Format simple: Level, Damage
                                damage = int(cells[1].get_text().strip())
                                attack_dict[level] = {'damage': damage}
                            elif len(cells) == 3:
                                # Format avec 2 colonnes de dégâts: Level, Min/Damage, Max/Damage2
                                damage1 = int(cells[1].get_text().strip())
                                damage2 = int(cells[2].get_text().strip())
                                attack_dict[level] = {'damage': damage1, 'damage2': damage2}
                        except:
                            continue
    except Exception as e:
        print(f"Erreur extraction Attack table: {e}")
    return attack_dict

def extract_super_table(soup):
    """Extrait la table de dégâts du Super par niveau avec support pour dégâts par seconde"""
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
                            # Détecter si c'est des dégâts par seconde en regardant les en-têtes
                            header_row = table.find('tr')
                            if header_row:
                                header_cells = header_row.find_all('td')
                                if len(header_cells) >= 2:
                                    header_text = header_cells[1].get_text().lower()
                                    if 'per second' in header_text or 'damage per second' in header_text:
                                        super_dict[level] = {'damage_per_second': value}
                                    else:
                                        super_dict[level] = {'damage': value}
                                else:
                                    super_dict[level] = {'damage': value}
                            else:
                                super_dict[level] = {'damage': value}
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
        # Mettre le nombre de projectiles à 1 quand il est vide
        elif label == 'Projectiles per attack':
            result[label] = '1'
    return result

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
            # Nouvelles colonnes de dégâts
            'Attack Damage_11': '',
            'Attack Damage2_11': '',
            'Super Damage_11': '',
            'Super Damage_per_second_11': '',
        }
        # Ajouter les stats simples additionnelles
        data.update(extract_additional_simple_stats(soup))
        # Santé niveau 11 uniquement
        health_dict = extract_health_table(soup)
        if 11 in health_dict:
            data['Health_11'] = health_dict[11]
        # Dégâts attaque par niveau avec nouvelle logique
        attack_dict = extract_attack_table(soup)
        if 11 in attack_dict:
            attack_data = attack_dict[11]
            if 'damage' in attack_data:
                data['Attack Damage_11'] = attack_data['damage']
            if 'damage2' in attack_data:
                data['Attack Damage2_11'] = attack_data['damage2']
        
        # Dégâts super par niveau avec nouvelle logique
        super_dict = extract_super_table(soup)
        if 11 in super_dict:
            super_data = super_dict[11]
            if 'damage' in super_data:
                data['Super Damage_11'] = super_data['damage']
            if 'damage_per_second' in super_data:
                data['Super Damage_per_second_11'] = super_data['damage_per_second']
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
            'Attack Damage_11': "Erreur réseau",
            'Attack Damage2_11': "Erreur réseau",
            'Super Damage_11': "Erreur réseau",
            'Super Damage_per_second_11': "Erreur réseau",
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
            'Attack Damage_11': "Erreur",
            'Attack Damage2_11': "Erreur",
            'Super Damage_11': "Erreur",
            'Super Damage_per_second_11': "Erreur",
            'Super Charge per Hit (%)': "Erreur",
            'Hypercharge per Hit (%)': "Erreur",
            'Gadget 1 Cooldown': "Erreur",
            'Gadget 2 Cooldown': "Erreur"
        }

def main():
    print("🎯 Scraper Brawl Stars Wiki - Version Améliorée v2.0")
    print("="*60)
    
    print("📋 Récupération de la liste des Brawlers...")
    brawlers = get_all_brawlers()
    print(f"✅ {len(brawlers)} Brawlers trouvés")
    
    # Option pour tester sur quelques Brawlers d'abord
    test_mode = input("\n🧪 Mode test (5 premiers Brawlers) ? (y/N): ").lower() == 'y'
    if test_mode:
        brawlers = brawlers[:5]
        print(f"🔬 Mode test activé - {len(brawlers)} Brawlers")
    
    # Option pour tester sur des Brawlers spécifiques
    test_specific = input("\n🎯 Tester des Brawlers spécifiques (ex: Spike,Colt) ? (laissez vide pour tous): ").strip()
    if test_specific:
        specific_brawlers = [b.strip() for b in test_specific.split(',')]
        brawlers = [b for b in brawlers if b in specific_brawlers]
        print(f"🔍 Test spécifique - {len(brawlers)} Brawlers: {', '.join(brawlers)}")
    
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
        if test_mode or test_specific:
            print(f"    Super: {data['Super Charge per Hit (%)']}")
            print(f"    Hyper: {data['Hypercharge per Hit (%)']}")
            print(f"    Gadget 1: {data['Gadget 1 Cooldown']}")
            print(f"    Gadget 2: {data['Gadget 2 Cooldown']}")
            print(f"    Attack Dmg: {data.get('Attack Damage_11', 'N/A')}")
            print(f"    Attack Dmg2: {data.get('Attack Damage2_11', 'N/A')}")
            print(f"    Super Dmg: {data.get('Super Damage_11', 'N/A')}")
            print(f"    Super DPS: {data.get('Super Damage_per_second_11', 'N/A')}")
            print()
        
        # Pause pour éviter de surcharger le serveur
        time.sleep(1.5)
        
        # Affichage du progrès tous les 10 Brawlers
        if i % 10 == 0 and not (test_mode or test_specific):
            success_rate = (successful / i) * 100
            print(f"   📈 Progression: {i}/{len(brawlers)} | Succès: {success_rate:.1f}%")
    
    # Créer le DataFrame
    df = pd.DataFrame(all_data)
    
    # Afficher les résultats
    print("\n" + "="*80)
    print("📊 RÉSULTATS DU SCRAPING")
    print("="*80)
    
    # Afficher un échantillon
    print(f"\n🔍 Aperçu des données (premiers {min(10, len(df))} résultats):")
    print(df.head(10).to_string(index=False))
    
    if len(df) > 10:
        print(f"\n... et {len(df) - 10} autres Brawlers")
    
    # Sauvegarder en CSV
    filename = 'brawler_complete_stats_v2.csv'
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\n💾 Données sauvegardées dans '{filename}'")
    
    # Statistiques détaillées
    print(f"\n📈 STATISTIQUES:")
    print(f"   • Total Brawlers scrapés: {len(df)}")
    print(f"   • Super Charge trouvé: {len(df[~df['Super Charge per Hit (%)'].isin(['N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    
    # Statistiques hypercharge
    print(f"   • Hypercharge trouvé: {len(df[~df['Hypercharge per Hit (%)'].isin(['N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    
    print(f"   • Gadget 1 trouvé: {len(df[~df['Gadget 1 Cooldown'].isin(['N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    print(f"   • Gadget 2 trouvé: {len(df[~df['Gadget 2 Cooldown'].isin(['N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    
    # Statistiques pour les nouvelles colonnes de dégâts
    if 'Attack Damage_11' in df.columns:
        print(f"   • Attack Damage trouvé: {len(df[~df['Attack Damage_11'].isin(['', 'N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    if 'Attack Damage2_11' in df.columns:
        print(f"   • Attack Damage2 trouvé: {len(df[~df['Attack Damage2_11'].isin(['', 'N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    if 'Super Damage_11' in df.columns:
        print(f"   • Super Damage trouvé: {len(df[~df['Super Damage_11'].isin(['', 'N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    if 'Super Damage_per_second_11' in df.columns:
        print(f"   • Super DPS trouvé: {len(df[~df['Super Damage_per_second_11'].isin(['', 'N/A', 'Erreur', 'Erreur réseau'])])}/{len(df)}")
    
    success_rate = (successful / len(df)) * 100
    print(f"   • Taux de succès global: {success_rate:.1f}%")
    
    # Afficher les Brawlers avec le plus de données
    print(f"\n🏆 TOP 5 des Brawlers avec le plus de données:")
    df['data_count'] = df.apply(lambda row: sum(1 for v in row.values[1:] 
                                              if v not in ['N/A', 'Erreur', 'Erreur réseau', '']), axis=1)
    top_brawlers = df.nlargest(5, 'data_count')[['Brawler', 'data_count']]
    total_columns = len(df.columns) - 1  # Exclure la colonne 'Brawler'
    for idx, row in top_brawlers.iterrows():
        print(f"   {row['Brawler']}: {row['data_count']}/{total_columns} données")

if __name__ == "__main__":
    main()