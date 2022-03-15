# solvers

Nous étudions les performances d’un solveur open-source, OR-Tools, dans la résolution par Programmation par Contrainte d’un problème d’ordonnancement de tâches
entre un ensemble de satellites en orbite et un ensemble d’antennes au sol partageant des fenêtres de visibilités connues. L’objectif est de maximiser le 
nombre de tâches effectuées en un temps donnée.  A cette fin, nous proposons deux modélisations mathématiques et informatiques du problème : l’une reposant sur
l’utilisation de variables de type "intervalle" présentes dans OR-tools (modèle multivarié), l’autre considérant des variables entières et étant davantage 
indépendante des objets pré-établis dans OR-Tools (modèle univarié). Nous analysons les performances du premier modèle sur différents scénario, puis nous 
comparons les performances de nos deux modèles sur des scénarios communs. On aboutit à des résultats sur l’influence de différents paramètres dans la 
résolution tels que le choix des paires satellite-tâches, le nombre de satellites et de tâches, la période totale des tâches. Aussi, la comparaison de nos deux
modèles prouve l’efficacité computationnelle des fonctions d’OR-Tools. Enfin, nous développons les méthodes de gestion de projet que nous avons utilisées. Nous
concluons à l’efficacité de la résolution par OR-Tools malgré une explosion du temps de calcul pour des scénario de planification plus complexes.

Mots clés : OR-Tools, RCPSP, open-source, satellites


## File structures

PIE_SXS10_data - data storage

src - source code of parser and model

Examples [OR-Tools].ipynb - notebook of several examples for utilization of OR-Tools

Parser and Classes.ipynb - notebook of parser and classes
