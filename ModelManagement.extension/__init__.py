
# devem ser usados Pilares Estruturais, e nao colunas arquitetonicas, para evitar
# incorrecao na área e volume total das paredes 

""" 
Validacao do Modelo___________________

# CORTES - Quantidade (len(lista todos os cortes))
# CORTES - Localização, direção, sentido
# CORTES - Representação (familia de simbolo deve ser X)
# FACHADAS - Quantidade (len(lista))

# AMBIENTES - Quantidade Total (len(lista))
# AMBIENTES - Quantidade por Pavimento (sendo nivel X o nivel do ambiente,len(lista))
# AMBIENTES - Ordem de identificação numérica
# AMBIENTES - Nome (allmodeltypename)
# AMBIENTES - Área (roomarea)

# PISOS - Quantidade
# PISOS - Nome
# PISOS - Tipo (familia?)
# PISOS - REV - Nome
# PISOS - REV - Código numérico
# PISOS - REV - Espessura
# PISOS - EST - Estrutura - Espessura
# PISOS - EST - Estrutura - Camada - Espessura
# PISOS - EST - Estrutura - Camada - Função
# PISOS - EST - Estrutura - Camada - Posicionamento relativo ao núcleo (acima/dentro/abaixo)

# ESCADAS - Quantidade
# ESCADAS - ESCADA - Quantidade de degraus
# ESCADAS - ESCADA - Lances - Posicionamento
# ESCADAS - ESCADA - Patamares - Quantidade
# ESCADAS - ESCADA - Patamares - Posicionamento
# ESCADAS - ESCADA - Nível de chegada
# ESCADAS - ESCADA - Nível de origem

# PAREDES - Tipos
# PAREDES - Posicionamento Geométrico
# PAREDES - PAREDE - Estrutura - Quantidade de Camadas
# PAREDES - PAREDE - Estrutura - Espessura


 """


""" 
POSSIVELMENTE UTEIS___________________

get parameter names
    define some_elem ...
    for param in some_elem.Parameters:
        print(param.Definition.Name) 
"""