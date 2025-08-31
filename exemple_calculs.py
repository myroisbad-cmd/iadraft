#!/usr/bin/env python3
"""
Exemple d'utilisation du CSV nettoyé pour des calculs
Ce script montre comment exploiter brawler_stats_clean.csv pour des analyses
"""

import pandas as pd
import numpy as np

def main():
    print("📊 Exemple d'utilisation du CSV nettoyé pour des calculs")
    print("=" * 60)
    
    # Charger le CSV nettoyé
    try:
        df = pd.read_csv('brawler_stats_clean.csv')
        print(f"✅ CSV chargé avec succès : {len(df)} brawlers")
    except FileNotFoundError:
        print("❌ Fichier brawler_stats_clean.csv non trouvé")
        print("   Exécutez d'abord v1.py pour générer le CSV")
        return
    
    print("\n📋 Colonnes disponibles :")
    for col in df.columns:
        print(f"   • {col}")
    
    # Exemples de calculs
    print("\n🧮 EXEMPLES DE CALCULS POSSIBLES :")
    
    # 1. Statistiques descriptives
    print("\n1️⃣ Statistiques de santé (Health_Level_11) :")
    if 'Health_Level_11' in df.columns:
        health_stats = df['Health_Level_11'].describe()
        print(f"   • Moyenne : {health_stats['mean']:.0f} HP")
        print(f"   • Médiane : {health_stats['50%']:.0f} HP")
        print(f"   • Min : {health_stats['min']:.0f} HP")
        print(f"   • Max : {health_stats['max']:.0f} HP")
    
    # 2. Comparaison par classe
    print("\n2️⃣ Vitesse moyenne par classe :")
    if 'Movement_Speed' in df.columns and 'Class' in df.columns:
        speed_by_class = df.groupby('Class')['Movement_Speed'].mean().sort_values(ascending=False)
        for class_name, avg_speed in speed_by_class.head().items():
            print(f"   • {class_name}: {avg_speed:.0f}")
    
    # 3. Analyse des cooldowns
    print("\n3️⃣ Analyse des cooldowns de gadgets :")
    gadget_cols = ['Gadget_1_Cooldown_Seconds', 'Gadget_2_Cooldown_Seconds']
    for col in gadget_cols:
        if col in df.columns:
            avg_cooldown = df[col].mean()
            if not pd.isna(avg_cooldown):
                print(f"   • {col}: {avg_cooldown:.1f}s en moyenne")
    
    # 4. Ratio Super Charge
    print("\n4️⃣ Top 3 des brawlers avec le meilleur Super Charge :")
    if 'Super_Charge_per_Hit_Percent' in df.columns:
        top_super = df.nlargest(3, 'Super_Charge_per_Hit_Percent')[['Brawler', 'Super_Charge_per_Hit_Percent']]
        for idx, row in top_super.iterrows():
            print(f"   • {row['Brawler']}: {row['Super_Charge_per_Hit_Percent']:.2f}%")
    
    # 5. Corrélation entre stats
    print("\n5️⃣ Corrélation entre santé et vitesse :")
    if 'Health_Level_11' in df.columns and 'Movement_Speed' in df.columns:
        correlation = df['Health_Level_11'].corr(df['Movement_Speed'])
        if not pd.isna(correlation):
            print(f"   • Corrélation : {correlation:.3f}")
            if correlation > 0.3:
                print("   • Corrélation positive forte")
            elif correlation < -0.3:
                print("   • Corrélation négative forte")
            else:
                print("   • Corrélation faible")
    
    # 6. Calcul d'un score composite
    print("\n6️⃣ Score composite (exemple) :")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print("   • Calcul d'un score basé sur plusieurs statistiques...")
        # Normaliser les colonnes importantes
        score_cols = ['Health_Level_11', 'Movement_Speed', 'Super_Charge_per_Hit_Percent']
        available_cols = [col for col in score_cols if col in df.columns]
        
        if len(available_cols) > 0:
            # Normalisation min-max
            df_score = df[available_cols].copy()
            for col in available_cols:
                df_score[col] = (df_score[col] - df_score[col].min()) / (df_score[col].max() - df_score[col].min())
            
            # Calcul du score composite (moyenne pondérée)
            df['Composite_Score'] = df_score.mean(axis=1)
            
            top_scores = df.nlargest(3, 'Composite_Score')[['Brawler', 'Composite_Score']]
            for idx, row in top_scores.iterrows():
                print(f"   • {row['Brawler']}: {row['Composite_Score']:.3f}")
    
    print(f"\n✨ Le CSV nettoyé permet facilement d'effectuer tous ces calculs !")
    print(f"   Toutes les valeurs sont numériques et prêtes à l'emploi.")

if __name__ == "__main__":
    main()