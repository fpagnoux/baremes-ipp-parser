sheets = {
    "baremes-ipp-prelevements-sociaux-social-security-contributions.xlsx": {
        "name": "prelevements_sociaux",
        "ignore": ["CNRACL", "IRCANTEC", "FILLON"],
    },
    "baremes-ipp-taxation-capital.xlsx": {"name": "taxation_capital"},
    "baremes-ipp-chomage-unemployment.xlsx": {"name": "chomage"},
    "baremes-ipp-retraites-pensions.xlsx": {
        "name": "retraites",
        "ignore": [
            "Sommaire (FR)",
            "Outline (EN)",
            "AOD_RG",  # valeurs de type "60 ans 9 mois"
            "AAD_RG",  # idem
            "Coeff_mino_arrco",  # Valeur en fonction de l'age de départ à la retraite, pas de la date
            "Coeff_mino_agirc",  # Valeur en fonction de l'age de départ à la retraite, pas de la date
            "Coeff_temp",  # Valeur en fonction de l'age de départ à la retraite, pas de la date
            "LA-FP-S",  # valeurs de type "60 ans 9 mois"
            "LA-FP-A",  # idem
            "AOD-FP-S",  # idem
            "AOD-FP-A",  # idem
            "AAD-FP",  # valeurs de type "Limite d'âge - 4 trimestres"
            "RAM",  # 2 colonnes '1948' qui contiennent des valeurs différentes
        ],
    },
    "baremes-ipp-marche-du-travail-labour-market.xlsx": {
        "name": "marche_travail",
        "ignore": [
            "Sommaire (FR)",
            "Outline (EN)",
            ]
    }
}
