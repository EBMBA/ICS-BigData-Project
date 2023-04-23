# Rapport Big Data 

### Projet partie 1

### 1. Le but de votre projet 

Le but de ce projet est de développer un système de recommandation d'images basé sur les préférences de l'utilisateur en utilisant Python. Le projet est divisé en plusieurs tâches, qui incluent la collecte, l'annotation, l'analyse et la visualisation des données, ainsi que la création du système de recommandation et des tests. 

La collecte de données implique le téléchargement d'un ensemble d'images et la récupération de métadonnées, à l'aide de fichiers JSON. La tâche d'étiquetage et d'annotation consiste à rechercher des sources pour des informations supplémentaires telles que des balises et des catégories, et à obtenir des informations sur les couleurs prédominantes et les tags. L'analyse de données implique la création d'un profil de préférences utilisateur en utilisant les images sélectionnées, ainsi que l'utilisation de différents types de classificateurs et d'algorithmes de regroupement pour ajouter des informations supplémentaires pour chaque image. 

La visualisation des données implique la création de graphiques et de tableaux pour afficher les caractéristiques des images téléchargées, telles que le nombre d'images disponibles pour chaque année et les différents types d'images. La tâche du système de recommandation consiste à construire un système de recommandation en utilisant des approches telles que le filtrage collaboratif, le filtrage basé sur le contenu ou une approche hybride. Les tests consistent à vérifier si les différentes fonctions du projet fonctionnent correctement. 

Le rapport final du projet doit être un document de 5 pages présentant les différentes étapes du projet, les résultats obtenus et les limites de l'approche choisie. En résumé, le but de ce projet est de créer un système de recommandation d'images personnalisé en utilisant Python en automatisant toutes les tâches liées à l'acquisition, l'annotation, l'analyse et la visualisation des données. 

 

### 2. Sources des données de vos images et leurs licences. 

### 3. Taille de vos données. 

### 4. Informations que vous avez décidé de stocker pour chaque image. 

### 5. Informations concernant les préférences de l'utilisateur 

Pour les préférences de l'utilisateur, on a décidé de stocker les informations suivantes :
- Les couleurs prédominantes de l'image
- La famille
- La localisation

### 6. Les modèles d'exploration de données et/ou d'apprentissage machine que vous avez utilisés avec les métriques obtenues. 

Afin de réaliser le système de recommandation, nous avions besoin des préférences de l'utilisateur stockées dans un fichier JSON. Les données sont donc extraites de ce fichier puis regroupées dans des tableaux correspondants à chaque image.
Par la suite un tableau contenant les résulats des préférences est également créés, il peut contenir la valeur 'favorite' si l'utilisateur a aimé la photo ou 'not_favorite' dans le cas contraire. Ces tableaux sont par la suite chargés dans des dataset pandas. 

Une fois les données d'entrée correctement préparées et formatées, nous avons pu par la suite mettre en place le système de recommandation.  

Nous avons choisi pour cela d'utiliser un classificateur forestier aléatoire qui est une méthode de classification en apprentissage automatique qui combine plusieurs arbres de décision pour produire un modèle de prédiction. Ce dernier a été choisi pour plusieurs raisons:
- il est capable de produire des modèles de prédiction très précis, ce qui est très utile pour les tâches de classification où la précision est primordiale
- il est très simple à utiliser de ne nécessite pas beaucoup de paramètres à régler
- il fourni également des information sur l'importance de chaque variable dans la décision, cela permet de comprendre les relations entre les données d'entrées et le résultat obtenu
Ses avantages en comparaison aux classificateur utilisant des machines à vecteurs de support (comme svc) est qu'il est possible de contrer le problème de sur-ajustement en changeant la taille de l'arbre.
Pour ces raisons le classicateur Random Forest nous a paru être un choix pertinent.

Une fois le système de recommandation mis en place, nous nous sommes heurté à un problème lors de nos tests. Lorsqu'un utilisateur souhaite obtenir une recommandation et fourni des données qui n'ont pas encore connues en tant que label dans notre arbre décision, cela provoque une erreur, il a donc été décidé de mettre en place de système de substitution aléatoire pour gérer ce problème. Lors que les que les utilisateurs utilisent la fonction de recommandation, nous vérifions si les valeurs fournies existent déjà dans notre arbre, si ce n'est pas le cas alors elles sont remplacées aléatoirement pas des valeurs existantes.

Nous avons par la suite poursuivi nos tests afin de d'évaluer la précision et la pertinence du système de recommandation. Pour cela, plusieurs profondeurs d'arbres on été testées, entre 2 et 5. La profondeur d'arbre est le principal élément permettant d'ajuster la précision de la recommandation, cependant une profondeur trop grande est plus susceptible de sur-ajuster les données d'entraînement, ce qui signifie qu'il sera très précis sur les données d'entraînement mais moins précis sur les nouvelles données. Dans notre cas, les données étant simple, elles ne nécessitent pas des arbres avec une grande profondeur.

Après avoir pu régler ces problèmes nous avons pu conclure nos tests du système de recommandation en utilisant des préférences fixes et non plus aléatoires et tester les prédictions pour des données présentes dans ces préférences.
Ces derniers tests nous ont permis de constater le bon fonctionnement de la fonctionnalité de recommandation et de confirmer le choix du Random Forest.


### 7. L'auto-évaluation de votre travail. 

Dans ce projet, on a mis en place un système de recommandation d'images en Python. On a réussi à collecter plus de 100 images en utilisant des données en libre accès, enregistrant toutes les métadonnées pertinentes dans des fichiers JSON. On a également annoté les images en utilisant des algorithmes de regroupement pour trouver les couleurs prédominantes et en ajoutant des tags, qui ont été saisis manuellement ou collectés auprès des utilisateurs. On a construit des profils d'utilisateurs à partir des informations recueillies en utilisant les images sélectionnées, et on a utilisé ces profils pour recommander des images pertinentes. 

On a réussi à automatiser la plupart des tâches liées à l'acquisition, l'annotation, l'analyse et la visualisation des données, ce qui a permis de gagner beaucoup de temps. Cependant, on a rencontré quelques difficultés dans la collecte des données et l'annotation des images, en particulier pour trouver des informations supplémentaires telles que les tags. 

La visualisation des données était une tâche intéressante et on a réussi à créer des graphiques pour montrer les différentes caractéristiques des images téléchargées, ainsi que les informations liées à chaque profil d'utilisateur. Enfin, on a testé le système de recommandation et a trouvé que les recommandations étaient pertinentes pour la plupart des utilisateurs. 

En conclusion, on est satisfait de notre travail et on a réussi à atteindre nos objectifs. Cependant, on pense qu'on aurait pu mieux planifier certaines tâches et trouver plus d'informations supplémentaires pour l'annotation des images. Dans l'ensemble, c'était un projet stimulant et on a appris beaucoup de choses intéressantes sur la collecte, l'annotation et la recommandation d'images. 

 

### 8. Remarques concernant les séances pratiques, les exercices et les possibilités d'amélioration. 

Concernant les exercices, j'ai remarqué qu'ils sont souvent bien conçus et pertinents pour le sujet étudié.

### 9. Conclusion 

 