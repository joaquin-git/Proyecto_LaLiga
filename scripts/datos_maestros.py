"""
Datos maestros usados por el generador del dataset BRONZE.

- Clubes, estadios y plantillas son REALES (aproximados a las temporadas
  2024/25 y 2025/26). Las plantillas pueden no ser exactas al 100 %.
- Años de nacimiento aproximados; día y mes de nacimiento son simulados.
- Salarios, cláusulas, estadísticas, lesiones (salvo tres casos públicos),
  partes médicos, informes de scouting, agentes y ojeadores son SIMULADOS.
- Importes de traspaso: aproximados a lo publicado en prensa, solo como
  referencia didáctica.
"""

# codigo: (nombre_oficial, nombre_corto, ciudad, estadio_principal, fuerza, nivel_salarial_M, zona, alias)
CLUBES = {
    "RMA": ("Real Madrid CF", "Real Madrid", "Madrid", "BERNABEU", 1.00, 9.0, "Centro", ["Real Madrid", "R. Madrid", "Madrid"]),
    "FCB": ("FC Barcelona", "Barça", "Barcelona", "MONTJUIC", 0.95, 7.0, "Cataluña-Baleares", ["Barça", "FC Barcelona", "Barcelona"]),
    "ATM": ("Atlético de Madrid", "Atlético", "Madrid", "METROPOLITANO", 0.75, 5.5, "Centro", ["Atlético de Madrid", "Atleti", "At. Madrid"]),
    "ATH": ("Athletic Club", "Athletic", "Bilbao", "SANMAMES", 0.55, 2.8, "Norte", ["Athletic Club", "Athletic Bilbao", "Athletic"]),
    "RSO": ("Real Sociedad de Fútbol", "Real Sociedad", "San Sebastián", "ANOETA", 0.40, 2.6, "Norte", ["Real Sociedad", "R. Sociedad"]),
    "VIL": ("Villarreal CF", "Villarreal", "Villarreal", "CERAMICA", 0.50, 2.6, "Levante", ["Villarreal", "Villarreal CF"]),
    "BET": ("Real Betis Balompié", "Betis", "Sevilla", "VILLAMARIN", 0.45, 2.4, "Sur", ["Betis", "Real Betis"]),
    "SEV": ("Sevilla FC", "Sevilla", "Sevilla", "PIZJUAN", 0.15, 2.4, "Sur", ["Sevilla", "Sevilla FC"]),
    "VAL": ("Valencia CF", "Valencia", "Valencia", "MESTALLA", 0.15, 1.8, "Levante", ["Valencia", "Valencia CF"]),
    "CEL": ("RC Celta de Vigo", "Celta", "Vigo", "BALAIDOS", 0.30, 1.5, "Norte", ["Celta", "Celta de Vigo", "RC Celta"]),
    "OSA": ("CA Osasuna", "Osasuna", "Pamplona", "SADAR", 0.25, 1.3, "Norte", ["Osasuna", "CA Osasuna"]),
    "GIR": ("Girona FC", "Girona", "Girona", "MONTILIVI", 0.15, 2.0, "Cataluña-Baleares", ["Girona", "Girona FC"]),
    "GET": ("Getafe CF", "Getafe", "Getafe", "COLISEUM", 0.10, 1.2, "Centro", ["Getafe", "Getafe CF"]),
    "RAY": ("Rayo Vallecano de Madrid", "Rayo Vallecano", "Madrid", "VALLECAS", 0.25, 1.1, "Centro", ["Rayo Vallecano", "Rayo"]),
    "MLL": ("RCD Mallorca", "Mallorca", "Palma", "SONMOIX", 0.20, 1.3, "Cataluña-Baleares", ["Mallorca", "RCD Mallorca"]),
    "ALA": ("Deportivo Alavés", "Alavés", "Vitoria-Gasteiz", "MENDIZORROZA", 0.05, 1.0, "Norte", ["Alavés", "Deportivo Alavés", "Alaves"]),
    "ESP": ("RCD Espanyol de Barcelona", "Espanyol", "Cornellà de Llobregat", "RCDE", 0.05, 1.1, "Cataluña-Baleares", ["Espanyol", "RCD Espanyol", "Español"]),
    "LPA": ("UD Las Palmas", "Las Palmas", "Las Palmas de Gran Canaria", "GRANCANARIA", -0.10, 1.0, "Sur", ["Las Palmas", "UD Las Palmas"]),
    "LEG": ("CD Leganés", "Leganés", "Leganés", "BUTARQUE", -0.10, 0.8, "Centro", ["Leganés", "CD Leganés", "Leganes"]),
    "VLL": ("Real Valladolid CF", "Valladolid", "Valladolid", "ZORRILLA", -0.40, 0.8, "Centro", ["Valladolid", "Real Valladolid", "Pucela"]),
    "LEV": ("Levante UD", "Levante", "Valencia", "CIUTAT", -0.10, 0.75, "Levante", ["Levante", "Levante UD"]),
    "ELC": ("Elche CF", "Elche", "Elche", "MARTINEZVALERO", 0.00, 0.8, "Levante", ["Elche", "Elche CF"]),
    "OVI": ("Real Oviedo", "Oviedo", "Oviedo", "TARTIERE", -0.15, 0.75, "Norte", ["Oviedo", "Real Oviedo"]),
}

# codigo: (nombre, ciudad, aforo)
ESTADIOS = {
    "BERNABEU": ("Santiago Bernabéu", "Madrid", 83186),
    "MONTJUIC": ("Estadi Olímpic Lluís Companys", "Barcelona", 55926),
    "JOHANCRUYFF": ("Estadi Johan Cruyff", "Sant Joan Despí", 6000),
    "CAMPNOU": ("Spotify Camp Nou", "Barcelona", 45401),
    "METROPOLITANO": ("Riyadh Air Metropolitano", "Madrid", 70460),
    "SANMAMES": ("San Mamés", "Bilbao", 53289),
    "ANOETA": ("Reale Arena", "San Sebastián", 39313),
    "CERAMICA": ("Estadio de la Cerámica", "Villarreal", 23008),
    "VILLAMARIN": ("Benito Villamarín", "Sevilla", 60721),
    "PIZJUAN": ("Ramón Sánchez-Pizjuán", "Sevilla", 43883),
    "MESTALLA": ("Mestalla", "Valencia", 49430),
    "BALAIDOS": ("Abanca-Balaídos", "Vigo", 24870),
    "SADAR": ("El Sadar", "Pamplona", 23576),
    "MONTILIVI": ("Estadi Municipal de Montilivi", "Girona", 14624),
    "COLISEUM": ("Coliseum", "Getafe", 16500),
    "VALLECAS": ("Estadio de Vallecas", "Madrid", 14708),
    "SONMOIX": ("Estadi Mallorca Son Moix", "Palma", 26020),
    "MENDIZORROZA": ("Mendizorroza", "Vitoria-Gasteiz", 19840),
    "RCDE": ("Stage Front Stadium", "Cornellà de Llobregat", 40000),
    "GRANCANARIA": ("Estadio de Gran Canaria", "Las Palmas de Gran Canaria", 32400),
    "BUTARQUE": ("Estadio Municipal de Butarque", "Leganés", 12454),
    "ZORRILLA": ("Estadio José Zorrilla", "Valladolid", 27618),
    "CIUTAT": ("Estadi Ciutat de València", "Valencia", 26354),
    "MARTINEZVALERO": ("Estadio Manuel Martínez Valero", "Elche", 31388),
    "TARTIERE": ("Estadio Carlos Tartiere", "Oviedo", 30500),
}

CLUBES_2425 = ["RMA", "FCB", "ATM", "ATH", "RSO", "VIL", "BET", "SEV", "VAL", "CEL",
               "OSA", "GIR", "GET", "RAY", "MLL", "ALA", "ESP", "LPA", "LEG", "VLL"]
CLUBES_2526 = ["RMA", "FCB", "ATM", "ATH", "RSO", "VIL", "BET", "SEV", "VAL", "CEL",
               "OSA", "GIR", "GET", "RAY", "MLL", "ALA", "ESP", "LEV", "ELC", "OVI"]
DESCENDIDOS_2425 = ["LPA", "LEG", "VLL"]
ASCENDIDOS_2526 = ["LEV", "ELC", "OVI"]

# Formato: nombre|posicion|nacionalidad|año_nacimiento|flags
# flags: '*' = jugador estrella ; 'L=<club propietario>' = jugador cedido
PLANTILLAS_2425 = {
"RMA": """
Thibaut Courtois|POR|Bélgica|1992|*
Andriy Lunin|POR|Ucrania|1999|
Dani Carvajal|DEF|España|1992|
Éder Militão|DEF|Brasil|1998|
Antonio Rüdiger|DEF|Alemania|1993|*
David Alaba|DEF|Austria|1992|
Ferland Mendy|DEF|Francia|1995|
Fran García|DEF|España|1999|
Lucas Vázquez|DEF|España|1991|
Raúl Asencio|DEF|España|2003|
Jude Bellingham|MED|Inglaterra|2003|*
Federico Valverde|MED|Uruguay|1998|*
Aurélien Tchouaméni|MED|Francia|2000|
Eduardo Camavinga|MED|Francia|2002|
Luka Modrić|MED|Croacia|1985|*
Dani Ceballos|MED|España|1996|
Arda Güler|MED|Turquía|2005|
Kylian Mbappé|DEL|Francia|1998|*
Vinícius Júnior|DEL|Brasil|2000|*
Rodrygo|DEL|Brasil|2001|
Brahim Díaz|DEL|Marruecos|1999|
Endrick|DEL|Brasil|2006|
""",
"FCB": """
Marc-André ter Stegen|POR|Alemania|1992|*
Iñaki Peña|POR|España|1999|
Jules Koundé|DEF|Francia|1998|*
Pau Cubarsí|DEF|España|2007|
Iñigo Martínez|DEF|España|1991|
Alejandro Balde|DEF|España|2003|
Ronald Araujo|DEF|Uruguay|1999|
Gerard Martín|DEF|España|2002|
Eric García|DEF|España|2001|
Pedri|MED|España|2002|*
Frenkie de Jong|MED|Países Bajos|1997|
Marc Casadó|MED|España|2003|
Dani Olmo|MED|España|1998|
Gavi|MED|España|2004|
Fermín López|MED|España|2003|
Lamine Yamal|DEL|España|2007|*
Raphinha|DEL|Brasil|1996|*
Robert Lewandowski|DEL|Polonia|1988|*
Ferran Torres|DEL|España|2000|
Pau Víctor|DEL|España|2001|
""",
"ATM": """
Jan Oblak|POR|Eslovenia|1993|*
Juan Musso|POR|Argentina|1994|
José María Giménez|DEF|Uruguay|1995|
Robin Le Normand|DEF|España|1996|
Clément Lenglet|DEF|Francia|1995|L=FCB
Nahuel Molina|DEF|Argentina|1998|
Javi Galán|DEF|España|1994|
Reinildo Mandava|DEF|Mozambique|1994|
Marcos Llorente|DEF|España|1995|
César Azpilicueta|DEF|España|1989|
Koke|MED|España|1992|
Rodrigo De Paul|MED|Argentina|1994|
Pablo Barrios|MED|España|2003|
Conor Gallagher|MED|Inglaterra|2000|
Giuliano Simeone|MED|Argentina|2002|
Samuel Lino|MED|Brasil|1999|
Axel Witsel|MED|Bélgica|1989|
Thomas Lemar|MED|Francia|1995|
Julián Álvarez|DEL|Argentina|2000|*
Antoine Griezmann|DEL|Francia|1991|*
Alexander Sørloth|DEL|Noruega|1995|
Ángel Correa|DEL|Argentina|1995|
""",
"ATH": """
Unai Simón|POR|España|1997|*
Julen Agirrezabala|POR|España|2000|
Óscar de Marcos|DEF|España|1989|
Dani Vivian|DEF|España|1999|
Aitor Paredes|DEF|España|2000|
Yeray Álvarez|DEF|España|1995|
Yuri Berchiche|DEF|España|1990|
Iñigo Lekue|DEF|España|1993|
Adama Boiro|DEF|España|2002|
Mikel Jauregizar|MED|España|2003|
Beñat Prados|MED|España|2001|
Oihan Sancet|MED|España|2000|
Iñigo Ruiz de Galarreta|MED|España|1993|
Mikel Vesga|MED|España|1993|
Unai Gómez|MED|España|2003|
Nico Williams|DEL|España|2002|*
Iñaki Williams|DEL|Ghana|1994|
Gorka Guruzeta|DEL|España|1996|
Álex Berenguer|DEL|España|1995|
Maroan Sannadi|DEL|España|2001|
""",
"RSO": """
Álex Remiro|POR|España|1995|
Unai Marrero|POR|España|2001|
Aritz Elustondo|DEF|España|1994|
Igor Zubeldia|DEF|España|1997|
Nayef Aguerd|DEF|Marruecos|1996|
Jon Aramburu|DEF|Venezuela|2002|
Aihen Muñoz|DEF|España|1997|
Sergio Gómez|DEF|España|2000|
Javi López|DEF|España|2002|
Martín Zubimendi|MED|España|1999|*
Brais Méndez|MED|España|1997|
Luka Sučić|MED|Croacia|2002|
Pablo Marín|MED|España|2003|
Jon Ander Olasagasti|MED|España|2000|
Takefusa Kubo|DEL|Japón|2001|*
Mikel Oyarzabal|DEL|España|1997|*
Ander Barrenetxea|DEL|España|2001|
Sheraldo Becker|DEL|Surinam|1995|
Orri Óskarsson|DEL|Islandia|2004|
""",
"VIL": """
Diego Conde|POR|España|1998|
Luiz Júnior|POR|Brasil|2001|
Juan Foyth|DEF|Argentina|1998|
Raúl Albiol|DEF|España|1985|
Logan Costa|DEF|Cabo Verde|2001|
Eric Bailly|DEF|Costa de Marfil|1994|
Sergi Cardona|DEF|España|1999|
Kiko Femenía|DEF|España|1991|
Alfonso Pedraza|DEF|España|1996|
Dani Parejo|MED|España|1989|
Santi Comesaña|MED|España|1996|
Pape Gueye|MED|Senegal|1999|
Álex Baena|MED|España|2001|*
Yéremy Pino|MED|España|2002|
Ilias Akhomach|MED|Marruecos|2004|
Ramón Terrats|MED|España|2000|
Ayoze Pérez|DEL|España|1993|*
Thierno Barry|DEL|Francia|2002|
Gerard Moreno|DEL|España|1992|
Nicolas Pépé|DEL|Costa de Marfil|1995|
""",
"BET": """
Rui Silva|POR|Portugal|1994|
Adrián San Miguel|POR|España|1987|
Héctor Bellerín|DEF|España|1995|
Diego Llorente|DEF|España|1993|
Marc Bartra|DEF|España|1991|
Natan|DEF|Brasil|2001|
Romain Perraud|DEF|Francia|1997|
Ricardo Rodríguez|DEF|Suiza|1992|
Youssouf Sabaly|DEF|Senegal|1993|
Johnny Cardoso|MED|Estados Unidos|2001|
Sergi Altimira|MED|España|2001|
Isco|MED|España|1992|*
Giovani Lo Celso|MED|Argentina|1996|
Pablo Fornals|MED|España|1996|
Abde Ezzalzouli|DEL|Marruecos|2001|
Jesús Rodríguez|DEL|España|2005|
Vitor Roque|DEL|Brasil|2005|
Chimy Ávila|DEL|Argentina|1994|
""",
"SEV": """
Ørjan Nyland|POR|Noruega|1990|
Álvaro Fernández|POR|España|1998|
José Ángel Carmona|DEF|España|2002|
Loïc Badé|DEF|Francia|2000|
Kike Salas|DEF|España|2002|
Adrià Pedrosa|DEF|España|1998|
Juanlu Sánchez|DEF|España|2003|
Gonzalo Montiel|DEF|Argentina|1997|
Tanguy Nianzou|DEF|Francia|2002|
Nemanja Gudelj|MED|Serbia|1991|
Lucien Agoumé|MED|Francia|2002|
Djibril Sow|MED|Suiza|1997|
Saúl Ñíguez|MED|España|1994|L=ATM
Albert Sambi Lokonga|MED|Bélgica|1999|L=Arsenal FC/Premier League/Inglaterra
Dodi Lukébakio|DEL|Bélgica|1997|
Isaac Romero|DEL|España|2000|
Kelechi Iheanacho|DEL|Nigeria|1996|
Chidera Ejuke|DEL|Nigeria|1998|
""",
"VAL": """
Giorgi Mamardashvili|POR|Georgia|2000|*
Stole Dimitrievski|POR|Macedonia del Norte|1993|
Cristhian Mosquera|DEF|España|2004|
Mouctar Diakhaby|DEF|Francia|1996|
César Tárrega|DEF|España|2002|
José Gayà|DEF|España|1995|
Dimitri Foulquier|DEF|Francia|1993|
Jesús Vázquez|DEF|España|2003|
Pepelu|MED|España|1998|
Javi Guerra|MED|España|2003|
Enzo Barrenechea|MED|Argentina|2001|L=Aston Villa/Premier League/Inglaterra
André Almeida|MED|Portugal|2000|
Diego López|DEL|España|2002|
Luis Rioja|DEL|España|1993|
Hugo Duro|DEL|España|1999|
Dani Gómez|DEL|España|1998|
Fran Pérez|DEL|España|2002|
Rafa Mir|DEL|España|1997|L=SEV
Umar Sadiq|DEL|Nigeria|1997|
""",
"CEL": """
Vicente Guaita|POR|España|1987|
Iván Villar|POR|España|1997|
Óscar Mingueza|DEF|España|1999|
Carl Starfelt|DEF|Suecia|1995|
Marcos Alonso|DEF|España|1990|
Javi Rodríguez|DEF|España|2003|
Carlos Domínguez|DEF|España|2001|
Javi Rueda|DEF|España|2003|
Fran Beltrán|MED|España|1999|
Ilaix Moriba|MED|Guinea|2003|
Hugo Sotelo|MED|España|2003|
Damián Rodríguez|MED|Uruguay|2003|
Williot Swedberg|MED|Suecia|2004|
Iago Aspas|DEL|España|1987|*
Borja Iglesias|DEL|España|1993|L=BET
Alfon González|DEL|España|1999|
Pablo Durán|DEL|España|2001|
Jonathan Bamba|DEL|Costa de Marfil|1996|
Hugo Álvarez|DEL|España|2003|
""",
"OSA": """
Sergio Herrera|POR|España|1993|
Aitor Fernández|POR|España|1991|
Jesús Areso|DEF|España|1999|
Alejandro Catena|DEF|España|1994|
Enzo Boyomo|DEF|Camerún|2001|
Juan Cruz|DEF|España|1992|
Abel Bretones|DEF|España|2000|
Jorge Herrando|DEF|España|2001|
Lucas Torró|MED|España|1994|
Jon Moncayola|MED|España|1998|
Aimar Oroz|MED|España|2001|
Pablo Ibáñez|MED|España|1998|
Rubén García|MED|España|1993|
Iker Muñoz|MED|España|2002|
Ante Budimir|DEL|Croacia|1991|*
Bryan Zaragoza|DEL|España|2001|L=FC Bayern Múnich/Bundesliga/Alemania
Moi Gómez|DEL|España|1994|
Raúl García de Haro|DEL|España|2000|
Kike Barja|DEL|España|1997|
""",
"GIR": """
Paulo Gazzaniga|POR|Argentina|1992|
Juan Carlos Martín|POR|España|1988|
Arnau Martínez|DEF|España|2003|
David López|DEF|España|1989|
Daley Blind|DEF|Países Bajos|1990|
Ladislav Krejčí|DEF|República Checa|1999|
Miguel Gutiérrez|DEF|España|2001|
Alejandro Francés|DEF|España|2002|
Yangel Herrera|MED|Venezuela|1998|
Oriol Romeu|MED|España|1991|L=FCB
Iván Martín|MED|España|1999|
Donny van de Beek|MED|Países Bajos|1997|
Arnaut Danjuma|DEL|Países Bajos|1997|L=VIL
Bryan Gil|DEL|España|2001|
Viktor Tsygankov|DEL|Ucrania|1997|
Yáser Asprilla|DEL|Colombia|2003|
Bojan Miovski|DEL|Macedonia del Norte|1999|
Cristhian Stuani|DEL|Uruguay|1986|
Abel Ruiz|DEL|España|2000|
""",
"GET": """
David Soria|POR|España|1993|
Jiří Letáček|POR|República Checa|1999|
Djené Dakonam|DEF|Togo|1991|
Omar Alderete|DEF|Paraguay|1996|
Domingos Duarte|DEF|Portugal|1995|
Juan Iglesias|DEF|España|1998|
Diego Rico|DEF|España|1993|
Allan Nyom|DEF|Camerún|1988|
Luis Milla|MED|España|1994|
Mauro Arambarri|MED|Uruguay|1995|
Carles Pérez|MED|España|1998|
Coba da Costa|MED|Portugal|2002|
Christantus Uche|MED|Nigeria|2003|
Borja Mayoral|DEL|España|1997|
Álvaro Rodríguez|DEL|Uruguay|2004|L=RMA
Bertuğ Yıldırım|DEL|Turquía|2002|
""",
"RAY": """
Augusto Batalla|POR|Argentina|1996|
Dani Cárdenas|POR|España|1997|
Andrei Rațiu|DEF|Rumanía|1998|
Florian Lejeune|DEF|Francia|1991|
Abdul Mumin|DEF|Ghana|1998|
Pep Chavarría|DEF|España|1998|
Iván Balliu|DEF|Albania|1992|
Aridane Hernández|DEF|España|1989|
Óscar Valentín|MED|España|1994|
Unai López|MED|España|1995|
Pathé Ciss|MED|Senegal|1994|
Isi Palazón|MED|España|1994|
Óscar Trejo|MED|Argentina|1988|
Pedro Díaz|MED|España|1998|
Jorge de Frutos|DEL|España|1997|
Álvaro García|DEL|España|1992|
Randy Nteka|DEL|Angola|1997|
Sergio Camello|DEL|España|2001|
Raúl de Tomás|DEL|España|1994|
Adrián Embarba|DEL|España|1992|
""",
"MLL": """
Dominik Greif|POR|Eslovaquia|1997|
Leo Román|POR|España|2000|
Pablo Maffeo|DEF|Argentina|1997|
Martin Valjent|DEF|Eslovaquia|1995|
Antonio Raíllo|DEF|España|1991|
Johan Mojica|DEF|Colombia|1992|
José Copete|DEF|España|1999|
Toni Lato|DEF|España|1997|
Samú Costa|MED|Portugal|2000|
Omar Mascarell|MED|Guinea Ecuatorial|1993|
Manu Morlanes|MED|España|1999|
Sergi Darder|MED|España|1993|
Dani Rodríguez|MED|España|1988|
Antonio Sánchez|MED|España|1997|
Vedat Muriqi|DEL|Kosovo|1994|*
Cyle Larin|DEL|Canadá|1995|
Takuma Asano|DEL|Japón|1994|
Robert Navarro|DEL|España|2002|
Abdón Prats|DEL|España|1992|
""",
"ALA": """
Antonio Sivera|POR|España|1996|
Owono|POR|Guinea Ecuatorial|2001|
Nahuel Tenaglia|DEF|Argentina|1996|
Abdel Abqar|DEF|Marruecos|1999|
Santiago Mouriño|DEF|Uruguay|2002|
Manu Sánchez|DEF|España|2000|L=CEL
Moussa Diarra|DEF|Mali|2000|
Jonny Otto|DEF|España|1994|
Antonio Blanco|MED|España|2000|
Ander Guevara|MED|España|1997|
Jon Guridi|MED|España|1995|
Carlos Vicente|MED|España|1999|
Joan Jordán|MED|España|1994|
Carles Aleñá|MED|España|1998|
Kike García|DEL|España|1989|*
Toni Martínez|DEL|España|1997|
Abde Rebbach|DEL|Argelia|1998|
Tomás Conechny|DEL|Argentina|1998|
""",
"ESP": """
Joan García|POR|España|2001|*
Fernando Pacheco|POR|España|1992|
Omar El Hilali|DEF|Marruecos|2003|
Leandro Cabrera|DEF|Uruguay|1991|
Marash Kumbulla|DEF|Albania|2000|L=AS Roma/Serie A/Italia
Sergi Gómez|DEF|España|1992|
Carlos Romero|DEF|España|2001|
Brian Oliván|DEF|España|1994|
Alex Král|MED|República Checa|1998|
Edu Expósito|MED|España|1996|
Pol Lozano|MED|España|1999|
Pere Milla|MED|España|1992|
Jofre Carreras|MED|España|2001|
Javi Puado|DEL|España|1998|
Alejo Véliz|DEL|Argentina|2003|
Walid Cheddira|DEL|Marruecos|1998|
Irvin Cardona|DEL|Francia|1997|
Roberto Fernández|DEL|España|2002|
""",
"LPA": """
Jasper Cillessen|POR|Países Bajos|1989|
Álvaro Valles|POR|España|1997|
Dinko Horkaš|POR|Croacia|1999|
Álex Suárez|DEF|España|1993|
Mika Mármol|DEF|España|2001|
Scott McKenna|DEF|Escocia|1996|
Viti Rozada|DEF|España|1997|
Álex Muñoz|DEF|España|1994|
Marvin Park|DEF|España|2000|
Kirian Rodríguez|MED|España|1996|
Javi Muñoz|MED|España|1995|
José Campaña|MED|España|1993|
Enzo Loiodice|MED|Francia|2000|
Alberto Moleiro|MED|España|2003|*
Sandro Ramírez|DEL|España|1995|
Oli McBurnie|DEL|Escocia|1996|
Jaime Mata|DEL|España|1988|
Adnan Januzaj|DEL|Bélgica|1995|
""",
"LEG": """
Marko Dmitrović|POR|Serbia|1992|
Juan Soriano|POR|España|1997|
Valentin Rosier|DEF|Francia|1996|
Sergio González|DEF|España|1992|
Matija Nastasić|DEF|Serbia|1993|
Jorge Sáenz|DEF|España|1996|
Enric Franquesa|DEF|España|1997|
Adrià Altimira|DEF|España|2001|
Renato Tapia|MED|Perú|1995|
Seydouba Cissé|MED|Guinea|2001|
Yvan Neyou|MED|Camerún|1997|
Óscar Rodríguez|MED|España|1998|
Darko Brašanac|MED|Serbia|1992|
Juan Cruz|DEL|España|2000|
Dani Raba|DEL|España|1995|
Miguel de la Fuente|DEL|España|1999|
Sébastien Haller|DEL|Costa de Marfil|1994|L=Borussia Dortmund/Bundesliga/Alemania
Diego García|DEL|España|2000|
Munir El Haddadi|DEL|Marruecos|1995|
""",
"VLL": """
Karl Hein|POR|Estonia|2002|
André Ferreira|POR|Portugal|1996|
Luis Pérez|DEF|España|1995|
Javi Sánchez|DEF|España|1997|
Eray Cömert|DEF|Suiza|1998|L=VAL
David Torres|DEF|España|2003|
Lucas Rosa|DEF|Brasil|2000|
Cenk Özkacar|DEF|Turquía|2000|
Kike Pérez|MED|España|1997|
Stanko Jurić|MED|Croacia|1996|
Selim Amallah|MED|Marruecos|1996|
Mario Martín|MED|España|2004|L=RMA
Anuar Mohamed|MED|Marruecos|1995|
Raúl Moro|DEL|España|2002|
Iván Sánchez|DEL|España|1992|
Mamadou Sylla|DEL|Senegal|1994|
Marcos André|DEL|Brasil|1996|
Juanmi Latasa|DEL|España|2001|
Chuki|DEL|España|2004|
""",
}

# Plantillas de los ascendidos en 2025/26 (solo jugadores que ya estaban en el club;
# los que llegan por traspaso/cesión se añaden con los MOVIMIENTOS).
PLANTILLAS_ASCENDIDOS_2526 = {
"LEV": """
Mathew Ryan|POR|Australia|1992|
Pablo Cuñat|POR|España|2001|
Jeremy Toljan|DEF|Alemania|1994|
Unai Elgezabal|DEF|España|1993|
Adrián de la Fuente|DEF|España|1999|
Matías Moreno|DEF|Argentina|2003|
Diego Pampín|DEF|España|2000|
Oriol Rey|MED|España|1998|
Pablo Martínez|MED|España|1998|
Unai Vencedor|MED|España|2001|
Carlos Álvarez|MED|España|2003|*
Kervin Arriaga|MED|Honduras|1998|
Roger Brugué|DEL|España|1996|
Iván Romero|DEL|España|2001|
Karl Etta Eyong|DEL|Camerún|2003|
José Luis Morales|DEL|España|1987|
""",
"ELC": """
Matías Dituro|POR|Argentina|1987|
Álvaro Núñez|DEF|España|2000|
Pedro Bigas|DEF|España|1990|
David Affengruber|DEF|Austria|2001|
Víctor Chust|DEF|España|2000|
John Donald|DEF|España|2000|
Marc Aguado|MED|España|2000|
Aleix Febas|MED|España|1996|
Rodrigo Mendoza|MED|España|2005|
Germán Valera|MED|España|2002|
Josan|MED|España|1989|
André Silva|DEL|Portugal|1995|
Yago Santiago|DEL|España|2003|
Grady Diangana|DEL|Inglaterra|1998|
""",
"OVI": """
Aarón Escandell|POR|España|1995|
Horațiu Moldovan|POR|Rumanía|1998|
Nacho Vidal|DEF|España|1995|
David Costas|DEF|España|1995|
Dani Calvo|DEF|España|1994|
Rahim Alhassane|DEF|Níger|2002|
Lucas Ahijado|DEF|España|1995|
Santi Cazorla|MED|España|1984|*
Santiago Colombatto|MED|Argentina|1997|
Alberto Reina|MED|España|1998|
Kwasi Sibo|MED|Ghana|1998|
Leander Dendoncker|MED|Bélgica|1995|
Ilyas Chaira|DEL|Marruecos|2001|
Haissem Hassan|DEL|Francia|2002|
Federico Viñas|DEL|Uruguay|1998|
Álex Forés|DEL|España|2001|
""",
}

# Jugadores que entran en LaLiga desde fuera (no están en ninguna plantilla inicial)
NUEVOS_JUGADORES = """
Cucho Hernández|DEL|Colombia|1999|
Antony|DEL|Brasil|2000|
Rubén Vargas|DEL|Suiza|1998|
Lucas Boyé|DEL|Argentina|1996|
Trent Alexander-Arnold|DEF|Inglaterra|1998|*
Dean Huijsen|DEF|España|2005|
Álvaro Carreras|DEF|España|2003|
Franco Mastantuono|MED|Argentina|2007|
Marcus Rashford|DEL|Inglaterra|1997|*
Roony Bardghji|DEL|Suecia|2005|
Thiago Almada|MED|Argentina|2001|
Dávid Hancko|DEF|Eslovaquia|1997|
Matteo Ruggeri|DEF|Italia|2002|
Marc Pubill|DEF|España|2003|
Giacomo Raspadori|DEL|Italia|2000|
Carlos Soler|MED|España|1997|
Duje Ćaleta-Car|DEF|Croacia|1996|
Georges Mikautadze|DEL|Georgia|2000|*
Tajon Buchanan|MED|Canadá|1999|
Renato Veiga|DEF|Portugal|2003|
Junior Firpo|DEF|República Dominicana|1996|
Nelson Deossa|MED|Colombia|2000|
Alexis Sánchez|DEL|Chile|1988|
Akor Adams|DEL|Nigeria|2000|
Batista Mendy|MED|Francia|2000|
Largie Ramazani|DEL|Bélgica|2001|
Lucas Beltrán|DEL|Argentina|2001|
Filip Ugrinic|MED|Serbia|1999|
Ionuț Radu|POR|Rumanía|1997|
Ferran Jutglà|DEL|España|1999|
Víctor Muñoz|DEL|España|2003|
Vitor Reis|DEF|Brasil|2006|
Claudio Echeverri|MED|Argentina|2006|
Vladyslav Vanat|DEL|Ucrania|2002|
Dominik Livaković|POR|Croacia|1995|
Adrián Liso|DEL|España|2005|
Luiz Felipe|DEF|Italia|1997|
Alemão|DEL|Brasil|1998|
Jan Virgili|DEL|España|2006|
Mateo Joseph|DEL|España|2003|
Tyrhys Dolan|DEL|Inglaterra|2001|
Clemens Riedel|DEF|Alemania|2003|
Salomón Rondón|DEL|Venezuela|1989|
"""

# Movimientos de mercado: fecha|jugador|origen|destino|tipo|importe_eur
# origen/destino: codigo de club de LaLiga o "Club|Liga|País" (club extranjero o de otra categoría)
# Los de verano 2024 ya están reflejados en las plantillas iniciales.
MOVIMIENTOS = """
2024-07-01|Kylian Mbappé|Paris Saint-Germain/Ligue 1/Francia|RMA|Libre|0
2024-07-21|Endrick|SE Palmeiras/Brasileirão/Brasil|RMA|Traspaso|47500000
2024-08-12|Julián Álvarez|Manchester City/Premier League/Inglaterra|ATM|Traspaso|75000000
2024-08-21|Conor Gallagher|Chelsea FC/Premier League/Inglaterra|ATM|Traspaso|42000000
2024-08-19|Alexander Sørloth|VIL|ATM|Traspaso|32000000
2024-07-23|Robin Le Normand|RSO|ATM|Traspaso|34500000
2024-08-09|Dani Olmo|RB Leipzig/Bundesliga/Alemania|FCB|Traspaso|55000000
2024-08-28|Giovani Lo Celso|Tottenham Hotspur/Premier League/Inglaterra|BET|Traspaso|3000000
2024-07-01|Luka Sučić|Red Bull Salzburg/Bundesliga austriaca/Austria|RSO|Traspaso|10000000
2024-08-30|Orri Óskarsson|FC Copenhague/Superliga danesa/Dinamarca|RSO|Traspaso|20000000
2024-07-04|Thierno Barry|FC Basel/Superliga suiza/Suiza|VIL|Traspaso|14000000
2024-08-01|Bojan Miovski|Aberdeen FC/Premiership escocesa/Escocia|GIR|Traspaso|8000000
2024-08-29|Arnaut Danjuma|VIL|GIR|Cesión|0
2024-08-30|Oriol Romeu|FCB|GIR|Cesión|0
2024-07-15|Abel Ruiz|SC Braga/Liga Portugal/Portugal|GIR|Traspaso|8000000
2024-08-15|Oli McBurnie|Sheffield United/Championship/Inglaterra|LPA|Libre|0
2024-08-30|Sébastien Haller|Borussia Dortmund/Bundesliga/Alemania|LEG|Cesión|0
2024-08-30|Clément Lenglet|FCB|ATM|Cesión|0
2025-01-15|Sébastien Haller|LEG|FC Utrecht/Eredivisie/Países Bajos|Cesión|0
2025-01-24|Rui Silva|BET|Sporting CP/Liga Portugal/Portugal|Traspaso|2000000
2025-01-30|Cucho Hernández|Columbus Crew/MLS/Estados Unidos|BET|Traspaso|12000000
2025-01-31|Antony|Manchester United/Premier League/Inglaterra|BET|Cesión|0
2025-01-31|Vitor Roque|BET|SE Palmeiras/Brasileirão/Brasil|Traspaso|25500000
2025-01-31|Rubén Vargas|FC Augsburg/Bundesliga/Alemania|SEV|Traspaso|4000000
2025-01-31|Lucas Boyé|Granada CF/LaLiga Hypermotion/España|ALA|Traspaso|5000000
2025-02-03|Cyle Larin|MLL|Southampton FC/Premier League/Inglaterra|Cesión|0
2025-06-01|Trent Alexander-Arnold|Liverpool FC/Premier League/Inglaterra|RMA|Traspaso|10000000
2025-06-01|Dean Huijsen|AFC Bournemouth/Premier League/Inglaterra|RMA|Traspaso|62500000
2025-06-30|Rafa Mir|VAL|SEV|Fin de cesión|0
2025-06-30|Albert Sambi Lokonga|SEV|Arsenal FC/Premier League/Inglaterra|Fin de cesión|0
2025-06-30|Enzo Barrenechea|VAL|Aston Villa/Premier League/Inglaterra|Fin de cesión|0
2025-06-30|Bryan Zaragoza|OSA|FC Bayern Múnich/Bundesliga/Alemania|Fin de cesión|0
2025-06-30|Arnaut Danjuma|GIR|VIL|Fin de cesión|0
2025-06-30|Antony|BET|Manchester United/Premier League/Inglaterra|Fin de cesión|0
2025-06-30|Manu Sánchez|ALA|CEL|Fin de cesión|0
2025-06-30|Eray Cömert|VLL|VAL|Fin de cesión|0
2025-06-30|Mario Martín|VLL|RMA|Fin de cesión|0
2025-07-01|Clément Lenglet|FCB|ATM|Libre|0
2025-06-30|Marash Kumbulla|ESP|AS Roma/Serie A/Italia|Fin de cesión|0
2025-07-01|Álvaro Carreras|SL Benfica/Liga Portugal/Portugal|RMA|Traspaso|50000000
2025-07-01|Luka Modrić|RMA|AC Milan/Serie A/Italia|Libre|0
2025-07-01|Lucas Vázquez|RMA|Bayer Leverkusen/Bundesliga/Alemania|Libre|0
2025-07-01|Joan García|ESP|FCB|Traspaso|25000000
2025-07-01|Iñigo Martínez|FCB|Al-Nassr/Saudi Pro League/Arabia Saudí|Libre|0
2025-07-01|Reinildo Mandava|ATM|Sunderland AFC/Premier League/Inglaterra|Libre|0
2025-07-01|César Azpilicueta|ATM|SEV|Libre|0
2025-07-01|Ángel Correa|ATM|Tigres UANL/Liga MX/México|Traspaso|10000000
2025-07-01|Samuel Lino|ATM|CR Flamengo/Brasileirão/Brasil|Traspaso|22000000
2025-07-01|Johnny Cardoso|BET|ATM|Traspaso|25000000
2025-07-01|Thiago Almada|Botafogo/Brasileirão/Brasil|ATM|Traspaso|21000000
2025-07-01|Dávid Hancko|Feyenoord/Eredivisie/Países Bajos|ATM|Traspaso|26000000
2025-07-01|Marc Pubill|UD Almería/LaLiga Hypermotion/España|ATM|Traspaso|16000000
2025-07-01|Jesús Areso|OSA|ATH|Traspaso|12000000
2025-07-01|Julen Agirrezabala|ATH|VAL|Cesión|0
2025-07-01|Martín Zubimendi|RSO|Arsenal FC/Premier League/Inglaterra|Traspaso|70000000
2025-07-01|Nayef Aguerd|RSO|Olympique de Marsella/Ligue 1/Francia|Traspaso|23000000
2025-07-01|Thierno Barry|VIL|Everton FC/Premier League/Inglaterra|Traspaso|30000000
2025-07-01|Georges Mikautadze|Olympique de Lyon/Ligue 1/Francia|VIL|Traspaso|31000000
2025-07-01|Tajon Buchanan|Inter de Milán/Serie A/Italia|VIL|Traspaso|12000000
2025-07-01|Alberto Moleiro|LPA|VIL|Traspaso|16000000
2025-07-01|Santiago Mouriño|ALA|VIL|Traspaso|10000000
2025-07-01|Eric Bailly|VIL|OVI|Libre|0
2025-07-01|Álvaro Valles|LPA|BET|Libre|0
2025-07-01|Junior Firpo|Leeds United/Premier League/Inglaterra|BET|Libre|0
2025-07-01|Jesús Rodríguez|BET|Como 1907/Serie A/Italia|Traspaso|22000000
2025-07-01|Dodi Lukébakio|SEV|SL Benfica/Liga Portugal/Portugal|Traspaso|20000000
2025-07-01|Saúl Ñíguez|ATM|CR Flamengo/Brasileirão/Brasil|Libre|0
2025-07-01|Alfon González|CEL|SEV|Libre|0
2025-07-01|Giorgi Mamardashvili|VAL|Liverpool FC/Premier League/Inglaterra|Traspaso|30000000
2025-07-01|Cristhian Mosquera|VAL|Arsenal FC/Premier League/Inglaterra|Traspaso|15000000
2025-07-01|Borja Iglesias|BET|CEL|Libre|0
2025-07-01|Ladislav Krejčí|GIR|Wolverhampton Wanderers/Premier League/Inglaterra|Traspaso|25000000
2025-07-01|Miguel Gutiérrez|GIR|SSC Napoli/Serie A/Italia|Traspaso|18000000
2025-07-01|Yangel Herrera|GIR|RSO|Traspaso|5000000
2025-07-01|Axel Witsel|ATM|GIR|Libre|0
2025-07-01|Omar Alderete|GET|Sunderland AFC/Premier League/Inglaterra|Traspaso|12000000
2025-07-01|Álvaro Rodríguez|GET|ELC|Traspaso|6000000
2025-07-01|Abdel Abqar|ALA|GET|Traspaso|8000000
2025-07-01|Kike García|ALA|ESP|Libre|0
2025-07-01|Marko Dmitrović|LEG|ESP|Libre|0
2025-07-01|Valentin Rosier|LEG|OSA|Libre|0
2025-07-01|Robert Navarro|MLL|ATH|Traspaso|2500000
2025-07-01|Salomón Rondón|CF Pachuca/Liga MX/México|OVI|Libre|0
2025-07-01|Víctor Muñoz|Real Madrid Castilla/Primera Federación/España|OSA|Traspaso|3500000
2025-07-01|Adrián Liso|Real Zaragoza/LaLiga Hypermotion/España|GET|Traspaso|5000000
2025-07-01|Jan Virgili|FC Barcelona Atlètic/Primera Federación/España|MLL|Traspaso|3000000
2025-07-01|Tyrhys Dolan|Blackburn Rovers/Championship/Inglaterra|ESP|Libre|0
2025-07-01|Alexis Sánchez|Udinese Calcio/Serie A/Italia|SEV|Libre|0
2025-07-08|Pau Víctor|FCB|SC Braga/Liga Portugal/Portugal|Traspaso|12000000
2025-07-10|Roony Bardghji|FC Copenhague/Superliga danesa/Dinamarca|FCB|Traspaso|2500000
2025-07-12|Álex Baena|VIL|ATM|Traspaso|42000000
2025-07-15|Iñaki Peña|FCB|ELC|Cesión|0
2025-07-15|Adrià Pedrosa|SEV|ELC|Cesión|0
2025-07-15|Ramón Terrats|VIL|ESP|Cesión|0
2025-07-20|Akor Adams|Montpellier HSC/Ligue 1/Francia|SEV|Traspaso|10000000
2025-07-20|Batista Mendy|Trabzonspor/Süper Lig/Turquía|SEV|Traspaso|3000000
2025-07-23|Marcus Rashford|Manchester United/Premier League/Inglaterra|FCB|Cesión|0
2025-07-25|Duje Ćaleta-Car|Olympique de Lyon/Ligue 1/Francia|RSO|Traspaso|4000000
2025-07-25|Filip Ugrinic|BSC Young Boys/Superliga suiza/Suiza|VAL|Traspaso|3000000
2025-07-28|Matteo Ruggeri|Atalanta BC/Serie A/Italia|ATM|Traspaso|17000000
2025-07-30|Ionuț Radu|Venezia FC/Serie A/Italia|CEL|Traspaso|5000000
2025-07-30|Ferran Jutglà|Club Brujas/Pro League/Bélgica|CEL|Traspaso|6000000
2025-08-01|Rafa Mir|SEV|ELC|Cesión|0
2025-08-01|Arnaut Danjuma|VIL|VAL|Libre|0
2025-08-01|Renato Veiga|Chelsea FC/Premier League/Inglaterra|VIL|Traspaso|24000000
2025-08-01|Mario Martín|RMA|GET|Cesión|0
2025-08-05|Largie Ramazani|Leeds United/Premier League/Inglaterra|VAL|Cesión|0
2025-08-05|Lucas Beltrán|ACF Fiorentina/Serie A/Italia|VAL|Cesión|0
2025-08-08|Vitor Reis|Manchester City/Premier League/Inglaterra|GIR|Cesión|0
2025-08-08|Claudio Echeverri|Manchester City/Premier League/Inglaterra|GIR|Cesión|0
2025-08-10|Vladyslav Vanat|Dinamo de Kiev/Premier League ucraniana/Ucrania|GIR|Traspaso|13000000
2025-08-10|Dominik Livaković|Fenerbahçe/Süper Lig/Turquía|GIR|Cesión|0
2025-08-10|Thomas Lemar|ATM|GIR|Cesión|0
2025-08-12|Yéremy Pino|VIL|Crystal Palace/Premier League/Inglaterra|Traspaso|30000000
2025-08-12|Carlos Soler|Paris Saint-Germain/Ligue 1/Francia|RSO|Cesión|0
2025-08-14|Franco Mastantuono|River Plate/Liga Profesional/Argentina|RMA|Traspaso|45000000
2025-08-15|Bryan Zaragoza|FC Bayern Múnich/Bundesliga/Alemania|CEL|Cesión|0
2025-08-15|Christantus Uche|GET|Crystal Palace/Premier League/Inglaterra|Cesión|0
2025-08-18|Luiz Felipe|Olympique de Marsella/Ligue 1/Francia|RAY|Libre|0
2025-08-18|Alemão|CF Pachuca/Liga MX/México|RAY|Traspaso|6000000
2025-08-18|Fran Pérez|VAL|RAY|Cesión|0
2025-08-20|Giacomo Raspadori|SSC Napoli/Serie A/Italia|ATM|Traspaso|22000000
2025-08-25|Mateo Joseph|Leeds United/Premier League/Inglaterra|MLL|Cesión|0
2025-08-25|Clemens Riedel|SV Darmstadt 98/2. Bundesliga/Alemania|ESP|Traspaso|3000000
2025-09-01|Antony|Manchester United/Premier League/Inglaterra|BET|Traspaso|22000000
2026-01-02|Endrick|RMA|Olympique de Lyon/Ligue 1/Francia|Cesión|0
"""

# Lesiones públicas reales (largas) que se fijan a mano; el resto se simula.
LESIONES_REALES = [
    # jugador, fecha_lesion, fecha_alta, tipo, zona, lado
    ("Marc-André ter Stegen", "2024-09-22", "2025-04-20", "Rotura del tendón rotuliano", "Rodilla", "derecha"),
    ("Dani Carvajal", "2024-10-05", "2025-06-15", "Rotura del ligamento cruzado anterior", "Rodilla", "derecha"),
    ("Éder Militão", "2024-11-09", "2025-07-20", "Rotura del ligamento cruzado anterior", "Rodilla", "derecha"),
]

NACIONALIDAD_DOBLE = {
    "Brahim Díaz": "Marruecos; España",
    "Iñaki Williams": "Ghana; España",
    "Jon Aramburu": "Venezuela; España",
    "Omar Mascarell": "Guinea Ecuatorial; España",
    "Munir El Haddadi": "Marruecos; España",
    "Robin Le Normand": "España; Francia",
    "Ilias Akhomach": "Marruecos; España",
    "Abde Ezzalzouli": "Marruecos; España",
    "Mouctar Diakhaby": "Francia; Guinea",
    "Ilaix Moriba": "Guinea; España",
    "Owono": "Guinea Ecuatorial; España",
    "Omar El Hilali": "Marruecos; España",
    "Dean Huijsen": "España; Países Bajos",
    "Johnny Cardoso": "Estados Unidos; Brasil",
    "Takefusa Kubo": "Japón",
}

ARBITROS = [
    "José María Sánchez Martínez", "Jesús Gil Manzano", "Juan Martínez Munuera",
    "Alejandro Hernández Hernández", "Ricardo de Burgos Bengoetxea", "José Luis Munuera Montero",
    "Mateo Busquets Ferrer", "Guillermo Cuadra Fernández", "Miguel Ángel Ortiz Arias",
    "César Soto Grado", "Javier Alberola Rojas", "Isidro Díaz de Mera Escuderos",
    "Alejandro Muñiz Ruiz", "Francisco José Hernández Maeso", "Mario Melero López",
    "José Luis Guzmán Mansilla", "Juan Pulido Santana", "Víctor García Verdura",
    "Alejandro Quintero González", "Adrián Cordero Vega",
]

# --- Todo lo de abajo es FICTICIO ---
AGENCIAS = [
    ("Iberia Sports Management", "contacto@iberiasports.es", ["Álvaro Mendieta", "Raquel Santamaría"]),
    ("Goal Partners Agency", "info@goalpartners.com", ["Daniel Okafor", "Sofía Lambert"]),
    ("Atlas Football Group", "office@atlasfootball.eu", ["Marco Bellini", "Irene Castell"]),
    ("Norte Representaciones", "agentes@norterep.es", ["Gorka Larrinaga"]),
    ("Primeira Talent", "geral@primeiratalent.pt", ["Tiago Monteiro", "Helena Sousa"]),
    ("Southern Cross Sports", "hello@southerncross.com.ar", ["Martín Echeverría", "Lucía Paredes"]),
    ("Kickoff Global", "management@kickoffglobal.co.uk", ["James Whitmore"]),
    ("Mediterráneo Sport", "info@mediterraneosport.es", ["Vicent Ferrer Pla", "Nuria Casals"]),
    ("Andes Football Consulting", "contacto@andesfootball.com", ["Felipe Araya"]),
    ("Elite Pro Agency", "elite@eliteproagency.fr", ["Julien Moreau", "Amadou Diallo"]),
    ("Brasil Craques Assessoria", "contato@brasilcraques.com.br", ["Rafael Nogueira"]),
    ("Sin agente", "", ["Representación familiar"]),
]

MEDICOS = [
    "Dr. Iñigo Arrieta", "Dra. Carmen Solís", "Dr. Pablo Medina", "Dra. Laura Vidal",
    "Dr. Andrés Ocaña", "Dra. Marta Gil", "Dr. Jordi Pons", "Dra. Elena Ruiz-Toledo",
    "Dr. Sergio Landa", "Dra. Ainhoa Zubiri", "Dr. Ramón Quesada", "Dra. Beatriz Navas",
    "Dr. Hugo Carrasco", "Dra. Silvia Romero", "Dr. Fermín Abad", "Dra. Teresa Llull",
    "Dr. Óscar Villalba", "Dra. Noelia Prieto", "Dr. Julián Herrero", "Dra. Rocío Montes",
    "Dr. Xabier Goikoetxea", "Dra. Patricia Lago", "Dr. Manuel Esteve",
]

OJEADORES = [
    # nombre, email, zona, estilo
    ("Marcos Ibarra", "m.ibarra@scoutinglab.es", "Norte", "detallado"),
    ("Lucía Ferrer", "l.ferrer@scoutinglab.es", "Levante", "detallado"),
    ("Javier Ortega", "j.ortega@scoutinglab.es", "Centro", "telegrafico"),
    ("Nerea Etxeberria", "n.etxeberria@scoutinglab.es", "Cataluña-Baleares", "mixto"),
    ("Andrés Molina", "a.molina@scoutinglab.es", "Sur", "telegrafico"),
    ("Paula Benítez", "p.benitez@scoutinglab.es", "Todas", "mixto"),
]
