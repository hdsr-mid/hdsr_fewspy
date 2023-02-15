import pandas as pd


expected_filters_sa = pd.DataFrame(
    {
        "RUW_OPVL_DEBIET_AANVOER": {"id": "RUW_OPVL_DEBIET_AANVOER", "name": "Aanvoer ivm watertekort"},
        "RUW_OPVL_DEBIET_AFVOER": {"id": "RUW_OPVL_DEBIET_AFVOER", "name": "Afvoer ivm wateroverschot"},
        "RUW_OPVL_DEBIET_SPOELING": {"id": "RUW_OPVL_DEBIET_SPOELING", "name": "Doorspoeling"},
        "RUW_OPVL_DEBIET_AKKOORD_AMSTERDAMRIJNKANAAL": {
            "id": "RUW_OPVL_DEBIET_AKKOORD_AMSTERDAMRIJNKANAAL",
            "name": "Amsterdam-Rijnkanaal",
        },
        "RUW_OPVL_DEBIET_AKKOORD_HAAK": {"id": "RUW_OPVL_DEBIET_AKKOORD_HAAK", "name": "Haak"},
        "RUW_OPVL_DEBIET_AKKOORD_OUDENDAM": {"id": "RUW_OPVL_DEBIET_AKKOORD_OUDENDAM", "name": "Oudendam"},
        "RUW_OPVL_DEBIET_AKKOORD_SLUISBODEGRAVEN": {
            "id": "RUW_OPVL_DEBIET_AKKOORD_SLUISBODEGRAVEN",
            "name": "Sluis Bodegraven",
        },
        "RUW_OPVL_DEBIET_AKKOORD_WEERDSLUIS": {"id": "RUW_OPVL_DEBIET_AKKOORD_WEERDSLUIS", "name": "Weerdsluis"},
        "RUW_OPVL_DEBIET_AKKOORD_HOLLANDSEIJSSELENLEK": {
            "id": "RUW_OPVL_DEBIET_AKKOORD_HOLLANDSEIJSSELENLEK",
            "name": "Hollandse IJssel en Lek",
        },
        "RUW_OPVL_DEBIET_AKKOORD_KWA": {"id": "RUW_OPVL_DEBIET_AKKOORD_KWA", "name": "KWA"},
        "RUW_OPVL_DEBIET_AKKOORD_OVERIGEGRENSPUNTEN": {
            "id": "RUW_OPVL_DEBIET_AKKOORD_OVERIGEGRENSPUNTEN",
            "name": "Overige grenspunten",
        },
        "RUW_OPVL_DEBIET_BALANS_AFVOERGEBIEDEN": {
            "id": "RUW_OPVL_DEBIET_BALANS_AFVOERGEBIEDEN",
            "name": "Afvoergebieden",
        },
        "RUW_OPVL_DEBIET_BALANS_BOEZEMWATERGANGEN": {
            "id": "RUW_OPVL_DEBIET_BALANS_BOEZEMWATERGANGEN",
            "name": "Boezemwatergangen",
        },
        "RUW_OPVL_WATERSTAND": {"id": "RUW_OPVL_WATERSTAND", "name": "Waterstanden"},
        "RUW_OPVL_KUNSTWERKEN_POMPVIJZEL": {"id": "RUW_OPVL_KUNSTWERKEN_POMPVIJZEL", "name": "Pompvijzel"},
        "RUW_OPVL_KUNSTWERKEN_STUW": {"id": "RUW_OPVL_KUNSTWERKEN_STUW", "name": "Stuw"},
        "RUW_OPVL_KUNSTWERKEN_SCHUIF": {"id": "RUW_OPVL_KUNSTWERKEN_SCHUIF", "name": "Schuif"},
        "RUW_OPVL_KUNSTWERKEN_DEBIETMETER": {"id": "RUW_OPVL_KUNSTWERKEN_DEBIETMETER", "name": "Debietmeter"},
        "RUW_OPVL_KUNSTWERKEN_KROOSHEK": {"id": "RUW_OPVL_KUNSTWERKEN_KROOSHEK", "name": "Krooshek"},
        "RUW_OPVL_KUNSTWERKEN_VISPASSAGE": {"id": "RUW_OPVL_KUNSTWERKEN_VISPASSAGE", "name": "Vispassage"},
        "RUW_OPVL_KUNSTWERKEN_AFSLUITER": {"id": "RUW_OPVL_KUNSTWERKEN_AFSLUITER", "name": "Afsluiter"},
        "RUW_OPVL_PEILSCHALEN": {"id": "RUW_OPVL_PEILSCHALEN", "name": "Peilschalen"},
        "RUW_OPVL_INLATEN": {"id": "RUW_OPVL_INLATEN", "name": "Inlaten"},
        "RUW_OPVL_SYSTEEM_ARK": {"id": "RUW_OPVL_SYSTEEM_ARK", "name": "Amsterdam-Rijnkanaal"},
        "RUW_OPVL_SYSTEEM_GEKAN_HOLL_IJSSEL": {
            "id": "RUW_OPVL_SYSTEEM_GEKAN_HOLL_IJSSEL",
            "name": "Gekan. Hollandse IJssel",
        },
        "RUW_OPVL_SYSTEEM_KROMME_RIJN": {"id": "RUW_OPVL_SYSTEEM_KROMME_RIJN", "name": "Kromme Rijn"},
        "RUW_OPV_SYSTEEML_LEIDSCHE_RIJN": {"id": "RUW_OPV_SYSTEEML_LEIDSCHE_RIJN", "name": "Leidsche Rijn"},
        "RUW_OPVL_SYSTEEM_MERWEDEKANAAL": {"id": "RUW_OPVL_SYSTEEM_MERWEDEKANAAL", "name": "Merwedekanaal"},
        "RUW_OPVL_SYSTEEM_OUDE_RIJN": {"id": "RUW_OPVL_SYSTEEM_OUDE_RIJN", "name": "Oude Rijn + Grecht + Wierickes"},
        "RUW_OPVL_SYSTEEM_VECHT": {"id": "RUW_OPVL_SYSTEEM_VECHT", "name": "Vecht"},
        "RUW_OPVL_SYSTEEM_STADSGRACHTEN_UTRECHT": {
            "id": "RUW_OPVL_SYSTEEM_STADSGRACHTEN_UTRECHT",
            "name": "Stadsgrachten Utrecht",
        },
        "RUW_OPVL_SYSTEEM_NEDERRIJN_LEK": {"id": "RUW_OPVL_SYSTEEM_NEDERRIJN_LEK", "name": "Nederrijn/Lek"},
        "RUW_OPVL_RAYONS_OOST": {"id": "RUW_OPVL_RAYONS_OOST", "name": "HDSR Oost"},
        "RUW_OPVL_RAYONS_WEST": {"id": "RUW_OPVL_RAYONS_WEST", "name": "HDSR West"},
        "RUW_OPVL_RAYONS_IJSSEL": {"id": "RUW_OPVL_RAYONS_IJSSEL", "name": "IJssel"},
        "RUW_OPVL_RAYONS_KROMME_RIJN": {"id": "RUW_OPVL_RAYONS_KROMME_RIJN", "name": "Kromme Rijn"},
        "RUW_OPVL_RAYONS_LEIDSCHE_RIJN": {"id": "RUW_OPVL_RAYONS_LEIDSCHE_RIJN", "name": "Leidsche Rijn"},
        "RUW_OPVL_RAYONS_OUDE_RIJN": {"id": "RUW_OPVL_RAYONS_OUDE_RIJN", "name": "Oude Rijn"},
        "MET_OPVL_MSW_DEBIET": {"id": "MET_OPVL_MSW_DEBIET", "name": "Debieten"},
        "MET_OPVL_MSW_HGTE": {"id": "MET_OPVL_MSW_HGTE", "name": "Waterstanden"},
        "RUW_OPVL": {"id": "RUW_OPVL", "name": "Oppervlaktewater (=alle mpt)"},
    }
)

expected_owd_filters_prd = pd.DataFrame(
    {
        "owdapi-opvlwater-noneq": {"id": "owdapi-opvlwater-noneq", "name": "non-equi"},
        "owdapi-opvlwater-15min": {"id": "owdapi-opvlwater-15min", "name": "15-min"},
        "owdapi-opvlwater-hour": {"id": "owdapi-opvlwater-hour", "name": "uur"},
        "owdapi-opvlwater-day": {"id": "owdapi-opvlwater-day", "name": "dag"},
        "owdapi-opvlwater-month": {"id": "owdapi-opvlwater-month", "name": "maand"},
        "owdapi-opvlwater-year": {"id": "owdapi-opvlwater-year", "name": "jaar"},
        "owdapi-grondwater-noneq": {"id": "owdapi-grondwater-noneq", "name": "non-equi"},
        "owdapi-grondwater-day": {"id": "owdapi-grondwater-day", "name": "dag"},
        "owdapi-grondwater-month": {"id": "owdapi-grondwater-month", "name": "maand"},
        "owdapi-grondwater-year": {"id": "owdapi-grondwater-year", "name": "jaar"},
        # "owdapi-neerslag-noneq": {"id": "owdapi-neerslag-noneq", "name": "non-equi"},
        "owdapi-neerslag-15min": {"id": "owdapi-neerslag-15min", "name": "15-min"},
        "owdapi-neerslag-5min": {"id": "owdapi-neerslag-5min", "name": "5-min"},
        "owdapi-neerslag-hour": {"id": "owdapi-neerslag-hour", "name": "uur"},
        "owdapi-neerslag-day": {"id": "owdapi-neerslag-day", "name": "dag"},
        "owdapi-neerslag-month": {"id": "owdapi-neerslag-month", "name": "maand"},
        "owdapi-neerslag-year": {"id": "owdapi-neerslag-year", "name": "jaar"},
        "OWD-API": {"id": "OWD-API", "name": "OWD-API"},
    }
)
